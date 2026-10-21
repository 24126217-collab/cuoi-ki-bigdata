import os
import pandas as pd
import numpy as np
from pymongo import MongoClient

MONGO_URI = "mongodb+srv://24126217_db_user:thanh01@cluster0.y9ul2pr.mongodb.net/"
DB_NAME = "e_commerce"

COLLECTIONS_CONFIG = [
    {
        "raw_col": "orders",
        "clean_col": "clean_orders",
        "id_field": "order_id",
        "raw_csv": "data/raw_orders.csv",
        "clean_csv": "data/clean_orders.csv"
    },
    {
        "raw_col": "customers",
        "clean_col": "clean_customers",
        "id_field": "customer_id",
        "raw_csv": "data/raw_customers.csv",
        "clean_csv": "data/clean_customers.csv"
    },
    {
        "raw_col": "products",
        "clean_col": "clean_products",
        "id_field": "product_id",
        "raw_csv": "data/raw_products.csv",
        "clean_csv": "data/clean_products.csv"
    },
    {
        "raw_col": "reviews",
        "clean_col": "clean_reviews",
        "id_field": "review_id",
        "raw_csv": "data/raw_reviews.csv",
        "clean_csv": "data/clean_reviews.csv"
    }
]


def clean_orders_df(df):
    """Quy tắc làm sạch cho ORDERS"""
    df['status'] = df['status'].fillna('Pending')
    df['shipping_address'] = df['shipping_address'].fillna('Chưa cập nhật')

    if df['total_amount'].isnull().sum() > 0:
        median_val = df['total_amount'].median()
        df['total_amount'] = df['total_amount'].fillna(median_val)

    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    df['order_id'] = pd.to_numeric(df['order_id'], errors='coerce').fillna(0).astype(int)
    df['customer_id'] = pd.to_numeric(df['customer_id'], errors='coerce').fillna(0).astype(int)
    df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce').fillna(0.0).astype(float)
    return df


def clean_customers_df(df):
    """Quy tắc làm sạch cho CUSTOMERS"""
    if 'name' in df.columns:
        df['name'] = df['name'].astype(str).str.strip().str.title()
    if 'email' in df.columns:
        df['email'] = df['email'].astype(str).str.strip().str.lower()
        df['email'] = df['email'].replace(['nan', 'none', ''], 'chua_cap_nhat@example.com')
    if 'phone' in df.columns:
        df['phone'] = df['phone'].astype(str).str.replace(r'\s+', '', regex=True)
        df['phone'] = df['phone'].replace(['nan', 'none', ''], 'Chưa cập nhật')
    if 'customer_id' in df.columns:
        df['customer_id'] = pd.to_numeric(df['customer_id'], errors='coerce').fillna(0).astype(int)
    return df


def clean_products_df(df):
    """Quy tắc làm sạch cho PRODUCTS"""
    if 'name' in df.columns:
        df['name'] = df['name'].astype(str).str.strip()
    if 'price' in df.columns:
        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0).astype(float)
        df = df[df['price'] > 0]
    return df


def clean_reviews_df(df):
    """Quy tắc làm sạch cho REVIEWS"""
    if 'rating' in df.columns:
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(5).astype(int)
        df['rating'] = df['rating'].clip(lower=1, upper=5)
    if 'comment' in df.columns:
        df['comment'] = df['comment'].astype(str).str.strip()
        df['comment'] = df['comment'].replace(['nan', 'none', ''], 'Không có nhận xét')
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    if 'review_id' in df.columns:
        df['review_id'] = pd.to_numeric(df['review_id'], errors='coerce').fillna(0).astype(int)
    if 'customer_id' in df.columns:
        df['customer_id'] = pd.to_numeric(df['customer_id'], errors='coerce').fillna(0).astype(int)
    return df


def process_collection(db, config):
    raw_name = config["raw_col"]
    clean_name = config["clean_col"]
    id_field = config["id_field"]

    print(f"\n--------------------------------------------------")
    print(f"📦 ĐANG XỬ LÝ COLLECTION: '{raw_name}' -> '{clean_name}'")
    print(f"--------------------------------------------------")

    raw_col = db[raw_name]
    raw_data = list(raw_col.find())
    
    if not raw_data:
        print(f"⚠️ Không tìm thấy dữ liệu trong collection '{raw_name}'. Bỏ qua.")
        return

    df = pd.DataFrame(raw_data)
    print(f"📥 Đã tải {len(df)} bản ghi thô từ '{raw_name}'.")

    df_raw_export = df.drop(columns=['_id'], errors='ignore')
    df_raw_export.to_csv(config["raw_csv"], index=False, encoding='utf-8-sig')
    print(f"💾 Đã lưu file thô: '{config['raw_csv']}'")

    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(' ', '_')
        .str.replace('(', '')
        .str.replace(')', '')
    )

    if '_id' in df.columns:
        df = df.drop(columns=['_id'])

    initial_count = len(df)
    if id_field in df.columns:
        df = df.drop_duplicates(subset=[id_field], keep='first')
        dedup_count = initial_count - len(df)
        print(f"🧹 Đã xóa {dedup_count} bản ghi bị trùng lặp theo '{id_field}'.")

    if raw_name == "orders":
        df = clean_orders_df(df)
    elif raw_name == "customers":
        df = clean_customers_df(df)
    elif raw_name == "products":
        df = clean_products_df(df)
    elif raw_name == "reviews":
        df = clean_reviews_df(df)

    print(f"✨ Số bản ghi đạt chuẩn sau làm sạch: {len(df)} dòng.")

    df.to_csv(config["clean_csv"], index=False, encoding='utf-8-sig')
    print(f"💾 Đã lưu file sạch: '{config['clean_csv']}'")

    clean_col = db[clean_name]
    clean_col.delete_many({})
    
    clean_records = df.to_dict('records')
    if clean_records:
        clean_col.insert_many(clean_records)
    
    print(f"✅ NẠP THÀNH CÔNG! Đã nạp {len(clean_records)} bản ghi sạch vào collection '{clean_name}'.")


def run_cleaning_pipeline():
    print("🚀 ĐANG KHỞI CHẠY DATA PIPELINE LÀM SẠCH TOÀN BỘ CSDL...")
    os.makedirs("data", exist_ok=True)

    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
    except Exception as e:
        print(f"❌ Lỗi kết nối CSDL: {e}")
        return

    for config in COLLECTIONS_CONFIG:
        process_collection(db, config)

    print("\n🎉 TẤT CẢ NHIỆM VỤ LÀM SẠCH DỮ LIỆU CỦA THÀNH VIÊN 2 ĐÃ HOÀN THÀNH VÀ ĐẨY LÊN CSDL!")


if __name__ == "__main__":
    run_cleaning_pipeline()