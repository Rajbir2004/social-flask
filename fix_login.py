with open('templates/auth/login.html', 'r') as f:
    content = f.read()

target = 'Need an account? <a href="{{ url_for(\'auth.register\') }}">Sign Up Now</a>'
replacement = 'Need an account? <a href="{{ url_for(\'auth.register\') }}">Sign Up Now</a><br><br><a href="{{ url_for(\'auth.reset_request\') }}">Forgot Password?</a>'

if target in content:
    content = content.replace(target, replacement)
    with open('templates/auth/login.html', 'w') as f:
        f.write(content)
    print('Added Forgot Password link to login.html')
else:
    print('Target not found in login.html')
