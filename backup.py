import os
from datetime import datetime

def create_backup():
    # Output file
    backup_file = 'backup.txt'
    
    # Files and directories to ignore
    ignore_files = {'README.md', 'backup.py', 'backup.txt'}
    ignore_dirs = {'__pycache__'}
    
    # Get current directory structure
    def get_directory_structure(start_path):
        structure = []
        for root, dirs, files in os.walk(start_path):
            # Remove ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            level = root.replace(start_path, '').count(os.sep)
            indent = '  ' * level
            structure.append(f'{indent}{os.path.basename(root)}/')
            for file in files:
                if file not in ignore_files:
                    structure.append(f'{indent}  {file}')
        return '\n'.join(structure)

    # Create backup content
    with open(backup_file, 'w', encoding='utf-8') as backup:
        # Write directory structure
        backup.write("Directory Structure:\n")
        backup.write("==================\n")
        backup.write(get_directory_structure('.') + "\n\n")
        
        # Write file contents
        backup.write("File Contents:\n")
        backup.write("=============\n\n")
        
        # Walk through directory
        for root, dirs, files in os.walk('.'):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                if file.endswith('.py') and file not in ignore_files:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        backup.write(f"File: {file_path}\n")
                        backup.write("=" * (len(file_path) + 6) + "\n")
                        backup.write(content)
                        backup.write("\n\n")
                    except Exception as e:
                        backup.write(f"Error reading {file_path}: {str(e)}\n\n")

if __name__ == "__main__":
    create_backup()
    print("Backup completed successfully!")