# -*- coding:utf-8 -*-
from datetime import datetime
from eve import Eve
from flask import redirect, request, Response, abort
from multiprocessing import Process
from settings import posts, ASSETS_URL, GCS_URL, ENV, REDIS_WRITE_HOST, REDIS_WRITE_PORT, REDIS_READ_HOST, REDIS_READ_PORT, REDIS_AUTH

import json
import random
import redis
import string
import sys, getopt
import time
import urllib.parse

from middleware import MetricsMiddleware

redis_read_port = int(REDIS_READ_PORT)
redis_write_port = int(REDIS_WRITE_PORT)
redis_readPool = redis.ConnectionPool(host = REDIS_READ_HOST, port = redis_read_port, password = REDIS_AUTH)
redis_read = redis.Redis(connection_pool=redis_readPool)
redis_writePool = redis.ConnectionPool(host = REDIS_WRITE_HOST, port = redis_write_port, password = REDIS_AUTH)
redis_write = redis.Redis(connection_pool=redis_writePool)

def get_full_contacts(item, key):
    """
    get all the contacts
    query string: /contacts?where={"_id": {"$in":[id1, id2, ...]}}
    """
    if key in item and item[key]:
        headers = dict(request.headers)
        tc = app.test_client()
        all_writers =  ",".join(map(lambda x: '"' + str(x["_id"]) + '"' if type(x) is dict else '"' + str(x) + '"', item[key]))
        resp = tc.get('contacts?where={"_id":{"$in":[' + all_writers + ']}}', headers=headers)
        resp_string = str(resp.data, encoding = "utf-8")
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

def get_full_relateds(item, key):
    """
    get all relateds and cache result in redis
    query string: /posts?where={"_id": {"$in":[id1, id2, ...]}}
    """
    all_relateds =  ",".join(map(lambda x: '"' + str(x["_id"]) + '"' if type(x) is dict else '"' + str(x) + '"', item[key]))
    global redis_read
    #global redis_write
    if key in item and item[key]:
        fullrelated_cached = redis_read.get('posts?where={"_id":{"$in":[' + all_relateds + ']}}')
        if fullrelated_cached is not None:
            resp_data = json.loads(fullrelated_cached)
        else:
            headers = dict(request.headers)
            tc = app.test_client()
            resp = tc.get('posts?where={"_id":{"$in":[' + all_relateds + ']}}', headers=headers)
            resp_data = json.loads(resp.data.decode("utf-8"))
            p = Process(target=_redis_write, args=('posts?where={"_id":{"$in":[' + all_relateds + ']}}', resp.data.decode("utf-8")))
            p.start()
            p.join()
        result = []
        for i in item[key]:
            for j in resp_data['_items']:
                if (type(i) is dict and str(j['_id']) == str(i['_id'])) or j['_id'] == str(i):
                    result.append(j)
                    continue
        item[key] = result
        # item[key] = resp_data['_items']
    return item

def replace_imageurl(obj):
    """
    replace formal gcs storage url in 
    - brief, content. image
    - non-empty heroImage, og_image, heroVideo
    """
    for key in [ 'brief', 'content' ]:
        if key in obj:
            obj_str = json.dumps(obj[key])
            obj_str = obj_str.replace(GCS_URL, ASSETS_URL)
            obj[key] = json.loads(obj_str)
    if 'heroImage' in obj and isinstance(obj['heroImage'], dict) and  'image' in obj['heroImage']:
        image_str = json.dumps(obj['heroImage']['image'])
        image_str = image_str.replace(GCS_URL, ASSETS_URL)
        obj['heroImage']['image'] = json.loads(image_str)
    if 'og_image' in obj and isinstance(obj['og_image'], dict) and  'image' in obj['og_image']:
        image_str = json.dumps(obj['og_image']['image'])
        image_str = image_str.replace(GCS_URL, ASSETS_URL)
        obj['og_image']['image'] = json.loads(image_str)
    if 'heroVideo' in obj and isinstance(obj['heroVideo'], dict) and  'video' in obj['heroVideo']:
        video_str = json.dumps(obj['heroVideo']['video'])
        video_str = video_str.replace(GCS_URL, ASSETS_URL)
        obj['heroVideo']['video'] = json.loads(video_str)
    if 'image' in obj and isinstance(obj['image'], dict):
        video_str = json.dumps(obj['image'])
        video_str = video_str.replace(GCS_URL, ASSETS_URL)
        obj['image'] = json.loads(video_str)
    return obj

