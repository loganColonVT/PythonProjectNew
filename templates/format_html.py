#!/usr/bin/env python3
"""
HTML Formatter - Formats HTML files for readability
- Uses 2 spaces for indentation
- Removes excessive blank lines
- Organizes scripts/styles
- Formats long attributes
"""

import re
from html.parser import HTMLParser


class HTMLFormatter:
    def __init__(self):
        self.output = []
        self.indent_level = 0
        self.indent_size = 2
        self.in_head = False
        self.in_body = False
        self.scripts = []
        self.styles = []
        self.current_tag = None
        self.current_data = []
        
    def format_file(self, content):
        """Main formatting function"""
        # Split content into lines
        lines = content.split('\n')
        formatted_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i].rstrip()
            
            # Skip completely empty lines for now (we'll add them back selectively)
            if not line.strip():
                i += 1
                continue
            
            # Handle closing tags
            if line.strip().startswith('</'):
                self.indent_level = max(0, self.indent_level - 1)
                formatted_lines.append(' ' * (self.indent_level * self.indent_size) + line.strip())
                i += 1
                continue
            
            # Handle opening tags
            if line.strip().startswith('<') and not line.strip().startswith('</'):
                tag_match = re.match(r'<(\w+)', line.strip())
                if tag_match:
                    tag_name = tag_match.group(1).lower()
                    
                    # Track head/body state
                    if tag_name == 'head':
                        self.in_head = True
                    elif tag_name == 'body':
                        self.in_body = True
                    elif tag_name == '/head':
                        self.in_head = False
                    elif tag_name == '/body':
                        self.in_body = False
                    
                    # Format the tag
                    formatted_tag = self.format_tag(line.strip())
                    formatted_lines.append(' ' * (self.indent_level * self.indent_size) + formatted_tag)
                    
                    # Increase indent for non-self-closing tags
                    if not self.is_self_closing(tag_name) and not line.strip().endswith('/>'):
                        self.indent_level += 1
                
                i += 1
                continue
            
            # Handle text content
            if line.strip() and not line.strip().startswith('<'):
                formatted_lines.append(' ' * (self.indent_level * self.indent_size) + line.strip())
                i += 1
                continue
            
            i += 1
        
        return '\n'.join(formatted_lines)
    
    def format_tag(self, tag_line):
        """Format a single tag with proper attribute wrapping"""
        # Handle very long class attributes
        if 'class="' in tag_line or "class='" in tag_line:
            # Extract class attribute
            class_match = re.search(r'class=["\']([^"\']+)["\']', tag_line)
            if class_match and len(class_match.group(1)) > 80:
                classes = class_match.group(1).strip()
                # Split into multiple lines
                class_parts = classes.split()
                formatted_classes = ' '.join(class_parts)
                # Replace in tag
                tag_line = re.sub(
                    r'class=["\']([^"\']+)["\']',
                    f'class="{formatted_classes}"',
                    tag_line
                )
        
        # Format attributes that are too long
        if len(tag_line) > 120:
            # Try to break long attributes
            tag_parts = tag_line.split()
            if len(tag_parts) > 3:
                # Keep tag name and first attribute on first line
                result = [tag_parts[0]]
                for part in tag_parts[1:]:
                    if len(' '.join(result) + ' ' + part) > 120:
                        result.append('\n' + ' ' * (self.indent_level * self.indent_size + self.indent_size) + part)
                    else:
                        result.append(part)
                return ' '.join(result)
        
        return tag_line
    
    def is_self_closing(self, tag_name):
        """Check if tag is self-closing"""
        self_closing_tags = ['img', 'br', 'hr', 'input', 'meta', 'link', 'base', 'area', 'embed', 'source', 'track', 'col', 'wbr']
        return tag_name.lower() in self_closing_tags


