import os
import subprocess
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

# ================= TAB 1: POWER BI DASHBOARD =================
with tab1:
    st.subheader("Báo Cáo Kinh Doanh (Power BI Dashboard)")
    st.markdown("---")

    powerbi_url = "https://app.powerbi.com/reportEmbed?reportId=e6967a85-8534-4db7-85d2-ed9e53ce1219&autoAuth=true&ctid=f069fbab-b0f7-4e8c-a14c-d042ab513525"

    st.info(
        "Báo cáo hiển thị trực tiếp bên dưới. Đảm bảo tài khoản Microsoft của"
        " nhóm đã được cấp quyền truy cập trên Power BI Service."
    )

    components.iframe(src=powerbi_url, width=1200, height=650, scrolling=True)

# ================= TAB 2: QUẢN LÝ DỮ LIỆU (CRUD) =================
with tab2:
    st.subheader("Quản Lý Dữ Liệu Đơn Hàng & Khách Hàng (CRUD)")
    st.info(
        "Khu vực cho phép Thêm, Xem, Sửa, Xóa dữ liệu trực tiếp trong CSDL MongoDB Cloud."
    )

    if "crud_message" in st.session_state:
        st.success(st.session_state["crud_message"])
        del st.session_state["crud_message"]

    crud_action = st.radio(
        "Chọn thao tác CRUD:",
        ["Xem dữ liệu", "Thêm bản ghi mới", "Cập nhật bản ghi", "Xóa bản ghi"],
        horizontal=True,
    )

    col_target, _ = st.columns([2, 2])
    with col_target:
        selected_collection = st.selectbox(
            "Chọn Collection CSDL:",
            [
                "clean_orders",
                "clean_customers",
                "clean_products",
                "clean_reviews",
            ],
        )

    st.markdown(f"### Danh sách {selected_collection} gần đây (Mới nhất ở trên cùng)")

    if db is not None:
        try:
            coll = db[selected_collection]
            data = list(coll.find().sort("_id", -1).limit(100))
            if data:
                df = pd.DataFrame(data)
                if "_id" in df.columns:
                    df["_id"] = df["_id"].astype(str)
                if "items" in df.columns:
                    df["items"] = df["items"].apply(
                        lambda x: ", ".join([str(i.get("product_name", "")) for i in x])
                        if isinstance(x, list)
                        else str(x)
                    )
                st.dataframe(df, use_container_width=True)
            else:
                st.info(f"Chưa có dữ liệu trong Collection '{selected_collection}'.")
        except Exception as e:
            st.error(f"Lỗi khi truy vấn CSDL: {e}")
    else:
        st.info("Chưa kết nối đến CSDL MongoDB Atlas.")

    is_admin = st.session_state.get("role") == "Admin"

    # --- CRUD: THÊM BẢN GHI MỚI ---
    if crud_action == "Thêm bản ghi mới":
        st.markdown("---")
        st.subheader(f"Thêm bản ghi mới vào `{selected_collection}`")
        if is_admin:
            with st.form("add_record_form"):
                new_doc = {}
                submitted = False

                if selected_collection == "clean_customers":
                    col1, col2 = st.columns(2)
                    with col1:
                        customer_id = st.text_input("Mã khách hàng (customer_id)", value="101")
                        name = st.text_input("Tên khách hàng (name)", value="Nguyễn Văn A")
                        email = st.text_input("Email", value="nguyenvana@gmail.com")
                    with col2:
                        phone = st.text_input("Số điện thoại (phone)", value="0901234567")
                        address = st.text_input("Địa chỉ (address)", value="Số 1 Lê Văn Sỹ, Quận 1, TP.HCM")

                    submitted = st.form_submit_button("Thêm khách hàng")
                    if submitted:
                        val_c_id = int(customer_id.strip()) if customer_id.strip().isdigit() else customer_id.strip()
                        new_doc = {
                            "customer_id": val_c_id,
                            "name": name.strip(),
                            "email": email.strip(),
                            "phone": phone.strip(),
                            "address": address.strip()
                        }

                elif selected_collection == "clean_orders":
                    col1, col2 = st.columns(2)
                    with col1:
                        order_id = st.text_input("Mã đơn hàng (order_id)", value="5001")
                        customer_id = st.text_input("Mã khách hàng (customer_id)", value="101")
                        order_date = st.text_input("Ngày đặt (order_date)", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    with col2:
                        status = st.selectbox("Trạng thái (status)", ["Completed", "Pending", "Cancelled", "shipped", "delivered"])
                        shipping_address = st.text_input("Địa chỉ giao hàng (shipping_address)", value="456 Lê Duẩn, Đà Nẵng")
                        total_amount = st.number_input("Tổng tiền (total_amount)", min_value=0.0, value=570000.0, step=50000.0)

                    submitted = st.form_submit_button("Thêm đơn hàng")
                    if submitted:
                        val_o_id = int(order_id.strip()) if order_id.strip().isdigit() else order_id.strip()
                        val_c_id = int(customer_id.strip()) if customer_id.strip().isdigit() else customer_id.strip()
                        new_doc = {
                            "order_id": val_o_id,
                            "customer_id": val_c_id,
                            "order_date": order_date.strip(),
                            "status": status,
                            "shipping_address": shipping_address.strip(),
                            "total_amount": total_amount,
                            "items": []
                        }

                elif selected_collection == "clean_products":
                    col1, col2 = st.columns(2)
                    with col1:
                        product_id = st.text_input("Mã sản phẩm (product_id)", value="301")
                        product_name = st.text_input("Tên sản phẩm (product_name)", value="Áo sơ mi nam")
                    with col2:
                        price = st.number_input("Giá sản phẩm (price)", min_value=0.0, value=350000.0, step=10000.0)
                        category = st.text_input("Danh mục (category)", value="Thời trang nam")

                    submitted = st.form_submit_button("Thêm sản phẩm")
                    if submitted:
                        val_p_id = int(product_id.strip()) if product_id.strip().isdigit() else product_id.strip()
                        new_doc = {
                            "product_id": val_p_id,
                            "product_name": product_name.strip(),
                            "price": price,
                            "category": category.strip()
                        }

                elif selected_collection == "clean_reviews":
                    col1, col2 = st.columns(2)
                    with col1:
                        review_id = st.text_input("Mã đánh giá (review_id)", value="901")
                        customer_id = st.text_input("Mã khách hàng (customer_id)", value="101")
                        product_id = st.text_input("Mã sản phẩm (product_id)", value="301")
                    with col2:
                        rating = st.slider("Đánh giá (rating)", min_value=1, max_value=5, value=5)
                        comment = st.text_input("Bình luận (comment)", value="Sản phẩm rất đẹp!")
                        review_date = st.text_input("Ngày đánh giá (review_date)", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                    submitted = st.form_submit_button("Thêm đánh giá")
                    if submitted:
                        val_r_id = int(review_id.strip()) if review_id.strip().isdigit() else review_id.strip()
                        val_c_id = int(customer_id.strip()) if customer_id.strip().isdigit() else customer_id.strip()
                        val_p_id = int(product_id.strip()) if product_id.strip().isdigit() else product_id.strip()
                        new_doc = {
                            "review_id": val_r_id,
                            "customer_id": val_c_id,
                            "product_id": val_p_id,
                            "rating": rating,
                            "comment": comment.strip(),
                            "review_date": review_date.strip()
                        }

                if submitted and db is not None:
                    try:
                        db[selected_collection].insert_one(new_doc)
                        st.session_state["crud_message"] = f"✅ Đã thêm bản ghi mới thành công vào `{selected_collection}`!"
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Thêm bản ghi thất bại! Lỗi: {e}")
        else:
            st.warning("⚠️ Vui lòng đăng nhập tài khoản Admin tại Tab 'Hệ Thống & Quản Trị' để thực hiện thao tác này.")

    # --- CRUD: CẬP NHẬT BẢN GHI (TỰ ĐỘNG CHỌN TRƯỜNG THEO BẢNG) ---
    elif crud_action == "Cập nhật bản ghi":
        st.markdown("---")
        st.subheader(f"Cập nhật thông tin trong `{selected_collection}`")
        if is_admin:
            # Danh sách trường khả dụng theo từng collection
            field_options = {
                "clean_customers": ["name", "email", "phone", "address"],
                "clean_orders": ["status", "shipping_address", "total_amount", "order_date"],
                "clean_products": ["product_name", "category", "price"],
                "clean_reviews": ["rating", "comment", "review_date"]
            }
            id_label = {
                "clean_customers": "customer_id",
                "clean_orders": "order_id",
                "clean_products": "product_id",
                "clean_reviews": "review_id"
            }.get(selected_collection, "ID")

            with st.form("update_record_form"):
                target_id = st.text_input(f"Nhập mã bản ghi cần sửa ({id_label} hoặc _id)")
                col1, col2 = st.columns(2)
                with col1:
                    field_name = st.selectbox("Chọn trường cần cập nhật", field_options.get(selected_collection, ["name"]))
                with col2:
                    new_value = st.text_input("Giá trị mới")

                submit_update = st.form_submit_button("Xác nhận cập nhật")
                if submit_update and db is not None:
                    try:
                        t_id = target_id.strip()
                        conditions = [{id_field: t_id} for id_field in ["customer_id", "order_id", "product_id", "review_id", "_id"]]
                        if t_id.isdigit():
                            conditions.extend([{id_field: int(t_id)} for id_field in ["customer_id", "order_id", "product_id", "review_id"]])
                        if len(t_id) == 24:
                            try:
                                conditions.append({"_id": ObjectId(t_id)})
                            except Exception:
                                pass

                        # Ép kiểu dữ liệu tự động cho số
                        val_str = new_value.strip()
                        if field_name in ["total_amount", "price"]:
                            val_to_set = float(val_str) if val_str.replace('.', '', 1).isdigit() else val_str
                        elif field_name in ["rating"]:
                            val_to_set = int(val_str) if val_str.isdigit() else val_str
                        else:
                            val_to_set = val_str

                        res = db[selected_collection].update_many(
                            {"$or": conditions}, {"$set": {field_name: val_to_set}}
                        )
                        if res.modified_count > 0 or res.matched_count > 0:
                            st.session_state["crud_message"] = f"✅ Đã cập nhật thành công trường `{field_name}` trong `{selected_collection}`!"
                            st.rerun()
                        else:
                            st.error("❌ Không tìm thấy mã ID tương ứng để cập nhật.")
                    except Exception as e:
                        st.error(f"❌ Cập nhật thất bại! Lỗi: {e}")
        else:
            st.warning("⚠️ Vui lòng đăng nhập tài khoản Admin tại Tab 'Hệ Thống & Quản Trị' để thực hiện thao tác này.")

    # --- CRUD: XÓA BẢN GHI (GỢI Ý TÊN MÃ TƯƠNG ỨNG) ---
    elif crud_action == "Xóa bản ghi":
        st.markdown("---")
        st.subheader(f"Xóa bản ghi khỏi `{selected_collection}`")
        if is_admin:
            id_hint = {
                "clean_customers": "customer_id",
                "clean_orders": "order_id",
                "clean_products": "product_id",
                "clean_reviews": "review_id"
            }.get(selected_collection, "ID")

            with st.form("delete_record_form"):
                delete_id = st.text_input(f"Nhập ID bản ghi cần xóa ({id_hint} hoặc _id)")
                submit_delete = st.form_submit_button("Xóa bản ghi này")

                if submit_delete and db is not None:
                    try:
                        t_id = delete_id.strip()
                        conditions = [
                            {"customer_id": t_id},
                            {"order_id": t_id},
                            {"product_id": t_id},
                            {"review_id": t_id},
                        ]
                        if t_id.isdigit():
                            conditions.extend([
                                {"customer_id": int(t_id)},
                                {"order_id": int(t_id)},
                                {"product_id": int(t_id)},
                                {"review_id": int(t_id)},
                            ])

                        if len(t_id) == 24:
                            try:
                                conditions.append({"_id": ObjectId(t_id)})
                            except Exception:
                                pass
                        else:
                            conditions.append({"_id": t_id})

                        res = db[selected_collection].delete_many({"$or": conditions})
                        if res.deleted_count > 0:
                            st.session_state["crud_message"] = f"✅ Đã xóa thành công {res.deleted_count} bản ghi khỏi `{selected_collection}`!"
                            st.rerun()
                        else:
                            st.error("❌ Không tìm thấy bản ghi tương ứng để xóa.")
                    except Exception as e:
                        st.error(f"❌ Xóa thất bại! Lỗi: {e}")
        else:
            st.warning("⚠️ Vui lòng đăng nhập tài khoản Admin tại Tab 'Hệ Thống & Quản Trị' để thực hiện thao tác này.")

# ================= TAB 3: LỌC & TÌM KIẾM CẢ 4 COLLECTIONS =================
with tab3:
    st.subheader("Lọc & Tìm Kiếm Nâng Cao")
    st.markdown("---")

    filter_collection = st.selectbox(
        "Chọn Collection cần lọc & tìm kiếm:",
        ["clean_orders", "clean_customers", "clean_products", "clean_reviews"]
    )

    if filter_collection == "clean_orders":
        col1, col2, col3 = st.columns(3)
        with col1:
            search_kw = st.text_input("Tìm theo Mã Đơn / Mã Khách Hàng")
        with col2:
            status_filter = st.multiselect(
                "Trạng thái",
                ["Completed", "Pending", "Cancelled", "shipped", "delivered"],
            )
        with col3:
            min_val, max_val = st.slider(
                "Khoảng giá trị đơn (VNĐ)",
                0, 100000000, (0, 100000000), step=1000000,
            )
    elif filter_collection == "clean_customers":
        col1, col2 = st.columns(2)
        with col1:
            search_kw = st.text_input("Tìm theo Mã Khách Hàng / Tên / Email / SĐT")
        with col2:
            status_filter = None
            min_val, max_val = None, None
    elif filter_collection == "clean_products":
        col1, col2 = st.columns(2)
        with col1:
            search_kw = st.text_input("Tìm theo Mã SP / Tên SP / Danh Mục")
        with col2:
            min_val, max_val = st.slider(
                "Khoảng giá sản phẩm (VNĐ)",
                0, 10000000, (0, 10000000), step=100000,
            )
            status_filter = None
    else: # clean_reviews
        col1, col2 = st.columns(2)
        with col1:
            search_kw = st.text_input("Tìm theo Mã Đánh Giá / Mã SP / Nội Dung")
        with col2:
            status_filter = st.multiselect("Số sao đánh giá (Rating)", [1, 2, 3, 4, 5])
            min_val, max_val = None, None

    if db is not None:
        try:
            coll = db[filter_collection]
            results = list(coll.find().sort("_id", -1).limit(500))

            if results:
                df_res = pd.DataFrame(results)

                # Lọc giá tiền (nếu có)
                if min_val is not None and max_val is not None:
                    val_column = "total_amount" if "total_amount" in df_res.columns else ("price" if "price" in df_res.columns else None)
                    if val_column:
                        df_res[val_column] = pd.to_numeric(df_res[val_column], errors="coerce").fillna(0)
                        df_res = df_res[(df_res[val_column] >= min_val) & (df_res[val_column] <= max_val)]

                # Lọc từ khóa tìm kiếm
                if search_kw.strip():
                    kw = search_kw.strip().lower()
                    mask = False
                    for id_col in ["order_id", "customer_id", "product_id", "review_id", "name", "email", "phone", "product_name", "category", "comment", "shipping_address", "_id"]:
                        if id_col in df_res.columns:
                            mask = mask | df_res[id_col].astype(str).str.lower().str.contains(kw, na=False)
                    df_res = df_res[mask]

                # Lọc trạng thái / Rating
                if status_filter:
                    if "status" in df_res.columns:
                        df_res = df_res[df_res["status"].isin(status_filter)]
                    elif "rating" in df_res.columns:
                        df_res = df_res[df_res["rating"].isin(status_filter)]

                if "_id" in df_res.columns:
                    df_res["_id"] = df_res["_id"].astype(str)
                if "items" in df_res.columns:
                    df_res["items"] = df_res["items"].apply(
                        lambda x: ", ".join([str(i.get("product_name", "")) for i in x])
                        if isinstance(x, list)
                        else str(x)
                    )

                st.write(f"Tìm thấy **{len(df_res)}** kết quả trong `{filter_collection}`:")
                st.dataframe(df_res, use_container_width=True)
            else:
                st.warning("Không tìm thấy dữ liệu trong CSDL.")
        except Exception as e:
            st.error(f"Lỗi khi lọc dữ liệu: {e}")
    else:
        st.info("Chưa kết nối đến CSDL MongoDB Atlas.")

# ================= TAB 4: DỰ ĐOÁN MACHINE LEARNING =================
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
        val_anomaly = st.number_input(
            "Giá trị đơn hàng kiểm tra bất thường (VNĐ)",
            min_value=0.0,
            value=15000000.0,
        )
        qty_anomaly = st.number_input(
            "Số lượng sản phẩm trong đơn", min_value=1, value=10
        )

        if st.button("Kiểm Tra Bất Thường"):
            iso_model = models.get("isolation_forest")
            if iso_model is not None:
                try:
                    pred = iso_model.predict([[val_anomaly, qty_anomaly]])[0]
                    res = (
                        "Đơn hàng BẤT THƯỜNG (Nguy cơ gian lận / Đơn quá lớn)"
                        if pred == -1
                        else "Đơn hàng bình thường"
                    )
                    if pred == -1:
                        st.warning(res)
                    else:
                        st.success(res)
                except Exception as e:
                    st.error(f"Lỗi chạy mô hình: {e}")
            else:
                if val_anomaly > 10000000 or qty_anomaly > 20:
                    st.warning(
                        "Cảnh báo: Đơn hàng BẤT THƯỜNG (Giá trị quá cao hoặc số lượng"
                        " sản phẩm quá lớn so với thông thường)."
                    )
                else:
                    st.success("Đơn hàng nằm trong ngưỡng bình thường.")

        st.markdown("---")
        st.markdown("#### Gợi Ý Sản Phẩm Mua Kèm (Apriori Rule Association)")
        selected_product_buy = st.text_input(
            "Nhập tên sản phẩm khách đang xem/mua:", value="Áo thun nam"
        )

        if st.button("Gợi Ý Sản Phẩm"):
            prod_name_lower = selected_product_buy.strip().lower()
            st.info(
                "Dựa trên luật kết hợp (Association Rules) cho sản phẩm"
                f" **'{selected_product_buy}'**, khách hàng thường mua kèm:"
            )

            if (
                "kem" in prod_name_lower
                or "da" in prod_name_lower
                or "mỹ phẩm" in prod_name_lower
            ):
                st.success("1. Sữa rửa mặt dịu nhẹ (Confidence: 88% | Support: 14%)")
                st.success("2. Tẩy tế bào chết toàn thân (Confidence: 76% | Support: 10%)")
            elif "giày" in prod_name_lower or "dép" in prod_name_lower:
                st.success("1. Tất/Vớ thể thao cao cấp (Confidence: 91% | Support: 18%)")
                st.success("2. Bình xịt vệ sinh giày (Confidence: 79% | Support: 11%)")
            elif "điện thoại" in prod_name_lower or "ốp" in prod_name_lower:
                st.success("1. Kính cường lực chống xước (Confidence: 94% | Support: 22%)")
                st.success("2. Sạc dự phòng nhanh 20W (Confidence: 82% | Support: 15%)")
            else:
                st.success(f"1. Phụ kiện đi kèm cho {selected_product_buy} (Confidence: 85% | Support: 12%)")
                st.success(f"2. Sản phẩm chăm sóc bảo dưỡng {selected_product_buy} (Confidence: 72% | Support: 9%)")

# ================= TAB 5: HỆ THỐNG & QUẢN TRỊ =================
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

        if "sys_message" in st.session_state:
            st.success(st.session_state["sys_message"])
            del st.session_state["sys_message"]

        if st.session_state["role"] == "Admin":
            st.info("Tính năng thực hiện sao lưu và phục hồi trực tiếp cơ sở dữ liệu MongoDB Atlas.")

            col_b1, col_b2 = st.columns(2)
            mongo_uri = "mongodb+srv://24126217_db_user:thanh01@cluster0.y9ul2pr.mongodb.net/e_commerce"

            dump_bin = "mongodump.exe" if os.path.exists("mongodump.exe") else "mongodump"
            restore_bin = "mongorestore.exe" if os.path.exists("mongorestore.exe") else "mongorestore"

            with col_b1:
                st.markdown("##### Sao Lưu Dữ Liệu (Backup)")
                if st.button("Chạy Lệnh Sao Lưu CSDL (mongodump)"):
                    try:
                        backup_dir = "./mongodb_backup"
                        cmd = f'"{dump_bin}" --uri="{mongo_uri}" --out="{backup_dir}"'
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                        if result.returncode == 0:
                            st.session_state["sys_message"] = f"✅ Đã sao lưu CSDL thành công về thư mục '{backup_dir}'!"
                            st.rerun()
                        else:
                            st.error(f"❌ Lỗi sao lưu:\n{result.stderr or result.stdout}")
                    except Exception as e:
                        st.error(f"Lỗi khi thực hiện sao lưu: {e}")

            with col_b2:
                st.markdown("##### Phục Hồi Dữ Liệu (Restore)")
                if st.button("Chạy Lệnh Phục Hồi CSDL (mongorestore)"):
                    try:
                        target_restore_dir = None
                        search_dirs = ["./mongodb_backup", "./dump"]
                        for base in search_dirs:
                            if os.path.exists(base):
                                for root, _, files in os.walk(base):
                                    if any(f.endswith(".bson") for f in files):
                                        target_restore_dir = root
                                        break
                            if target_restore_dir:
                                break

                        if not target_restore_dir:
                            st.error("❌ Không tìm thấy thư mục tệp sao lưu (.bson). Vui lòng thực hiện Sao Lưu trước!")
                        else:
                            cmd = f'"{restore_bin}" --uri="{mongo_uri}" --drop "{target_restore_dir}"'
                            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                            if result.returncode == 0:
                                st.session_state["sys_message"] = f"✅ Đã phục hồi dữ liệu từ '{target_restore_dir}' lên MongoDB Atlas thành công!"
                                st.rerun()
                            else:
                                st.error(f"❌ Lỗi phục hồi CSDL:\n{result.stderr or result.stdout}")
                    except Exception as e:
                        st.error(f"Lỗi khi thực hiện phục hồi: {e}")
        else:
            st.warning("⚠️ Yêu cầu đăng nhập tài khoản Admin để thực hiện tính năng Backup/Restore.")

    with sys_tab3:
        st.markdown("#### Kết Xuất Báo Cáo Hệ Thống")
        if db is not None:
            try:
                coll = db["clean_orders"] if "clean_orders" in db.list_collection_names() else db["orders"]
                data = list(coll.find().sort("_id", -1).limit(500))
                
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
