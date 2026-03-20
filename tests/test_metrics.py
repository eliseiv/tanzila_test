def test_metrics_endpoint_returns_prometheus_format(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")


def test_metrics_contains_custom_counter(client):
    client.get("/health")
    response = client.get("/metrics")
    assert "app_request_count_total" in response.text


def test_metrics_contains_custom_histogram(client):
    client.post("/process", json={"data": "test"})
    response = client.get("/metrics")
    assert "app_request_latency_seconds_bucket" in response.text


def test_metrics_contains_instrumentator_metrics(client):
    client.get("/health")
    response = client.get("/metrics")
    body = response.text
    assert "http_request_duration_seconds" in body or "http_requests_total" in body


def test_metrics_counter_increments(client):
    client.get("/health")
    r1 = client.get("/metrics")

    client.get("/health")
    r2 = client.get("/metrics")

    assert r1.text != r2.text


def test_metrics_contains_log_events_counter(client):
    client.get("/message/0")
    response = client.get("/metrics")
    assert "app_log_events_total" in response.text


def test_metrics_warnings_increment_on_bad_request(client):
    r1 = client.get("/metrics")
    client.get("/message/9999")
    r2 = client.get("/metrics")

    assert r1.text != r2.text
    assert "app_log_events_total" in r2.text
