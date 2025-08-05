import streamlit as st
import pandas as pd
import plotly.express as px
import re

# -------------------- 页面配置 --------------------
st.set_page_config(
    page_title="五指山猪生化指标",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- 自定义 CSS：让侧边栏蓝色背景、黑色文字 --------------------
custom_css = """
<style>
[data-testid="stSidebar"] {
    background-color: #61afdd;
}
[data-testid="stSidebar"] * {
    color: black !important;
}
[data-testid="stSidebar"] > div:first-child {
    border: none !important;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# -------------------- 上传和加载数据 --------------------
@st.cache_data
def load_data(file) -> pd.DataFrame:
    return pd.read_csv(file)

def extract_numeric_age(age_str):
    if isinstance(age_str, str):
        numbers = re.findall(r"\d+", age_str)
        if numbers:
            try:
                return float(numbers[0])
            except ValueError:
                return None
    elif isinstance(age_str, (int, float)):
        return age_str
    return None

# -------------------- 页面标题 & 侧边栏 --------------------
st.title("五指山猪生化指标")

st.sidebar.title("生化指标")
uploaded_file = st.sidebar.file_uploader("上传 CSV 文件", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    st.sidebar.success("✔ 文件上传成功")

    # 校验 & 清洗数据
    required_cols = ["Age", "Gender"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        st.error(f"CSV 缺少列：{missing}")
    else:
        df["Age"] = df["Age"].apply(extract_numeric_age)
        df = df.dropna(subset=["Age"])
        numeric_cols = df.select_dtypes(include=["int", "float"]).columns

        if len(numeric_cols) == 0:
            st.warning("❗ 未找到可用于图表的数值列")
        else:
            # 筛选条件
            metric = st.sidebar.selectbox("选择生化指标", numeric_cols)
            group_by = st.sidebar.radio("分组方式", ["按性别", "按年龄"])

            unique_ages = sorted(df["Age"].unique())
            selected_ages = st.sidebar.multiselect("选择年龄（月）", unique_ages, default=unique_ages[:3])

            df_filtered = df[df["Age"].isin(selected_ages)]

            if df_filtered.empty:
                st.warning("⚠ 筛选后无数据，请调整条件")
            else:
                st.subheader(f"{metric} 的数据分布（{group_by}）")

                if group_by == "按性别":
                    fig = px.box(
                        df_filtered, x="Gender", y=metric,
                        color="Gender", points="all",
                        title=f"{metric} 按性别的箱线图"
                    )
                else:
                    fig = px.box(
                        df_filtered, x="Age", y=metric,
                        color="Age", points="all",
                        title=f"{metric} 按年龄的箱线图"
                    )

                st.plotly_chart(fig, use_container_width=True)

                st.subheader("详细数据")
                st.dataframe(df_filtered[["Age", "Gender", metric]])
else:
    st.info("📁 请上传 CSV 文件以开始分析。")