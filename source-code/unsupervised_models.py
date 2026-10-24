import pandas as pd
import os
import joblib
import warnings
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest

# Tắt các cảnh báo UserWarning không cần thiết từ scikit-learn
warnings.filterwarnings("ignore")

def load_model_file(model_dir, base_name):
    """Tự động kiểm tra file có đuôi .pkl, .joblib hoặc không có đuôi file"""
    path_pkl = os.path.join(model_dir, f"{base_name}.pkl")
    path_joblib = os.path.join(model_dir, f"{base_name}.joblib")
    path_no_ext = os.path.join(model_dir, base_name)
    
    if os.path.exists(path_pkl):
        return joblib.load(path_pkl)
    elif os.path.exists(path_joblib):
        return joblib.load(path_joblib)
    elif os.path.exists(path_no_ext):
        return joblib.load(path_no_ext)
    else:
        raise FileNotFoundError(f"Không tìm thấy file '{base_name}' trong thư mục: {model_dir}")

# 1. PHẦN PHÂN CỤM KHÁCH HÀNG (K-MEANS)
def predict_customer_cluster(recency, frequency, monetary, model_dir='models'):
    km = load_model_file(model_dir, 'kmeans_model')
    scaler = load_model_file(model_dir, 'scaler')
    X = scaler.transform([[recency, frequency, monetary]])
    return int(km.predict(X)[0])

# 2. PHẦN GỢI Ý SẢN PHẨM (APRIORI + FALLBACK)
def get_popular_recommendations(target_product, rules_df, df_encoded, top_n=3):
    target_lower = target_product.lower()
    matched_rules = rules_df[rules_df['antecedents'].str.lower().str.contains(target_lower, regex=False)]
    
    if not matched_rules.empty:
        top_recommendations = matched_rules.sort_values(by='lift', ascending=False).head(top_n)
        return top_recommendations['consequents'].tolist()
    else:
        print(f"[Fallback] Không tìm thấy luật cho '{target_product}'. Trả về sản phẩm phổ biến.")
        popular_products = df_encoded.sum().sort_values(ascending=False)
        results = [prod for prod in popular_products.index if prod.lower() != target_lower][:top_n]
        return results

# 3. PHẦN PHÁT HIỆN BẤT THƯỜNG (ISOLATION FOREST)
def predict_anomaly(total_amount, num_items, model_dir='models'):
    iso = load_model_file(model_dir, 'isolation_forest')
    prediction = iso.predict([[total_amount, num_items]])[0]
    score = iso.decision_function([[total_amount, num_items]])[0]
    is_anomaly = True if prediction == -1 else False
    return is_anomaly, score
if __name__ == "__main__":
    print("--- 🧪 KIỂM THỬ CÁC HÀM CỦA TV3 ---")
    
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Định vị tự động thư mục 'models'
    MODEL_PATH = os.path.join(CURRENT_DIR, "models")
    if not os.path.exists(MODEL_PATH):
        MODEL_PATH = os.path.join(CURRENT_DIR, "..", "TV3_Unsupervised_ML", "models")
    if not os.path.exists(MODEL_PATH):
        MODEL_PATH = os.path.join(CURRENT_DIR, "..", "models")
        
    print(f"📁 Đường dẫn thư mục models: {MODEL_PATH}")

    # 1. Test Phân cụm Khách hàng
    try:
        cluster = predict_customer_cluster(10, 5, 2000000, model_dir=MODEL_PATH)
        print(f"✅ Cụm khách hàng dự đoán: Cụm {cluster}")
    except Exception as e:
        print(f"❌ Lỗi Phân cụm: {e}")

    # 2. Test Phát hiện Bất thường
    try:
        is_anomaly, score = predict_anomaly(50000000, 100, model_dir=MODEL_PATH)
        print(f"⚠️ Đơn hàng bất thường: {is_anomaly} (Score: {score:.4f})")
    except Exception as e:
        print(f"❌ Lỗi Phát hiện bất thường: {e}")






















