import os
from flask import Flask
from config import Config
from extensions import db, login_manager, mail
import cloudinary
import cloudinary.uploader
import cloudinary.api
import cloudinary
import cloudinary.uploader
import cloudinary.api

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    if app.config.get("CLOUDINARY_CLOUD_NAME"):
        cloudinary.config(cloud_name=app.config.get("CLOUDINARY_CLOUD_NAME"), api_key=app.config.get("CLOUDINARY_API_KEY"), api_secret=app.config.get("CLOUDINARY_API_SECRET"), secure=True)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.post import post_bp
    from routes.user import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(user_bp)

    # Ensure upload folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    print("Connecting to database...", flush=True)
    with app.app_context():
        db.create_all()
    print("Database connected!", flush=True)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
