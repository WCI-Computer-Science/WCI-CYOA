from flask import Flask, request
import configs

def redirect_http_https():
    if request.is_secure:
        return
    url = request.url.replace("http://", "https://", 1)
    return redirect(url, 301)

def create_app():
    app = Flask(__name__)
    app.config.from_object(configs)

    with app.app_context():
        from application.blueprints import index, users
        from application.models import database
        app.register_blueprint(index.bp)
        app.register_blueprint(users.bp)
        app.before_request(redirect_http_https)

        database.init_app(app)
    
    return app