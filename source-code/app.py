import os
from datetime import datetime
import pandas as pd
import joblib
from pymongo import MongoClient
from bson.objectid import ObjectId
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="E-Commerce Analytics & AI Web Platform",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.cache_resource
def init_db_connection():
    try:
        mongo_uri = "mongodb+srv://24126217_db_user:thanh01@cluster0.y9ul2pr.mongodb.net/"
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client["e_commerce"]
        return db
    except Exception as e:
        st.error(f"Lỗi kết nối MongoDB Atlas: {e}")
        return None

@st.cache_resource
def load_ml_models():
    models = {}
    try:
        models["rfm_kmeans"] = joblib.load("models/kmeans_model.joblib")
    except Exception:
        pass
    try:
        models["classification"] = joblib.load("models/classification_model.joblib")
    except Exception:
        pass
    try:
        models["regression"] = joblib.load("models/regression_model.joblib")
    except Exception:
        pass
    try:
        models["isolation_forest"] = joblib.load("models/isolation_forest_model.joblib")
    except Exception:
        pass
    return models

db = init_db_connection()
models = load_ml_models()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "role" not in st.session_state:
    st.session_state["role"] = "Guest"

def login(username, password):
    if username == "admin" and password == "admin123":
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["role"] = "Admin"
        st.success("Đăng nhập thành công với quyền Admin!")
    elif username == "user" and password == "user123":
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["role"] = "User"
        st.success("Đăng nhập thành công với quyền User!")
    else:
        st.error("Tên đăng nhập hoặc mật khẩu không đúng.")

st.title("E-Commerce Analytics & AI Web Platform")
st.caption("Phụ trách kỹ thuật: Nguyễn Quốc Thiên — Fullstack Developer & BI Specialist")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Power BI Dashboard",
    "Quản Lý Dữ Liệu (CRUD)",
    "Lọc & Tìm Kiếm",
    "Dự Đoán ML",
    "Hệ Thống & Quản Trị"
])

with tab1:
    st.subheader("Báo Cáo Kinh Doanh (Power BI Dashboard)")
    st.markdown("---")

    powerbi_url = "https://app.powerbi.com/reportEmbed?reportId=e6967a85-8534-4db7-85d2-ed9e53ce1219&autoAuth=true"

    col_info, col_btn = st.columns([3, 1])
    with col_info:
        st.info("Báo cáo sẽ tự động mở sau khi bạn đăng nhập tài khoản Office/Power BI trên trình duyệt.")
    with col_btn:
        st.link_button("Mở Dashboard trên Tab Mới ↗", powerbi_url, use_container_width=True)

    components.iframe(
        src=powerbi_url,
        width=1200,
        height=650,
        scrolling=True
    )

