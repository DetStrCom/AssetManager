import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db as _db
from models import User, Location, Asset_Category, Asset
from datetime import date


@pytest.fixture(scope='function')
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'RATELIMIT_ENABLED': False,
        'SERVER_NAME': 'localhost',
    })

    with app.app_context():
        _db.drop_all()
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    with app.app_context():
        yield _db


@pytest.fixture(scope='function')
def client(app, db):
    return app.test_client()


@pytest.fixture
def sample_location(db):
    location = Location(
        office_name='Test Office',
        address='123 Test Street',
        city='London',
        country='UK',
        contact_phone='+441234567890'
    )
    db.session.add(location)
    db.session.commit()
    return location


@pytest.fixture
def sample_category(db):
    category = Asset_Category(
        name='Test Laptops',
        description='Laptops for testing'
    )
    db.session.add(category)
    db.session.commit()
    return category


@pytest.fixture
def admin_user(db, sample_location):
    user = User(
        username='testadmin',
        email='testadmin@company.com',
        role='admin',
        department='IT',
        location_id=sample_location.id
    )
    user.set_password('Adm1n@Pass')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def regular_user(db, sample_location):
    user = User(
        username='testuser',
        email='testuser@company.com',
        role='regular',
        department='Engineering',
        location_id=sample_location.id
    )
    user.set_password('Us3r@Pass')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_asset(db, sample_category, sample_location, regular_user):
    asset = Asset(
        asset_tag='TST-001',
        name='Test MacBook Pro',
        description='A test laptop for unit tests',
        serial_number='SN12345',
        purchase_date=date(2023, 6, 1),
        purchase_price=2499.00,
        status='In Use',
        assigned_to_user_id=regular_user.id,
        category_id=sample_category.id,
        location_id=sample_location.id,
        warranty_expiry=date(2026, 6, 1)
    )
    db.session.add(asset)
    db.session.commit()
    return asset


@pytest.fixture
def logged_in_admin(client, admin_user):
    client.post('/login', data={
        'username': admin_user.username,
        'password': 'Adm1n@Pass'
    }, follow_redirects=True)
    return client


@pytest.fixture
def logged_in_user(client, regular_user):
    client.post('/login', data={
        'username': regular_user.username,
        'password': 'Us3r@Pass'
    }, follow_redirects=True)
    return client
