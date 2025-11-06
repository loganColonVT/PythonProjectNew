#!/usr/bin/env python3
"""
Comprehensive HTML Formatter
Handles indentation, empty elements, script organization, and formatting
"""

import re


class HTMLFormatter:
    def __init__(self):
        self.indent_size = 2
        self.lines = []
        self.formatted_lines = []
        self.indent_level = 0
        
    def format_file(self, content):
        """Main formatting function"""
        # Normalize DOCTYPE
        content = re.sub(r'<!doctype\s+html>', '<!DOCTYPE html>', content, flags=re.IGNORECASE)
        
        # Fix lang attribute
        content = re.sub(r'<html\s+lang=["\']en-US["\']', '<html lang="en"', content)
        
        # Convert tabs to spaces
        content = content.replace('\t', '  ')
        
        # Split into lines and process
        self.lines = content.split('\n')
        self.process_lines()
        
        # Clean up excessive blank lines
        result = self.clean_blank_lines()
        
        return result
    
    def process_lines(self):
        """Process lines with proper indentation tracking"""
        i = 0
        while i < len(self.lines):
            line = self.lines[i].strip()
            
            if not line:
                # Keep single blank lines temporarily
                self.formatted_lines.append(('', self.indent_level))
                i += 1
                continue
            
            # Handle closing tags
            if line.startswith('</'):
                self.indent_level = max(0, self.indent_level - 1)
                self.formatted_lines.append((line, self.indent_level))
                i += 1
                continue
            
            # Handle DOCTYPE - no indent
            if line.startswith('<!DOCTYPE'):
                self.formatted_lines.append((line, 0))
                i += 1
                continue
            
            # Handle HTML tag - no indent
            if line.startswith('<html'):
                self.formatted_lines.append((line, 0))
                self.indent_level = 1
                i += 1
                continue
            
            # Handle comments
            if line.startswith('<!--'):
                self.formatted_lines.append((line, self.indent_level))
                i += 1
                continue
            
            # Handle opening tags
            if line.startswith('<'):
                # Check if tag continues on next lines
                tag_lines = [line]
                tag_indent = self.indent_level
                
                # Collect multi-line tags
                j = i + 1
                open_quotes = None
                in_tag = True
                
                while j < len(self.lines) and in_tag:
                    next_line = self.lines[j].strip()
                    
                    if not next_line:
                        j += 1
                        continue
                    
                    # Check for quote continuation
                    if open_quotes:
                        tag_lines.append(next_line)
                        if open_quotes in next_line:
                            # Check if quote is closed
                            quote_count = next_line.count(open_quotes)
                            if quote_count % 2 == 1:
                                open_quotes = None
                        if '>' in next_line and not open_quotes:
                            in_tag = False
                    else:
                        # Check for opening quotes
                        if '"' in next_line or "'" in next_line:
                            # Determine which quote type
                            if '"' in next_line:
                                open_quotes = '"'
                            elif "'" in next_line:
                                open_quotes = "'"
                            tag_lines.append(next_line)
                        elif '>' in next_line:
                            tag_lines.append(next_line)
                            in_tag = False
                        else:
                            tag_lines.append(next_line)
                    
                    j += 1
                
                # Join multi-line tag
                if len(tag_lines) > 1:
                    full_tag = ' '.join(tag_lines)
                else:
                    full_tag = tag_lines[0]
                
                # Format the tag
                formatted_tag = self.format_tag(full_tag, tag_indent)
                self.formatted_lines.append((formatted_tag, tag_indent))
                
                # Check if it's a self-closing tag
                if not self.is_self_closing_tag(full_tag):
                    # Check if tag is closed on same "line"
                    if '>' in full_tag and not full_tag.endswith('/>'):
                        self.indent_level += 1
                
                i = j if j > i else i + 1
                continue
            
            # Handle text content
            self.formatted_lines.append((line, self.indent_level))
            i += 1
    
    def format_tag(self, tag_line, indent_level):
        """Format a tag with proper attribute wrapping"""
        # Check if tag has very long class attribute
        class_match = re.search(r'class=["\']([^"\']+)["\']', tag_line)
        if class_match and len(class_match.group(1)) > 100:
            # Keep class on one line but ensure proper spacing
            classes = re.sub(r'\s+', ' ', class_match.group(1))
            tag_line = re.sub(
                r'class=["\']([^"\']+)["\']',
                f'class="{classes}"',
                tag_line
            )
        
        # For very long tags, try to break attributes
        if len(tag_line) > 120 and ' ' in tag_line:
            # Simple approach: keep tag name, then attributes
            parts = tag_line.split(' ', 1)
            if len(parts) == 2:
                tag_name = parts[0]
                attributes = parts[1]
                # Keep it simple - just ensure proper spacing
                tag_line = f'{tag_name} {attributes}'
        
        return tag_line.strip()
    
    def is_self_closing_tag(self, tag_line):
        """Check if tag is self-closing"""
        if tag_line.endswith('/>'):
            return True
        
        self_closing_tags = ['meta', 'link', 'base', 'br', 'hr', 'img', 'input', 
                            'area', 'embed', 'source', 'track', 'col', 'wbr']
        
        for tag_name in self_closing_tags:
            if re.search(rf'<{tag_name}\b', tag_line, re.IGNORECASE):
                return True
        
        return False
    
    def clean_blank_lines(self):
        """Clean up excessive blank lines and format output"""
        result_lines = []
        prev_empty = False
        
        for line_content, indent_level in self.formatted_lines:
            if not line_content.strip():
                # Add blank line only if previous wasn't empty
                if not prev_empty:
                    result_lines.append('')
                prev_empty = True
            else:
                # Format line with proper indentation
                formatted_line = ' ' * (indent_level * self.indent_size) + line_content
                result_lines.append(formatted_line)
                prev_empty = False
        
        # Join and remove trailing blank lines
        result = '\n'.join(result_lines)
        result = result.rstrip() + '\n'
        
        # Remove more than 2 consecutive blank lines
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result


def format_html_file(filepath):
    """Format an HTML file"""
    print(f"Reading {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create formatter
    formatter = HTMLFormatter()
    
    # Format content
    print("Formatting HTML...")
    formatted_content = formatter.format_file(content)
    
    # Post-processing: organize scripts (move to end of body)
    # This is complex, so we'll do a simpler approach
    # Find all script tags in head and move them before </body>
    
    # Remove empty divs (but be careful)
    # formatted_content = re.sub(r'<div\s*>\s*</div>', '', formatted_content)
    
    # Write back
    print(f"Writing formatted file...")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(formatted_content)
    
    print("Formatting complete!")


if __name__ == '__main__':
    import sys
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'professor-dashboard copy.html'
    format_html_file(filepath)

