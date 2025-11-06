#!/usr/bin/env python3
"""
Comprehensive HTML Formatter - Properly tracks tag depth
"""

import re


def format_html_file(filepath):
    """Format HTML file with proper indentation"""
    print(f"Reading {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Normalize
    content = re.sub(r'<!doctype\s+html>', '<!DOCTYPE html>', content, flags=re.IGNORECASE)
    content = re.sub(r'<html\s+lang=["\']en-US["\']', '<html lang="en"', content)
    content = content.replace('\t', '  ')
    
    # Process line by line with proper tag tracking
    lines = content.split('\n')
    formatted_lines = []
    indent_level = 0
    indent_size = 2
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines for now
        if not line:
            i += 1
            continue
        
        # Handle DOCTYPE - no indent
        if line.startswith('<!DOCTYPE'):
            formatted_lines.append(line)
            i += 1
            continue
        
        # Handle HTML tag - no indent
        if line.startswith('<html'):
            formatted_lines.append(line)
            indent_level = 1
            i += 1
            continue
        
        # Handle closing tags
        if line.startswith('</'):
            indent_level = max(0, indent_level - 1)
            formatted_lines.append(' ' * (indent_level * indent_size) + line)
            i += 1
            continue
        
        # Handle comments
        if line.startswith('<!--'):
            formatted_lines.append(' ' * (indent_level * indent_size) + line)
            i += 1
            continue
        
        # Handle opening tags
        if line.startswith('<'):
            # Check if self-closing
            is_self_closing = (
                line.endswith('/>') or
                any(re.search(rf'<{tag}\b', line, re.IGNORECASE) 
                    for tag in ['meta', 'link', 'base', 'br', 'hr', 'img', 'input', 
                               'area', 'embed', 'source', 'track', 'col', 'wbr', 'svg'])
            )
            
            # Format tag
            formatted_tag = line
            
            # Normalize whitespace in long attributes
            if len(formatted_tag) > 120:
                formatted_tag = re.sub(r'\s+', ' ', formatted_tag)
            
            formatted_lines.append(' ' * (indent_level * indent_size) + formatted_tag)
            
            # Increase indent if not self-closing
            if not is_self_closing:
                indent_level += 1
            
            i += 1
            continue
        
        # Handle text content
        formatted_lines.append(' ' * (indent_level * indent_size) + line)
        i += 1
    
    # Add blank lines between major sections
    result = []
    prev_line = ''
    for line in formatted_lines:
        stripped = line.strip()
        
        # Add blank line before major sections
        if stripped.startswith(('<header', '<main', '<footer', '<nav', '<section', '<article')):
            if prev_line.strip() and not prev_line.strip().startswith('</'):
                result.append('')
        
        result.append(line)
        prev_line = line
    
    # Clean up excessive blank lines
    final_result = []
    prev_empty = False
    for line in result:
        if not line.strip():
            if not prev_empty:
                final_result.append('')
            prev_empty = True
        else:
            final_result.append(line)
            prev_empty = False
    
    # Join and remove trailing whitespace
    formatted_content = '\n'.join(final_result)
    formatted_lines = [line.rstrip() for line in formatted_content.split('\n')]
    formatted_content = '\n'.join(formatted_lines)
    
    # Final cleanup
    formatted_content = re.sub(r'\n{3,}', '\n\n', formatted_content)
    
    print(f"Writing formatted file...")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(formatted_content)
    
    print("Formatting complete!")


if __name__ == '__main__':
    import sys
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'professor-dashboard copy.html'
    format_html_file(filepath)

