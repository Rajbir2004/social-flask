import sys, os
def replace(path, old, new):
    with open(path, 'r') as f: content = f.read()
    if old in content:
        with open(path, 'w') as f: f.write(content.replace(old, new))
        print('Updated ' + path)
replace('app.py', 'from extensions import db, login_manager, mail', 'from extensions import db, login_manager, mail\nimport cloudinary\nimport cloudinary.uploader\nimport cloudinary.api')
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
    else:
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_fn)
        form_picture.save(picture_path)
        return picture_fn'''
replace('routes/post.py', save_old, save_new)
replace('routes/user.py', save_old, save_new)
