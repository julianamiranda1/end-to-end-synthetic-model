from main import app

def test_root_route_exists():
    assert any(route.path == "/" and "GET" in route.methods for route in app.routes)


def test_health_route_exists():
    assert any(route.path == "/health" and "GET" in route.methods for route in app.routes)


def test_predict_route_exists():
    assert any(route.path == "/ml/predict" for route in app.routes)
