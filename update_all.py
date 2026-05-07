import sys, os
def replace(path, old, new):
    with open(path, 'r') as f: content = f.read()
    if old in content:
        with open(path, 'w') as f: f.write(content.replace(old, new))
        print('Updated ' + path)

replace('app.py', 'from extensions import db, login_manager, mail', 'from extensions import db, login_manager, mail\nimport cloudinary\nimport cloudinary.uploader\nimport cloudinary.api')

replace('app.py', 'mail.init_app(app)', 'mail.init_app(app)\n    if app.config.get("CLOUDINARY_CLOUD_NAME"):\n        cloudinary.config(cloud_name=app.config.get("CLOUDINARY_CLOUD_NAME"), api_key=app.config.get("CLOUDINARY_API_KEY"), api_secret=app.config.get("CLOUDINARY_API_SECRET"), secure=True)')

save_old = '''def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_fn)
    form_picture.save(picture_path)
    return picture_fn'''

save_new = '''import cloudinary.uploader
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

replace('routes/post.py', save_old, save_new)
replace('routes/user.py', save_old, save_new)

like_old = '''@login_required
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

like_new = '''from flask import jsonify
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    liked_now = False
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

replace('routes/post.py', like_old, like_new)
