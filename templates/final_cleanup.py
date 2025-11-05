import re

# Read the file
with open('professor-dashboard copy.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the JSON blob after <body
# The pattern is: <body"contacts_and_campaigns_redesign" ... "email":{"signUp":"Sign up for news and updates"}
# followed by \n  <body
pattern = r'<body"[^"]*"contacts_and_campaigns_redesign".*?"email":\{"signUp":"Sign up for news and updates"\}\s*\n\s*<body'
replacement = '<body'

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Also remove any remaining Squarespace CDN URLs and convert them to Flask url_for
# Find all URLs starting with https://assets.squarespace.com, https://static1.squarespace.com, etc.
def replace_cdn_url(match):
    url = match.group(0)
    # Extract filename
    filename = url.split('/')[-1].split('?')[0]  # Remove query params
    
    # Determine file type based on extension
    if filename.endswith('.css'):
        return f"{{{{ url_for('static', filename='css/{filename}') }}}}"
    elif filename.endswith('.js'):
        return f"{{{{ url_for('static', filename='js/{filename}') }}}}"
    elif filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp')):
        return f"{{{{ url_for('static', filename='images/{filename}') }}}}"
    else:
        return url  # Keep original if we can't determine type

# Replace Squarespace CDN URLs
cdn_patterns = [
    r'https://assets\.squarespace\.com/[^"\s]+',
    r'https://static1\.squarespace\.com/[^"\s]+',
    r'https://images\.squarespace-cdn\.com/[^"\s]+',
    r'https://definitions\.sqspcdn\.com/[^"\s]+'
]

for pattern in cdn_patterns:
    content = re.sub(pattern, replace_cdn_url, content)

# Remove any script/link tags loading from squarespace.com, sqspcdn.com, or typekit.net
content = re.sub(r'<script[^>]*src=["\'][^"\']*(?:squarespace|sqspcdn|typekit)[^"\']*["\'][^>]*></script>', '', content, flags=re.IGNORECASE)
content = re.sub(r'<link[^>]*href=["\'][^"\']*(?:squarespace|sqspcdn|typekit)[^"\']*["\'][^>]*>', '', content, flags=re.IGNORECASE)

# Remove data-controller attributes
content = re.sub(r'\s+data-controller="[^"]*"', '', content)

# Write back
with open('professor-dashboard copy.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Final cleanup completed")

