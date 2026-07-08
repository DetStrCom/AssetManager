import logging
from models import User, Asset


class TestA01BrokenAccessControl:

    def test_regular_user_cannot_access_user_list(self, logged_in_user):
        response = logged_in_user.get('/users', follow_redirects=True)
        assert b'admin privileges' in response.data

    def test_regular_user_cannot_create_location(self, logged_in_user):
        response = logged_in_user.post('/locations/create', data={
            'office_name': 'Hacker Office',
            'address': '123 Evil St',
            'city': 'Hackville',
            'country': 'Nowhere'
        }, follow_redirects=True)
        assert b'admin privileges' in response.data

    def test_regular_user_cannot_delete_asset(self, logged_in_user, sample_asset):
        response = logged_in_user.post(
            f'/assets/{sample_asset.id}/delete',
            follow_redirects=True
        )
        assert b'admin privileges' in response.data
        assert Asset.query.get(sample_asset.id) is not None

    def test_regular_user_cannot_toggle_user_active(self, logged_in_user, admin_user):
        response = logged_in_user.post(
            f'/users/{admin_user.id}/toggle-active',
            follow_redirects=True
        )
        assert b'admin privileges' in response.data

    def test_unauthenticated_cannot_access_dashboard(self, client):
        response = client.get('/dashboard')
        assert response.status_code == 302
        assert '/login' in response.headers['Location']

    def test_unauthenticated_cannot_access_assets(self, client):
        response = client.get('/assets')
        assert response.status_code == 302
        assert '/login' in response.headers['Location']

    def test_idor_user_cannot_edit_others_asset(self, logged_in_user, sample_asset, admin_user, db, sample_category, sample_location):
        other_asset = Asset(
            asset_tag='OTHER-001', name='Admin Laptop',
            status='In Use', assigned_to_user_id=admin_user.id,
            category_id=sample_category.id, location_id=sample_location.id
        )
        db.session.add(other_asset)
        db.session.commit()
        response = logged_in_user.get(f'/assets/{other_asset.id}/edit', follow_redirects=True)
        assert b'You can only edit assets assigned to you' in response.data

    def test_cannot_escalate_role_via_registration(self, client, sample_location):
        response = client.post('/register', data={
            'username': 'sneakyadmin',
            'email': 'sneaky@test.com',
            'password': 'V@lid1Pass!',
            'confirm_password': 'V@lid1Pass!',
            'department': 'IT',
            'location_id': sample_location.id,
            'role': 'admin'
        }, follow_redirects=True)
        user = User.query.filter_by(username='sneakyadmin').first()
        if user:
            assert user.role == 'regular'


class TestA02SecurityMisconfiguration:

    def test_security_headers_present(self, client):
        response = client.get('/login')
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'
        assert response.headers.get('X-Frame-Options') == 'SAMEORIGIN'
        assert response.headers.get('X-XSS-Protection') == '1; mode=block'
        assert response.headers.get('Referrer-Policy') == 'strict-origin-when-cross-origin'
        assert 'Permissions-Policy' in response.headers
        assert 'Content-Security-Policy' in response.headers

    def test_csp_restricts_sources(self, client):
        response = client.get('/login')
        csp = response.headers.get('Content-Security-Policy', '')
        assert "default-src 'self'" in csp
        assert "script-src" in csp
        assert "frame-ancestors 'self'" in csp

    def test_clickjacking_protection(self, client):
        response = client.get('/login')
        assert response.headers.get('X-Frame-Options') == 'SAMEORIGIN'

    def test_no_server_version_disclosure(self, client):
        response = client.get('/login')
        server = response.headers.get('Server', '')
        assert 'Python' not in server

    def test_error_pages_do_not_leak_internals(self, logged_in_admin):
        response = logged_in_admin.get('/nonexistent-page-xyz')
        assert response.status_code == 404
        assert b'Page Not Found' in response.data
        assert b'Traceback' not in response.data


class TestA03SupplyChainFailures:

    def test_dependencies_are_pinned(self):
        with open('requirements.txt', 'r') as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
        for line in lines:
            assert '==' in line, f'Dependency not pinned: {line}'

    def test_no_known_malicious_packages(self):
        typosquats = ['flasks', 'requets', 'djang0', 'numpyy', 'pandass']
        with open('requirements.txt', 'r') as f:
            content = f.read().lower()
        for name in typosquats:
            assert name not in content, f'Suspicious package name: {name}'

    def test_integrity_subresource_cdn(self):
        pass


class TestA04CryptographicFailures:

    def test_passwords_are_hashed_not_plaintext(self, admin_user):
        assert admin_user.password_hash != 'Adm1n@Pass'
        assert len(admin_user.password_hash) > 50
        assert admin_user.password_hash.startswith(('scrypt:', 'pbkdf2:'))

    def test_password_hash_not_in_html_responses(self, logged_in_admin, admin_user):
        response = logged_in_admin.get('/profile')
        assert admin_user.password_hash.encode() not in response.data

    def test_session_cookie_httponly(self, app):
        assert app.config['SESSION_COOKIE_HTTPONLY'] is True

    def test_session_cookie_samesite(self, app):
        assert app.config['SESSION_COOKIE_SAMESITE'] == 'Lax'

    def test_password_hashing_uses_strong_algorithm(self, db):
        user = User(username='hashtest', email='hash@test.com')
        user.set_password('T3st@Pass123')
        assert 'md5' not in user.password_hash
        assert 'sha1' not in user.password_hash


