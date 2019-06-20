from flask import request
from datadog import DogStatsd
import time 

# Setup statsd client for localhost:9125
statsd = DogStatsd(host="localhost", port=9125)

def start_request_latency_timer():
    """
    Inject request start time info in Flask request object.
    Using Eve event hook could not get us the proper fields for current objects.
    """
    request.start = time.time()

def stop_request_latency_timer(response):
    """
    When the GET request about to finish,
    stop the http request latency timer and create the latency metrics
    """
    resp_time = time.time() - request.start
    statsd.histogram('request_latency_seconds',
        resp_time,
        tags=[
            'app:tr-projects-rest',
            'path: %s' % request.path,
        ]
    )
    return response

def count_request(response):
    statsd.increment('request_total',
        tags=[
            'app:tr-projects-rest',
            'method: %s' % request.method, 
            'path: %s' % request.path,
            'status: %s' % str(response.status_code)
            ]
    )
    return response

def MetricsMiddleware(app):
    app.before_request(start_request_latency_timer)
    app.after_request(count_request)
    app.after_request(stop_request_latency_timer)
    