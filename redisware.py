from werkzeug.wrappers import Request
from flask import make_response

class RedisCache:

    def __init__(self, read_target=None, write_target=None):
        self.reader = read_target
        self.writer = write_target

    def set(self, key, ttl, value):
        print("RedisCache set: ",key, ttl)
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
            print("non cached conditions")
            response = self.app(environ, start_response)

            for r in response:
                yield r
        else:
            # Cache cases
            print("cached case")
            cached = self.cache.get(request.full_path)
        
            if cached is not None:
                # Cache hit, direct respond
                print("cache hits:{}".format(request.full_path))
                headers = [
                    ('Content-Type', 'application/json'),
                    ('Cache-Control', 'max-age=1500,must-revalidate'),
                    # ('Content-Length', len([cached])),
                    ]
                start_response('200 OK', headers)
                # Must create iterator
                yield cached

            else:
                # Cache miss, pass to Eve and save redis
                print("cached misses:{}".format(request.full_path))
                response = self.app(environ, start_response)

                # Send response to redis unless 'error' exists in it
                # ttl set to default or conform to exception rules
                results = bytearray()

                for r in response:
                    # extend the result bytearray
                    # cannot use append for bytes object
                    results.extend(r)
                    # re-yield the iterator
                    yield r

                redis_content = results.decode('utf8')
                if 'error' not in redis_content:
                    ttl = self.default_ttl
                    if request.path in self._rules:
                        ttl = self._rules[request.path]
                    self.cache.set(request.full_path, ttl, redis_content)
                else:
                    print('error response!')

                return response