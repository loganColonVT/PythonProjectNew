#!/usr/bin/env python3
"""
Final HTML Formatter - Properly handles HTML structure
"""

import re


def format_html_file(filepath):
    """Format HTML file with proper indentation"""
    print(f"Reading {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Step 1: Normalize basic structure
    content = re.sub(r'<!doctype\s+html>', '<!DOCTYPE html>', content, flags=re.IGNORECASE)
    content = re.sub(r'<html\s+lang=["\']en-US["\']', '<html lang="en"', content)
    content = content.replace('\t', '  ')  # Convert tabs to spaces
    
    # Step 2: Process line by line with proper tag tracking
    lines = content.split('\n')
    formatted = []
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
            formatted.append(line)
            i += 1
            continue
        
        # Handle HTML tag - no indent
        if line.startswith('<html'):
            formatted.append(line)
            indent_level = 1
            i += 1
            continue
        
        # Handle closing tags
        if line.startswith('</'):
            indent_level = max(0, indent_level - 1)
            formatted.append(' ' * (indent_level * indent_size) + line)
            i += 1
            continue
        
        # Handle comments
        if line.startswith('<!--'):
            formatted.append(' ' * (indent_level * indent_size) + line)
            i += 1
            continue
        
        # Handle opening tags - need to handle multi-line tags
        if line.startswith('<'):
            # Check if this tag spans multiple lines
            tag_content = [line]
            j = i + 1
            
            # Look ahead to see if tag continues
            while j < len(lines):
                next_line = lines[j].strip()
                if not next_line:
                    j += 1
                    continue
                
                # If we find another tag starting, we're done
                if next_line.startswith('<') and not next_line.startswith('</'):
                    break
                
                # If we find a closing bracket, we're done
                if '>' in next_line:
                    tag_content.append(next_line)
                    j += 1
                    break
                
                # Continue collecting tag parts
                tag_content.append(next_line)
                j += 1
            
            # Join tag parts
            full_tag = ' '.join(tag_content)
            
            # Check if self-closing
            is_self_closing = (
                full_tag.endswith('/>') or
                any(re.search(rf'<{tag}\b', full_tag, re.IGNORECASE) 
                    for tag in ['meta', 'link', 'base', 'br', 'hr', 'img', 'input', 
                               'area', 'embed', 'source', 'track', 'col', 'wbr'])
            )
            
            # Format long class attributes
            if 'class=' in full_tag and len(full_tag) > 120:
                # Normalize whitespace in class attribute
                full_tag = re.sub(r'\s+', ' ', full_tag)
            
            # Add formatted tag
            formatted.append(' ' * (indent_level * indent_size) + full_tag)
            
            # Increase indent if not self-closing
            if not is_self_closing:
                indent_level += 1
            
            i = j
            continue
        
        # Handle text content
        formatted.append(' ' * (indent_level * indent_size) + line)
        i += 1
    
    # Step 3: Add blank lines between major sections
    result = []
    prev_line = ''
    for line in formatted:
        stripped = line.strip()
        
        # Add blank line before major sections
        if stripped.startswith('<header') or stripped.startswith('<main') or \
           stripped.startswith('<footer') or stripped.startswith('<nav') or \
           stripped.startswith('<section'):
            if prev_line.strip() and not prev_line.strip().startswith('</'):
                result.append('')
        
        result.append(line)
        prev_line = line
    
    # Step 4: Clean up excessive blank lines
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
    
    # Join and write
    formatted_content = '\n'.join(final_result)
    
    # Remove trailing whitespace from each line
    formatted_lines = [line.rstrip() for line in formatted_content.split('\n')]
    formatted_content = '\n'.join(formatted_lines)
    
    # Final cleanup: remove more than 2 consecutive blank lines
    formatted_content = re.sub(r'\n{3,}', '\n\n', formatted_content)
    
    print(f"Writing formatted file...")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(formatted_content)
    
    print("Formatting complete!")


if __name__ == '__main__':
    import sys
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'professor-dashboard copy.html'
    format_html_file(filepath)

