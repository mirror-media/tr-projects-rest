# -*- coding:utf-8 -*-
from datetime import datetime
from eve import Eve
from flask import redirect, request, Response, abort
from settings import posts, ASSETS_URL, GCS_URL, ENV, REDIS_WRITE_HOST, REDIS_WRITE_PORT, REDIS_READ_HOST, \
    REDIS_READ_PORT, REDIS_AUTH, YT_API_KEY
from bson import json_util


import json
import re
import redis
import string
import time
import urllib.parse
import requests


#from helpers.metrics import MetricsMiddleware
from helpers.redis import Redisware, RedisCache
from settings import REDIS_TTL, REDIS_EXCEPTIONS

redis_read_port = int(REDIS_READ_PORT)
redis_write_port = int(REDIS_WRITE_PORT)
redis_readPool = redis.ConnectionPool(host=REDIS_READ_HOST, port=redis_read_port, password=REDIS_AUTH)
redis_read = redis.Redis(connection_pool=redis_readPool)
redis_writePool = redis.ConnectionPool(host=REDIS_WRITE_HOST, port=redis_write_port, password=REDIS_AUTH)
redis_write = redis.Redis(connection_pool=redis_writePool)

def get_full_contacts(item, key):
    """
    get all the contacts
    query string: /contacts?where={"_id": {"$in":[id1, id2, ...]}}
    """
    if key in item and item[key]:
        headers = dict(request.headers)
        tc = app.test_client()
        all_writers = ",".join(
            map(lambda x: '"' + str(x["_id"]) + '"' if type(x) is dict else '"' + str(x) + '"', item[key]))
        resp = tc.get('contacts?where={"_id":{"$in":[' + all_writers + ']}}', headers=headers)
        resp_string = str(resp.data, encoding="utf-8")
        if isinstance(resp_string, str):
            resp_data = json.loads(resp_string)
            result = []
            for i in item[key]:
                for j in resp_data['_items']:
                    if (type(i) is dict and str(j['_id']) == str(i['_id'])) or j['_id'] == str(i):
                        result.append(j)
                        continue
            item[key] = result
        # item[key] = resp_data['_items']
    return item

def get_full_relateds(item, key, endpoint = 'posts'):
    """
    get all relateds and cache result in redis
    query string: /posts?where={"_id": {"$in":[id1, id2, ...]}}
    """
    if type(item[key]) is list:
        all_relateds = ",".join(
            map(lambda x: '"' + str(x["_id"]) + '"' if type(x) is dict else '"' + str(x) + '"', item[key]))
    elif type(item[key]) is dict and "_id" in item[key]:
        all_relateds = '"' + str(item[key]["_id"]) + '"'
    if key in item and item[key]:
        headers = dict(request.headers)
        tc = app.test_client()
        resp = tc.get(endpoint + '?where={"_id":{"$in":[' + str(all_relateds) + ']}}', headers=headers)
        resp_data = json.loads(resp.data.decode("utf-8"))
        if type(item[key]) is list:
            result = []
            for i in item[key]:
                for j in resp_data['_items']:
                    if (type(i) is dict and str(j['_id']) == str(i['_id'])) or j['_id'] == str(i):
                        result.append(j)
                        continue
            item[key] = result
        elif type(item[key]) is dict:
            item[key] = resp_data['_items'][0]
        # item[key] = resp_data['_items']
    return item

def replace_imageurl(obj):
    """
    replace formal gcs storage url in 
    - brief, content. image
    - non-empty heroImage, og_image, heroVideo
    """
    for key in ['brief', 'content', 'style']:
        if key in obj:
            obj_str = json_util.dumps(obj[key])
            obj_str = obj_str.replace(GCS_URL, ASSETS_URL)
            obj[key] = json_util.loads(obj_str)
    if 'heroImage' in obj and isinstance(obj['heroImage'], dict) and 'image' in obj['heroImage']:
        image_str = json_util.dumps(obj['heroImage']['image'])
        image_str = image_str.replace(GCS_URL, ASSETS_URL)
        obj['heroImage']['image'] = json_util.loads(image_str)
    if 'og_image' in obj and isinstance(obj['og_image'], dict) and 'image' in obj['og_image']:
        image_str = json_util.dumps(obj['og_image']['image'])
        image_str = image_str.replace(GCS_URL, ASSETS_URL)
        obj['og_image']['image'] = json_util.loads(image_str)
    if 'heroVideo' in obj and isinstance(obj['heroVideo'], dict) and 'video' in obj['heroVideo']:
        video_str = json_util.dumps(obj['heroVideo']['video'])
        video_str = video_str.replace(GCS_URL, ASSETS_URL)
        obj['heroVideo']['video'] = json_util.loads(video_str)
    if 'image' in obj and isinstance(obj['image'], dict):
        video_str = json_util.dumps(obj['image'])
        video_str = video_str.replace(GCS_URL, ASSETS_URL)
        obj['image'] = json_util.loads(video_str)
    return obj


