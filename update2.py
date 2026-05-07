import sys
import os

# 1. Update app.py to configure Cloudinary
with open('app.py', 'r') as f:
    app_content = f.read()
if 'import cloudinary' not in app_content:
    app_content = app_content.replace('from extensions import db, login_manager, mail', 
        '}'''from extensions import db, login_manager, mail
import cloudinary
import cloudinary.uploader
import cloudinary.api''')
    target = 'mail.init_app(app)'
    replacement = '''mail.init_app(app)
    if app.config.get('CLOUDINARY_CLOUD_NAME'):
        cloudinary.config(
            cloud_name = app.config.get('CLOUDINARY_CLOUD_NAME'),
            api_key = app.config.get('CLOUDINARY_API_KEY'),
            api_secret = app.config.get('CLOUDINARY_API_SECRET'),
            secure=True
        )'''
    app_content = app_content.replace(target, replacement)
    with open('app.py', 'w') as f:
        f.write(app_content)
    print('Updated app.py')

# 2. Update routes/post.py
with open('routes/post.py', 'r') as f:
    post_content = f.read()
target_save = '''def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_fn)
    form_picture.save(picture_path)
    return picture_fn'''
replacement_save = '''import cloudinary.uploader
def save_picture(form_picture):
    if current_app.config.get('CLOUDINARY_CLOUD_NAME'):
        result = cloudinary.uploader.upload(form_picture)
        return result["secure_url"]
    else:
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_fn)
        form_picture.save(picture_path)
        return picture_fn'''
if 'cloudinary.uploader' not in post_content:
    post_content = post_content.replace(target_save, replacement_save)
    
    # Add AJAX likes
    target_like = '''@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
    else:
        new_like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(new_like)
        db.session.commit()
    return redirect(request.referrer or url_for('post.feed'))'''
    replacement_like = '''from flask import jsonify
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    liged_now = False
    if like:
        db.session.delete(like)
        db.session.commit()
    else:
        new_like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(new_like)
        db.session.commit()
        liked_now = True
    if request.is_json:
        return jsonify({'liked': liked_now, 'like_count': len(post.likes)})
    return redirect(request.referrer or url_for('post.feed'))'''
    post_content = post_content.replace(target_like, replacement_like)
    with open('routes/post.py', 'w') as f:
        f.write(post_content)
    print('Updated routes/post.py')

# 3. Update routes/user.py
with open('routes/user.py', 'r') as f:
    user_content = f.read()
if 'cloudinary.uploader' not in user_content:
    user_content = user_content.replace(target_save, replacement_save)
    with open('routes/user.py', 'w') as f:
        f.write(user_content)
    print('Updated routes/user.py')
