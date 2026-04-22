"""
API test suite for NetTrack.

Some tests are already written to demonstrate the testing patterns used here.
The TODOs are yours to complete as part of the assessment.
"""
import json


# ---------------------------------------------------------------------------
# Assets — list / read
# ---------------------------------------------------------------------------

def test_get_assets_returns_list(flask_client):
    """GET /api/assets returns a paginated list with the expected fields."""
    response = flask_client.get('/api/assets')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert 'assets' in data
    assert 'total' in data
    assert 'page' in data
    assert 'pages' in data
    assert isinstance(data['assets'], list)


def test_get_assets_pagination_metadata(flask_client):
    """Pagination metadata reflects the actual number of records in the database."""
    response = flask_client.get('/api/assets')
    data = json.loads(response.data)

    # The test database is seeded with 12 assets (see conftest.py)
    assert data['total'] == 12
    assert data['page'] == 1
    assert data['per_page'] == 10


def test_get_single_asset(flask_client):
    """GET /api/assets/<id> returns the correct asset."""
    response = flask_client.get('/api/assets/1')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data['id'] == 1
    assert 'name' in data
    assert 'status' in data
    assert 'asset_type' in data


def test_get_asset_not_found(flask_client):
    """GET /api/assets/<id> returns 404 for a nonexistent asset."""
    response = flask_client.get('/api/assets/99999')
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Assets — create
# ---------------------------------------------------------------------------

def test_create_asset_success(flask_client):
    """POST /api/assets with valid data creates a new asset and returns 201."""
    payload = {
        'name': 'New Test Workstation',
        'asset_type': 'workstation',
        'client_id': 1,
        'serial_number': 'TST-WS-999',
    }
    response = flask_client.post(
        '/api/assets',
        data=json.dumps(payload),
        content_type='application/json',
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == 'New Test Workstation'
    assert data['status'] == 'active'


def test_create_asset_missing_fields(flask_client):
    """
    TODO: Implement this test.

    POST /api/assets with required fields missing should return 400, not 500.
    The response body should contain an 'error' key with a descriptive message.

    Required fields: name, asset_type, client_id
    """
    # TODO: send a POST with an empty (or incomplete) body and assert:
    #   - status code is 400
    #   - response JSON contains an 'error' key
    pass


# ---------------------------------------------------------------------------
# Assets — toggle status
# ---------------------------------------------------------------------------

def test_toggle_active_asset_becomes_inactive(flask_client):
    """Toggling an active asset should set its status to 'inactive'."""
    # Asset 1 is seeded as 'active'
    response = flask_client.post('/api/assets/1/toggle')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data['status'] == 'inactive'


def test_toggle_inactive_asset_becomes_active(flask_client):
    """
    TODO: Implement this test.

    Toggling an inactive asset should restore it to 'active', NOT set it to 'retired'.
    Asset 2 is seeded with status='inactive' (see conftest.py).

    Assert:
      - status code is 200
      - returned status is 'active'
    """
    response = flask_client.post('/api/assets/2/toggle')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data['status'] == 'active'


# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

def test_get_clients(flask_client):
    """GET /api/clients returns all clients."""
    response = flask_client.get('/api/clients')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert 'clients' in data
    assert len(data['clients']) == 2


def test_get_client_includes_assets(flask_client):
    """GET /api/clients/<id> includes the client's assets in the response."""
    response = flask_client.get('/api/clients/1')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert 'assets' in data
    assert isinstance(data['assets'], list)
    assert len(data['assets']) > 0


def test_delete_client_with_assets_fails(flask_client):
    """
    TODO: Implement this test.

    Deleting a client that still has assets assigned should return a 409 (Conflict),
    not a 500 Internal Server Error.

    Client 1 (Acme Corporation) has assets assigned to it (see conftest.py).

    Assert:
      - status code is 409
      - response JSON contains an 'error' key
    """
    # TODO: implement this test
    pass
