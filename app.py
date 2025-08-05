import streamlit as st
import pandas as pd
import plotly.express as px
import re

# -------------------- 页面配置 --------------------
st.set_page_config(
    page_title="五指山猪生化指标与生物信息平台",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- 自定义 CSS：让侧边栏背景保持蓝色，文字改为黑色 --------------------
custom_css = """
<style>
/* 1. 整体侧边栏区域 */
[data-testid="stSidebar"] {
    background-color: #61afdd;  /* 深蓝色背景 */
}

/* 2. 侧边栏内所有元素的文字设为黑色 */
[data-testid="stSidebar"] * {
    color: black !important;   /* 文字改为黑色 */
}

/*
   如果有需要，可以注释掉下面这行，
   避免对某些按钮或单选框选中态产生视觉冲突
   （可根据需要精调）
*/

/* 3. 去掉侧边栏与主区之间默认的分割线(可选) */
[data-testid="stSidebar"] > div:first-child {
    border: none !important;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 如果仅需改文字颜色，可删除其它 CSS 片段，这里保留以示完整

# -------------------- 使用 Session State 进行导航管理 --------------------
if "current_page" not in st.session_state:
    st.session_state.current_page = "首页"  # 默认首页


@st.cache_data
def load_data(file) -> pd.DataFrame:
    """读取 CSV，并返回 DataFrame。使用缓存提高性能。"""
    return pd.read_csv(file)


def extract_numeric_age(age_str):
    if isinstance(age_str, str):
        import re
        numbers = re.findall(r"\d+", age_str)
        if numbers:
            try:
                return float(numbers[0])
            except ValueError:
                return None
    elif isinstance(age_str, (int, float)):
        return age_str
    return None


def show_home():
    st.title("五指山猪生物信息平台 - 首页")
    st.markdown("""
    欢迎访问 **五指山猪生物信息平台**！

    **本平台提供**：
    - **生化指标**：五指山猪生化指标数据可视化
    - **心脏单细胞图谱**
    - **肾脏单细胞图谱**
    - **团队介绍**
    - **联系我们**

    **请通过左侧导航栏切换到各个功能页面**。
    """)


def show_biochemistry():
    st.title("五指山猪生化指标")
    st.sidebar.subheader("上传 CSV 文件")
    uploaded_file = st.sidebar.file_uploader("选择 CSV 文件", type=["csv"])
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        st.sidebar.success("✔文件上传成功！")

        required_cols = ["Age", "Gender"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.error(f"CSV 缺少必要列：{missing_cols}")
            return

        df["Age"] = df["Age"].apply(extract_numeric_age)
        df = df.dropna(subset=["Age"])
        numeric_cols = df.select_dtypes(include=["int", "float"]).columns
        if len(numeric_cols) == 0:
            st.warning("没有检测到数值型列，无法可视化。")
            return

        st.sidebar.subheader("数据筛选")
        selected_metric = st.sidebar.selectbox("选择生化指标", numeric_cols)
        group_by = st.sidebar.radio("选择分组方式", ["按性别", "按年龄"])

        unique_ages = sorted(df["Age"].unique())
        default_ages = unique_ages[:3] if len(unique_ages) >= 3 else unique_ages
        selected_ages = st.sidebar.multiselect("选择年龄", unique_ages, default=default_ages)

        df_filtered = df[df["Age"].isin(selected_ages)]
        if df_filtered.empty:
            st.warning("筛选后无数据，请调整筛选条件。")
            return

        st.subheader(f" {selected_metric} 的数据分布（{group_by}）")
        if group_by == "按性别":
            fig = px.box(
                df_filtered, x="Gender", y=selected_metric,
                color="Gender", points="all",
                title=f"{selected_metric} 按性别的箱线图"
            )
        else:
            fig = px.box(
                df_filtered, x="Age", y=selected_metric,
                color="Age", points="all",
                title=f"{selected_metric} 按年龄的箱线图"
            )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("详细数据")
        st.dataframe(df_filtered[["Age", "Gender", selected_metric]])
    else:
        st.warning("请上传 CSV 文件以进行可视化。")


def show_heart():
    st.title("五指山猪心脏单细胞图谱")
    st.markdown("此页面用于展示五指山猪心脏单细胞测序数据，目前数据尚未上传。")


def show_kidney():
    st.title("五指山猪肾脏单细胞图谱")
    st.markdown("此页面用于展示五指山猪肾脏单细胞测序数据，目前数据尚未上传。")


def show_team():
    st.title("团队介绍")
    st.markdown("""
    我们的研究团队专注于 **五指山猪的生物信息学研究**，主要涵盖：

    - 生化指标数据分析
    - 单细胞测序研究
    - 基因组学 & 免疫学

    **我们的目标**：
    - 通过数据分析，解析五指山猪的生物学特性
    - 为未来的医学 & 农业研究提供基础数据

    **🤝 欢迎合作 & 交流！**
    """)


def show_contact():
    st.title("联系我们")
    st.markdown("""
    **邮箱**：example@university.edu  
    **研究机构**：某大学生命科学学院  
    **电话**：+86-1234-5678  
    **官网**：[www.example.com](https://www.example.com)
    """)


# -------------------- 左侧导航 --------------------
nav_pages = ["首页", "生化指标", "心脏单细胞图谱", "肾脏单细胞图谱", "团队介绍", "联系我们"]
st.sidebar.title("功能导航")
selected_page = st.sidebar.radio("请选择页面", nav_pages,
                                 index=nav_pages.index(st.session_state.current_page))
if selected_page != st.session_state.current_page:
    st.session_state.current_page = selected_page


# -------------------- 主体逻辑 --------------------
def main():
    if st.session_state.current_page == "首页":
        show_home()
    elif st.session_state.current_page == "生化指标":
        show_biochemistry()
    elif st.session_state.current_page == "心脏单细胞图谱":
        show_heart()
    elif st.session_state.current_page == "肾脏单细胞图谱":
        show_kidney()
    elif st.session_state.current_page == "团队介绍":
        show_team()
    elif st.session_state.current_page == "联系我们":
        show_contact()


if __name__ == "__main__":
    main()