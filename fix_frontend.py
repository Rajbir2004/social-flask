import os

def fix_image_src(content):
    content = content.replace(
        "{{ url_for('static', filename='uploads/' + post.image_file) }}",
        "{% if post.image_file.startswith('http') %}{{ post.image_file }}{% else %}{{ url_for('static', filename='uploads/' + post.image_file) }}{% endif %}"
    )
    content = content.replace(
        "{{ url_for('static', filename='uploads/' + post.author.profile_pic) }}",
        "{% if post.author.profile_pic.startswith('http') %}{{ post.author.profile_pic }}{% else %}{{ url_for('static', filename='uploads/' + post.author.profile_pic) }}{% endif %}"
    )
    content = content.replace(
        "{{ url_for('static', filename='uploads/' + current_user.profile_pic) }}",
        "{% if current_user.profile_pic.startswith('http') %}{{ current_user.profile_pic }}{% else %}{{ url_for('static', filename='uploads/' + current_user.profile_pic) }}{% endif %}"
    )
    content = content.replace(
        "{{ url_for('static', filename='uploads/' + user.profile_pic) }}",
        "{% if user.profile_pic.startswith('http') %}{{ user.profile_pic }}{% else %}{{ url_for('static', filename='uploads/' + user.profile_pic) }}{% endif %}"
    )
    content = content.replace(
        'class="d-inline"',
        'class="d-inline like-form"'
    )
    return content

for root, _, files in os.walk('templates'):
    for file in files:
        if file.endswith('.html'):
            path = os.path.join(root, file)
            with open(path, 'r') as f:
                content = f.read()
            new_content = fix_image_src(content)
            if new_content != content:
                with open(path, 'w') as f:
                    f.write(new_content)
                print("Fixed " + path)

ajax_script = '''
<script>
document.addEventListener('DOMContentLoaded', function() {
    const likeForms = document.querySelectorAll('.like-form');
    likeForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const url = this.action;
            const btn = this.querySelector('button');
            const container = this.closest('.post-actions');
            const countSpan = container.querySelector('.like-count');
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if(data.liked) {
                    btn.classList.add('liked');
                } else {
                    btn.classList.remove('liked');
                }
                countSpan.textContent = data.like_count + ' likes';
            })
            .catch(error => console.error('Error:', error));
        });
    });
});
</script>
</body>
'''

with open('templates/base.html', 'r') as f: base_html = f.read()
if 'likeForms' not in base_html:
    base_html = base_html.replace('</body>', ajax_script)
    with open('templates/base.html', 'w') as f: f.write(base_html)
    print("Added AJAX to base.html")
