import os
import glob

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = (content
            .replace('AuraRise', 'AuraRise')
            .replace('AuraRise', 'AuraRise')
            .replace('aurarise', 'aurarise')
            .replace('aurarise', 'aurarise')
        )
        
        if content != new_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

# Process all files
count = 0
for root, dirs, files in os.walk(r'D:\New folder\resume1'):
    # Skip .git and other folders
    if '.git' in root or '__pycache__' in root or '.venv' in root:
        continue
    for f in files:
        if f.endswith(('.html', '.py', '.txt', '.json', '.md', '.yml', '.yaml', '.toml', '.js', '.css')):
            filepath = os.path.join(root, f)
            if replace_in_file(filepath):
                count += 1

print(f"\nTotal files updated: {count}")
