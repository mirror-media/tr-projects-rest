import time 
from flask import request
from prometheus_client import Counter, Histogram

PROMETHEUS_CONTENT_TYPE = 'text/plain; version=0.0.4; charset=utf-8'

http_request_count = Counter(
    'http_request_total','HTTP request Total Count')

http_request_latency = Histogram(
    'http_request_latency_seconds', 'HTTP request latency',
    ['endpoint'])

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
    http_request_count.inc()
    http_request_latency.labels(request.path).observe(resp_time)
    return response

def MetricsMiddleware(app):
    app.before_request(start_request_latency_timer)
    app.after_request(stop_request_latency_timer)