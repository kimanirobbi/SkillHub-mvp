import os
import shutil

def remove_directory(path):
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
            print(f"Removed directory: {path}")
        except Exception as e:
            print(f"Error removing {path}: {e}")
    else:
        print(f"Directory does not exist: {path}")

# Remove migrations directory
remove_directory('migrations')

# Remove any .pyc files and __pycache__ directories
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.pyc'):
            try:
                os.remove(os.path.join(root, file))
            except Exception as e:
                print(f"Error removing {file}: {e}")
    
    for dir in dirs:
        if dir == '__pycache__':
            remove_directory(os.path.join(root, dir))

print("Cleanup complete. You can now run 'flask db init' to create a fresh migrations directory.")
