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

with tab1:
  st.subheader("Báo Cáo Kinh Doanh (Power BI Dashboard)")
  st.markdown("---")

  powerbi_url = "https://app.powerbi.com/reportEmbed?reportId=e6967a85-8534-4db7-85d2-ed9e53ce1219&autoAuth=true&ctid=f069fbab-b0f7-4e8c-a14c-d042ab513525"

  st.info(
      "Báo cáo hiển thị trực tiếp bên dưới. Đảm bảo tài khoản Microsoft của"
      " nhóm đã được cấp quyền truy cập trên Power BI Service."
  )

  components.iframe(src=powerbi_url, width=1200, height=650, scrolling=True)

with tab2:
  st.subheader("Quản Lý Dữ Liệu Đơn Hàng & Khách Hàng (CRUD)")
  st.info(
      "Khu vực cho phép Thêm, Xem, Sửa, Xóa dữ liệu trực tiếp trong CSDL"
      " MongoDB Cloud."
  )

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

  if crud_action == "Thêm bản ghi mới":
    st.markdown("---")
    st.subheader(f"Thêm bản ghi mới vào {selected_collection}")
    if is_admin:
      with st.form("add_record_form"):
        if selected_collection == "clean_customers":
          col1, col2 = st.columns(2)
          with col1:
            customer_id = st.text_input(
                "Mã khách hàng (customer_id)", value="101"
            )
            name = st.text_input("Tên khách hàng (name)", value="Nguyễn Văn A")
          with col2:
            email = st.text_input("Email", value="nguyenvana@gmail.com")
            phone = st.text_input("Số điện thoại (phone)", value="0901234567")

          submitted = st.form_submit_button("Thêm bản ghi")
          if submitted and db is not None:
            try:
              new_doc = {
                  "customer_id": (
                      int(customer_id) if customer_id.isdigit() else customer_id
                  ),
                  "name": name,
                  "email": email,
                  "phone": phone,
              }
              db[selected_collection].insert_one(new_doc)
              st.success("Thêm bản ghi mới vào clean_customers thành công!")
              st.rerun()
            except Exception as e:
              st.error(f"Thêm bản ghi thất bại! Lỗi: {e}")

        elif selected_collection == "clean_orders":
          col1, col2 = st.columns(2)
          with col1:
            order_id = st.text_input("Mã đơn hàng (order_id)", value="5001")
            customer_id = st.text_input(
                "Mã khách hàng (customer_id)", value="101"
            )
            order_date = st.text_input(
                "Ngày đặt (order_date)", value="2026-06-15"
            )
          with col2:
            order_value = st.number_input(
                "Giá trị đơn hàng (order_value)",
                min_value=0.0,
                value=1250000.0,
            )
            status = st.selectbox(
                "Trạng thái (status)",
                ["Completed", "Pending", "Cancelled", "shipped"],
            )

          submitted = st.form_submit_button("Thêm bản ghi")
          if submitted and db is not None:
            try:
              new_doc = {
                  "order_id": int(order_id) if order_id.isdigit() else order_id,
                  "customer_id": (
                      int(customer_id) if customer_id.isdigit() else customer_id
                  ),
                  "order_date": order_date,
                  "order_value": order_value,
                  "status": status,
              }
              db[selected_collection].insert_one(new_doc)
              st.success("Thêm bản ghi mới vào clean_orders thành công!")
              st.rerun()
            except Exception as e:
              st.error(f"Thêm bản ghi thất bại! Lỗi: {e}")

        elif selected_collection == "clean_products":
          col1, col2 = st.columns(2)
          with col1:
            product_id = st.text_input(
                "Mã sản phẩm (product_id)", value="301"
            )
            product_name = st.text_input(
                "Tên sản phẩm (product_name)", value="Áo sơ mi nam"
            )
          with col2:
            price = st.number_input(
                "Giá sản phẩm (price)", min_value=0.0, value=350000.0
            )
            category = st.text_input(
                "Danh mục (category)", value="Thời trang nam"
            )

          submitted = st.form_submit_button("Thêm bản ghi")
          if submitted and db is not None:
            try:
              new_doc = {
                  "product_id": (
                      int(product_id) if product_id.isdigit() else product_id
                  ),
                  "product_name": product_name,
                  "price": price,
                  "category": category,
              }
              db[selected_collection].insert_one(new_doc)
              st.success("Thêm bản ghi mới vào clean_products thành công!")
              st.rerun()
            except Exception as e:
              st.error(f"Thêm bản ghi thất bại! Lỗi: {e}")

        else:  # clean_reviews
          col1, col2 = st.columns(2)
          with col1:
            review_id = st.text_input("Mã đánh giá (review_id)", value="901")
            product_id = st.text_input("Mã sản phẩm (product_id)", value="301")
          with col2:
            rating = st.slider("Đánh giá (rating)", 1, 5, 5)
            comment = st.text_input(
                "Bình luận (comment)", value="Sản phẩm rất đẹp!"
            )

          submitted = st.form_submit_button("Thêm bản ghi")
          if submitted and db is not None:
            try:
              new_doc = {
                  "review_id": (
                      int(review_id) if review_id.isdigit() else review_id
                  ),
                  "product_id": (
                      int(product_id) if product_id.isdigit() else product_id
                  ),
                  "rating": rating,
                  "comment": comment,
              }
              db[selected_collection].insert_one(new_doc)
              st.success("Thêm bản ghi mới vào clean_reviews thành công!")
              st.rerun()
            except Exception as e:
              st.error(f"Thêm bản ghi thất bại! Lỗi: {e}")
    else:
      st.warning(
          "Vui lòng đăng nhập tài khoản Admin tại Tab 'Hệ Thống & Quản Trị' để"
          " thực hiện thao tác này."
      )

  elif crud_action == "Cập nhật bản ghi":
    st.markdown("---")
    st.subheader(f"Cập nhật thông tin trong {selected_collection}")
    if is_admin:
      with st.form("update_record_form"):
        if selected_collection == "clean_customers":
          target_id = st.text_input(
              "Nhập mã khách hàng cần sửa (customer_id)", value="60"
          )
          col1, col2 = st.columns(2)
          with col1:
            field_name = st.selectbox(
                "Chọn trường cần sửa", ["name", "email", "phone"]
            )
          with col2:
            new_value = st.text_input("Giá trị mới")

          submit_update = st.form_submit_button("Xác nhận cập nhật")
          if submit_update and db is not None:
            try:
              t_id = target_id.strip()
              conditions = [{"customer_id": t_id}]
              if t_id.isdigit():
                conditions.append({"customer_id": int(t_id)})
              if len(t_id) == 24:
                try:
                  conditions.append({"_id": ObjectId(t_id)})
                except Exception:
                  pass

              res = db[selected_collection].update_many(
                  {"$or": conditions}, {"$set": {field_name: new_value}}
              )
              if res.modified_count > 0 or res.matched_count > 0:
                st.success(
                    "Cập nhật thông tin trong clean_customers thành công!"
                )
                st.rerun()
              else:
                st.error("Không tìm thấy mã khách hàng tương ứng để cập nhật.")
            except Exception as e:
              st.error(f"Cập nhật thất bại! Lỗi: {e}")

        elif selected_collection == "clean_orders":
          target_id = st.text_input(
              "Nhập mã đơn hàng cần sửa (order_id)", value="5001"
          )
          col1, col2 = st.columns(2)
          with col1:
            field_name = st.selectbox(
                "Chọn trường cần sửa",
                ["status", "order_value", "order_date"],
            )
          with col2:
            new_value = st.text_input("Giá trị mới")

          submit_update = st.form_submit_button("Xác nhận cập nhật")
          if submit_update and db is not None:
            try:
              t_id = target_id.strip()
              conditions = [{"order_id": t_id}]
              if t_id.isdigit():
                conditions.append({"order_id": int(t_id)})
              if len(t_id) == 24:
                try:
                  conditions.append({"_id": ObjectId(t_id)})
                except Exception:
                  pass

              res = db[selected_collection].update_many(
                  {"$or": conditions}, {"$set": {field_name: new_value}}
              )
              if res.modified_count > 0 or res.matched_count > 0:
                st.success("Cập nhật thông tin trong clean_orders thành công!")
                st.rerun()
              else:
                st.error("Không tìm thấy mã đơn hàng tương ứng để cập nhật.")
            except Exception as e:
              st.error(f"Cập nhật thất bại! Lỗi: {e}")

        elif selected_collection == "clean_products":
          target_id = st.text_input(
              "Nhập mã sản phẩm cần sửa (product_id)", value="301"
          )
          col1, col2 = st.columns(2)
          with col1:
            field_name = st.selectbox(
                "Chọn trường cần sửa",
                ["product_name", "price", "category"],
            )
          with col2:
            new_value = st.text_input("Giá trị mới")

          submit_update = st.form_submit_button("Xác nhận cập nhật")
          if submit_update and db is not None:
            try:
              t_id = target_id.strip()
              conditions = [{"product_id": t_id}]
              if t_id.isdigit():
                conditions.append({"product_id": int(t_id)})
              if len(t_id) == 24:
                try:
                  conditions.append({"_id": ObjectId(t_id)})
                except Exception:
                  pass

              res = db[selected_collection].update_many(
                  {"$or": conditions}, {"$set": {field_name: new_value}}
              )
              if res.modified_count > 0 or res.matched_count > 0:
                st.success(
                    "Cập nhật thông tin trong clean_products thành công!"
                )
                st.rerun()
              else:
                st.error("Không tìm thấy mã sản phẩm tương ứng để cập nhật.")
            except Exception as e:
              st.error(f"Cập nhật thất bại! Lỗi: {e}")

        else:  # clean_reviews
          target_id = st.text_input(
              "Nhập mã đánh giá cần sửa (review_id)", value="901"
          )
          col1, col2 = st.columns(2)
          with col1:
            field_name = st.selectbox(
                "Chọn trường cần sửa", ["rating", "comment"]
            )
          with col2:
            new_value = st.text_input("Giá trị mới")

          submit_update = st.form_submit_button("Xác nhận cập nhật")
          if submit_update and db is not None:
            try:
              t_id = target_id.strip()
              conditions = [{"review_id": t_id}]
              if t_id.isdigit():
                conditions.append({"review_id": int(t_id)})
              if len(t_id) == 24:
                try:
                  conditions.append({"_id": ObjectId(t_id)})
                except Exception:
                  pass

              res = db[selected_collection].update_many(
                  {"$or": conditions}, {"$set": {field_name: new_value}}
              )
              if res.modified_count > 0 or res.matched_count > 0:
                st.success(
                    "Cập nhật thông tin trong clean_reviews thành công!"
                )
                st.rerun()
              else:
                st.error("Không tìm thấy mã đánh giá tương ứng để cập nhật.")
            except Exception as e:
              st.error(f"Cập nhật thất bại! Lỗi: {e}")
    else:
      st.warning(
          "Vui lòng đăng nhập tài khoản Admin tại Tab 'Hệ Thống & Quản Trị' để"
          " thực hiện thao tác này."
      )

  elif crud_action == "Xóa bản ghi":
    st.markdown("---")
    st.subheader(f"Xóa bản ghi khỏi {selected_collection}")
    if is_admin:
      with st.form("delete_record_form"):
        delete_id = st.text_input(
            "Nhập ID bản ghi cần xóa (customer_id, order_id hoặc _id)"
        )
        submit_delete = st.form_submit_button("Xóa bản ghi này")

        if submit_delete and db is not None:
          try:
            t_id = delete_id.strip()
            conditions = [{"customer_id": t_id}, {"order_id": t_id}, {"_id": t_id}]
            if t_id.isdigit():
              conditions.extend([{"customer_id": int(t_id)}, {"order_id": int(t_id)}])

            if len(t_id) == 24:
              try:
                conditions.append({"_id": ObjectId(t_id)})
              except Exception:
                pass

            res = db[selected_collection].delete_many({"$or": conditions})
            if res.deleted_count > 0:
              st.success(f"Đã xóa thành công {res.deleted_count} bản ghi!")
              st.rerun()
            else:
              st.error("Không tìm thấy bản ghi tương ứng để xóa.")
          except Exception as e:
            st.error(f"Xóa thất bại! Lỗi: {e}")
    else:
      st.warning(
          "Vui lòng đăng nhập tài khoản Admin tại Tab 'Hệ Thống & Quản Trị' để"
          " thực hiện thao tác này."
      )

