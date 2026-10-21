import os
import pandas as pd
import numpy as np
from pymongo import MongoClient

# 1. CẤU HÌNH KẾT NỐI CSDL
MONGO_URI = "mongodb+srv://24126217_db_user:thanh01@cluster0.y9ul2pr.mongodb.net/"
DB_NAME = "e_commerce"
RAW_COLLECTION = "orders"
CLEAN_COLLECTION = "clean_orders"

def run_cleaning_pipeline():
    print("🚀 ĐANG KHỞI CHẠY DATA PIPELINE LÀM SẠCH DỮ LIỆU...")

    # --- BƯỚC 1: TRÍCH XUẤT DỮ LIỆU TỪ MONGODB ---
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        raw_col = db[RAW_COLLECTION]
        
        raw_data = list(raw_col.find())
        df = pd.DataFrame(raw_data)
        print(f"📥 Đã tải {len(df)} bản ghi thô từ MongoDB.")
    except Exception as e:
        print(f"❌ Lỗi kết nối CSDL: {e}")
        return

    # Sao lưu file CSV thô vào thư mục data/
    os.makedirs("data", exist_ok=True)
    df_raw_export = df.drop(columns=['_id'], errors='ignore')
    df_raw_export.to_csv("data/raw_orders.csv", index=False, encoding='utf-8-sig')
    print("💾 Đã lưu 'data/raw_orders.csv' (Sản phẩm bàn giao 1).")

    # --- BƯỚC 2: CHUẨN HÓA TÊN CỘT VỀ SNAKE_CASE ---
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(' ', '_')
        .str.replace('(', '')
        .str.replace(')', '')
    )

    if '_id' in df.columns:
        df = df.drop(columns=['_id'])

    # --- BƯỚC 3: LOẠI BỎ BẢN GHI TRÙNG LẶP ---
    initial_count = len(df)
    df = df.drop_duplicates(subset=['order_id'], keep='first')
    dedup_count = initial_count - len(df)
    print(f"🧹 Đã xóa {dedup_count} bản ghi bị trùng lặp (order_id).")

    # --- BƯỚC 4: XỬ LÝ DỮ LIỆU KHUYẾT THIẾU (MISSING VALUES) ---
    df['status'] = df['status'].fillna('Pending')
    df['shipping_address'] = df['shipping_address'].fillna('Chưa cập nhật')

    if df['total_amount'].isnull().sum() > 0:
        median_val = df['total_amount'].median()
        df['total_amount'] = df['total_amount'].fillna(median_val)
        print(f"🛠️ Đã điền {df['total_amount'].isnull().sum()} giá trị thiếu 'total_amount' bằng Median: {median_val:,.0f} VNĐ")

    # --- BƯỚC 5: CHUẨN HÓA ĐỊNH DẠNG & KIỂU DỮ LIỆU ---
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['order_id'] = df['order_id'].astype(int)
    df['customer_id'] = df['customer_id'].astype(int)
    df['total_amount'] = df['total_amount'].astype(float)

    print(f"✨ Tổng số bản ghi đạt chuẩn sau làm sạch: {len(df)} dòng.")

    # --- BƯỚC 6: XUẤT FILE SẠCH .CSV ---
    df.to_csv("data/clean_orders.csv", index=False, encoding='utf-8-sig')
    print("💾 Đã lưu 'data/clean_orders.csv' (Sản phẩm bàn giao 2).")

    # --- BƯỚC 7: NẠP DỮ LIỆU SẠCH VÀO MONGODB (DATA INGESTION) ---
    clean_col = db[CLEAN_COLLECTION]
    clean_col.delete_many({})
    
    clean_records = df.to_dict('records')
    clean_col.insert_many(clean_records)
    
    print(f"✅ NẠP THÀNH CÔNG! Đã đẩy {len(clean_records)} bản ghi sạch vào collection '{CLEAN_COLLECTION}'.")
    print("🎉 TẤT CẢ NHIỆM VỤ CỦA THÀNH VIÊN 2 ĐÃ HOÀN THÀNH!")

if __name__ == "__main__":
    run_cleaning_pipeline()