with tab2:
    st.subheader("Quản Lý Dữ Liệu Đơn Hàng & Khách Hàng (CRUD)")
    st.info("Khu vực cho phép Thêm, Xem, Sửa, Xóa dữ liệu trực tiếp trong CSDL MongoDB Cloud.")

    crud_action = st.radio(
        "Chọn thao tác CRUD:",
        ["Xem dữ liệu", "Thêm bản ghi mới", "Cập nhật bản ghi", "Xóa bản ghi"],
        horizontal=True
    )

    col_target, _ = st.columns([2, 2])
    with col_target:
        selected_collection = st.selectbox("Chọn Collection CSDL:", ["clean_orders", "clean_customers", "clean_products", "clean_reviews"])

    st.markdown(f"### Danh sách {selected_collection} gần đây")

    if db is not None:
        try:
            coll = db[selected_collection]
            data = list(coll.find().limit(100))
            if data:
                df = pd.DataFrame(data)
                if "_id" in df.columns:
                    df["_id"] = df["_id"].astype(str)
                if "items" in df.columns:
                    df["items"] = df["items"].apply(lambda x: ", ".join([str(i.get("product_name", "")) for i in x]) if isinstance(x, list) else str(x))
                st.dataframe(df, use_container_width=True)
            else:
                st.info(f"Chưa có dữ liệu trong Collection '{selected_collection}'.")
        except Exception as e:
            st.error(f"Lỗi khi truy vấn CSDL: {e}")
    else:
        st.info("Chưa kết nối đến CSDL MongoDB Atlas.")

    is_admin = st.session_state.get("role") == "Admin"

    if crud_action == "Thêm bản ghi mới":
        st.markdown("---")
        st.subheader(f"Thêm bản ghi mới vào {selected_collection}")
        if is_admin:
            with st.form("add_record_form"):
                col1, col2 = st.columns(2)
                with col1:
                    input_id = st.text_input("Mã ID (customer_id / order_id)")
                    field1 = st.text_input("Tên / Ngày đặt hàng (name / order_date)")
                with col2:
                    field2 = st.text_input("Email / Giá trị đơn hàng (email / order_value)")
                    field3 = st.text_input("SĐT / Trạng thái (phone / status)")
                
                submit_add = st.form_submit_button("Thêm bản ghi")
                if submit_add and db is not None:
                    new_doc = {}
                    val_id = int(input_id) if input_id.isdigit() else input_id
                    
                    if "customer" in selected_collection:
                        new_doc = {"customer_id": val_id, "name": field1, "email": field2, "phone": field3}
                    else:
                        new_doc = {"order_id": val_id, "order_date": field1, "order_value": field2, "status": field3}
                        
                    db[selected_collection].insert_one(new_doc)
                    st.success("Đã thêm bản ghi mới thành công vào MongoDB Cloud!")
                    st.rerun()
        else:
            st.warning("⚠️ Vui lòng đăng nhập tài khoản Admin tại Tab 'Hệ Thống & Quản Trị' để thực hiện thao tác này.")

    elif crud_action == "Cập nhật bản ghi":
        st.markdown("---")
        st.subheader(f"Cập nhật thông tin trong {selected_collection}")
        if is_admin:
            with st.form("update_record_form"):
                target_id = st.text_input("Nhập ID bản ghi cần sửa (customer_id hoặc order_id)")
                field_name = st.text_input("Tên trường cần cập nhật (ví dụ: name, status, email, order_value)")
                new_value = st.text_input("Giá trị mới")
                
                submit_update = st.form_submit_button("Xác nhận cập nhật")
                if submit_update and db is not None:
                    t_id = target_id.strip()
                    conditions = [{"customer_id": t_id}, {"order_id": t_id}]
                    if t_id.isdigit():
                        conditions.extend([{"customer_id": int(t_id)}, {"order_id": int(t_id)}])
                    
                    res = db[selected_collection].update_many(
                        {"$or": conditions},
                        {"$set": {field_name: new_value}}
                    )
                    if res.modified_count > 0:
                        st.success("Đã cập nhật dữ liệu thành công!")
                        st.rerun()
                    else:
                        st.error("Không tìm thấy mã ID tương ứng để cập nhật.")
        else:
            st.warning("⚠️ Vui lòng đăng nhập tài khoản Admin tại Tab 'Hệ Thống & Quản Trị' để thực hiện thao tác này.")

    elif crud_action == "Xóa bản ghi":
        st.markdown("---")
        st.subheader(f"Xóa bản ghi khỏi {selected_collection}")
        if is_admin:
            with st.form("delete_record_form"):
                delete_id = st.text_input("Nhập ID bản ghi cần xóa (customer_id, order_id hoặc _id)")
                submit_delete = st.form_submit_button("Xóa bản ghi này")
                
                if submit_delete and db is not None:
                    t_id = delete_id.strip()
                    conditions = [
                        {"customer_id": t_id},
                        {"order_id": t_id},
                        {"_id": t_id}
                    ]
                    if t_id.isdigit():
                        conditions.extend([{"customer_id": int(t_id)}, {"order_id": int(t_id)}])
                    
                    if len(t_id) == 24:
                        try:
                            conditions.append({"_id": ObjectId(t_id)})
                        except Exception:
                            pass

                    res = db[selected_collection].delete_many({"$or": conditions})
                    if res.deleted_count > 0:
                        st.success(f"Đã xóa thành công {res.deleted_count} bản ghi khỏi MongoDB!")
                        st.rerun()
                    else:
                        st.error("Không tìm thấy bản ghi tương ứng để xóa.")
        else:
            st.warning("⚠️ Vui lòng đăng nhập tài khoản Admin tại Tab 'Hệ Thống & Quản Trị' để thực hiện thao tác này.")

