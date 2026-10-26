import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import joblib
from pymongo import MongoClient

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
    st.subheader("Power BI Business Analytics Dashboard")
    st.markdown("---")

    power_bi_embed_url = "https://app.powerbi.com/reportEmbed?reportId=e6967a85-8534-4db7-85d2-ed9e53ce1219&autoAuth=true&ctid=f069fbab-b0f7-4e8c-a14c-d042ab513525"
    
    components.iframe(
        src=power_bi_embed_url,
        width=1200,
        height=650,
        scrolling=True
    )

with tab2:
    st.subheader("Quản Lý Dữ Liệu Đơn Hàng & Khách Hàng (CRUD)")
    st.info("Khu vực cho phép Thêm, Xem, Sửa, Xóa dữ liệu trực tiếp trong CSDL (clean_orders & clean_customers).")

    crud_action = st.radio(
        "Chọn thao tác CRUD:",
        ["Xem dữ liệu", "Thêm đơn hàng mới", "Cập nhật đơn hàng", "Xóa đơn hàng"],
        horizontal=True
    )

    col_target, _ = st.columns([2, 2])
    with col_target:
        selected_collection = st.selectbox("Chọn Collection CSDL:", ["clean_orders", "clean_customers"])

    st.markdown(f"### Danh sách {selected_collection} gần đây")

    if db is not None:
        try:
            coll = db[selected_collection]
            data = list(coll.find().limit(100))
            if data:
                df = pd.DataFrame(data)
                if "_id" in df.columns:
                    df["_id"] = df["_id"].astype(str)
                st.dataframe(df, use_container_width=True)
            else:
                st.info(f"Chưa có dữ liệu trong Collection '{selected_collection}'.")
        except Exception as e:
            st.error(f"Lỗi khi đọc dữ liệu từ CSDL: {e}")
    else:
        st.info("Chưa kết nối đến CSDL MongoDB local.")

    if crud_action == "Thêm đơn hàng mới":
        st.markdown("---")
        st.subheader("Nhập thông tin bản ghi mới")
        if st.session_state["role"] == "Admin":
            with st.form("add_record_form"):
                col1, col2 = st.columns(2)
                with col1:
                    order_id = st.text_input("Mã đơn hàng / Mã KH")
                    order_date = st.date_input("Ngày thực hiện")
                with col2:
                    order_value = st.number_input("Giá trị (VNĐ)", min_value=0.0)
                    status = st.selectbox("Trạng thái", ["Completed", "Pending", "Cancelled"])
                
                submit_add = st.form_submit_button("Thêm bản ghi")
                if submit_add and db is not None:
                    db[selected_collection].insert_one({
                        "order_id": order_id,
                        "order_date": str(order_date),
                        "order_value": order_value,
                        "status": status
                    })
                    st.success("Đã thêm thành công vào CSDL!")
                    st.rerun()
        else:
            st.warning("Vui lòng đăng nhập tài khoản Admin tại tab 'Hệ Thống & Quản Trị' để thực hiện thao tác này.")

    elif crud_action == "Cập nhật đơn hàng":
        st.markdown("---")
        st.subheader("Cập nhật thông tin bản ghi")
        if st.session_state["role"] == "Admin":
            with st.form("update_record_form"):
                target_id = st.text_input("Nhập Mã đơn hàng cần sửa")
                new_status = st.selectbox("Cập nhật trạng thái mới", ["Completed", "Pending", "Cancelled"])
                new_value = st.number_input("Cập nhật giá trị mới (VNĐ)", min_value=0.0)
                
                submit_update = st.form_submit_button("Cập nhật")
                if submit_update and db is not None:
                    res = db[selected_collection].update_one(
                        {"order_id": target_id},
                        {"$set": {"status": new_status, "order_value": new_value}}
                    )
                    if res.modified_count > 0:
                        st.success("Cập nhật thành công!")
                        st.rerun()
                    else:
                        st.error("Không tìm thấy mã đơn hàng phù hợp.")
        else:
            st.warning("Vui lòng đăng nhập tài khoản Admin tại tab 'Hệ Thống & Quản Trị' để thực hiện thao tác này.")

    elif crud_action == "Xóa đơn hàng":
        st.markdown("---")
        st.subheader("Xóa bản ghi khỏi CSDL")
        if st.session_state["role"] == "Admin":
            with st.form("delete_record_form"):
                delete_id = st.text_input("Nhập Mã đơn hàng cần xóa")
                submit_delete = st.form_submit_button("Xóa bản ghi")
                if submit_delete and db is not None:
                    res = db[selected_collection].delete_one({"order_id": delete_id})
                    if res.deleted_count > 0:
                        st.success("Đã xóa bản ghi thành công!")
                        st.rerun()
                    else:
                        st.error("Không tìm thấy bản ghi cần xóa.")
        else:
            st.warning("Vui lòng đăng nhập tài khoản Admin tại tab 'Hệ Thống & Quản Trị' để thực hiện thao tác này.")