def clean_item(item, content='draft'):
    """
    delete 
    - _updated, _created
    - all except relateds/title, heroImage, slug, _id
    - sections/extend_cats, sytle, og_title, og_description, javascript, css, catogories
    - heroImage/image/iptc, gcsDir, gcsBucket
    - heroVideo/gcsDir, gcsBucket
    - brief/draft
    - content/draft
    """
    if '_updated' in item:
        del item['_updated']
    if '_created' in item:
        del item['_created']
    if 'relateds' in item:
        keep = ["title", "heroImage", "slug", "_id", "categories"]
        for r in item['relateds']:
            if isinstance(r, dict):
                for k in list(r):
                    if k not in keep:
                        del r[k]
    if 'sections' in item:
        for i in item['sections']:
            if isinstance(i, dict):
                if 'extend_cats' in i:
                    del i['extend_cats']
                if 'style' in i:
                    del i['style']
                if 'og_title' in i:
                    del i['og_title']
                if 'og_description' in i:
                    del i['og_description']
                if 'javascript' in i:
                    del i['javascript']
                if 'css' in i:
                    del i['css']
                if 'categories' in i:
                    del i['categories']
    if 'heroImage' in item and isinstance(item['heroImage'], dict) and 'image' in item['heroImage']:
        if 'iptc' in item['heroImage']['image']:
            del item['heroImage']['image']['iptc']
        if 'gcsDir' in item['heroImage']['image']:
            del item['heroImage']['image']['gcsDir']
        if 'gcsBucket' in item['heroImage']['image']:
            del item['heroImage']['image']['gcsBucket']
    if 'heroVideo' in item and isinstance(item['heroVideo'], dict) and 'video' in item['heroVideo']:
        if 'gcsDir' in item['heroVideo']['video']:
            del item['heroVideo']['video']['gcsDir']
        if 'gcsBucket' in item['heroVideo']['video']:
            del item['heroVideo']['video']['gcsBucket']
    if content != 'draft' and 'brief' in item and isinstance(item['brief'], dict) and 'draft' in item['brief']:
        del item['brief']['draft']
    if content != 'draft' and 'content' in item and isinstance(item['content'], dict) and 'draft' in item['content']:
        del item['content']['draft']
    return item


def before_returning_posts(response):
    """
    For each post data
    - Delete brief/draft, content/draft
    - If clean=content in query, also delete brief/html, content/html
    - If post/style is 'script' wrap the <p> in content/html with <div>
    - Replace image url
    - If related=full, and 'style' is 'photography', get_full_related
    - clean_item
    """
    related = request.args.get('related')
    clean = request.args.get('clean')
    keep = request.args.get('keep')
    tag = request.args.get('tag')
    if '_items' in response and isinstance(response['_items'], list):
        items = response['_items']
        for item in items:
            item["word_count"] = 0
            if 'content' in item and isinstance(item['content'], dict) and 'html' in item['content']:
                item['word_count'] = len(item['content']['html'])
            if clean == 'content':
                if 'brief' in item and isinstance(item['brief'], dict) and 'html' in item['brief']:
                    del item['brief']['html']
                if 'content' in item and isinstance(item['content'], dict) and 'html' in item['content']:
                    item['word_count'] = len(item['content']['html'])
                    del item['content']['html']
            if 'style' in item and item["style"] == 'script':
                script_parsing = item['content']['html']
                scenes = script_parsing.split("<p><code>page</code></p>")
                page_div = "".join(map(lambda x: '<div class="page">' + x + '</div>', scenes))
                item['content']['html'] = page_div
            replace_imageurl(item)
            # if related == 'full' and item['style'] == 'photography':
            if related == 'article':
                if 'heroVideo' in item and isinstance(item['heroVideo'], dict):
                    item = get_full_relateds(item, 'heroVideo', 'videos')
            if related == 'full':
                item = get_full_relateds(item, 'relateds')
            if related == 'cultureposts':
                item = get_full_relateds(item, 'relateds', 'cultureposts')
            item = clean_item(item, keep)
        return response
    else:
        abort(404)


