import os
import shutil
import datetime

# Configuration
SOURCE_DIR = "/home/emky/n8n"
BASE_DEST_DIR = "/home/emky/n8n/documentacion/3_WORK_LOGS_AND_HISTORY/TOOLS_HISTORY"

# File patterns to move (skip core system files)
EXTENSIONS = ('.py', '.js', '.json', '.txt', '.sqlite')
SKIP_FILES = {
    'package.json', 'package-lock.json', 'ecosystem.config.js', 
    'agentes.json', 'history.json', 'Dockerfile', 'docker-compose.yml', 'start-n8n.sh',
    'database.sqlite', 'database_copy.sqlite', 'os' # core files
}

def reorganize():
    if not os.path.exists(BASE_DEST_DIR):
        os.makedirs(BASE_DEST_DIR)
        print(f"Created base directory: {BASE_DEST_DIR}")

    files = [f for f in os.listdir(SOURCE_DIR) if os.path.isfile(os.path.join(SOURCE_DIR, f))]
    
    moved_count = 0
    for filename in files:
        if filename.endswith(EXTENSIONS) and filename not in SKIP_FILES:
            src_path = os.path.join(SOURCE_DIR, filename)
            
            # Get modification date for history grouping
            mtime = os.path.getmtime(src_path)
            date_str = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
            
            dest_folder = os.path.join(BASE_DEST_DIR, date_str)
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)
            
            dest_path = os.path.join(dest_folder, filename)
            
            # Avoid overwriting if same filename exists (unlikely in root but safe)
            if os.path.exists(dest_path):
                name, ext = os.path.splitext(filename)
                dest_path = os.path.join(dest_folder, f"{name}_{int(mtime)}{ext}")

            print(f"Moving: {filename} -> {date_str}/")
            shutil.move(src_path, dest_path)
            moved_count += 1

    print(f"\nTotal files moved: {moved_count}")

if __name__ == "__main__":
    reorganize()
