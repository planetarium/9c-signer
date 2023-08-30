def test_main(fx_test_client):
    resp = fx_test_client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"Hello": "World"}


def test_pong(fx_test_client):
    resp = fx_test_client.get("/ping")
    assert resp.status_code == 200
    assert resp.json() == {"msg": "pong"}