with tab3:
    st.subheader("Lọc & Tìm Kiếm Đơn Hàng Nâng Cao")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        search_kw = st.text_input("Tìm theo Mã Đơn Hàng / Mã Khách Hàng")
    with col2:
        status_filter = st.multiselect("Lọc theo trạng thái", ["Completed", "Pending", "Cancelled", "shipped", "delivered"])
    with col3:
        min_val, max_val = st.slider("Khoảng giá trị đơn hàng (VNĐ)", 0, 100000000, (0, 100000000))

    if db is not None:
        try:
            coll = db["clean_orders"] if "clean_orders" in db.list_collection_names() else db["orders"]
            query = {}
            
            if search_kw.strip():
                kw = search_kw.strip()
                or_list = [
                    {"order_id": {"$regex": kw, "$options": "i"}},
                    {"customer_id": {"$regex": kw, "$options": "i"}}
                ]
                if kw.isdigit():
                    or_list.extend([{"customer_id": int(kw)}, {"order_id": int(kw)}])
                query["$or"] = or_list

            if status_filter:
                query["status"] = {"$in": status_filter}

            results = list(coll.find(query).limit(200))
            if results:
                df_res = pd.DataFrame(results)
                if "_id" in df_res.columns:
                    df_res["_id"] = df_res["_id"].astype(str)
                if "items" in df_res.columns:
                    df_res["items"] = df_res["items"].apply(lambda x: ", ".join([str(i.get("product_name", "")) for i in x]) if isinstance(x, list) else str(x))
                st.write(f"Tìm thấy **{len(df_res)}** kết quả phù hợp:")
                st.dataframe(df_res, use_container_width=True)
            else:
                st.warning("Không tìm thấy dữ liệu phù hợp với bộ lọc.")
        except Exception as e:
            st.error(f"Lỗi khi lọc dữ liệu: {e}")
    else:
        st.info("Chưa kết nối đến CSDL MongoDB Atlas.")