def clean_item(item):
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
        keep = ["title", "heroImage", "slug", "_id"]
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
    if 'brief' in item and isinstance(item['brief'], dict) and 'draft' in item['brief']:
        del item['brief']['draft']
    if 'content' in item and isinstance(item['content'], dict) and 'draft' in item['content']:
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
    if '_items' in response and isinstance(response['_items'], list):
        items = response['_items']
        for item in items:
            if 'brief' in item and isinstance(item['brief'], dict) and 'draft' in item['brief']:
                del item['brief']['draft']
            if 'content' in item and isinstance(item['content'], dict) and 'draft' in item['content']:
                del item['content']['draft']
            if clean == 'content':
                if 'brief' in item and isinstance(item['brief'], dict) and 'html' in item['brief']:
                    del item['brief']['html']
                if 'content' in item and isinstance(item['content'], dict) and 'html' in item['content']:
                    del item['content']['html']
            if item["style"] == 'script':
                script_parsing = item['content']['html']
                scenes = script_parsing.split("<p><code>page</code></p>")
                page_div = "".join(map(lambda x: '<div class="page">' + x + '</div>', scenes))
                item['content']['html'] = page_div
            replace_imageurl(item)
            if related == 'full' and item['style'] == 'photography':
                item = get_full_relateds(item, 'relateds')
            item = clean_item(item)
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
        if 'brief' in item and isinstance(item['brief'], dict) and 'draft' in item['brief'] and 'apiData' in item['brief']:
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
        if 'brief' in item and isinstance(item['brief'], dict) and 'draft' in item['brief'] and 'apiData' in item['brief']:
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

def before_returning_listing(response):
    """
    Delete brief/draft, apiData
    Fill in heroVideo/coverPhoto, but only keep image,_id, description, tags, createTime
    """
    if '_items' in response and isinstance(response['_items'], list):
        for item in response['_items']:
            item = clean_item(item)
            if 'brief' in item and isinstance(item['brief'], dict) and 'draft' in item['brief'] and 'apiData' in item['brief']:
                del item['brief']['draft']
                del item['brief']['apiData']
            if 'heroVideo' in item and isinstance(item['heroVideo'], dict) and 'coverPhoto' in item['heroVideo'] and item['heroVideo']['coverPhoto']:
                headers = dict(request.headers)
                tc = app.test_client()
                cover_photo = str(item['heroVideo']['coverPhoto'])
                resp = tc.get('images?where={"_id":{"$in":["' + cover_photo + '"]}}', headers=headers)
                resp_data = json.loads(resp.data.decode("utf-8"))
                if '_items' in resp_data and len(resp_data['_items']) > 0:
                    result = {x: resp_data['_items'][0][x] for x in ('image','_id','description','tags','createTime')}
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
    return response

def before_returning_sections(response):
    """
    sort section
    """
    items = response['_items']
    sortedItems = sorted(items, key = lambda x: x["sortOrder"])
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
    if max_results is not None and int(max_results) > 25:
        abort(404)
    req = urllib.parse.unquote(request.full_path)
    global redis_read
    general_cached = redis_read.get(req)
    if general_cached is not None:
        cached_resp = json.loads(general_cached)
        if "header" in cached_resp:
            cached_header = cached_resp['header']
            del cached_resp["header"]
            return Response(json.dumps(cached_resp), headers=cached_header)
    isCampaign = request.args.get('isCampaign')
    if resource == 'posts' or resource == 'meta':
        if isCampaign:
            if isCampaign == 'true':
                lookup.update({"isCampaign": True})
            elif isCampaign == 'false':
                lookup.update({"isCampaign": False})
        elif isCampaign is None:
            lookup.update({"isCampaign": False})

