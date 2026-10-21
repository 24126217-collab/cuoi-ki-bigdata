import random
from datetime import datetime, timedelta
from pymongo import MongoClient

MONGO_URI = "mongodb+srv://24126217_db_user:thanh01@cluster0.y9ul2pr.mongodb.net/"
DB_NAME = "e_commerce"

PRODUCTS_POOL = [
    {"product_id": "66e3c0012222222222222201", "name": " Áo Thun Unisex Form Rộng Oversize ", "price": 190000},
    {"product_id": "66e3c0012222222222222202", "name": " Bàn Phím Cơ Keychron K2 ", "price": 1850000},
    {"product_id": "66e3c0012222222222222203", "name": "Giày Sneaker Thể Thao Êm Chân", "price": 620000},
    {"product_id": "66e3c0012222222222222204", "name": "Chuột Không Dây Logitech MX Master 3S", "price": 2450000},
    {"product_id": "66e3c0012222222222222205", "name": "Tai Nghe Bluetooth Sony WH-1000XM5", "price": 6990000},
    {"product_id": "66e3c0012222222222222206", "name": "Sạc Dự Phòng Anker 20000mAh", "price": 850000},
    {"product_id": "66e3c0012222222222222209", "name": "Kem Chống Nắng Dưỡng Ẩm", "price": 280000},
    {"product_id": "66e3c0012222222222222210", "name": "Nước Tẩy Trang Dịu Nhẹ", "price": 190000},
]

def generate_products_data(db):
    """Khởi tạo collection 'products' (14-20 bản ghi thô)"""
    print("🔄 Đang sinh dữ liệu thô cho 'products'...")
    products_col = db["products"]
    products_col.delete_many({})
    
    raw_products = []
    for item in PRODUCTS_POOL:
        raw_products.append({
            "_id": item["product_id"],
            "name": item["name"] if random.random() > 0.1 else f"  {item['name']}  ",
            "category_id": "66e3b0011111111111111101",
            "price": item["price"] if random.random() > 0.05 else -50000  
        })
    products_col.insert_many(raw_products)
    print(f"✅ Đã nạp {len(raw_products)} bản ghi thô vào 'products'.")

def generate_customers_data(db, num_records=1000):
    """Khởi tạo collection 'customers' (1.000 bản ghi thô)"""
    print(f"🔄 Đang sinh {num_records} bản ghi thô cho 'customers'...")
    customers_col = db["customers"]
    customers_col.delete_many({})
    
    first_names = ["Hải", "Khoa", "Minh", "Trần", "Nguyễn", "Lê", "Phạm", "Hoàng"]
    last_names = ["Mai Lê", "Quang Bùi", "Anh Tuấn", "Thị Hoa", "Văn Nam"]
    cities = ["Hải Phòng", "TP.HCM", "Hà Nội", "Đà Nẵng", None]

    raw_customers = []
    for i in range(1, num_records + 1):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        email = f"user{i}@example.net" if random.random() > 0.05 else None
        phone = f"09 {random.randint(1000, 9999)} {random.randint(1000, 9999)}"
        
        raw_customers.append({
            "customer_id": i,
            "name": name if random.random() > 0.05 else f"  {name}  ",
            "email": email,
            "phone": phone,
            "address": {
                "street": f"Số {random.randint(1, 100)} Lê Văn Sỹ",
                "ward": f"Phường {random.randint(1, 15)}",
                "district": f"Quận {random.randint(1, 12)}",
                "city": random.choice(cities)
            }
        })
    customers_col.insert_many(raw_customers)
    print(f"✅ Đã nạp {len(raw_customers)} bản ghi thô vào 'customers'.")

def generate_reviews_data(db, num_records=2000):
    """Khởi tạo collection 'reviews' (2.000 bản ghi thô)"""
    print(f"🔄 Đang sinh {num_records} bản ghi thô cho 'reviews'...")
    reviews_col = db["reviews"]
    reviews_col.delete_many({})
    
    comments = [
        "Chất lượng tuyệt vời, sẽ tiếp tục ủng hộ shop.",
        "Hàng đóng gói chưa cẩn thận lắm.",
        "Giao hàng nhanh, sản phẩm giống mô tả.",
        "Dùng bình thường, không có gì nổi bật.",
        ""
    ]
    
    raw_reviews = []
    start_date = datetime(2026, 1, 1)
    
    for i in range(1, num_records + 1):
        created_at = start_date + timedelta(days=random.randint(0, 280))
        prod = random.choice(PRODUCTS_POOL)
        
        raw_reviews.append({
            "review_id": i,
            "customer_id": random.randint(1, 1000),
            "product_id": prod["product_id"],
            "rating": random.choice([1, 2, 3, 4, 5, 0, 6]), 
            "comment": random.choice(comments),
            "created_at": created_at
        })
    reviews_col.insert_many(raw_reviews)
    print(f"✅ Đã nạp {len(raw_reviews)} bản ghi thô vào 'reviews'.")

def generate_orders_data(db, num_records=6000):
    """Khởi tạo collection 'orders' (6.000 bản ghi thô)"""
    print(f"🔄 Đang sinh {num_records} bản ghi thô cho 'orders'...")
    orders_col = db["orders"]
    orders_col.delete_many({})

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
        selected_items = random.sample(PRODUCTS_POOL, num_items)
        
        items_detail = []
        total_amount = 0
        for item in selected_items:
            qty = random.randint(1, 3)
            subtotal = item['price'] * qty
            total_amount += subtotal
            items_detail.append({
                "product_id": item['product_id'],
                "product_name": item['name'].strip(),
                "quantity": qty,
                "price": item['price']
            })

        order_date = start_date + timedelta(days=random.randint(0, 280), hours=random.randint(0, 23), minutes=random.randint(0, 59))

        order = {
            "order_id": i,
            "customer_id": random.randint(1, 1000),
            "order_date": order_date,
            "status": random.choice(statuses),
            "shipping_address": random.choice(addresses),
            "total_amount": total_amount if random.random() > 0.02 else None,
            "items": items_detail
        }
        
        if random.random() < 0.01 and i > 10:
            order["order_id"] = random.randint(1, i - 1)
            
        raw_orders.append(order)

    orders_col.insert_many(raw_orders)
    print(f"✅ Đã nạp {len(raw_orders)} bản ghi thô vào 'orders'.")

def run_crawler():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        
        print("🚀 BẮT ĐẦU QUY TRÌNH THU THẬP/CÀO DỮ LIỆU THÔ CHO TOÀN BỘ CSDL...")
        generate_products_data(db)
        generate_customers_data(db, 1000)
        generate_reviews_data(db, 2000)
        generate_orders_data(db, 6000)
        
        print("\n🎉 HOÀN THÀNH TẤT CẢ TÁC VỤ CÀO/TẠO DỮ LIỆU THÔ!")

    except Exception as e:
        print(f"❌ Lỗi khi cào/nạp dữ liệu: {e}")

if __name__ == "__main__":
    run_crawler()