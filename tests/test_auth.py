class TestLogin:

    def test_login_page_loads(self, client):
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Sign In' in response.data

    def test_login_success(self, client, admin_user):
        response = client.post('/login', data={
            'username': 'testadmin',
            'password': 'Adm1n@Pass'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Dashboard' in response.data
        assert b'Welcome back' in response.data

    def test_login_wrong_password(self, client, admin_user):
        response = client.post('/login', data={
            'username': 'testadmin',
            'password': 'WrongPassword1!'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data

    def test_login_nonexistent_user(self, client, db):
        response = client.post('/login', data={
            'username': 'nobody',
            'password': 'Whatever1!'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data

    def test_login_redirects_authenticated_user(self, logged_in_admin):
        response = logged_in_admin.get('/login')
        assert response.status_code == 302

    def test_login_inactive_user(self, client, regular_user, db):
        regular_user.is_active = False
        db.session.commit()
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'Us3r@Pass'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Dashboard' not in response.data


class TestRegister:

    def test_register_page_loads(self, client, sample_location):
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Create Account' in response.data

    def test_register_success(self, client, sample_location):
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@company.com',
            'password': 'N3wUs3r@Pass',
            'confirm_password': 'N3wUs3r@Pass',
            'department': 'Sales',
            'location_id': sample_location.id
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Registration successful' in response.data

    def test_register_duplicate_username(self, client, admin_user, sample_location):
        response = client.post('/register', data={
            'username': 'testadmin',
            'email': 'different@company.com',
            'password': 'V@lid1Pass',
            'confirm_password': 'V@lid1Pass',
            'department': 'IT',
            'location_id': sample_location.id
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Username already exists' in response.data

    def test_register_duplicate_email(self, client, admin_user, sample_location):
        response = client.post('/register', data={
            'username': 'differentuser',
            'email': 'testadmin@company.com',
            'password': 'V@lid1Pass',
            'confirm_password': 'V@lid1Pass',
            'department': 'IT',
            'location_id': sample_location.id
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Email already registered' in response.data

    def test_register_weak_password(self, client, sample_location):
        response = client.post('/register', data={
            'username': 'weakuser',
            'email': 'weak@company.com',
            'password': 'short',
            'confirm_password': 'short',
            'department': 'IT',
            'location_id': sample_location.id
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Password must be at least 8 characters' in response.data

    def test_register_password_mismatch(self, client, sample_location):
        response = client.post('/register', data={
            'username': 'mismatch',
            'email': 'mismatch@company.com',
            'password': 'V@lid1Pass',
            'confirm_password': 'Different1!',
            'department': 'IT',
            'location_id': sample_location.id
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Passwords must match' in response.data


class TestLogout:

    def test_logout(self, logged_in_admin):
        response = logged_in_admin.post('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'You have been logged out' in response.data

    def test_logout_requires_post(self, logged_in_admin):
        response = logged_in_admin.get('/logout')
        assert response.status_code == 405
