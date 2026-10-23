import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest

# 1. PHẦN PHÂN CỤM KHÁCH HÀNG (K-MEANS)
def predict_customer_cluster(recency, frequency, monetary, model_dir='../models'):
    km = joblib.load(f'{model_dir}/kmeans_model.pkl')
    scaler = joblib.load(f'{model_dir}/scaler.pkl')
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
def predict_anomaly(total_amount, num_items, model_dir='../models'):
    iso = joblib.load(f'{model_dir}/isolation_forest.pkl')
    prediction = iso.predict([[total_amount, num_items]])[0]
    score = iso.decision_function([[total_amount, num_items]])[0]
    is_anomaly = True if prediction == -1 else False
    return is_anomaly, score
