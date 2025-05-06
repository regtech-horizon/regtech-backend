#!/usr/bin/env python
import os
import urllib.parse
from pathlib import Path

def find_database_module():
    """Find the database configuration file in the project."""
    # Common paths where database configuration might be found
    potential_paths = [
        '/app/api/db/database.py',
        '/app/api/utils/settings.py',
        '/app/api/utils/config.py',
        '/app/api/db/Storage.py'
    ]
    
    for path in potential_paths:
        if os.path.exists(path):
            return path
    
    # If not found in common paths, search for it
    for root, _, files in os.walk('/app'):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                with open(full_path, 'r') as f:
                    content = f.read()
                    if 'create_engine' in content and 'DB_PASSWORD' in content:
                        return full_path
    
    return None

def fix_database_connection(file_path):
    """Fix the database connection string by properly URL-encoding the password."""
    if not file_path:
        print("Database configuration file not found!")
        return False
    
    print(f"Found database configuration at: {file_path}")
    
    # Read the file content
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Make a backup
    backup_path = f"{file_path}.bak"
    with open(backup_path, 'w') as backup:
        backup.write(content)
    print(f"Created backup at: {backup_path}")
    
    # Check if the issue is in environment variables
    db_password = os.environ.get('DB_PASSWORD', '')
    if '@' in db_password:
        print(f"Found '@' in DB_PASSWORD environment variable")
        # Option 1: Update the environment variable
        encoded_password = urllib.parse.quote_plus(db_password)
        print(f"Original password contains '@'. URL-encoded password: {encoded_password}")
        print("You should update your environment variable DB_PASSWORD with the encoded value")
        
        # Option 2: Modify the code to encode the password
        if "DB_PASSWORD" in content and "create_engine" in content:
            modified_content = content.replace(
                "f\"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}\"",
                "f\"postgresql://{DB_USER}:{urllib.parse.quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}\""
            )
            
            # Add import if not already present
            if "import urllib.parse" not in modified_content:
                if "import" in modified_content:
                    # Add after the last import
                    import_lines = [line for line in content.split('\n') if line.strip().startswith('import') or line.strip().startswith('from')]
                    last_import = import_lines[-1]
                    last_import_index = content.find(last_import) + len(last_import)
                    modified_content = content[:last_import_index] + "\nimport urllib.parse" + content[last_import_index:]
                else:
                    # Add to the beginning
                    modified_content = "import urllib.parse\n" + content
            
            # Save the changes
            with open(file_path, 'w') as file:
                file.write(modified_content)
            print(f"Updated {file_path} to URL-encode the password")
            return True
    
    # If the issue wasn't found in environment variables, look for hardcoded connection strings
    if "regtechuser:***@25@db" in content:
        # Fix hardcoded connection string
        modified_content = content.replace(
            "regtechuser:***@25@db",
            "regtechuser:%40@25@db"  # URL-encode the @ to %40
        )
        
        with open(file_path, 'w') as file:
            file.write(modified_content)
        print(f"Updated hardcoded connection string in {file_path}")
        return True
    
    print("Could not automatically fix the issue. Please check the database configuration manually.")
    return False

def main():
    print("Searching for database configuration file...")
    db_file = find_database_module()
    if fix_database_connection(db_file):
        print("\nFix applied successfully!")
        print("Now try restarting your application to see if the connection works.")
        print("\nIf the issue persists, you may need to:")
        print("1. Update your DB_PASSWORD environment variable in your Docker configuration")
        print("2. Restart your Docker container with: docker-compose restart regtech_web")
    else:
        print("\nCould not automatically fix the issue.")
        print("You may need to manually inspect your database configuration.")

if __name__ == "__main__":
    main()
