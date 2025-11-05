# Read the file
with open('professor-dashboard copy.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with the malformed <body tag and the next <body tag
output_lines = []
skip_until_body = False

for i, line in enumerate(lines):
    if skip_until_body:
        if line.strip().startswith('<body'):
            skip_until_body = False
            output_lines.append(line)
        # Skip all lines until we find the body tag
    elif line.strip().startswith('<body"'):
        # This is the malformed line - replace it with just <body
        output_lines.append('  <body\n')
        skip_until_body = True
    else:
        output_lines.append(line)

# Write back
with open('professor-dashboard copy.html', 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print("JSON blob removed")

