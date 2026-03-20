def test_root_redirects_to_docs(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/docs"


def test_health_returns_healthy(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_message_existing(client):
    response = client.get("/message/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "Test message 1" in data["text"]


def test_get_message_last(client):
    response = client.get("/message/12")
    assert response.status_code == 200
    assert response.json()["id"] == 12


def test_get_message_not_found(client):
    response = client.get("/message/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_message_invalid_zero(client):
    response = client.get("/message/0")
    assert response.status_code == 400
    assert "positive" in response.json()["detail"].lower()


def test_get_message_invalid_negative(client):
    response = client.get("/message/-1")
    assert response.status_code == 400


def test_process_valid_data(client):
    response = client.post("/process", json={"data": "hello world"})
    assert response.status_code == 200
    data = response.json()
    assert data["received"] == "hello world"
    assert data["status"] == "processed"


def test_process_strips_whitespace(client):
    response = client.post("/process", json={"data": "  padded  "})
    assert response.status_code == 200
    assert response.json()["received"] == "padded"


def test_process_empty_data_rejected(client):
    response = client.post("/process", json={"data": ""})
    assert response.status_code == 422


def test_process_whitespace_only_rejected(client):
    response = client.post("/process", json={"data": " "})
    assert response.status_code == 422


def test_process_tabs_newlines_only_rejected(client):
    response = client.post("/process", json={"data": " \t\n "})
    assert response.status_code == 422


def test_process_missing_field(client):
    response = client.post("/process", json={"wrong": "value"})
    assert response.status_code == 422


def test_process_no_body(client):
    response = client.post("/process")
    assert response.status_code == 422