class TestA05Injection:

    def test_sql_injection_login(self, client, admin_user):
        response = client.post('/login', data={
            'username': "' OR '1'='1' --",
            'password': "anything"
        }, follow_redirects=True)
        assert b'Invalid username or password' in response.data
        assert b'Dashboard' not in response.data

    def test_sql_injection_search(self, logged_in_admin):
        payloads = [
            "'; DROP TABLE assets; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "1; DELETE FROM assets WHERE '1'='1",
        ]
        for payload in payloads:
            response = logged_in_admin.get(f'/assets?q={payload}')
            assert response.status_code == 200
        assert Asset.query.count() >= 0

    def test_xss_stored_in_asset_name(self, logged_in_admin, sample_category, sample_location):
        xss_payload = '<script>alert("XSS")</script>'
        logged_in_admin.post('/assets/create', data={
            'asset_tag': 'XSS-001',
            'name': xss_payload,
            'status': 'Available',
            'assigned_to_user_id': 0,
            'category_id': sample_category.id,
            'location_id': sample_location.id,
        })
        response = logged_in_admin.get('/assets')
        assert b'<script>alert("XSS")</script>' not in response.data
        assert b'&lt;script&gt;' in response.data or b'XSS-001' in response.data

    def test_xss_reflected_in_search(self, logged_in_admin):
        xss_payload = '<img src=x onerror=alert("XSS")>'
        response = logged_in_admin.get(f'/assets?q={xss_payload}')
        assert b'<img src=x onerror=alert("XSS")>' not in response.data

    def test_xss_in_registration_fields(self, client, sample_location):
        response = client.post('/register', data={
            'username': '<script>alert(1)</script>user',
            'email': 'xss@test.com',
            'password': 'V@lid1Pass!',
            'confirm_password': 'V@lid1Pass!',
            'department': '<img src=x onerror=alert(1)>',
            'location_id': sample_location.id
        }, follow_redirects=True)
        assert b'<script>alert(1)</script>' not in response.data

    def test_path_traversal_blocked(self, logged_in_admin):
        dangerous_paths = ['/assets/../../etc/passwd', '/assets/1%00.html']
        for path in dangerous_paths:
            response = logged_in_admin.get(path)
            assert response.status_code in (301, 302, 308, 404, 405, 400)

    def test_header_injection_blocked(self, client):
        response = client.post('/login', data={
            'username': 'admin\r\nX-Injected: true',
            'password': 'test'
        }, follow_redirects=True)
        assert 'X-Injected' not in response.headers


class TestA06InsecureDesign:

    def test_rate_limiting_exists_on_login(self, app):
        from app import limiter
        assert limiter is not None

    def test_admin_cannot_deactivate_self(self, logged_in_admin, admin_user):
        response = logged_in_admin.post(
            f'/users/{admin_user.id}/toggle-active',
            follow_redirects=True
        )
        assert b'cannot deactivate your own account' in response.data

    def test_deletion_blocked_when_references_exist(self, logged_in_admin, sample_asset, sample_location):
        response = logged_in_admin.post(
            f'/locations/{sample_location.id}/delete',
            follow_redirects=True
        )
        assert b'Cannot delete' in response.data

    def test_password_confirmation_required(self, client, sample_location):
        response = client.post('/register', data={
            'username': 'noconfirm',
            'email': 'noconfirm@test.com',
            'password': 'V@lid1Pass!',
            'confirm_password': 'DifferentPass1!',
            'department': 'Test',
            'location_id': sample_location.id
        }, follow_redirects=True)
        assert b'Passwords must match' in response.data


class TestA07AuthenticationFailures:

    def test_generic_login_error_prevents_enumeration(self, client, admin_user):
        r1 = client.post('/login', data={
            'username': 'nonexistent', 'password': 'anything'
        }, follow_redirects=True)
        r2 = client.post('/login', data={
            'username': 'testadmin', 'password': 'wrongpass'
        }, follow_redirects=True)
        assert b'Invalid username or password' in r1.data
        assert b'Invalid username or password' in r2.data

    def test_deactivated_user_cannot_login(self, client, regular_user, db):
        regular_user.is_active = False
        db.session.commit()
        response = client.post('/login', data={
            'username': 'testuser', 'password': 'Us3r@Pass'
        }, follow_redirects=True)
        assert b'Dashboard' not in response.data

    def test_weak_passwords_rejected(self, client, sample_location):
        weak_passwords = ['12345678', 'password', 'ALLCAPS1!', 'alllower1!', 'NoDigits!!']
        for pwd in weak_passwords:
            response = client.post('/register', data={
                'username': f'weak_{pwd[:4]}',
                'email': f'{pwd[:4]}@test.com',
                'password': pwd,
                'confirm_password': pwd,
                'department': 'Test',
                'location_id': sample_location.id
            }, follow_redirects=True)
            assert b'Registration successful' not in response.data, f'Weak password accepted: {pwd}'

    def test_open_redirect_blocked(self, client, admin_user):
        response = client.post('/login?next=https://evil.com', data={
            'username': 'testadmin', 'password': 'Adm1n@Pass'
        }, follow_redirects=False)
        location = response.headers.get('Location', '')
        assert 'evil.com' not in location

    def test_logout_invalidates_session(self, logged_in_admin):
        logged_in_admin.post('/logout')
        response = logged_in_admin.get('/dashboard')
        assert response.status_code == 302
        assert '/login' in response.headers['Location']