def post_get_callback(resource, request, payload):
    ttl = 600
    if resource == 'images':
        ttl = 7*24*60*60
    if resource == 'albums' or resource == 'event' or resource == 'topics' or resource == 'lists' or resource == 'meta' or resource == 'tags' or resource == 'posts':
        ttl = 600
    if resource == 'partners' or resource == 'externals' or resource == 'contacts':
        ttl = 24*60*60

    result = payload.get_data().decode('utf-8')
    req = urllib.parse.unquote(request.full_path)
    p = Process(target=_redis_write, args=(req, result, ttl))
    p.start()
    p.join()

#app = Eve(auth=RolesAuth)
app = Eve()

# Wrap app with metrics layer
MetricsMiddleware(app)

# These two event hooks seems deprecated
app.on_replace_article += lambda item, original: remove_extra_fields(item)
app.on_insert_article += lambda items: remove_extra_fields(items[0])

# Before return json, refining data content for posts, albums, meta, listing, choices, topics, sections
app.on_fetched_resource_posts += before_returning_posts
app.on_fetched_resource_albums += before_returning_albums
app.on_fetched_resource_meta += before_returning_meta
app.on_fetched_resource_listing += before_returning_listing
app.on_fetched_resource_choices += before_returning_choices
app.on_fetched_resource_topics += before_returning_topics
app.on_fetched_resource_sections += before_returning_sections

# Grand scale modification
app.on_pre_GET += pre_get_callback
app.on_post_GET += post_get_callback

@app.route("/getlist", methods=['GET'])
def get_list():
    headers = dict(request.headers)
    req = urllib.parse.unquote(request.full_path)
    fetch_req = req.replace('getlist', 'listing')
    start = time.time()
    global redis_read
    #global redis_write
    listing_cached = redis_read.get(req)
    total_time = (time.time() - start)*1000
    if (total_time > 3):
        print("get list from redis: " + str(total_time))
    if listing_cached is not None:
        cached_resp = json.loads(listing_cached)
        if "header" in cached_resp:
            listing_header = cached_resp['header']
            del cached_resp["header"]
            return Response(json.dumps(cached_resp), headers=listing_header)
    tc = app.test_client()
    resp = tc.get(fetch_req, headers=headers)
    resp_object = json.loads(resp.data)
    resp_object['header'] = dict(resp.headers)
    if '_items' in resp_object and isinstance(resp_object['_items'], list):
        resp_object = before_returning_listing(resp_object)
        result = json.dumps(resp_object)
        p = Process(target=_redis_write, args=(req, result))
        p.start()
        p.join()
    else:
        result = json.dumps(resp_object)

    return Response(result, headers=dict(resp.headers))
    #return before_returning_listing(result)

@app.route("/getmeta", methods=['GET'])
def get_meta():
    headers = dict(request.headers)
    req = urllib.parse.unquote(request.full_path)
    fetch_req = req.replace('getmeta', 'meta')
    global redis_read
    listing_cached = redis_read.get(req)
    if listing_cached is not None:
        cached_resp = json.loads(listing_cached)
        if "header" in cached_resp:
            listing_header = cached_resp['header']
            del cached_resp["header"]
            return Response(json.dumps(cached_resp), headers=listing_header)
    tc = app.test_client()
    resp = tc.get(fetch_req, headers=headers)
    resp_object = json.loads(resp.data)
    resp_object['header'] = dict(resp.headers)
    if '_items' in resp_object and isinstance(resp_object['_items'], list):
        resp_object = before_returning_meta(resp_object)
        result = json.dumps(resp_object)
        p = Process(target=_redis_write, args=(req, result))
        p.start()
        p.join()
    else:
        result = json.dumps(resp_object)

    return Response(result, headers=dict(resp.headers))
    #return before_returning_listing(result)

