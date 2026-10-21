import random
from datetime import datetime, timedelta
from pymongo import MongoClient

# 1. CẤU HÌNH KẾT NỐI MONGODB
# Dán chuỗi kết nối từ Bước 4 vào giữa 2 dấu ngoặc kép bên dưới:
MONGO_URI = "mongodb+srv://24126217_db_user:thanh01@cluster0.y9ul2pr.mongodb.net/"

DB_NAME = "e_commerce"
COLLECTION_RAW = "orders"

def generate_mock_ecom_data(num_records=6000):
    """Giả lập/cào dữ liệu đơn hàng TMĐT đạt chuẩn quy mô > 5.000 bản ghi"""
    print(f"🔄 Đang thu thập/cào {num_records} bản ghi dữ liệu TMĐT...")
    
    products_pool = [
        {"product_id": "PROD001", "product_name": "Bàn Phím Cơ Keychron K2", "price": 1850000},
        {"product_id": "PROD002", "product_name": "Kem Chống Nắng Dưỡng Ẩm", "price": 280000},
        {"product_id": "PROD003", "product_name": "Chuột Không Dây Logitech MX Master 3S", "price": 2450000},
        {"product_id": "PROD004", "product_name": "Tai Nghe Bluetooth Sony WH-1000XM5", "price": 6990000},
        {"product_id": "PROD005", "product_name": "Áo Thun Cotton Form Wide", "price": 190000},
        {"product_id": "PROD006", "product_name": "Sạc Dự Phòng Anker 20000mAh", "price": 850000},
    ]
    
    statuses = ["Completed", "Completed", "Completed", "Cancelled", "Pending", None]
    addresses = [
        "81 Khóm 13 Bà Triệu, Phường 5, Quận 5, Đà Nẵng",
        "123 Nguyễn Văn Cừ, Quận 5, TP.HCM",
        "456 Lê Duẩn, Quận Thanh Khê, Đà Nẵng",
        "789 Cầu Giấy, Quận Cầu Giấy, Hà Nội",
        None
    ]

    raw_orders = []
    start_date = datetime(2026, 1, 1)

    for i in range(1, num_records + 1):
        num_items = random.randint(1, 3)
        selected_items = random.sample(products_pool, num_items)
        
        items_detail = []
        total_amount = 0
        for item in selected_items:
            qty = random.randint(1, 3)
            subtotal = item['price'] * qty
            total_amount += subtotal
            items_detail.append({
                "product_id": item['product_id'],
                "product_name": item['product_name'],
                "quantity": qty,
                "price": item['price']
            })

        order_date = start_date + timedelta(days=random.randint(0, 280), hours=random.randint(0, 23), minutes=random.randint(0, 59))

        order = {
            "order_id": i,
            "customer_id": random.randint(100, 999),
            "order_date": order_date,
            "status": random.choice(statuses),
            "shipping_address": random.choice(addresses),
            "total_amount": total_amount if random.random() > 0.02 else None,
            "items": items_detail
        }
        
        # Cố tình tạo 1% bản ghi trùng lặp (Duplicates) để test pipeline làm sạch
        if random.random() < 0.01 and i > 10:
            order["order_id"] = random.randint(1, i - 1)
            
        raw_orders.append(order)

    return raw_orders

def run_crawler():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        raw_col = db[COLLECTION_RAW]

        # Cập nhật/Ghi mới dữ liệu thô vào collection orders
        raw_col.delete_many({})
        orders_data = generate_mock_ecom_data(6000)
        raw_col.insert_many(orders_data)
        
        print(f"✅ Đã cào thành công và lưu {len(orders_data)} bản ghi thô vào MongoDB collection '{COLLECTION_RAW}'.")

    except Exception as e:
        print(f"❌ Lỗi khi cào/nạp dữ liệu: {e}")

if __name__ == "__main__":
    run_crawler()