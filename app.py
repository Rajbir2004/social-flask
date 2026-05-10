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
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(user_bp)
        app.register_blueprint(admin_bp)

    # Ensure upload folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    print("Connecting to database...", flush=True)
    with app.app_context():
        db.create_all()
    print("Database connected!", flush=True)

    
    from flask_login import current_user
    from datetime import datetime, timezone
    from models import Notification

    @app.before_request
    def before_request():
        from models import User
        if User.query.filter_by(is_admin=True).first() is None:
            first_user = User.query.first()
            if first_user:
                first_user.is_admin = True
                db.session.commit()
        if current_user.is_authenticated:
            current_user.last_seen = datetime.now(timezone.utc)
            db.session.commit()
            if current_user.is_banned:
                from flask_login import logout_user
                logout_user()
                flash('Your account has been banned.', 'danger')

    @app.context_processor
    def inject_notifications():
        if current_user.is_authenticated:
            count = Notification.query.filter_by(recipient_id=current_user.id, is_read=False).count()
            return dict(unread_notifications=count)
        return dict(unread_notifications=0)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
