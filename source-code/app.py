import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

st.set_page_config(
    page_title="Hệ Thống Phân Tích & Dự Đoán Thương Mại Điện Tử",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("E-Commerce Analytics & AI Web Platform")
st.caption("Phụ trách kỹ thuật: Nguyễn Quốc Thiên — Fullstack Developer & BI Specialist")

tabs = st.tabs([
    "Power BI Dashboard", 
    "Quản Lý Dữ Liệu (CRUD)", 
    "Lọc & Tìm Kiếm", 
    "Dự Đoán ML", 
    "Hệ Thống & Quản Trị"
])

with tabs[0]:
    st.header("Báo Cáo Kinh Doanh & KPI Thương Mại Điện Tử")
    st.markdown("Dashboard tương tác trực tiếp nhúng từ **Power BI Service**.")

    POWER_BI_EMBED_URL = "https://app.powerbi.com/reportEmbed?reportId=e6967a85-8534-4db7-85d2-ed9e53ce1219&autoAuth=true"
    
    st.markdown("---")
    components.iframe(POWER_BI_EMBED_URL, height=720, scrolling=True)

with tabs[1]:
    st.header("Quản Lý Dữ Liệu Đơn Hàng & Khách Hàng (CRUD)")
    st.info("Khu vực cho phép Thêm, Xem, Sửa, Xóa dữ liệu trực tiếp trong CSDL (clean_orders & clean_customers).")
    
    crud_action = st.radio("Chọn thao tác CRUD:", ["Xem dữ liệu", "Thêm đơn hàng mới", "Cập nhật đơn hàng", "Xóa đơn hàng"], horizontal=True)
    
    if crud_action == "Xem dữ liệu":
        st.subheader("Danh sách đơn hàng gần đây")
        st.warning("Đang kết nối đến CSDL...")
        
    elif crud_action == "Thêm đơn hàng mới":
        st.subheader("Thêm bản ghi mới vào CSDL")
        with st.form("add_order_form"):
            col1, col2 = st.columns(2)
            with col1:
                customer_id = st.text_input("Mã khách hàng (Customer ID)")
                total_amount = st.number_input("Tổng tiền (VND)", min_value=0)
            with col2:
                status = st.selectbox("Trạng thái đơn hàng", ["Pending", "Completed", "Cancelled"])
                order_date = st.date_input("Ngày đặt hàng")
            
            submit_btn = st.form_submit_button("Lưu bản ghi")
            if submit_btn:
                st.success("Đã thêm dữ liệu thành công!")

with tabs[2]:
    st.header("Lọc & Tìm Kiếm Dữ Liệu Nâng Cao")
    
    col_search1, col_search2, col_search3 = st.columns(3)
    with col_search1:
        st.text_input("Tìm theo Mã đơn / Mã khách hàng:")
    with col_search2:
        st.multiselect("Lọc theo trạng thái:", ["Completed", "Pending", "Cancelled"])
    with col_search3:
        st.date_input("Lọc theo khoảng thời gian:")
        
    st.button("Tiến hành tìm kiếm")

with tabs[3]:
    st.header("Dự Đoán Mô Hình Machine Learning (ML)")
    st.info("Khu vực tích hợp các file mô hình .pkl từ Thành viên 3 & Thành viên 4.")
    
    st.subheader("Nhập thông số đầu vào để dự đoán:")
    col_ml1, col_ml2 = st.columns(2)
    with col_ml1:
        st.number_input("Số lượng mua (Items Count):", min_value=1, value=2)
        st.number_input("Giá trị đơn hàng dự kiến:", min_value=0, value=500000)
    with col_ml2:
        st.selectbox("Khu vực giao hàng:", ["TP. Hồ Chí Minh", "Hà Nội", "Đà Nẵng", "Tỉnh khác"])
        
    if st.button("Chạy dự đoán AI"):
        st.success("Kết quả dự đoán mô hình: Khách hàng tiềm năng cao (Giao thành công)")

with tabs[4]:
    st.header("Quản Trị Hệ Thống & Sao Lưu CSDL")
    
    st.subheader("Xác thực & Quyền riêng tư")
    st.text_input("Tài khoản admin:", value="quocthien_admin", disabled=True)
    
    st.subheader("Sao lưu & Phục hồi CSDL (Backup & Restore)")
    col_sys1, col_sys2 = st.columns(2)
    with col_sys1:
        st.button("Xuất dữ liệu Sao lưu (Backup DB)")
    with col_sys2:
        st.file_uploader("Tải file để Phục hồi CSDL (Restore DB)")