@app.route("/getposts", methods=['GET'])
def get_post():
    headers = dict(request.headers)
    req = urllib.parse.unquote(request.full_path)
    fetch_req = req.replace('getposts', 'posts')
    start = time.time()
    global redis_read
    listing_cached = redis_read.get(req)
    total_time = (time.time() - start)*1000
    if (total_time > 3):
        print("getpost from redis: " + str(total_time))
    if listing_cached is not None:
        cached_resp = json.loads(listing_cached)
        if "header" in cached_resp:
            listing_header = cached_resp['header']
            del cached_resp["header"]
            return Response(json.dumps(cached_resp), headers=listing_header)
    tc = app.test_client()
    resp = tc.get(fetch_req, headers=headers)
    try:
        resp_object = json.loads(resp.data)
    except:
        resp_object = {}
    resp_object['header'] = dict(resp.headers)
    resp_object = before_returning_posts(resp_object)
    result = json.dumps(resp_object)
    p = Process(target=_redis_write, args=(req, result, 604800))
    p.start()
    p.join()
    return Response(result, headers=dict(resp.headers))

@app.route("/sections-featured", methods=['GET', 'POST'])
def get_sections_latest():
    response = { "_items": {},
                 "_links": {
                            "self": { "href":"sections-latest", "title": "sections latest"},
                            "parent":{ "parent": "/", "title": "Home" } } }
    headers = dict(request.headers)
    content = request.args.get('content') or 'posts'
    tc = app.test_client()
    global redis_read
    #global redis_write
    section_cached = redis_read.get("/sections")
    if section_cached is not None:
        section_items = json.loads(section_cached)
    else:
        resp = tc.get('/sections', headers=headers)
        resp_header = dict(resp.headers)
        if "Content-Length" in headers:
            del headers["Content-Length"]
        resp_data = json.loads(resp.data.decode("utf-8"))
        if ("_error" not in resp_data and "_items" in resp_data):
            section_items = resp_data["_items"]
            section_items = sorted(section_items, key = lambda x: x["sortOrder"])
            p = Process(target=_redis_write, args=("/sections", json.dumps(section_items)))
            p.start()
            p.join()
        else:
            section_items = { "_items": [] }
    for item in section_items:
        if (item['name'] == 'foodtravel'):
            if (content == 'meta'):
                endpoint = 'getmeta'
            else:
                endpoint = 'getlist'
            sec_resp = tc.get('/' + endpoint + '?where={"sections":"' + item['_id'] + '","isFeatured":true}&max_results=5&sort=-publishedDate', headers=headers)
            resp_header = dict(sec_resp.headers)
            sec_items = json.loads(sec_resp.data.decode("utf-8"))
            if '_error' not in sec_items and "_items" in sec_items:
                #response[item['name']] = sec_items['_items']
                for sec_item in sec_items:
                    clean_item(sec_item)
                    replace_imageurl(sec_item)
                response['_items'][item['name']] = sec_items['_items']
    return Response(json.dumps(response), headers=resp_header)

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
        topic_data = json.loads(topic_resp.data.decode("utf-8"))
        if "_items" in topic_data and len(topic_data["_items"]) > 0:
            topic_data["_items"][0] = clean_item(topic_data["_items"][0])
            if 'brief' in topic_data["_items"][0] and 'apiData' in topic_data["_items"][0]['brief']:
                del topic_data["_items"][0]['brief']['apiData']
            replace_imageurl(topic_data["_items"][0])
            response['topic'] = topic_data["_items"][0]
        activity_uri = '/activities?where={"topics":"' + topicId + '"}&max_results=40'
        resp = tc.get(activity_uri, headers=headers)
        resp_header = dict(resp.headers)
        activities_data = json.loads(resp.data.decode("utf-8"))
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
        node_data = json.loads(resp.data.decode("utf-8"))
        if "sort" in response["topic"] and response["topic"]["sort"] == 'desc':
            reverse = True
        else:
            reverse = False
        if "_items" in node_data:
            response["nodes"] = sorted(node_data["_items"], key = lambda x: datetime.strptime(x["nodeDate"], '%Y/%m/%d'), reverse = reverse)
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
        return Response(json.dumps(response), headers=resp_header)
    else:
        abort(404)

