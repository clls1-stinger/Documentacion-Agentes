import os
import shutil
import datetime

# Configuration
SOURCE_DIR = "/home/emky/n8n"
BASE_DEST_DIR = "/home/emky/n8n/documentacion/3_WORK_LOGS_AND_HISTORY/TOOLS_HISTORY"

# Patterns to INCLUDE in this pass (the ones missed or requested)
INCLUDE_EXTENSIONS = ('.log', '.sqlite', '.md', '.txt', '.json', '.js', '.sh', '.py')
EXCLUDE_FILES = {
    'package.json', 'package-lock.json', 'ecosystem.config.js', 
    'agentes.json', 'history.json', 'Dockerfile', 'docker-compose.yml', 'start-n8n.sh',
    'database.sqlite', 'config' # ABSOLUTELY ESSENTIAL
}

def deep_cleanup():
    if not os.path.exists(BASE_DEST_DIR):
        os.makedirs(BASE_DEST_DIR)

    files = [f for f in os.listdir(SOURCE_DIR) if os.path.isfile(os.path.join(SOURCE_DIR, f))]
    
    moved_count = 0
    for filename in files:
        if filename in EXCLUDE_FILES:
            continue
            
        src_path = os.path.join(SOURCE_DIR, filename)
        
        # Determine if we should move it
        should_move = False
        if filename.endswith(INCLUDE_EXTENSIONS):
            should_move = True
        elif filename == 'os': # Move the large 'os' file mentioned in logs/screenshot
            should_move = True

        if should_move:
            mtime = os.path.getmtime(src_path)
            date_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
            dest_folder = os.path.join(BASE_DEST_DIR, date_str)
            
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)
            
            dest_path = os.path.join(dest_folder, filename)
            
            if os.path.exists(dest_path):
                name, ext = os.path.splitext(filename)
                dest_path = os.path.join(dest_folder, f"{name}_{int(mtime)}{ext}")

            print(f"Moving: {filename} -> {date_str}/")
            shutil.move(src_path, dest_path)
            moved_count += 1

    print(f"\nTotal files moved in deep cleanup: {moved_count}")

if __name__ == "__main__":
    deep_cleanup()