def before_returning_albums(response):
    """
    - delete brief/draft and brief/apiData in albums
    - if replace!= false, replace the image url in albums
    - if writer=full, get all the contacts for vocals
    """
    writer = request.args.get('writers')
    replace = request.args.get('replace')
    items = response['_items']
    for item in items:
        item = clean_item(item)
        if 'brief' in item and isinstance(item['brief'], dict) and 'draft' in item['brief'] and 'apiData' in item[
            'brief']:
            del item['brief']['draft']
            del item['brief']['apiData']
        if replace != 'false':
            replace_imageurl(item)
        if writer == 'full':
            item = get_full_contacts(item, 'vocals')
    return response


def before_returning_meta(response):
    """
    - delete brief/draft and brief/apiData in meta
    - if replace!= false, replace the image url in meta
    - if related=full, or related=full but there are relateds in response,
    get all the related for meta
    """
    related = request.args.get('related')
    replace = request.args.get('replace')
    items = response['_items']
    for item in items:
        item = clean_item(item)
        if 'brief' in item and isinstance(item['brief'], dict) and 'draft' in item['brief'] and 'apiData' in item[
            'brief']:
            del item['brief']['draft']
            del item['brief']['apiData']
        if replace != 'false':
            replace_imageurl(item)
        if related == 'full':
            item = get_full_relateds(item, 'relateds')
        else:
            if related == 'false' and 'relateds' in item:
                del item['relateds']
    return response

def before_returning_watches(response):
    """
    - if replace!= false, replace the image url in meta
    - if related=full, or related=full but there are relateds in response,
    get all the related for meta
    """
    related = request.args.get('related')
    replace = request.args.get('replace')
    items = response['_items']
    for item in items:
        if related == 'full':
            item = get_full_relateds(item, 'relateds')
            item = get_full_relateds(item, 'relatedwatch', 'watches')
        else:
            if related == 'false' and 'relateds' in item:
                del item['relateds']
        if replace != 'false':
            replace_imageurl(item)
    return response

def before_returning_listing(response):
    """
    Delete brief/draft, apiData
    Fill in heroVideo/coverPhoto, but only keep image,_id, description, tags, createTime
    """
    if '_items' in response and isinstance(response['_items'], list):
        for item in response['_items']:
            item = clean_item(item)
            if 'brief' in item and isinstance(item['brief'], dict) and 'draft' in item['brief'] and 'apiData' in item[
                'brief']:
                del item['brief']['draft']
                del item['brief']['apiData']
            if 'heroVideo' in item and isinstance(item['heroVideo'], dict) and 'coverPhoto' in item['heroVideo'] and \
                    item['heroVideo']['coverPhoto']:
                headers = dict(request.headers)
                tc = app.test_client()
                cover_photo = str(item['heroVideo']['coverPhoto'])
                resp = tc.get('images?where={"_id":{"$in":["' + cover_photo + '"]}}', headers=headers)
                resp_data = json_util.loads(resp.data.decode("utf-8"))
                if '_items' in resp_data and len(resp_data['_items']) > 0:
                    result = {x: resp_data['_items'][0][x] for x in
                              ('image', '_id', 'description', 'tags', 'createTime')}
                    item['heroVideo']['coverPhoto'] = result
            replace_imageurl(item)
    else:
        print(response)
    return response


def before_returning_choices(response):
    """
    choices become full_relateds choices, but delete:
    - content, relateds. writers, photographers, camera_man, sections, topics, vocals, tags
    - brief/apiData, draft
    """
    for item in response['_items']:
        item = get_full_relateds(item, 'choices')
        for i in item['choices']:
            if 'content' in i:
                del i['content']
            if 'relateds' in i:
                del i['relateds']
            if 'brief' in i:
                if 'apiData' in i['brief']:
                    del i['brief']['apiData']
                if 'draft' in i['brief']:
                    del i['brief']['draft']
            if 'writers' in i:
                del i['writers']
            if 'photographers' in i:
                del i['photographers']
            if 'camera_man' in i:
                del i['camera_man']
            if 'sections' in i:
                del i['sections']
            if 'topics' in i:
                del i['topics']
            if 'vocals' in i:
                del i['vocals']
            if 'tags' in i:
                del i['tags']
    return response


