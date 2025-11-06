#!/usr/bin/env python3
"""
HTML Formatter using BeautifulSoup for proper parsing
"""

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False
    print("BeautifulSoup not available. Using simpler formatter.")

import re


def format_with_beautifulsoup(content):
    """Format HTML using BeautifulSoup"""
    soup = BeautifulSoup(content, 'html.parser')
    
    # Format the soup with proper indentation
    formatted = soup.prettify(indent=2)
    
    # Clean up some BeautifulSoup quirks
    # Remove extra blank lines
    lines = formatted.split('\n')
    cleaned_lines = []
    prev_empty = False
    
    for line in lines:
        stripped = line.rstrip()
        
        # Skip multiple consecutive empty lines
        if not stripped:
            if not prev_empty:
                cleaned_lines.append('')
            prev_empty = True
        else:
            cleaned_lines.append(stripped)
            prev_empty = False
    
    return '\n'.join(cleaned_lines)


def format_simple(content):
    """Simple formatter without BeautifulSoup"""
    # Normalize DOCTYPE
    content = re.sub(r'<!doctype\s+html>', '<!DOCTYPE html>', content, flags=re.IGNORECASE)
    
    # Fix lang attribute
    content = re.sub(r'<html\s+lang=["\']en-US["\']', '<html lang="en"', content)
    
    # Convert tabs to spaces
    content = content.replace('\t', '  ')
    
    # Remove trailing whitespace
    lines = content.split('\n')
    lines = [line.rstrip() for line in lines]
    content = '\n'.join(lines)
    
    # Remove excessive blank lines (more than 2 consecutive)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Simple indentation fix - track tag depth
    lines = content.split('\n')
    formatted_lines = []
    indent_level = 0
    indent_size = 2
    
    for line in lines:
        stripped = line.strip()
        
        if not stripped:
            # Keep single blank lines
            formatted_lines.append('')
            continue
        
        # Handle closing tags
        if stripped.startswith('</'):
            indent_level = max(0, indent_level - 1)
            formatted_lines.append(' ' * (indent_level * indent_size) + stripped)
            continue
        
        # Handle DOCTYPE and HTML tag - no indent
        if stripped.startswith('<!DOCTYPE') or (stripped.startswith('<html') and indent_level == 0):
            formatted_lines.append(stripped)
            if stripped.startswith('<html'):
                indent_level = 1
            continue
        
        # Handle comments
        if stripped.startswith('<!--'):
            formatted_lines.append(' ' * (indent_level * indent_size) + stripped)
            continue
        
        # Handle opening tags
        if stripped.startswith('<'):
            # Check if this is a self-closing tag
            is_self_closing = (
                stripped.endswith('/>') or
                any(re.search(rf'<{tag}\b', stripped, re.IGNORECASE) for tag in 
                    ['meta', 'link', 'base', 'br', 'hr', 'img', 'input', 'area', 'embed', 'source', 'track', 'col', 'wbr'])
            )
            
            formatted_lines.append(' ' * (indent_level * indent_size) + stripped)
            
            if not is_self_closing:
                indent_level += 1
            continue
        
        # Handle text content
        formatted_lines.append(' ' * (indent_level * indent_size) + stripped)
    
    return '\n'.join(formatted_lines)


def format_html_file(filepath):
    """Format an HTML file"""
    print(f"Reading {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try BeautifulSoup first, fall back to simple formatter
    if BEAUTIFULSOUP_AVAILABLE:
        try:
            print("Using BeautifulSoup formatter...")
            formatted_content = format_with_beautifulsoup(content)
        except Exception as e:
            print(f"BeautifulSoup failed: {e}. Using simple formatter...")
            formatted_content = format_simple(content)
    else:
        print("Using simple formatter...")
        formatted_content = format_simple(content)
    
    # Post-processing: fix common issues
    # Remove empty divs (but keep structure)
    # Fix excessive blank lines
    formatted_content = re.sub(r'\n{3,}', '\n\n', formatted_content)
    
    # Write back
    print(f"Writing formatted file...")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(formatted_content)
    
    print("Formatting complete!")


if __name__ == '__main__':
    import sys
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'professor-dashboard copy.html'
    format_html_file(filepath)

