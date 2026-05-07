import sys

with open('routes/auth.py', 'r') as f:
    content = f.read()

imports = '''from forms import RegistrationForm, LoginForm, OTPForm, RequestResetForm, ResetPasswordForm
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
        mail.send(msg)
    except Exception as e:
        print(f'\\n--- DEVELOPMENT MODE ---')
        print(f'Failed to send reset email.')
        print(f'Your reset link for {user.email} is: {url_for("auth.reset_token", token=token, _external=True)}')
        print(f'------------------------\\n', flush=True)

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
'''

if 'def send_reset_email' not in content:
    content = content.replace('from forms import RegistrationForm, LoginForm, OTPForm', imports)
    with open('routes/auth.py', 'w') as f:
        f.write(content)
    print('Added reset routes to auth.py')

# Update login.html to add Forgot Password link
with open('templates/auth/login.html', 'r') as f:
    login_html = f.read()
if 'reset_request' not in login_html:
    target = '{{ form.submit(class="btn btn-outline-info") }}'
    replacement = '''{{ form.submit(class="btn btn-outline-info") }}
            <small class="text-muted ml-2">
                <a href="{{ url_for('auth.reset_request') }}">Forgot Password?</a>
            </small>'''
    login_html = login_html.replace(target, replacement)
    with open('templates/auth/login.html', 'w') as f:
        f.write(login_html)
    print('Updated login.html with forgot password link')