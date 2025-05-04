# db_finder.py
import os
import sys
import importlib
import inspect
from sqlalchemy import create_engine, inspect as sqlalchemy_inspect
from sqlalchemy.engine import Engine

# Recursively search for modules and inspect them
def inspect_module(module_name, checked=None):
    if checked is None:
        checked = set()
    
    if module_name in checked:
        return
    
    checked.add(module_name)
    print(f"Inspecting module: {module_name}")
    
    try:
        module = importlib.import_module(module_name)
        
        # Look for SQLAlchemy engine objects
        for name, obj in inspect.getmembers(module):
            # Check if it's a SQLAlchemy Engine
            if isinstance(obj, Engine):
                print(f"Found SQLAlchemy Engine in {module_name}.{name}")
                conn_info = obj.url
                print(f"  Connection URL: {conn_info}")
            
            # Look for create_engine calls in the functions
            if inspect.isfunction(obj) or inspect.ismethod(obj):
                try:
                    source = inspect.getsource(obj)
                    if "create_engine" in source:
                        print(f"Found create_engine call in {module_name}.{name}")
                        print(f"  Source snippet: {source[:200]}...")
                except Exception:
                    pass
        
        # Inspect submodules
        if hasattr(module, "__path__"):
            pkg_path = module.__path__[0]
            for item in os.listdir(pkg_path):
                if item.endswith('.py') and item != '__init__.py':
                    submodule = f"{module_name}.{item[:-3]}"
                    inspect_module(submodule, checked)
                elif os.path.isdir(os.path.join(pkg_path, item)) and os.path.exists(os.path.join(pkg_path, item, '__init__.py')):
                    submodule = f"{module_name}.{item}"
                    inspect_module(submodule, checked)
    except ImportError:
        print(f"Could not import {module_name}")
    except Exception as e:
        print(f"Error inspecting {module_name}: {e}")

# Start with known module paths
for base_module in ['api', 'app', 'api.v1', 'app.api', 'app.api.v1']:
    inspect_module(base_module)

# Also check if there's a database.py file directly in the path
if os.path.exists('/app/database.py'):
    print("Found /app/database.py file")
    # Try to load it directly
    sys.path.insert(0, '/app')
    try:
        import database
        print("Successfully imported database module")
        for name, obj in inspect.getmembers(database):
            if isinstance(obj, Engine):
                print(f"Found SQLAlchemy Engine in database.{name}")
                conn_info = obj.url
                print(f"  Connection URL: {conn_info}")
    except Exception as e:
        print(f"Error importing database module: {e}")
