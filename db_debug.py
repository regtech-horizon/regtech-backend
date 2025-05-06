# Create this as db_debug.py in your app directory
import os
import urllib.parse

# Print the raw DATABASE_URL
db_url = os.environ.get('DATABASE_URL', '')
print(f"Raw DATABASE_URL: {db_url}")

# Parse the URL to see components
parsed = urllib.parse.urlparse(db_url)
print(f"Parsed components:")
print(f"  - scheme: {parsed.scheme}")
print(f"  - netloc: {parsed.netloc}")
print(f"  - username: {parsed.username}")
print(f"  - password: {parsed.password}")  # Will be shown in logs, be careful
print(f"  - hostname: {parsed.hostname}")
print(f"  - port: {parsed.port}")
print(f"  - path: {parsed.path}")

# Try to find where the database connection is configured
import inspect
import importlib
import sys

# Look for potential database config files
for path in sys.path:
    print(f"Checking path: {path}")

# Try to locate modules that might handle DB connection
try:
    # Check common file locations for database setup
    potential_db_modules = [
        'app.db', 'app.database', 'app.config', 'database', 'config',
        'app.core.database', 'app.core.config', 'api.database', 'api.config',
        'app.api.database', 'app.api.config', 'api.v1.database', 'api.v1.config'
    ]
    
    for module_name in potential_db_modules:
        try:
            print(f"Trying to import {module_name}")
            module = importlib.import_module(module_name)
            print(f"Successfully imported {module_name}")
            
            # Look for db-related attributes
            db_attrs = [attr for attr in dir(module) if 'db' in attr.lower() or 'database' in attr.lower() or 'engine' in attr.lower()]
            if db_attrs:
                print(f"Potential database attributes in {module_name}: {db_attrs}")
        except ImportError:
            print(f"Could not import {module_name}")
except Exception as e:
    print(f"Error during module investigation: {e}")
