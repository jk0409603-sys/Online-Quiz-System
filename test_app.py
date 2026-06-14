from app import app


def test_health_endpoint():
    client = app.test_client()
    response = client.get('/api/health')
    assert response.status_code == 200
    assert 'status' in response.get_json()


def test_demo_endpoint():
    client = app.test_client()
    response = client.get('/api/demo')
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
    assert 'focus' in data

