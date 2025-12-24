#!/usr/bin/env python3
"""
Script to fix line length issues by breaking long lines appropriately.
"""

import os
import re
from pathlib import Path

def fix_long_lines(file_path):
    """Fix long lines in a file by breaking them appropriately."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if len(line) > 100:
            # Try to break long f-strings
            if 'f"' in line and line.count('f"') == 1:
                # Find the f-string part
                f_string_match = re.search(r'f"([^"]*)"', line)
                if f_string_match:
                    f_string = f_string_match.group(1)
                    if len(f_string) > 80:
                        # Break the f-string into multiple parts
                        parts = f_string.split(' ')
                        if len(parts) > 1:
                            # Try to break at logical points
                            mid_point = len(parts) // 2
                            first_part = ' '.join(parts[:mid_point])
                            second_part = ' '.join(parts[mid_point:])
                            
                            # Create the broken line
                            prefix = line[:f_string_match.start()]
                            suffix = line[f_string_match.end():]
                            
                            new_line = f'{prefix}f"{first_part}"\n    f"{second_part}"{suffix}'
                            fixed_lines.append(new_line)
                            continue
            
            # Try to break long print statements
            if line.strip().startswith('print(') and 'f"' in line:
                # Extract the print content
                print_match = re.search(r'print\((.*)\)', line)
                if print_match:
                    print_content = print_match.group(1)
                    if len(print_content) > 80:
                        # Break the print statement
                        indent = len(line) - len(line.lstrip())
                        spaces = ' ' * (indent + 4)
                        
                        # Try to break at commas or logical points
                        if ',' in print_content:
                            parts = print_content.split(',', 1)
                            if len(parts) == 2:
                                new_line = f"{' ' * indent}print({parts[0]},\n{spaces}{parts[1]})"
                                fixed_lines.append(new_line)
                                continue
        
        fixed_lines.append(line)
    
    # Write back if changes were made
    new_content = '\n'.join(fixed_lines)
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {file_path}")
        return True
    return False

def main():
    """Main function to fix line lengths in all Python files."""
    # Get all Python files
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        if any(skip in root for skip in ['venv', '__pycache__', '.git', 'node_modules']):
            continue
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    fixed_count = 0
    for file_path in python_files:
        if fix_long_lines(file_path):
            fixed_count += 1
    
    print(f"Fixed {fixed_count} files")

if __name__ == "__main__":
    main()



