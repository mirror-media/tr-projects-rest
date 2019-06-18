# import json
from werkzeug.wrappers import Request
# import urllib.parse
from flask import make_response

class RedisCache:

    def __init__(self, read_target=None, write_target=None):
        self.read = read_target
        self.write = write_target

    def set(self, key, ttl, value):
        print("RedisCache set: ",key, ttl)
        self.write.setex(key, ttl, value)

    def get(self, key):
        return self.read.get(key)
    
class Redisware(object):

    def __init__(self, app, rules={}, cache=None):
        self.app = app
        self._rules = rules
        self.cache = cache

    def __call__(self, environ, start_response):
        # Not yet in Flask context, cannot use Flask's request
        # Use werkzeug Request to parse environ
        request = Request(environ)
        cached = None

        if request.path in self._rules:
            cached = self.cache.get(request.full_path)
        
        if cached is not None:
            print("cache hits")
            headers = [
                ('Content-Type', 'application/json'),
                ('Cache-Control', 'max-age=1500,must-revalidate'),
                # ('Content-Length', len([cached])),
                ]
            start_response('200 OK', headers)
            # Must create iterator
            yield cached

        else:
            print("cached misses")
            response = self.app(environ, start_response)
            results = bytearray()

            for r in response:
                # extend the result bytearray
                # cannot use append for bytes object
                results.extend(r)
                # re-yield the iterator
                yield r

            self.cache.set(request.full_path, self._rules[request.path], bytes(results))
            return response