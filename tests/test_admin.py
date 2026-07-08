from models import User, Location, Asset_Category, Asset
from datetime import date


class TestUserManagement:

    def test_user_list_requires_admin(self, logged_in_user):
        response = logged_in_user.get('/users', follow_redirects=True)
        assert response.status_code == 200
        assert b'admin privileges' in response.data

    def test_user_list_loads_for_admin(self, logged_in_admin, regular_user):
        response = logged_in_admin.get('/users')
        assert response.status_code == 200
        assert b'testuser' in response.data

    def test_deactivate_user(self, logged_in_admin, regular_user, db):
        response = logged_in_admin.post(
            f'/users/{regular_user.id}/toggle-active',
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'deactivated' in response.data
        db.session.refresh(regular_user)
        assert regular_user.is_active is False

    def test_activate_user(self, logged_in_admin, regular_user, db):
        regular_user.is_active = False
        db.session.commit()
        response = logged_in_admin.post(
            f'/users/{regular_user.id}/toggle-active',
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'activated' in response.data
        db.session.refresh(regular_user)
        assert regular_user.is_active is True

    def test_cannot_deactivate_self(self, logged_in_admin, admin_user):
        response = logged_in_admin.post(
            f'/users/{admin_user.id}/toggle-active',
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'cannot deactivate your own account' in response.data


class TestLocationDeletion:

    def test_delete_empty_location(self, logged_in_admin, db):
        location = Location(
            office_name='Empty Office',
            address='1 Empty St',
            city='Nowhere',
            country='UK'
        )
        db.session.add(location)
        db.session.commit()
        loc_id = location.id

        response = logged_in_admin.post(
            f'/locations/{loc_id}/delete',
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'deleted successfully' in response.data
        assert Location.query.get(loc_id) is None

    def test_cannot_delete_location_with_assets(self, logged_in_admin, sample_asset, sample_location):
        response = logged_in_admin.post(
            f'/locations/{sample_location.id}/delete',
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Cannot delete' in response.data
        assert Location.query.get(sample_location.id) is not None

    def test_cannot_delete_location_with_users(self, logged_in_admin, admin_user, db):
        loc = admin_user.location
        response = logged_in_admin.post(
            f'/locations/{loc.id}/delete',
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Cannot delete' in response.data


class TestCategoryDeletion:

    def test_delete_empty_category(self, logged_in_admin, db):
        category = Asset_Category(name='Empty Category', description='Nothing here')
        db.session.add(category)
        db.session.commit()
        cat_id = category.id

        response = logged_in_admin.post(
            f'/categories/{cat_id}/delete',
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'deleted successfully' in response.data
        assert Asset_Category.query.get(cat_id) is None

    def test_cannot_delete_category_with_assets(self, logged_in_admin, sample_asset, sample_category):
        response = logged_in_admin.post(
            f'/categories/{sample_category.id}/delete',
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Cannot delete' in response.data
        assert Asset_Category.query.get(sample_category.id) is not None