def before_returning_topics(response):
    """
    delete brief/apiData, draft
    """
    for item in response['_items']:
        if 'brief' in item:
            if 'apiData' in item['brief']:
                del item['brief']['apiData']
            if 'draft' in item['brief']:
                del item['brief']['draft']
        replace_imageurl(item)
    return response


def before_returning_sections(response):
    """
    sort section
    """
    items = response['_items']
    sortedItems = sorted(items, key=lambda x: x["sortOrder"])
    response['_items'] = sortedItems
    return response


def remove_extra_fields(item):
    accepted_fields = list(schema)
    for field in list(item):
        if field not in accepted_fields and field != '_id':
            del item[field]


def pre_get_callback(resource, request, lookup):
    """
    If requested resource is posts or meta, and isCampaign=true
    add additional lookup in the query
    """
    max_results = request.args.get('max_results')
    if max_results is not None and int(max_results) > 100:
        abort(404)
    isCampaign = request.args.get('isCampaign')
    if resource == 'posts' or resource == 'meta':
        if isCampaign:
            if isCampaign == 'true':
                lookup.update({"isCampaign": True})
            elif isCampaign == 'false':
                lookup.update({"isCampaign": False})
        elif isCampaign is None:
            lookup.update({"isCampaign": False})


def generate_data(keywords, section, max_results=100, page=1):

    section_id = {"時事": "57e1e0e5ee85930e00cad4e9",
                  "娛樂": "57e1e11cee85930e00cad4ea",
                  "財經理財": "596441d04bbe120f002a319a",
                  "人物": "596441604bbe120f002a3197",
                  "國際": "5964400d4bbe120f002a3191",
                  "美食旅遊": "57dfe399ee85930e00cad4d6",
                  "瑪法達": "5971aa8ce531830d00e32812",
                  "文化": "5964418a4bbe120f002a3198",
                  "汽車鐘錶": "57dfe3b0ee85930e00cad4d7",
                  "最新": "57e1e153ee85930e00cad4eb"
                  }
    if keywords is not None:
        keywords = keywords.split('%20')
    else:
        keywords = []
    should = []
    must = [{"multi_match": {"query": keyword,
                             "type": "phrase",
                             "fields": ["title^2", "content", "writers.name"]
                             }
             } for keyword in keywords]
    must.append({"match": {"isAudioSiteOnly": False}})
    if section:
        must.append({"match": {"sections._id": section_id[section]}})
    offset = (page - 1) * max_results
    data = {"from": 0 + offset, "size": max_results,
            "query": {
                "bool": {
                    "must": must,
                    "should": should
                }

            },
            "sort": [
                {"publishedDate": {"order": "desc"}},
                "_score"
            ]
            }
    return data

def youtube_endpoint(params, endpoint):
    youtube_api_endpoint = "https://www.googleapis.com/youtube/v3/"
    # print("CURRENT URI: ", "{}{}?{}&key={}".format(youtube_api_endpoint, endpoint, params, YT_API_KEY))
    
    return "{}{}?{}&key={}".format(youtube_api_endpoint, endpoint, params, YT_API_KEY)


def request_api(params, endpoint):
    r = requests.get(youtube_endpoint(params, endpoint))
    try:
        return r.json()
    except:
        return []

# data = generate_data('蔡英文','最新')

# app = Eve(auth=RolesAuth)
app = Eve()

# These two event hooks seems deprecated
app.on_replace_article += lambda item, original: remove_extra_fields(item)
app.on_insert_article += lambda items: remove_extra_fields(items[0])

# Before return json, refining data content for posts, albums, meta, listing, choices, topics, sections
app.on_fetched_resource_posts += before_returning_posts
app.on_fetched_resource_cultureposts += before_returning_posts
app.on_fetched_resource_albums += before_returning_albums
app.on_fetched_resource_meta += before_returning_meta
app.on_fetched_resource_watches += before_returning_watches
app.on_fetched_resource_listing += before_returning_listing
app.on_fetched_resource_choices += before_returning_choices
app.on_fetched_resource_topics += before_returning_topics
app.on_fetched_resource_sections += before_returning_sections

