import sys
import subprocess

subprocess.check_call([sys.executable, "-m", "pip", "install", "pymongo", "bcrypt", "pyjwt"])

import datetime
import bcrypt
import jwt
import pymongo

MONGO_URI = "mongodb+srv://24126217_db_user:thanh01@cluster0.y9ul2pr.mongodb.net/" 
SECRET_KEY = "bi_mat_do_an_big_data_2026"  
ALGORITHM = "HS256"

client = pymongo.MongoClient(MONGO_URI)
db = client["e_commerce"]
users_collection = db["users"]



def register_user(username, password, role="User"):
    if users_collection.find_one({"username": username}):
        return {"status": "error", "message": "Tài khoản đã tồn tại!"}

   
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)

    user_doc = {
        "username": username,
        "password_hash": hashed_password.decode("utf-8"),
        "role": role, 
        "created_at": datetime.datetime.utcnow(),
    }
    users_collection.insert_one(user_doc)
    return {"status": "success", "message": f"Đã tạo tài khoản {username} ({role})"}


def login_user(username, password):
    user = users_collection.find_one({"username": username})
    if not user:
        return {"status": "error", "message": "Sai tài khoản hoặc mật khẩu!"}

    if bcrypt.checkpw(
        password.encode("utf-8"), user["password_hash"].encode("utf-8")
    ):
        payload = {
            "username": user["username"],
            "role": user["role"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return {
            "status": "success",
            "token": token,
            "role": user["role"],
            "message": "Đăng nhập thành công!",
        }
    else:
        return {"status": "error", "message": "Sai tài khoản hoặc mật khẩu!"}


def verify_token_and_role(token, required_role=None):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_role = payload.get("role")


        if required_role and user_role != required_role:
            return {
                "valid": False,
                "message": f"Truy cập bị từ chối! Yêu cầu quyền {required_role}",
            }

        return {
            "valid": True,
            "username": payload.get("username"),
            "role": user_role,
        }
    except jwt.ExpiredSignatureError:
        return {"valid": False, "message": "Token đã hết hạn đăng nhập!"}
    except jwt.InvalidTokenError:
        return {"valid": False, "message": "Token không hợp lệ!"}


if __name__ == "__main__":
    print("--- TEST MODULE AUTH ---")
    print(register_user("admin_duan", "matkhau123", role="Admin"))

    login_result = login_user("admin_duan", "matkhau123")
    print("Kết quả đăng nhập:", login_result)

    if login_result["status"] == "success":
        user_token = login_result["token"]
        auth_check = verify_token_and_role(user_token, required_role="Admin")
        print("Xác thực quyền Admin:", auth_check)
