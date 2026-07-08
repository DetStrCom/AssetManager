from routes.auth import auth_bp
from routes.main import main_bp
from routes.assets import assets_bp
from routes.locations import locations_bp
from routes.categories import categories_bp
from routes.users import users_bp


def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(locations_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(users_bp)
