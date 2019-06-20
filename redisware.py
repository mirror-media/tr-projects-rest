from werkzeug.wrappers import Request, Response
from flask import make_response
from itertools import tee

class RedisCache:

    def __init__(self, read_target=None, write_target=None):
        self.reader = read_target
        self.writer = write_target

    def set(self, key, ttl, value):
        self.writer.setex(key, ttl, value)

    def get(self, key):
        return self.reader.get(key)
    
class Redisware(object):

    def __init__(self, app, rules={}, cache=None, default_ttl=0):
        self.app = app
        self._rules = rules
        self.cache = cache
        self.default_ttl = default_ttl

    def __call__(self, environ, start_response):
        # Not yet in Flask context, cannot use Flask's request
        # Use werkzeug Request to parse environ
        request = Request(environ)
        cached = None

        if (self.default_ttl == 0) and (request.path not in self._rules):
            # Non-cache cases
            return self.app(environ, start_response)
        else:
            # Cache cases
            cached = self.cache.get(request.full_path)
            if cached is not None:
                # Cache hit, direct respond
                response = Response(cached, content_type='application/json')
                return response(environ, start_response)
            else:
                # Cache miss, pass to Eve and save redis
                response = self.app(environ, start_response)
                # Duplicate original iterator
                resp_iter, redis_iter = tee(response, 2)
                # Send response to redis unless 'error' exists in it
                # ttl set to default or conform to exception rules
                results = bytearray()
                for r in redis_iter:
                    # extend the result bytearray
                    # cannot use append for bytes object
                    results.extend(r)

                redis_content = results.decode('utf-8')
                if 'error' not in redis_content and len(redis_content) != 0:
                    ttl = self.default_ttl
                    if request.path in self._rules:
                        ttl = self._rules[request.path]
                    self.cache.set(request.full_path, ttl, redis_content)

                return resp_iter