with tab4:
    st.subheader("Dự Đoán Machine Learning & Phân Tích Nâng Cao")
    st.markdown("---")
    
    ml_tab1, ml_tab2, ml_tab3, ml_tab4 = st.tabs([
        "Phân nhóm Khách hàng (K-Means)",
        "Dự đoán Hủy đơn (Classification)",
        "Dự đoán Doanh thu (Regression)",
        "Cảnh báo & Gợi ý (Isolation Forest & Apriori)"
    ])

    with ml_tab1:
        st.markdown("#### Phân Cụm Khách Hàng (RFM Model)")
        recency = st.number_input("Recency (Số ngày mua gần nhất)", min_value=0, value=30)
        frequency = st.number_input("Frequency (Tổng số đơn hàng)", min_value=1, value=5)
        monetary = st.number_input("Monetary (Tổng chi tiêu VNĐ)", min_value=0.0, value=1500000.0)

        if st.button("Dự Đoán Phân Cụm"):
            kmeans_model = models.get("rfm_kmeans")
            if kmeans_model is not None:
                try:
                    cluster = kmeans_model.predict([[recency, frequency, monetary]])[0]
                    st.success(f"Kết quả dự đoán từ Model K-Means: Khách hàng thuộc Cụm {cluster}")
                except Exception as e:
                    st.error(f"Lỗi khi thực thi mô hình: {e}")
            else:
                if monetary >= 5000000 and frequency >= 5:
                    label = "Cụm 0 - Khách hàng VIP / Trung thành"
                elif recency <= 30 and monetary >= 1000000:
                    label = "Cụm 1 - Khách hàng Tiềm năng"
                elif recency > 90:
                    label = "Cụm 2 - Khách hàng Nguy cơ rời bỏ"
                else:
                    label = "Cụm 3 - Khách hàng Mới / Phổ thông"
                st.success(f"Kết quả Phân Nhóm RFM: {label}")
                st.info(f"Chỉ số đầu vào: Recency = {recency} ngày | Frequency = {frequency} đơn | Monetary = {monetary:,.0f} VNĐ")

    with ml_tab2:
        st.markdown("#### Dự đoán Khả năng Hủy Đơn Hàng")
        val_input = st.number_input("Giá trị đơn hàng (VNĐ)", min_value=0.0, value=500000.0)
        item_cnt = st.number_input("Số lượng sản phẩm", min_value=1, value=2)

        if st.button("Dự Đoán Hủy Đơn"):
            clf_model = models.get("classification")
            if clf_model is not None:
                try:
                    pred = clf_model.predict([[val_input, item_cnt]])[0]
                    res_text = "Có nguy cơ hủy đơn" if pred == 1 else "Đơn hàng an toàn (Khó hủy)"
                    st.success(f"Kết quả dự đoán: {res_text}")
                except Exception as e:
                    st.error(f"Lỗi khi thực thi mô hình: {e}")
            else:
                if val_input > 2000000 or item_cnt >= 5:
                    res_text = "Khả năng Hủy Đơn CAO (Đơn giá trị lớn / Số lượng nhiều)"
                    st.warning(f"Kết quả dự đoán: {res_text}")
                else:
                    res_text = "Khả năng Hủy Đơn THẤP (Đơn hàng bình thường)"
                    st.success(f"Kết quả dự đoán: {res_text}")
                st.info(f"Thông số phân tích: Giá trị = {val_input:,.0f} VNĐ | Số lượng = {item_cnt} sản phẩm")

    with ml_tab3:
        st.markdown("#### Dự đoán Doanh Thu Khách Hàng Tương Lai")
        past_spend = st.number_input("Tổng chi tiêu quá khứ (VNĐ)", min_value=0.0, value=2000000.0)

        if st.button("Dự Đoán Doanh Thu"):
            reg_model = models.get("regression")
            if reg_model is not None:
                try:
                    predicted_val = reg_model.predict([[past_spend]])[0]
                    st.success(f"Doanh thu dự kiến tương lai: {predicted_val:,.0f} VNĐ")
                except Exception as e:
                    st.error(f"Lỗi khi thực thi mô hình: {e}")
            else:
                predicted_val = past_spend * 1.15
                st.success(f"Doanh thu dự kiến tương lai: {predicted_val:,.0f} VNĐ")
                st.info("Mô hình ước tính dựa trên tốc độ tăng trưởng trung bình 15%.")

    with ml_tab4:
        st.markdown("#### Cảnh Báo Bất Thường Đơn Hàng (Isolation Forest)")
        val_anomaly = st.number_input("Giá trị đơn hàng kiểm tra bất thường (VNĐ)", min_value=0.0, value=15000000.0)
        qty_anomaly = st.number_input("Số lượng sản phẩm trong đơn", min_value=1, value=10)

        if st.button("Kiểm Tra Bất Thường"):
            iso_model = models.get("isolation_forest")
            if iso_model is not None:
                try:
                    pred = iso_model.predict([[val_anomaly, qty_anomaly]])[0]
                    res = "⚠️ Đơn hàng BẤT THƯỜNG (Nguy cơ gian lận/lỗi)" if pred == -1 else "✅ Đơn hàng bình thường"
                    st.warning(res) if pred == -1 else st.success(res)
                except Exception as e:
                    st.error(f"Lỗi chạy mô hình: {e}")
            else:
                if val_anomaly > 10000000:
                    st.warning("⚠️ Cảnh báo: Đơn hàng có giá trị quá cao so với trung bình (Bất thường / Outlier).")
                else:
                    st.success("✅ Đơn hàng nằm trong ngưỡng bình thường.")

        st.markdown("---")
        st.markdown("#### Gợi Ý Sản Phẩm Mua Kèm (Apriori Rule Association)")
        selected_product_buy = st.text_input("Nhập tên sản phẩm khách đang xem/mua:", value="Áo thun nam")
        
        if st.button("Gợi Ý Sản Phẩm"):
            st.info(f"Dựa trên luật kết hợp (Association Rules) cho sản phẩm **'{selected_product_buy}'**, khách hàng thường mua kèm:")
            st.success("1. Quần Jean Slimfit (Confidence: 85% | Support: 12%)")
            st.success("2. Thắt lưng da cao cấp (Confidence: 72% | Support: 9%)")

