import os
import sys
import subprocess
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

MONGODUMP_EXE = os.path.join(CURRENT_DIR, "mongodump.exe")
MONGORESTORE_EXE = os.path.join(CURRENT_DIR, "mongorestore.exe")

BASE_DIR = os.path.dirname(CURRENT_DIR)
BACKUP_DIR = os.path.join(BASE_DIR, "backups")


MONGO_URI = (
    "mongodb+srv://24126217_db_user:thanh01@cluster0.y9ul2pr.mongodb.net/"
)
DB_NAME = "e_commerce"

def backup_database():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"backup_{DB_NAME}_{timestamp}"
    target_path = os.path.join(BACKUP_DIR, folder_name)

    cmd = [
        MONGODUMP_EXE,
        f"--uri={MONGO_URI}",
        f"--db={DB_NAME}",
        f"--out={target_path}",
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True
        )
        return {
            "status": "success",
            "message": "Sao lưu CSDL thành công!",
            "folder": folder_name,
            "path": target_path,
        }
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": f"Lỗi khi thực hiện mongodump: {e.stderr}",
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "message": f"Không tìm thấy file mongodump.exe tại: {MONGODUMP_EXE}",
        }

def restore_database(target_folder_name=None):
    if not os.path.exists(BACKUP_DIR) or not os.listdir(BACKUP_DIR):
        return {"status": "error", "message": "Chưa có bản sao lưu nào tồn tại!"}

    if target_folder_name:
        backup_folder = os.path.join(BACKUP_DIR, target_folder_name)
    else:
        all_backups = sorted(os.listdir(BACKUP_DIR), reverse=True)
        backup_folder = os.path.join(BACKUP_DIR, all_backups[0])

    if not os.path.exists(backup_folder):
        return {
            "status": "error",
            "message": f"Không tìm thấy đường dẫn bản sao lưu: {backup_folder}",
        }

    cmd = [
        MONGORESTORE_EXE,
        f"--uri={MONGO_URI}",
        f"--nsInclude={DB_NAME}.*",  
        "--numParallelCollections=1",  
        "--drop",  
        backup_folder,
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True
        )
        return {
            "status": "success",
            "message": "Đã khôi phục thành công CSDL từ bản sao lưu!",
            "restored_from": os.path.basename(backup_folder),
        }
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": f"Lỗi khi thực hiện mongorestore: {e.stderr}",
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "message": f"Không tìm thấy file mongorestore.exe tại: {MONGORESTORE_EXE}",
        }

if __name__ == "__main__":
    print("--- TEST MODULE BACKUP & RESTORE ---")
    print("\n1. Đang chạy Backup...")
    backup_res = backup_database()
    print("Kết quả Backup:", backup_res)

    if backup_res["status"] == "success":
        print("\n2. Đang chạy Restore...")
        restore_res = restore_database()
        print("Kết quả Restore:", restore_res)