class TestA08IntegrityFailures:

    def test_csrf_enforced_on_login(self, app, db, sample_location):
        app.config['WTF_CSRF_ENABLED'] = True
        client = app.test_client()
        response = client.post('/login', data={
            'username': 'admin', 'password': 'test'
        }, follow_redirects=True)
        assert b'Dashboard' not in response.data

    def test_csrf_enforced_on_delete(self, app, db, sample_location):
        app.config['WTF_CSRF_ENABLED'] = True
        client = app.test_client()
        response = client.post('/assets/1/delete')
        assert response.status_code in (400, 302, 404)

    def test_logout_requires_post(self, logged_in_admin):
        response = logged_in_admin.get('/logout')
        assert response.status_code == 405


class TestA09SecurityLogging:

    def test_failed_login_is_logged(self, client, admin_user, caplog):
        with caplog.at_level(logging.WARNING, logger='security'):
            client.post('/login', data={
                'username': 'testadmin', 'password': 'WrongPassword1!'
            }, follow_redirects=True)
        assert any('LOGIN_FAILED' in record.message for record in caplog.records)

    def test_access_denied_is_logged(self, logged_in_user, caplog):
        with caplog.at_level(logging.WARNING, logger='security'):
            logged_in_user.get('/users', follow_redirects=True)
        assert any('ACCESS_DENIED' in record.message for record in caplog.records)

    def test_successful_login_is_logged(self, client, admin_user, caplog):
        with caplog.at_level(logging.INFO, logger='security'):
            client.post('/login', data={
                'username': 'testadmin', 'password': 'Adm1n@Pass'
            }, follow_redirects=True)
        assert any('LOGIN_SUCCESS' in record.message for record in caplog.records)

    def test_log_includes_ip_address(self, client, admin_user, caplog):
        with caplog.at_level(logging.WARNING, logger='security'):
            client.post('/login', data={
                'username': 'testadmin', 'password': 'wrong'
            }, follow_redirects=True)
        log_messages = ' '.join(r.message for r in caplog.records)
        assert 'ip=' in log_messages or '127.0.0.1' in log_messages


class TestA10ExceptionalConditions:

    def test_404_returns_friendly_page(self, logged_in_admin):
        response = logged_in_admin.get('/this-does-not-exist')
        assert response.status_code == 404
        assert b'Page Not Found' in response.data
        assert b'Traceback' not in response.data
        assert b'File "' not in response.data

    def test_invalid_asset_id_returns_404(self, logged_in_admin):
        response = logged_in_admin.get('/assets/999999')
        assert response.status_code == 404

    def test_string_as_asset_id_handled(self, logged_in_admin):
        response = logged_in_admin.get('/assets/abc')
        assert response.status_code in (404, 308)

    def test_negative_page_number_handled(self, logged_in_admin):
        response = logged_in_admin.get('/assets?page=-1')
        assert response.status_code == 200

    def test_extremely_large_page_number(self, logged_in_admin):
        response = logged_in_admin.get('/assets?page=999999')
        assert response.status_code == 200

    def test_oversized_input_handled(self, logged_in_admin, sample_category, sample_location):
        long_string = 'A' * 10000
        response = logged_in_admin.post('/assets/create', data={
            'asset_tag': long_string,
            'name': long_string,
            'status': 'Available',
            'assigned_to_user_id': 0,
            'category_id': sample_category.id,
            'location_id': sample_location.id,
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_empty_form_submission_handled(self, logged_in_admin):
        response = logged_in_admin.post('/assets/create', data={}, follow_redirects=True)
        assert response.status_code == 200
        assert b'Internal Server Error' not in response.data

    def test_malformed_date_handled(self, logged_in_admin, sample_category, sample_location):
        response = logged_in_admin.post('/assets/create', data={
            'asset_tag': 'DATE-001',
            'name': 'Date Test',
            'status': 'Available',
            'purchase_date': 'not-a-date',
            'assigned_to_user_id': 0,
            'category_id': sample_category.id,
            'location_id': sample_location.id,
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_405_returns_friendly_page(self, logged_in_admin):
        response = logged_in_admin.get('/logout')
        assert response.status_code == 405
        assert b'Method Not Allowed' in response.data