# Grand scale modification
app.on_pre_GET += pre_get_callback

# Hooks for refining duplicate endpoints
app.on_fetched_resource_getlist += before_returning_listing
app.on_fetched_resource_getmeta += before_returning_meta
app.on_fetched_resource_getposts += before_returning_posts

# Enable metrics middle layer
#MetricsMiddleware(app)
# Enable redis middleware
redis_cache = RedisCache(read_target=redis_read, write_target=redis_write)
app.wsgi_app = Redisware(app.wsgi_app, rules=REDIS_EXCEPTIONS, cache=redis_cache, ttl_config=REDIS_TTL)


@app.route("/sections-featured", methods=['GET', 'POST'])
def get_sections_latest():
    response = {"_items": {},
                "_links": {
                    "self": {"href": "sections-latest", "title": "sections latest"},
                    "parent": {"parent": "/", "title": "Home"}}}
    headers = dict(request.headers)
    content = request.args.get('content') or 'posts'
    tc = app.test_client()
    resp = tc.get('/sections', headers=headers)
    resp_header = dict(resp.headers)
    if "Content-Length" in headers:
        del headers["Content-Length"]
    resp_data = json_util.loads(resp.data.decode("utf-8"))
    if ("_error" not in resp_data and "_items" in resp_data):
        section_items = resp_data["_items"]
        section_items = sorted(section_items, key=lambda x: x["sortOrder"])
    else:
        section_items = {"_items": []}

    for item in section_items:
        if (item['name'] == 'foodtravel'):
            if (content == 'meta'):
                endpoint = 'getmeta'
            else:
                endpoint = 'getlist'
            sec_resp = tc.get('/' + endpoint + '?where={"sections":"' + item[
                '_id'] + '","isFeatured":true}&max_results=5&sort=-publishedDate', headers=headers)
            resp_header = dict(sec_resp.headers)
            sec_items = json_util.loads(sec_resp.data.decode("utf-8"))
            if '_error' not in sec_items and "_items" in sec_items:
                # response[item['name']] = sec_items['_items']
                for sec_item in sec_items:
                    clean_item(sec_item)
                    replace_imageurl(sec_item)
                response['_items'][item['name']] = sec_items['_items']
    return Response(json_util.dumps(response), headers=resp_header)


@app.route("/timeline/<topicId>", methods=['GET'])
def get_timeline(topicId):
    if topicId:
        item_ids = []
        activities_data = []
        response = {}
        response['topic'] = None
        activities = {}
        headers = dict(request.headers)
        tc = app.test_client()
        topic_url = '/topics?where={"_id":"' + topicId + '"}'
        topic_resp = tc.get(topic_url, headers=headers)
        topic_data = json_util.loads(topic_resp.data.decode("utf-8"))
        if "_items" in topic_data and len(topic_data["_items"]) > 0:
            topic_data["_items"][0] = clean_item(topic_data["_items"][0])
            if 'brief' in topic_data["_items"][0] and 'apiData' in topic_data["_items"][0]['brief']:
                del topic_data["_items"][0]['brief']['apiData']
            replace_imageurl(topic_data["_items"][0])
            response['topic'] = topic_data["_items"][0]
        activity_uri = '/activities?where={"topics":"' + topicId + '"}&max_results=40'
        resp = tc.get(activity_uri, headers=headers)
        resp_header = dict(resp.headers)
        activities_data = json_util.loads(resp.data.decode("utf-8"))
        if "_items" not in activities_data:
            activities_data["_items"] = []
        for item in activities_data["_items"]:
            item = clean_item(item)
            replace_imageurl(item)
            item_ids.append(item["_id"])
            if "topics" in item:
                if isinstance(item['topics'], dict):
                    # remove the dulplication topic meta
                    del item["topics"]
                activities[item['_id']] = item
        id_string = ",".join(map(lambda x: '"' + x + '"', item_ids))
        featured_nodes = '/nodes?where={"activity":{"$in":[' + id_string + ']},"isFeatured":true}&max_results=40'
        resp = tc.get(featured_nodes, headers=headers)
        node_data = json_util.loads(resp.data.decode("utf-8"))
        if "sort" in response["topic"] and response["topic"]["sort"] == 'desc':
            reverse = True
        else:
            reverse = False
        if "_items" in node_data:
            response["nodes"] = sorted(node_data["_items"], key=lambda x: datetime.strptime(x["nodeDate"], '%Y/%m/%d'),
                                       reverse=reverse)
        if "_meta" in node_data:
            response["_meta"] = node_data["_meta"]
        if "nodes" in response:
            for node in response["nodes"]:
                node = clean_item(node)
                if "content" in node and "html" in node["content"]:
                    del node["content"]["html"]
                replace_imageurl(node)
                if "activity" in node and "_id" in node["activity"] and node["activity"]["_id"] in activities:
                    node["activity"] = activities[node["activity"]["_id"]]
        return Response(json_util.dumps(response), headers=resp_header)
    else:
        abort(404)


