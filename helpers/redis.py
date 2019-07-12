from werkzeug.wrappers import Request, Response
from itertools import tee
import json
from multiprocessing import Process

class RedisCache:
    '''
    RedisCache wraps redis connection pool, and exposes two methods to get and set key from redis
    :param read_target: redis read server
    :type read_target: redis.ConnectionPool
    :param write_target: redis write server
    :type write_target: redis.ConnectionPool
    '''
    def __init__(self, read_target=None, write_target=None):
        self.reader = read_target
        self.writer = write_target

    def set(self, key, value, ttl):
        '''
        set key:value with expiration ttl
        :param key: redis key
        :type key: str
        :param value: content to be stored in redis
        :type value: str
        :param ttl: desired TTL for key:value
        :type ttl: int
        '''
        if self.writer:
            self.writer.setex(key, ttl, value)
        else:
            # TODO: handle the case when there is no redis server set
            pass

    def get(self, key):
        '''
        get content from redis with key
        :param key: redis key
        :type key: str 
        '''
        if self.reader:
            return self.reader.get(key)
        else:
            # TODO: handle the case when there is no redis server set
            pass
    
class Redisware(object):
    '''
    Redisware decide redis cacheability for each request
    :param app: Flask app
    :type app: flask
    :param rules: Besides default_ttl, rules will be checked to decide cacheability
    :type rules: dict
    :param cache: Redis backend to be used in get/set action
    :type cache: RedisCache
    :param ttl_config: TTL settings used in redis. 0 for not caching generally.
    :type ttl_config: dict
    '''
    def __init__(self, app, rules={}, cache=None, ttl_config={}):
        self.app = app
        self._rules = rules
        self.cache = cache
        
        self.default_ttl = ttl_config.get('default', 0)
        self.error_ttl = ttl_config.get('error', 0)

    def __call__(self, environ, start_response):
        '''
        __call__ whether to get or set cache in redis, or pass request to Flask app
        :returns: The data from either redis or database
        :rtype: ClosingIterator
        '''
        # Not yet in Flask context, cannot use Flask's request
        # Use werkzeug Request to parse environ
        request = Request(environ)
        cached = None

        if (self.default_ttl == 0) and (request.path not in self._rules):
            # Non-cache cases, go on with Flask
            return self.app(environ, start_response)
        else:
            # Cache cases
            # TODO: logging cache situation
            cached = self.cache.get(request.full_path)
            if cached is not None:
                # Cache hit, directly respond
                response = Response(cached, content_type='application/json')
                return response(environ, start_response)
            else:
                # Cache miss, pass to Eve and save redis
                response = self.app(environ, start_response)
                # Make 2 copy of original iterator
                resp_iter, redis_iter = tee(response, 2)
                raw_resp = bytearray()
                for r in redis_iter:
                    # Cannot use append for bytes object, extend the result bytearray instead
                    raw_resp.extend(r)

                # Send response to redis unless 'error' exists in it
                # ttl set to default or conform to exception rules
                resp_str = raw_resp.decode('utf-8')
                resp_json = json.loads(resp_str)
                ttl = self.default_ttl
                if '_error' in resp_json:
                    ttl = self.error_ttl
                if request.path in self._rules:
                    ttl = self._rules[request.path]
                p = Process(target=self.cache.set, args=(request.full_path, resp_str, ttl))
                p.start()
                p.join()
                return resp_iter
