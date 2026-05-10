from datetime import datetime, timezone
import os
import secrets
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_required
from extensions import db
from models import User, Post, Notification, Report
from forms import EditProfileForm
from werkzeug.utils import secure_filename

user_bp = Blueprint('user', __name__)

import cloudinary.uploader
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
        return picture_fn

@user_bp.route('/user/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts
    return render_template('user/profile.html', user=user, posts=posts)

@user_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            # optionally delete old picture
            current_user.profile_pic = picture_file
        current_user.username = form.username.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('user.profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.bio.data = current_user.bio
    return render_template('user/edit_profile.html', title='Edit Profile', form=form)

@user_bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.', 'danger')
        return redirect(url_for('post.feed'))
    if user == current_user:
        flash('You cannot follow yourself!', 'warning')
        return redirect(url_for('user.profile', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are following {username}!', 'success')
    return redirect(url_for('user.profile', username=username))

@user_bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'User {username} not found.', 'danger')
        return redirect(url_for('post.feed'))
    if user == current_user:
        flash('You cannot unfollow yourself!', 'warning')
        return redirect(url_for('user.profile', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You are not following {username}.', 'info')
    return redirect(url_for('user.profile', username=username))

@user_bp.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    users = []
    if query:
        users = User.query.filter(User.username.ilike(f'%{query}%')).all()
    return render_template('user/search.html', users=users, query=query)

@user_bp.route('/user/<string:username>/report', methods=['POST'])
@login_required
def report_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    reason = request.form.get('reason')
    if not reason:
        flash('Please provide a reason for reporting.', 'warning')
        return redirect(url_for('user.profile', username=user.username))
    report = Report(reporter_id=current_user.id, reported_user_id=user.id, reason=reason)
    db.session.add(report)
    db.session.commit()
    flash('User has been reported for review.', 'info')
    return redirect(url_for('user.profile', username=user.username))

@user_bp.route('/notifications')
@login_required
def notifications():
    notifs = Notification.query.filter_by(recipient_id=current_user.id).order_by(Notification.timestamp.desc()).all()
    # Mark all as read
    for n in notifs:
        n.is_read = True
    db.session.commit()
    return render_template('user/notifications.html', notifications=notifs)
