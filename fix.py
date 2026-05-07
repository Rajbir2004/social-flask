import re
with open('routes/post.py', 'r') as f: content = f.read()

# Fix save_picture in post.py
content = re.sub(r'import cloudinary\.uploader\s*def save_picture.*?return picture_fn', 
'''import cloudinary.uploader
def save_picture(form_picture):
    if current_app.config.get('CLOUDINARY_CLOUD_NAME'):
        result = cloudinary.uploader.upload(form_picture)
        return result['secure_url']
    else:
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_fn)
        form_picture.save(picture_path)
        return picture_fn''', content, flags=re.DOTALL)

# Fix like_post in post.py
content = re.sub(r'@post_bp\.route\(\'/post/<int:post_id>/like\', methods=\[\'POST\'\]\).*?return redirect\(request\.referrer or url_for\(\'post\.feed\'\)\)',
'''from flask import jsonify
@post_bp.route('/post/<int:post_id>/like', methods=['POST'])
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
    return redirect(request.referrer or url_for('post.feed'))''', content, flags=re.DOTALL)

with open('routes/post.py', 'w') as f: f.write(content)

with open('routes/user.py', 'r') as f: user_content = f.read()

# Fix save_picture in user.py
user_content = re.sub(r'import cloudinary\.uploader\s*def save_picture.*?return picture_fn', 
'''import cloudinary.uploader
def save_picture(form_picture):
    if current_app.config.get('CLOUDINARY_CLOUD_NAME'):
        result = cloudinary.uploader.upload(form_picture)
        return result['secure_url']
    else:
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_fn)
        form_picture.save(picture_path)
        return picture_fn''', user_content, flags=re.DOTALL)

with open('routes/user.py', 'w') as f: f.write(user_content)

print('Fixed routes')
