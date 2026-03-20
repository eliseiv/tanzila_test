from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "app_request_count_total",
    "Total request count by endpoint and method",
    ["endpoint", "method"],
)

REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Request latency in seconds by endpoint",
    ["endpoint"],
    buckets=(0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 10.0),
)

LOG_EVENTS = Counter(
    "app_log_events_total",
    "Application log events by severity level",
    ["level"],
)