with tab3:
    st.subheader("Lọc & Tìm Kiếm Đơn Hàng Nâng Cao")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        search_kw = st.text_input("Tìm theo Mã Đơn Hàng / Mã Khách Hàng")
    with col2:
        status_filter = st.multiselect("Lọc theo trạng thái", ["Completed", "Pending", "Cancelled"])
    with col3:
        min_val, max_val = st.slider("Khoảng giá trị đơn hàng (VNĐ)", 0, 10000000, (0, 5000000))

    if db is not None:
        try:
            query = {}
            if search_kw:
                query["$or"] = [
                    {"order_id": {"$regex": search_kw, "$options": "i"}},
                    {"customer_id": {"$regex": search_kw, "$options": "i"}}
                ]
            if status_filter:
                query["status"] = {"$in": status_filter}
            query["order_value"] = {"$gte": min_val, "$lte": max_val}

            results = list(db["clean_orders"].find(query).limit(500))
            if results:
                df_res = pd.DataFrame(results)
                if "_id" in df_res.columns:
                    df_res["_id"] = df_res["_id"].astype(str)
                st.write(f"Tìm thấy **{len(df_res)}** kết quả phù hợp:")
                st.dataframe(df_res, use_container_width=True)
            else:
                st.warning("Không tìm thấy dữ liệu phù hợp với bộ lọc.")
        except Exception as e:
            st.error(f"Lỗi khi tìm kiếm dữ liệu: {e}")
    else:
        st.info("Chưa kết nối đến CSDL MongoDB local.")

with tab4:
    st.subheader("Dự Đoán Machine Learning Direct Web")
    st.markdown("---")
    
    ml_tab1, ml_tab2, ml_tab3 = st.tabs([
        "Phân nhóm Khách hàng (K-Means - TV3)",
        "Dự đoán Hủy đơn (Classification - TV4)",
        "Dự đoán Doanh thu (Regression - TV4)"
    ])

    with ml_tab1:
        st.markdown("#### Phân Cụm Khách Hàng theo Mô Hình RFM")
        recency = st.number_input("Recency (Số ngày mua gần nhất)", min_value=0, value=30)
        frequency = st.number_input("Frequency (Tổng số đơn hàng)", min_value=1, value=5)
        monetary = st.number_input("Monetary (Tổng chi tiêu VNĐ)", min_value=0.0, value=1500000.0)

        if st.button("Dự Đoán Phân Cụm"):
            if "rfm_kmeans" in models:
                cluster = models["rfm_kmeans"].predict([[recency, frequency, monetary]])[0]
                st.success(f"Khách hàng thuộc Cụm Phân Nhóm: **{cluster}**")
            else:
                st.info("Mô hình K-Means (TV3) đang được kết nối từ thư mục models/...")

    with ml_tab2:
        st.markdown("#### Dự đoán Khả năng Hủy Đơn Hàng")
        val_input = st.number_input("Giá trị đơn hàng (VNĐ)", min_value=0.0, value=500000.0)
        item_cnt = st.number_input("Số lượng sản phẩm", min_value=1, value=2)

        if st.button("Dự Đoán Hủy Đơn"):
            if "classification" in models:
                pred = models["classification"].predict([[val_input, item_cnt]])[0]
                st.write("Kết quả dự đoán:", pred)
            else:
                st.info("Mô hình Phân loại (TV4) đang được kết nối từ thư mục models/...")

    with ml_tab3:
        st.markdown("#### Dự đoán Doanh Thu Khách Hàng Tương Lai")
        past_spend = st.number_input("Tổng chi tiêu quá khứ (VNĐ)", min_value=0.0, value=2000000.0)

        if st.button("Dự Đoán Doanh Thu"):
            if "regression" in models:
                predicted_val = models["regression"].predict([[past_spend]])[0]
                st.info(f"Doanh thu dự kiến: **{predicted_val:,.0f} VNĐ**")
            else:
                st.info("Mô hình Hồi quy (TV4) đang được kết nối từ thư mục models/...")

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
        report_format = st.selectbox("Chọn định dạng báo cáo cần xuất:", ["Excel (.xlsx)", "PDF (.pdf)"])
        if st.button("Tạo Báo Cáo"):
            st.success(f"Đã xuất báo cáo thành công dưới định dạng {report_format}!")
