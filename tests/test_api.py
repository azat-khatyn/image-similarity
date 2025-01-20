from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)

def test_index_page():
    """Тест главной страницы"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Compare two images using advanced algorithms" in response.text


def test_compare_endpoint_invalid_method():
    """Тест эндпоинта /compare/ с некорректным методом"""
    response = client.post(
        "/compare/",
        data={
            "input1": "https://example.com/image1.jpg",
            "input2": "https://example.com/image2.jpg",
            "method": "invalid",
        },
    )
    assert response.status_code == 400
    assert "Invalid method" in response.text
