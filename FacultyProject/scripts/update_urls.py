import os
import glob
import re

# Resolve root directory templates dynamically
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))

for filepath in glob.glob(os.path.join(template_dir, '*.html')):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace url_for('route_name' with url_for('main.route_name' 
    # ensuring we don't prefix 'static' or already 'main' prefixed routes
    updated_content = re.sub(r"url_for\('(?!(static|main\.))([^']+)'", r"url_for('main.\2'", content)
    updated_content = re.sub(r"url_for\(\"(?!(static|main\.))([^\"]+)\"", r"url_for('main.\2'", updated_content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(updated_content)

print("Updated all templates successfully.")
