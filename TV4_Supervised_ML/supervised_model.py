from pathlib import Path
import ast
import joblib
import pandas as pd

# Đường dẫn tới thư mục mô hình
BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"


def load_models():
    """Tải mô hình và danh sách biến đầu vào."""
    reg_model = joblib.load(
        MODEL_DIR / "regression_model.joblib"
    )
    cls_model = joblib.load(
        MODEL_DIR / "classification_model.joblib"
    )
    reg_features = joblib.load(
        MODEL_DIR / "regression_features.joblib"
    )
    cls_features = joblib.load(
        MODEL_DIR / "classification_features.joblib"
    )

    return reg_model, cls_model, reg_features, cls_features


def extract_item_features(items):
    """Chuyển danh sách sản phẩm thành đặc trưng ML."""
    if isinstance(items, str):
        items = ast.literal_eval(items)

    if not isinstance(items, list) or not items:
        raise ValueError("Giỏ hàng phải có ít nhất một sản phẩm")

    quantities = []
    prices = []

    for item in items:
        if not isinstance(item, dict):
            raise ValueError("Mỗi sản phẩm phải là dictionary")

        quantity = float(item["quantity"])
        price = float(item["price"])

        if quantity <= 0 or price < 0:
            raise ValueError("Số lượng và giá không hợp lệ")

        quantities.append(quantity)
        prices.append(price)

    return {
        "item_count": sum(quantities),
        "unique_products": len(items),
        "avg_item_price": sum(prices) / len(prices),
        "max_item_price": max(prices)
    }


def predict_order_value(items):
    """Ước tính giá trị giỏ hàng bằng Random Forest."""
    reg_model, _, reg_features, _ = load_models()

    features = extract_item_features(items)
    X = pd.DataFrame([features])[reg_features]

    prediction = reg_model.predict(X)[0]

    return round(float(prediction), 2)


def predict_cancellation(items, order_date, previous_orders):
    """Thử nghiệm dự đoán khả năng hủy đơn."""
    _, cls_model, _, cls_features = load_models()

    features = extract_item_features(items)

    date = pd.to_datetime(order_date)

    features.update({
        "month": date.month,
        "day_of_week": date.dayofweek,
        "hour": date.hour,
        "previous_orders": int(previous_orders)
    })

    X = pd.DataFrame([features])[cls_features]

    prediction = int(cls_model.predict(X)[0])
    probability = float(
        cls_model.predict_proba(X)[0][1]
    )

    return {
        "prediction": prediction,
        "status": "Cancelled" if prediction == 1
                  else "Completed",
        "cancel_probability": round(probability, 4)
    }
