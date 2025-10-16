import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import matplotlib.pyplot as plt
from utils.token_manager import get_gspread_client
# ===== ตั้งค่า Google Sheet =====
SHEET_NAME = "Contact Information (Responses)"  # เปลี่ยนชื่อไฟล์จริง
import streamlit as st
import altair as alt
from api.fujikaservice_rest_api import fetch_all_products

# เรียกใช้งาน
client = get_gspread_client()

sheet = client.open(SHEET_NAME).sheet1
rows = sheet.get_all_values()

# ===== แปลงเป็น DataFrame =====
df = pd.DataFrame(rows[1:], columns=rows[0])

# ===== ลบ column ซ้ำ =====
df = df.loc[:, ~df.columns.duplicated()]

# ===== เลือกเฉพาะคอลัมน์ A–s (0–19) =====
df_selected = df.iloc[:, :19]

# ===== ทำความสะอาดค่า Model =====
df_selected['Model'] = df_selected['Model'].str.strip()

# ===== นับอันดับ Model =====
model_series = df_selected['Model']
model_counts = model_series.value_counts()
top_models = model_counts.head(3)

# ===== ตั้งค่า Streamlit Dashboard =====
st.set_page_config(page_title="📊 Dashboard แบบสอบถาม", layout="wide")

st.title("📊 Dashboard ข้อมูลจาก Google Form")
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f2f6;  /* สีพื้นหลัง */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ===== ตัวค้นหา Model =====
st.subheader("🔍 ค้นหาอันดับ Model")

st.markdown(
    """
    <style>
    textarea {
        background-color: #ffffff !important;  /* พื้นหลังสีขาว */
        color: #000000 !important;             /* ตัวอักษรสีดำ */
        border: 2px solid #cccccc !important;  /* ขอบสีเทาอ่อน */
        border-radius: 10px !important;
        padding: 0px !important;

    }
    </style>
    """,
    unsafe_allow_html=True
)

search_model = st.text_area("ตรวจสอบ Model" , height=10)


if search_model:
    search_model_clean = search_model.strip()

    if search_model_clean in df_selected['Model'].values:
        rank = model_counts.index.get_loc(search_model_clean) + 1
        count = model_counts[search_model_clean]

        st.success(f"Model {search_model_clean} อยู่ในอันดับที่ {rank} (จำนวนคำสั่งซื้อ {count})")

        with st.expander(f"📄 ดูรายละเอียดของ Model {search_model_clean}"):
            # ดึงข้อมูลของ Model
            model_data = df_selected[df_selected['Model'] == search_model_clean]

            # เลือก column ที่ต้องการ
            columns_to_show = ['Timestamp', 'Address - ที่อยู่', 'ช่องทางการสั่งซื้อ', 
                               'ข้อเสนอแนะ ติชม', 'รู้จักเราทางไหน']
            columns_exist = [col for col in columns_to_show if col in model_data.columns]
            model_data_filtered = model_data[columns_exist]

            # เปลี่ยนชื่อ column ให้เข้าใจง่าย
            new_names = ["เวลา", "ที่อยู่", "ช่องทางการสั่งซื้อ", "ข้อเสนอแนะ ติชม", "รู้จักเราทางไหน"]
            model_data_filtered.columns = new_names[:len(columns_exist)]

            # แสดง DataFrame
            st.dataframe(model_data_filtered)

    else:
        st.warning(f"ไม่พบประวัติ {search_model_clean} ในข้อมูล")

# ===== แสดง 3 อันดับ Model =====
st.subheader("3 อันดับ Model ที่มียอดสั่งซื้อสูงสุด")
st.bar_chart(top_models)

st.markdown("---")
import altair as alt
import streamlit as st

if 'ช่องทางการสั่งซื้อ' in df_selected.columns:
    st.subheader("📊 จัดอันดับยอดคำสั่งซื้อตามช่องทางการสั่งซื้อ")

    # ====== 1. นับจำนวนแต่ละช่องทาง ======
    channel_counts = df_selected['ช่องทางการสั่งซื้อ'].value_counts().reset_index()
    channel_counts.columns = ['ช่องทาง', 'จำนวน']

    # ====== 2. เพิ่มคอลัมน์เปอร์เซ็นต์ ======
    total_orders = channel_counts['จำนวน'].sum()
    channel_counts['เปอร์เซ็นต์'] = (channel_counts['จำนวน'] / total_orders * 100).round(2)

    # ====== 3. หาค่าสูงสุดและต่ำสุด ======
    max_channel = channel_counts.iloc[0]
    min_channel = channel_counts.iloc[-1]

    # ====== 4. สร้างกราฟแท่ง ======
    bars = alt.Chart(channel_counts).mark_bar(size=25).encode(
        x='จำนวน:Q',
        y=alt.Y('ช่องทาง:N', sort='-x'),
        color='ช่องทาง:N',
        tooltip=['ช่องทาง', 'จำนวน', 'เปอร์เซ็นต์']
    )

    # ====== 5. เพิ่มตัวเลขเปอร์เซ็นต์บนแท่ง ======
    text = alt.Chart(channel_counts).mark_text(
        align='left',
        baseline='middle',
        dx=3  # ระยะห่างจากแท่ง
    ).encode(
        x='จำนวน:Q',
        y=alt.Y('ช่องทาง:N', sort='-x'),
        text=alt.Text('เปอร์เซ็นต์:Q', format='.2f')
    )

    # ====== 6. รวมแท่ง + ตัวเลข ======
    chart = (bars + text).properties(height=300)

    st.altair_chart(chart, use_container_width=True)

    # ====== 7. แสดงช่องทางมาก/น้อยสุด ======
    st.markdown(f"""
    <div style="
        padding: 8px 12px; 
        background-color:#d4edda; 
        color:#155724; 
        border-radius:5px; 
        width: fit-content;
        display:inline-block;
        margin-bottom:5px;
        font-size:14px;
    ">
    📈 ยอดคำสั่งซื้อมากที่สุด <b>{max_channel['ช่องทาง']}</b> ({max_channel['จำนวน']} ครั้ง, {max_channel['เปอร์เซ็นต์']}%)
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="
        padding: 8px 12px; 
        background-color:#fff3cd; 
        color:#856404; 
        border-radius:5px; 
        width: fit-content;
        display:inline-block;
        font-size:14px;
    ">
    📉 ยอดคำสั่งซื้อน้อยที่สุด <b>{min_channel['ช่องทาง']}</b> ({min_channel['จำนวน']} ครั้ง, {min_channel['เปอร์เซ็นต์']}%)
    </div>
    """, unsafe_allow_html=True)


