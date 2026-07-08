from models import Asset


class TestAssetList:

    def test_asset_list_requires_login(self, client):
        response = client.get('/assets')
        assert response.status_code == 302
        assert '/login' in response.headers['Location']

    def test_asset_list_loads(self, logged_in_admin, sample_asset):
        response = logged_in_admin.get('/assets')
        assert response.status_code == 200
        assert b'TST-001' in response.data
        assert b'Test MacBook Pro' in response.data

    def test_asset_search_by_tag(self, logged_in_admin, sample_asset):
        response = logged_in_admin.get('/assets?q=TST-001')
        assert response.status_code == 200
        assert b'TST-001' in response.data

    def test_asset_search_by_name(self, logged_in_admin, sample_asset):
        response = logged_in_admin.get('/assets?q=MacBook')
        assert response.status_code == 200
        assert b'Test MacBook Pro' in response.data

    def test_asset_search_by_serial(self, logged_in_admin, sample_asset):
        response = logged_in_admin.get('/assets?q=SN12345')
        assert response.status_code == 200
        assert b'TST-001' in response.data

    def test_asset_search_no_results(self, logged_in_admin, sample_asset):
        response = logged_in_admin.get('/assets?q=nonexistentxyz')
        assert response.status_code == 200
        assert b'No Assets Found' in response.data

    def test_asset_filter_by_status(self, logged_in_admin, sample_asset):
        response = logged_in_admin.get('/assets?status=In+Use')
        assert response.status_code == 200
        assert b'TST-001' in response.data

    def test_asset_filter_excludes_other_status(self, logged_in_admin, sample_asset):
        response = logged_in_admin.get('/assets?status=Available')
        assert response.status_code == 200
        assert b'TST-001' not in response.data


class TestAssetView:

    def test_asset_view_loads(self, logged_in_admin, sample_asset):
        response = logged_in_admin.get(f'/assets/{sample_asset.id}')
        assert response.status_code == 200
        assert b'TST-001' in response.data
        assert b'Test MacBook Pro' in response.data
        assert b'SN12345' in response.data

    def test_asset_view_404(self, logged_in_admin):
        response = logged_in_admin.get('/assets/99999')
        assert response.status_code == 404


class TestAssetCreate:

    def test_asset_create_page_loads(self, logged_in_admin, sample_category, sample_location):
        response = logged_in_admin.get('/assets/create')
        assert response.status_code == 200
        assert b'Save Asset' in response.data

    def test_asset_create_success(self, logged_in_admin, sample_category, sample_location):
        response = logged_in_admin.post('/assets/create', data={
            'asset_tag': 'NEW-001',
            'name': 'New Test Asset',
            'description': 'A brand new asset',
            'serial_number': 'NEWSN001',
            'status': 'Available',
            'assigned_to_user_id': 0,
            'category_id': sample_category.id,
            'location_id': sample_location.id,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'NEW-001' in response.data

    def test_asset_create_duplicate_tag(self, logged_in_admin, sample_asset, sample_category, sample_location):
        response = logged_in_admin.post('/assets/create', data={
            'asset_tag': 'TST-001',
            'name': 'Duplicate Tag Asset',
            'status': 'Available',
            'assigned_to_user_id': 0,
            'category_id': sample_category.id,
            'location_id': sample_location.id,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Asset tag already exists' in response.data


class TestAssetDelete:

    def test_asset_delete_admin(self, logged_in_admin, sample_asset, db):
        asset_id = sample_asset.id
        response = logged_in_admin.post(f'/assets/{asset_id}/delete', follow_redirects=True)
        assert response.status_code == 200
        assert b'deleted successfully' in response.data
        assert Asset.query.get(asset_id) is None

    def test_asset_delete_regular_user_forbidden(self, logged_in_user, sample_asset):
        response = logged_in_user.post(f'/assets/{sample_asset.id}/delete', follow_redirects=True)
        assert response.status_code == 200
        assert b'admin privileges' in response.data

    def test_asset_delete_404(self, logged_in_admin):
        response = logged_in_admin.post('/assets/99999/delete')
        assert response.status_code == 404
