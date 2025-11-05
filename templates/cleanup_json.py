import re

# Read the file
with open('professor-dashboard copy.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the JSON blob after <body
# Find the pattern: <body followed by JSON until the actual body attributes start
# Match everything from "contacts_and_campaigns_redesign" to "email":{"signUp":"Sign up for news and updates"}
pattern = r'<body"[^"]*"contacts_and_campaigns_redesign".*?"email":\{"signUp":"Sign up for news and updates"\}\s*'
replacement = '<body'

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write back
with open('professor-dashboard copy.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("JSON blob removed from body tag")

