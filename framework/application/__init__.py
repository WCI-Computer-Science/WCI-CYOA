from flask import Flask
import configs

def create_app():
    app = Flask(__name__)
    app.config.from_object(configs)

    with app.app_context():
        from application.blueprints import index, users
        app.register_blueprint(index.bp)
        app.register_blueprint(users.bp)
    
    return app