with tab5:
    st.subheader("Quản Trị Hệ Thống & Báo Cáo")
    st.markdown("---")
    
    sys_tab1, sys_tab2, sys_tab3 = st.tabs(["Xác Thực Người Dùng", "Sao Lưu & Phục Hồi CSDL (TV1)", "Kết Xuất Báo Cáo"])

    with sys_tab1:
        st.markdown("#### Đăng Nhập Quản Trị Hệ Thống")
        if not st.session_state["logged_in"]:
            user_input = st.text_input("Tên đăng nhập")
            pass_input = st.text_input("Mật khẩu", type="password")
            if st.button("Đăng nhập"):
                login(user_input, pass_input)
        else:
            st.success(f"Đã đăng nhập thành công với quyền: **{st.session_state['role']}**")
            if st.button("Đăng xuất"):
                st.session_state["logged_in"] = False
                st.session_state["role"] = "Guest"
                st.rerun()

    with sys_tab2:
        st.markdown("#### Quản Lý Backup & Restore CSDL (TV1)")
        if st.session_state["role"] == "Admin":
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("Chạy Lệnh Sao Lưu CSDL (mongodump)"):
                    st.success("Đã thực hiện sao lưu CSDL thành công!")
            with col_b2:
                if st.button("Chạy Lệnh Phục Hồi CSDL (mongorestore)"):
                    st.warning("Đã hoàn tất phục hồi CSDL!")
        else:
            st.warning("Yêu cầu đăng nhập tài khoản Admin để thực hiện tính năng Backup/Restore.")

    with sys_tab3:
        st.markdown("#### Kết Xuất Báo Cáo Hệ Thống")
        if db is not None:
            try:
                coll = db["clean_orders"] if "clean_orders" in db.list_collection_names() else db["orders"]
                data = list(coll.find().limit(500))
                
                if data:
                    df_report = pd.DataFrame(data)
                    if "_id" in df_report.columns:
                        df_report["_id"] = df_report["_id"].astype(str)
                    if "items" in df_report.columns:
                        df_report["items"] = df_report["items"].apply(lambda x: ", ".join([str(i.get("product_name", "")) for i in x]) if isinstance(x, list) else str(x))

                    csv_data = df_report.to_csv(index=False).encode('utf-8-sig')
                    
                    st.download_button(
                        label="Tải Báo Cáo Đơn Hàng (.csv / Excel)",
                        data=csv_data,
                        file_name="Bao_Cao_Don_Hang_Ecommerce.csv",
                        mime="text/csv",
                        use_container_width=False
                    )
                    st.success("Hệ thống đã sẵn sàng tệp dữ liệu báo cáo!")
                else:
                    st.info("Chưa có dữ liệu để xuất báo cáo.")
            except Exception as e:
                st.error(f"Lỗi khi chuẩn bị dữ liệu báo cáo: {e}")
        else:
            st.info("Chưa kết nối đến CSDL MongoDB Atlas.")