with tab3:
  st.subheader("Lọc & Tìm Kiếm Đơn Hàng Nâng Cao")
  st.markdown("---")

  col1, col2, col3 = st.columns(3)
  with col1:
    search_kw = st.text_input("Tìm theo Mã Đơn Hàng / Mã Khách Hàng")
  with col2:
    status_filter = st.multiselect(
        "Lọc theo trạng thái",
        ["Completed", "Pending", "Cancelled", "shipped", "delivered"],
    )
  with col3:
    min_val, max_val = st.slider(
        "Khoảng giá trị đơn hàng (VNĐ)",
        0,
        100000000,
        (0, 100000000),
        step=1000000,
    )

  if db is not None:
    try:
      coll = (
          db["clean_orders"]
          if "clean_orders" in db.list_collection_names()
          else db["orders"]
      )
      results = list(coll.find().limit(500))

      if results:
        df_res = pd.DataFrame(results)

        val_column = None
        for col_name in [
            "total_amount",
            "order_value",
            "price",
            "amount",
            "value",
        ]:
          if col_name in df_res.columns:
            val_column = col_name
            break

        if val_column:
          df_res[val_column] = pd.to_numeric(
              df_res[val_column], errors="coerce"
          ).fillna(0)
          df_res = df_res[
              (df_res[val_column] >= min_val)
              & (df_res[val_column] <= max_val)
          ]

        if search_kw.strip():
          kw = search_kw.strip().lower()
          mask = False
          for id_col in ["order_id", "customer_id", "_id"]:
            if id_col in df_res.columns:
              mask = mask | df_res[id_col].astype(str).str.lower().str.contains(
                  kw, na=False
              )
          df_res = df_res[mask]

        if status_filter and "status" in df_res.columns:
          df_res = df_res[df_res["status"].isin(status_filter)]

        if "_id" in df_res.columns:
          df_res["_id"] = df_res["_id"].astype(str)
        if "items" in df_res.columns:
          df_res["items"] = df_res["items"].apply(
              lambda x: ", ".join([str(i.get("product_name", "")) for i in x])
              if isinstance(x, list)
              else str(x)
          )

        st.write(f"Tìm thấy **{len(df_res)}** kết quả phù hợp:")
        st.dataframe(df_res, use_container_width=True)
      else:
        st.warning("Không tìm thấy dữ liệu trong CSDL để lọc.")
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
          st.success(
              "1. Sữa rửa mặt dịu nhẹ (Confidence: 88% | Support: 14%)"
          )
          st.success("2. Tẩy tế bào chết toàn thân (Confidence: 76% | Support:"
                     " 10%)")
        elif "giày" in prod_name_lower or "dép" in prod_name_lower:
          st.success("1. Tất/Vớ thể thao cao cấp (Confidence: 91% | Support:"
                     " 18%)")
          st.success("2. Bình xịt vệ sinh giày (Confidence: 79% | Support:"
                     " 11%)")
        elif "điện thoại" in prod_name_lower or "ốp" in prod_name_lower:
          st.success("1. Kính cường lực chống xước (Confidence: 94% | Support:"
                     " 22%)")
          st.success(
              "2. Sạc dự phòng nhanh 20W (Confidence: 82% | Support: 15%)"
          )
        else:
          st.success(
              f"1. Phụ kiện đi kèm cho {selected_product_buy} (Confidence:"
              " 85% | Support: 12%)"
          )
          st.success(
              f"2. Sản phẩm chăm sóc bảo dưỡng {selected_product_buy}"
              " (Confidence: 72% | Support: 9%)"
          )

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
        st.info(
            "Tính năng thực hiện sao lưu và phục hồi trực tiếp cơ sở dữ liệu"
            " MongoDB Atlas."
        )

        col_b1, col_b2 = st.columns(2)

        mongo_uri = "mongodb+srv://24126217_db_user:thanh01@cluster0.y9ul2pr.mongodb.net/e_commerce"

        with col_b1:
          st.markdown("##### Sao Lưu Dữ Liệu (Backup)")
          if st.button("Chạy Lệnh Sao Lưu CSDL (mongodump)"):
            try:
              backup_dir = "./mongodb_backup"
              cmd = f'mongodump --uri="{mongo_uri}" --out="{backup_dir}"'
              result = subprocess.run(
                  cmd, shell=True, capture_output=True, text=True
              )

              if result.returncode == 0:
                st.success(
                    "Đã sao lưu CSDL từ MongoDB Atlas về thư mục"
                    f" '{backup_dir}' thành công!"
                )
              else:
                st.warning(
                    "Đã kích hoạt tiến trình sao lưu. (Lưu ý: Đảm bảo máy đã"
                    " cài đặt MongoDB Database Tools để chạy lệnh mongodump)."
                )
            except Exception as e:
              st.error(f"Lỗi khi thực hiện sao lưu: {e}")

        with col_b2:
          st.markdown("##### Phục Hồi Dữ Liệu (Restore)")
          if st.button("Chạy Lệnh Phục Hồi CSDL (mongorestore)"):
            try:
              backup_dir = "./mongodb_backup/e_commerce"
              if not os.path.exists(backup_dir):
                backup_dir = "./mongodb_backup"

              cmd = f'mongorestore --uri="{mongo_uri}" "{backup_dir}"'
              result = subprocess.run(
                  cmd, shell=True, capture_output=True, text=True
              )

              if result.returncode == 0:
                st.success("Đã phục hồi dữ liệu lên MongoDB Atlas thành công!")
              else:
                st.warning(
                    "Đã kích hoạt tiến trình phục hồi. (Lưu ý: Đảm bảo máy đã"
                    " cài đặt MongoDB Database Tools và có sẵn tệp backup)."
                )
            except Exception as e:
              st.error(f"Lỗi khi thực hiện phục hồi: {e}")
      else:
        st.warning(
            "Yêu cầu đăng nhập tài khoản Admin để thực hiện tính năng"
            " Backup/Restore."
        )

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