st.markdown("----")
st.markdown("---")
if 'รู้จักเราทางไหน' in df_selected.columns:
    st.subheader("📊 ผลการตรวจสอบว่ารู้จักเราจากช่องทางไหน")

    know_counts = df_selected['รู้จักเราทางไหน'].value_counts().reset_index()
    know_counts.columns = ['ช่องทาง', 'จำนวน']

    fig = px.pie(
        know_counts,
        names='ช่องทาง',
        values='จำนวน',
        color='ช่องทาง',
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.4  # ทำเป็น donut chart
    )
    st.plotly_chart(fig, use_container_width=True)



st.subheader("📄 ข้อเสนอแนะ ติชมทั้งหมด")

# กรองเฉพาะแถวที่มีข้อเสนอแนะ
df_feedback = df_selected[
    df_selected['ข้อเสนอแนะ ติชม'].notna() & 
    (df_selected['ข้อเสนอแนะ ติชม'].str.strip() != "") &
    (df_selected['ข้อเสนอแนะ ติชม'].str.strip() != "-")
].copy()  # copy เพื่อไม่ให้ warning

# เพิ่มลำดับ
df_feedback.insert(0, 'ลำดับ', range(1, len(df_feedback)+1))

# แสดง DataFrame พร้อม 'ช่องทางการสั่งซื้อ'
columns_to_show = ['ลำดับ', 'Model', 'ช่องทางการสั่งซื้อ', 'ข้อเสนอแนะ ติชม']
st.dataframe(df_feedback[columns_to_show])

# นับจำนวนข้อเสนอแนะต่อ Model
feedback_counts = df_feedback.groupby('Model').size().reset_index(name='จำนวนข้อเสนอแนะ')
total_feedback = len(df_feedback)
st.markdown(f"จำนวนข้อเสนอแนะทั้งหมด: {total_feedback} รายการ")


st.title("สินค้า FujikaService realtime from website")

# ===== ดึงข้อมูล products =====
@st.cache_data(ttl=600)
def get_products():
    return fetch_all_products()

df_products = get_products()

if df_products.empty:
    st.warning("ไม่มีข้อมูลสินค้า")
    st.stop()

# ===== สินค้าขายดี / ขายไม่ดี =====
st.subheader("💥 สินค้าขายดี / 📉 สินค้าขายไม่ดี")
top_selling = df_products.sort_values(by='rating_count', ascending=False).head(5)
bottom_selling = df_products.sort_values(by='rating_count').head(5)

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 💥 ขายดี 5 อันดับแรก")
    st.dataframe(top_selling[['name', 'rating_count', 'stock_quantity', 'average_rating']])
with col2:
    st.markdown("### 📉 ขายไม่ดี 5 อันดับแรก")
    st.dataframe(bottom_selling[['name', 'rating_count', 'stock_quantity', 'average_rating']])

# ===== สต็อกเหลือ =====
st.subheader("⚠️ สต็อกสินค้าเหลือเท่าไหร่")
low_stock = df_products.sort_values(by='stock_quantity').head(5)
st.dataframe(low_stock[['name', 'stock_quantity']])

# ===== คะแนนรีวิวเฉลี่ย =====
st.subheader("⭐ คะแนนรีวิวเฉลี่ย")
best_rated = df_products.sort_values(by='average_rating', ascending=False).head(5)
st.dataframe(best_rated[['name', 'average_rating', 'rating_count']])

# ===== กราฟขายดีตามจำนวนรีวิว =====
st.subheader("📊 กราฟสินค้าขายดี (Top 10 ตามจำนวนรีวิว)")
top10 = df_products.sort_values(by='rating_count', ascending=False).head(10)
chart = alt.Chart(top10).mark_bar().encode(
    x=alt.X('rating_count:Q', title='จำนวนรีวิว'),
    y=alt.Y('name:N', sort='-x', title='ชื่อสินค้า'),
    color='rating_count:Q',
    tooltip=['name', 'rating_count', 'stock_quantity', 'average_rating']
).properties(height=400)
st.altair_chart(chart, use_container_width=True)
