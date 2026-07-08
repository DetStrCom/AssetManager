from datetime import date, timedelta
from models import User, Location, Asset_Category, Asset


class TestUserModel:

    def test_set_and_check_password(self, db):
        user = User(username='passtest', email='pass@test.com')
        user.set_password('S3cur3@Pass')
        assert user.password_hash is not None
        assert user.password_hash != 'S3cur3@Pass'
        assert user.check_password('S3cur3@Pass') is True
        assert user.check_password('wrongpassword') is False

    def test_is_admin(self, admin_user, regular_user):
        assert admin_user.is_admin() is True
        assert regular_user.is_admin() is False

    def test_is_active_default(self, db):
        user = User(username='activetest', email='active@test.com')
        user.set_password('T3st@Pass')
        db.session.add(user)
        db.session.commit()
        assert user.is_active is True

    def test_deactivate_user(self, regular_user, db):
        regular_user.is_active = False
        db.session.commit()
        assert regular_user.is_active is False

    def test_user_repr(self, regular_user):
        assert 'testuser' in repr(regular_user)

    def test_user_location_relationship(self, regular_user, sample_location):
        assert regular_user.location == sample_location
        assert regular_user in sample_location.users


class TestLocationModel:

    def test_location_creation(self, sample_location):
        assert sample_location.office_name == 'Test Office'
        assert sample_location.city == 'London'
        assert sample_location.country == 'UK'

    def test_location_repr(self, sample_location):
        assert 'Test Office' in repr(sample_location)


class TestAssetCategoryModel:

    def test_category_creation(self, sample_category):
        assert sample_category.name == 'Test Laptops'
        assert sample_category.description == 'Laptops for testing'

    def test_category_repr(self, sample_category):
        assert 'Test Laptops' in repr(sample_category)


class TestAssetModel:

    def test_asset_creation(self, sample_asset):
        assert sample_asset.asset_tag == 'TST-001'
        assert sample_asset.name == 'Test MacBook Pro'
        assert sample_asset.status == 'In Use'
        assert sample_asset.purchase_price == 2499.00

    def test_warranty_valid(self, sample_asset):
        sample_asset.warranty_expiry = date.today() + timedelta(days=365)
        assert sample_asset.is_warranty_valid() is True

    def test_warranty_expired(self, sample_asset):
        sample_asset.warranty_expiry = date.today() - timedelta(days=1)
        assert sample_asset.is_warranty_valid() is False

    def test_warranty_none(self, sample_asset):
        sample_asset.warranty_expiry = None
        assert sample_asset.is_warranty_valid() is False

    def test_asset_category_relationship(self, sample_asset, sample_category):
        assert sample_asset.category == sample_category
        assert sample_asset in sample_category.assets

    def test_asset_location_relationship(self, sample_asset, sample_location):
        assert sample_asset.location == sample_location

    def test_asset_user_relationship(self, sample_asset, regular_user):
        assert sample_asset.assigned_user == regular_user
        assert sample_asset in regular_user.assigned_assets

    def test_asset_repr(self, sample_asset):
        assert 'TST-001' in repr(sample_asset)
        assert 'Test MacBook Pro' in repr(sample_asset)
