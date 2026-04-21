import shutil
import os
from datetime import datetime

def backup_reports_and_db():
    backup_dir = os.path.join(os.getcwd(), 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    # Backup reports
    reports_dir = os.path.join(os.getcwd(), 'agentic_rnd_tool', 'reports')
    if os.path.exists(reports_dir):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        shutil.make_archive(os.path.join(backup_dir, f'reports_backup_{timestamp}'), 'zip', reports_dir)
    # Backup database
    db_path = os.path.join(os.getcwd(), 'agentic_rnd_tool', 'users.db')
    if os.path.exists(db_path):
        shutil.copy2(db_path, os.path.join(backup_dir, f'users_{timestamp}.db'))
    print(f"Backup complete. Files saved in {backup_dir}")

if __name__ == '__main__':
    backup_reports_and_db()
