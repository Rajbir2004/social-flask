import random
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from extensions import db, mail
from models import User, OTP
from forms import RegistrationForm, LoginForm, OTPForm, RequestResetForm, ResetPasswordForm
auth_bp = Blueprint('auth', __name__)
def send_reset_email(user):
    token = user.get_reset_token()
    from flask import current_app
    sender = current_app.config.get('MAIL_USERNAME')
    msg = Message('Password Reset Request', sender=sender, recipients=[user.email])
    msg.body = f"""To reset your password, visit the following link:
{url_for('auth.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
"""
    try:
        import socket
        socket.setdefaulttimeout(5)
        mail.send(msg)
    except Exception as e:
        print(f'\n--- DEVELOPMENT MODE ---')
        print(f'Failed to send reset email.')
        print(f'Your reset link for {user.email} is: {url_for("auth.reset_token", token=token, _external=True)}')
        print(f'------------------------\n', flush=True)

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('post.feed'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_request.html', title='Reset Password', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('post.feed'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        from werkzeug.security import generate_password_hash
        hashed_password = generate_password_hash(form.password.data)
        user.password = hashed_password
        from extensions import db
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_token.html', title='Reset Password', form=form)




from flask import current_app
def send_otp_email(user_email, otp_code):
    sender = current_app.config.get('MAIL_USERNAME')
    msg = Message('Verify your account', sender=sender, recipients=[user_email])
    msg.body = f'Your OTP code is {otp_code}. It is valid for 10 minutes.'
    try:
        import socket
        socket.setdefaulttimeout(5)
        mail.send(msg)
    except Exception as e:
        print(f'\n--- DEVELOPMENT MODE ---')
        print(f'Failed to send email. Check your MAIL_USERNAME and MAIL_PASSWORD in .env.')
        print(f'Your OTP code for {user_email} is: {otp_code}')
        print(f'------------------------\n', flush=True)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('post.feed'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        
        # Save details to session instead of DB
        session['pending_user'] = {
            'username': form.username.data,
            'email': form.email.data,
            'password': hashed_password
        }
        
        # Generate OTP
        otp_code = str(random.randint(100000, 999999))
        otp = OTP(email=form.email.data, otp_code=otp_code)
        db.session.add(otp)
        db.session.commit()
        
        send_otp_email(form.email.data, otp_code)
        session['verify_email'] = form.email.data
        
        flash('Please check your email for the OTP to verify your account.', 'info')
        return redirect(url_for('auth.verify_otp'))
    return render_template('auth/register.html', title='Register', form=form)

@auth_bp.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if current_user.is_authenticated:
        return redirect(url_for('post.feed'))
    email = session.get('verify_email')
    pending_user = session.get('pending_user')
    if not email or not pending_user:
        flash('Please register first.', 'warning')
        return redirect(url_for('auth.register'))
        
    form = OTPForm()
    if form.validate_on_submit():
        otp_record = OTP.query.filter_by(email=email).order_by(OTP.created_at.desc()).first()
        if otp_record and otp_record.otp_code == form.otp_code.data:
            # Create user now
            user = User(
                username=pending_user['username'],
                email=pending_user['email'],
                password=pending_user['password']
            )
            db.session.add(user)
            
            OTP.query.filter_by(email=email).delete()
            db.session.commit()
            
            login_user(user)
            session.pop('verify_email', None)
            session.pop('pending_user', None)
            flash('Your account has been verified and created!', 'success')
            return redirect(url_for('post.feed'))
        else:
            flash('Invalid OTP or OTP expired. Please try again.', 'danger')
            
    return render_template('auth/verify_otp.html', title='Verify OTP', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('post.feed'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('post.feed'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('auth/login.html', title='Login', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