def format_html_file(filepath):
    """Format an HTML file"""
    print(f"Reading {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Step 1: Normalize DOCTYPE
    content = re.sub(r'<!doctype\s+html>', '<!DOCTYPE html>', content, flags=re.IGNORECASE)
    
    # Step 2: Fix lang attribute
    content = re.sub(r'<html\s+lang=["\']en-US["\']', '<html lang="en"', content)
    
    # Step 3: Remove excessive blank lines (more than 2 consecutive)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Step 4: Convert tabs to spaces
    content = content.replace('\t', '  ')
    
    # Step 5: Remove trailing whitespace
    lines = content.split('\n')
    lines = [line.rstrip() for line in lines]
    content = '\n'.join(lines)
    
    # Step 6: Format with proper indentation using a simpler approach
    lines = content.split('\n')
    formatted_lines = []
    indent_level = 0
    indent_size = 2
    in_head = False
    in_body = False
    skip_empty_line = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Skip empty lines temporarily
        if not stripped:
            skip_empty_line = True
            continue
        
        # Handle closing tags
        if stripped.startswith('</'):
            indent_level = max(0, indent_level - 1)
            formatted_lines.append(' ' * (indent_level * indent_size) + stripped)
            skip_empty_line = False
            continue
        
        # Handle opening tags
        if stripped.startswith('<') and not stripped.startswith('</'):
            # Check for doctype - no indent
            if stripped.startswith('<!DOCTYPE'):
                formatted_lines.append(stripped)
                skip_empty_line = False
                continue
            
            # Check for html tag - no indent
            if stripped.startswith('<html'):
                formatted_lines.append(stripped)
                indent_level = 1
                skip_empty_line = False
                continue
            
            # Check for head/body tags
            if stripped.startswith('<head'):
                in_head = True
                in_body = False
            elif stripped.startswith('<body'):
                in_head = False
                in_body = True
            elif stripped.startswith('</head'):
                in_head = False
            elif stripped.startswith('</body'):
                in_body = False
            
            # Format long class attributes
            if 'class=' in stripped and len(stripped) > 100:
                # Try to format the class attribute better
                class_match = re.search(r'class=["\']([^"\']+)["\']', stripped)
                if class_match:
                    classes = class_match.group(1).strip()
                    # Keep it on one line but ensure proper spacing
                    stripped = re.sub(r'\s+', ' ', stripped)
            
            formatted_lines.append(' ' * (indent_level * indent_size) + stripped)
            
            # Check if this is a self-closing tag
            if not stripped.endswith('/>') and not self_closing_tag(stripped):
                # Check if tag is closed on same line
                if '>' in stripped and not stripped.endswith('>'):
                    # Tag continues on next line or is closed
                    pass
                else:
                    indent_level += 1
            
            skip_empty_line = False
            continue
        
        # Handle text content
        formatted_lines.append(' ' * (indent_level * indent_size) + stripped)
        skip_empty_line = False
    
    # Add blank lines between major sections
    result = []
    prev_line = ''
    for i, line in enumerate(formatted_lines):
        stripped = line.strip()
        
        # Add blank line before major sections
        if stripped.startswith('<header') or stripped.startswith('<main') or stripped.startswith('<footer') or stripped.startswith('<nav'):
            if prev_line.strip() and not prev_line.strip().startswith('</'):
                result.append('')
        
        result.append(line)
        prev_line = line
    
    # Join and clean up excessive blank lines
    formatted_content = '\n'.join(result)
    formatted_content = re.sub(r'\n{3,}', '\n\n', formatted_content)
    
    # Write back
    print(f"Writing formatted file...")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(formatted_content)
    
    print("Formatting complete!")


def self_closing_tag(line):
    """Check if line contains a self-closing tag"""
    self_closing = ['img', 'br', 'hr', 'input', 'meta', 'link', 'base', 'area', 'embed', 'source', 'track', 'col', 'wbr']
    for tag in self_closing:
        if re.search(rf'<{tag}\b', line, re.IGNORECASE):
            return True
    return False


if __name__ == '__main__':
    import sys
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'professor-dashboard copy.html'
    format_html_file(filepath)