@app.route("/combo", methods=['GET'])
def handle_combo():
    start = time.time()
    endpoints = {
        'posts': '/posts?sort=-publishedDate&clean=content&where={"style":{"$nin":["projects", "readr"]}}',
        'sectionfeatured': '/sections-featured?content=meta',
        'choices': '/editorchoices',
        'meta': '/getmeta?sort=-publishedDate&clean=content&related=full',
        'sections': '/sections?sort=sortOrder&max_results=20',
        'topics': '/topics?sort=sortOrder&max_results=12',
        'posts-vue': '/getlist?sort=-publishedDate&clean=content&max_results=20&related=false&isAudioSiteOnly=false',
        'projects': 'getlist?where={"style":{"$in":["projects", "readr"]}}&sort=-publishedDate&related=false'
    }
    response = {"_endpoints": {},
                "_links": {
                    "self": {"href": "sections-latest", "title": "sections latest"},
                    "parent": {"parent": "/", "title": "Home"}}}
    headers = dict(request.headers)
    start = time.time()
    tc = app.test_client()
    req = request.args.getlist('endpoint')
    for action in req:
        if action in endpoints:
            action_resp = tc.get(endpoints[action], headers=headers)
            headers = action_resp.headers
            action_data = json.loads(action_resp.data.decode("utf-8"))
            if "_error" not in action_data and "_items" in action_data and len(action_data["_items"]) > 0:
                if '_meta' in action_data:
                    response['_meta'] = action_data['_meta']
                if action == 'choices':
                    response["_endpoints"][action] = {}
                    response["_endpoints"][action]['_items'] = []
                    for item in action_data["_items"]:
                        if "choices" in item:
                            response["_endpoints"][action]['_items'].append(item["choices"])
                    #print(response["_endpoints"][action])
                else:
                    response["_endpoints"][action] = action_data
                for item in response["_endpoints"][action]["_items"]:
                    replace_imageurl(item)
    # If there is no request args for endpoint, set the header Content-Type to json
    if not ('Content-Type' in headers and headers['Content-Type'] == "application/json"):
        headers['Content-Type'] = "application/json"
    return Response(json_util.dumps(response), headers=headers)


@app.route("/posts-alias", methods=['GET', 'POST'])
def get_posts_byname():
    allow_collections = ['sections', 'categories', 'tags', 'topics']
    headers = dict(request.headers)
    tc = app.test_client()
    collection = request.args.get('collection')
    name = request.args.get('name')
    content = request.args.get('content')
    if content == 'meta':
        endpoint = 'getmeta'
    else:
        endpoint = 'posts'
    if collection in allow_collections:
        if collection == 'categories':
            table = 'postcategories'
        else:
            table = collection
        r = tc.get("/" + table + "/" + name, headers=headers)
        rs_data = json_util.loads(r.data.decode("utf-8"))
        if "_error" not in rs_data and "_id" in rs_data:
            collection_id = rs_data['_id']
            req = '/' + endpoint + '?where={"' + collection + '":"' + collection_id + '"}'
            for key in dict(request.args):
                if key != 'collection' and key != 'name':
                    req += '&' + key + '=' + request.args.get(key)
            resp = tc.get(req, headers=headers)
            resp_data = json_util.loads(resp.data.decode("utf-8"))
            for i in resp_data['_items']:
                replace_imageurl(i)
            return Response(json_util.dumps(resp_data), headers=resp.headers)
        else:
            return r
    else:
        r = tc.get("/posts")
    return r