@app.route("/combo", methods=['GET'])
def handle_combo():
    start = time.time()
    endpoints = {'posts': '/posts?sort=-publishedDate&clean=content&where={"style":{"$nin":["projects", "readr"]}}', 'sectionfeatured': '/sections-featured?content=meta', 'choices': '/choices?max_results=1&sort=-pickDate',\
     'meta': '/getmeta?sort=-publishedDate&clean=content&related=full', 'sections': '/sections?sort=sortOrder&max_results=20', 'topics':'/topics?sort=sortOrder&max_results=10', 'posts-vue': '/getlist?sort=-publishedDate&clean=content&max_results=20&related=false', 'projects': 'getlist?where={"style":{"$in":["projects", "readr"]}}&sort=-publishedDate&related=false'}
    response = { "_endpoints": {},
                 "_links": {
                            "self": { "href":"sections-latest", "title": "sections latest"},
                            "parent":{ "parent": "/", "title": "Home" } } }
    headers = dict(request.headers)
    start = time.time()
    global redis_read
    #global redis_write
    cached = redis_read.get(request.url)
    total_time = (time.time() - start)*1000
    if (cached and total_time > 3):
        print("get combo from redis: " + str(total_time))
    if cached is not None:
        return Response(cached.decode("utf-8"), headers=headers)
    tc = app.test_client()
    req = request.args.getlist('endpoint')
    for action in req:
        if action in endpoints:
            action_resp = tc.get(endpoints[action], headers=headers)
            headers = action_resp.headers
            # print(json.loads(str(action_resp.data)))
            action_data = json.loads(action_resp.data.decode("utf-8"))
            if "_error" not in action_data and "_items" in action_data and len(action_data["_items"]) > 0:
                if '_meta' in action_data:
                    response['_meta'] = action_data['_meta']
                if action == 'choices':
                    response["_endpoints"][action] = {}
                    response["_endpoints"][action]['_items'] = action_data["_items"][0]["choices"]
                else:
                    response["_endpoints"][action] = action_data
                for item in response["_endpoints"][action]["_items"]:
                    replace_imageurl(item)
    # If there is no request args for endpoint, set the header Content-Type to json
    if not ('Content-Type' in headers and headers['Content-Type'] == "application/json"):
       headers['Content-Type'] = "application/json"
    p = Process(target=_redis_write, args=(request.full_path, json.dumps(response).encode("utf-8")))
    p.start()
    p.join()
    # done = time.time()
    # elapsed = str(done - start)
    #print("[INFO] API " + request.url + " interval " + elapsed)
    return Response(json.dumps(response), headers=headers)

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
        rs_data = json.loads(r.data.decode("utf-8"))
        if "_error" not in rs_data and "_id" in rs_data:
            collection_id = rs_data['_id']
            req = '/'+ endpoint + '?where={"' + collection + '":"' + collection_id + '"}'
            for key in dict(request.args):
                if key != 'collection' and key != 'name':
                    req += '&' + key + '=' + request.args.get(key)
            resp = tc.get(req, headers=headers)
            resp_data = json.loads(resp.data.decode("utf-8"))
            for i in resp_data['_items']:
                replace_imageurl(i)
            return Response(json.dumps(resp_data), headers=resp.headers)
        else:
            return r
    else:
        r = tc.get("/posts")
    return r

def _redis_write(key, value, ttl = 300):
    global redis_write
    redis_write.setex(key, ttl, value)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True, debug=True)
