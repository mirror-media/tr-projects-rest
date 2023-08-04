from eve import Eve
from flask import request, Response, abort
from settings import REDIS_WRITE_HOST, REDIS_WRITE_PORT, REDIS_READ_HOST, \
    REDIS_READ_PORT, REDIS_AUTH, YT_API_KEY
from bson import json_util

import redis
import requests

from helpers.metrics import MetricsMiddleware
from helpers.redis import Redisware, RedisCache
from settings import REDIS_TTL, REDIS_EXCEPTIONS


redis_read_port = int(REDIS_READ_PORT)
redis_write_port = int(REDIS_WRITE_PORT)
redis_readPool = redis.ConnectionPool(host=REDIS_READ_HOST, port=redis_read_port, password=REDIS_AUTH)
redis_read = redis.Redis(connection_pool=redis_readPool)
redis_writePool = redis.ConnectionPool(host=REDIS_WRITE_HOST, port=redis_write_port, password=REDIS_AUTH)
redis_write = redis.Redis(connection_pool=redis_writePool)


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


# app = Eve(auth=RolesAuth)
app = Eve()

# Enable metrics middle layer
MetricsMiddleware(app)
# Enable redis middleware
redis_cache = RedisCache(read_target=redis_read, write_target=redis_write)
app.wsgi_app = Redisware(app.wsgi_app, rules=REDIS_EXCEPTIONS, cache=redis_cache, ttl_config=REDIS_TTL)


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


if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0', port=8080, threaded=True, debug=True)