@app.route('/search', methods=['GET'])
def search():
    """An API endpoint to call mirror search engine
    keywords: Keywords needs to be searched, sep by blank space
    section: predefined in website
    max_result : results shown per page

    Returns:
        [list] -- List of json
    """
    ES_HOST = "textsearch-elasticsearch-coordinating-only.text-search.svc.cluster.local"
    ESurl = 'http://' + ES_HOST + ":9200/plate.posts/_doc/_search"
    keywords = request.args.get('keywords')
    section = request.args.get('section')
    max_results = request.args.get('max_results')
    page = request.args.get('page')
    # size = max_result * page
    
    max_results = int(max_results) if max_results else 100
    page = int(page) if page else 1

    headers = {'Content-Type': 'application/json'}
    
    r = requests.post(ESurl, json=generate_data(keywords, section, max_results=max_results, page=page))

    r.encoding = 'utf-8'
    #print(r.json())
    if 'hits' in r.json() and 'hits' in r.json()['hits'] and not r.json()['hits']['hits']:
        for h in r.json()['hits']['hits']:
            if "_source" in h and "content" in h["_source"]:
                del h["_source"]["content"]
        r = requests.post(ESurl, json=generate_data(keywords, section='', max_results=max_results, page=page))
    r.encoding = 'utf-8'
    r.close()
    #return Response(json_util.dumps(r.text), headers=headers)
    return Response(json_util.dumps(r.json()), headers=headers)


@app.route('/youtube/search', methods=['GET'])
def yt_search():
    endpoint = 'search'
    params = request.query_string.decode("utf-8")
    search_result_returned = request_api(params, endpoint)

    if search_result_returned:
        if "error" in search_result_returned.keys():
            print(search_result_returned)
            abort(400)
        else:
            if "pageInfo" in search_result_returned.keys():
                del search_result_returned["pageInfo"]
            return Response(json_util.dumps(search_result_returned), headers={'Content-Type': 'application/json'})
    else:
        abort(204)


@app.route('/youtube/videos', methods=['GET'])
def yt_videos():
    endpoint = 'videos'
    params = request.query_string.decode("utf-8")
    video_items_returned = request_api(params, endpoint)

    if video_items_returned:
        if "error" in video_items_returned.keys():
            print(video_items_returned)
            abort(400)
        else:
            if "pageInfo" in video_items_returned.keys():
                del video_items_returned["pageInfo"]
            return Response(json_util.dumps(video_items_returned), headers={'Content-Type': 'application/json'})
    else:
        abort(204)


@app.route('/youtube/channels', methods=['GET'])
def yt_channels():
    endpoint = 'channels'
    params = request.query_string.decode("utf-8")
    channel_items_returned = request_api(params, endpoint)

    if channel_items_returned:
        if "error" in channel_items_returned.keys():
            abort(400)
        else:
            if "pageInfo" in channel_items_returned.keys():
                del channel_items_returned["pageInfo"]
            return Response(json_util.dumps(channel_items_returned), headers={'Content-Type': 'application/json'})
    else:
        abort(204)

@app.route("/youtube/playlistItems", methods=['GET'])
def youtube():
    endpoint = 'playlistItems'
    params = request.query_string.decode("utf-8")
    playlist_items_returned = request_api(params, endpoint)

    if playlist_items_returned:
        if "error" in playlist_items_returned.keys():
            abort(400)
        else:
            if "pageInfo" in playlist_items_returned.keys():
                del playlist_items_returned["pageInfo"]
            return Response(json_util.dumps(playlist_items_returned), headers={'Content-Type': 'application/json'})
    else:
        abort(204)


@app.route("/converthtml", methods=["POST"])
def convert2draft():
    """
    An API endpoint receives json formatted data like {"html": "<html>...</html>"} to convert html into draft format
    {"draft": {"draft": {}, "html": }}
    Returns:
        [json] -- {"draft": dict, "html": str, "apiData": List}
    """
    from convert_html.draft import convert_html_to_draft

    input_text = request.data
    html = input_text.decode('utf-8')
    if html:
        draft = convert_html_to_draft(html)
        return draft
    else:
        abort(400)

@app.route("/converttext", methods=["POST"])
def convert_from_text():
    from convert_html.draft import text_to_draft
    import html

    input_text = request.data.decode('utf-8')
    text = html.escape(input_text)

    draft = text_to_draft(text)
    if draft:
        return draft
    else:
        abort(400)

if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0', port=8080, threaded=True, debug=True)
