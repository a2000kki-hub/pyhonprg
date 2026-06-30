from flask import Flask
from prometheus_client import make_wsgi_app, Counter
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)

# A simple metric to track page views in Grafana
REQUEST_COUNT = Counter('app_requests_total', 'Total number of requests to the main endpoint')

@app.route('/')
def home():
    REQUEST_COUNT.inc()
    return "Hello World! Monitoring is active."

# Add prometheus wsgi middleware to route /metrics requests
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
