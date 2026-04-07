import streamlit as st
import pandas as pd
import random

# --- 1. ページ設定 ---
st.set_page_config(page_title="汉诗 75 首", layout="centered")

st.markdown("""
    <style>
    /* ボタンの共通スタイル */
    .stButton button { width: 100%; height: 3.5em; font-size: 1.1rem !important; margin-bottom: 8px; border-radius: 8px; }
    /* 出題ボックスのスタイル */
    .poem-box { background-color: #f8f9fa; padding: 25px; border-radius: 15px; text-align: center; border: 1px solid #e9ecef; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    h1 { text-align: center; font-size: 1.8rem !important; color: #1B2631; }
    h3 { text-align: center; font-size: 2rem !important; color: #2E4053; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("诵读经典：汉诗 75 首")

# --- 2. データの読み込み ---
@st.cache_data
def load_data():
    df = pd.read_csv("kanshi_data.csv")
    df["category"] = df["category"].fillna("")
    df["level"] = ((df["id"] - 1) // 5) + 1
    return df

df = load_data()

# --- 3. サイドバー ---
st.sidebar.header("🎯 学习范围 (Range)")
max_level = int(df["level"].max())
selected_levels = st.sidebar.multiselect(
    "选择阶段 (Level)", 
    options=list(range(1, max_level + 1)),
    default=[1, 2, 3]
)

with st.sidebar.expander("更多筛选 (More Filters)"):
    dynasties = sorted(df["dynasty"].unique())
    selected_dynasty = st.multiselect("按朝代 (Dynasty)", options=dynasties)
    authors = sorted(df["author"].unique())
    selected_author = st.multiselect("按作者 (Author)", options=authors)
    all_tags = []
    for cat in df["category"]:
        normalized = str(cat).replace("，", ",").replace("、", ",").replace("·", ",").replace("/", ",")
        all_tags.extend([t.strip() for t in normalized.split(",") if t.strip()])
    unique_tags = sorted(list(set(all_tags)))
    selected_tags = st.multiselect("按标签 (Tags)", options=unique_tags)

# --- 4. フィルター実行 ---
filtered_df = df.copy()
if selected_levels:
    filtered_df = filtered_df[filtered_df["level"].isin(selected_levels)]
if selected_dynasty:
    filtered_df = filtered_df[filtered_df["dynasty"].isin(selected_dynasty)]
if selected_author:
    filtered_df = filtered_df[filtered_df["author"].isin(selected_author)]
if selected_tags:
    def check_tags(cat_str):
        norm = str(cat_str).replace("，", ",").replace("、", ",").replace("·", ",").replace("/", ",")
        poem_tags = [t.strip() for t in norm.split(",") if t.strip()]
        return any(t in poem_tags for t in selected_tags)
    filtered_df = filtered_df[filtered_df["category"].apply(check_tags)]

# --- 5. メイン：出題システム ---
if 'current_poem' not in st.session_state:
    st.session_state.current_poem = None
if 'hint_level' not in st.session_state:
    st.session_state.hint_level = 0

# 次の問題を出すボタン
if st.button("✨ 随机抽题 (Next Poem)"):
    if not filtered_df.empty:
        st.session_state.current_poem = filtered_df.sample(1).iloc[0]
        st.session_state.hint_level = 0
    else:
        st.error("没有符合条件的诗。")

# 問題表示
if st.session_state.current_poem is not None:
    p = st.session_state.current_poem
    st.markdown('<div class="poem-box">', unsafe_allow_html=True)
    st.markdown(f"### {p['title']}")
    
    # ヒント表示（ヒント1：作者、2：第一句、3：全文）
    if st.session_state.hint_level >= 1:
        st.write(f"作者：[{p['dynasty']}] {p['author']}")
    if st.session_state.hint_level >= 2:
        st.info(f"第一句：{p['phrase_1']}")
    if st.session_state.hint_level >= 3:
        st.success(f"全文：\n\n{p['full_text']}")
    st.markdown('</div>', unsafe_allow_html=True)

    # 操作ボタン：3列に配置（ヒント / 答え / 会了）
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💡 提示"):
            if st.session_state.hint_level < 3:
                st.session_state.hint_level += 1
    with col2:
        if st.button("📖 答案"):
            st.session_state.hint_level = 3 # 一気に全文表示
    with col3:
        if st.button("✅ 会了"):
            st.balloons()

# --- 6. 一覧表示 ---
st.divider()
st.subheader(f"📚 当前范围内共有 {len(filtered_df)} 首")
if filtered_df.empty:
    st.write("请在侧辺栏选择学习范围。")
else:
    for index, row in filtered_df.iterrows():
        with st.expander(f"{row['id']}. {row['title']} / {row['author']}"):
            st.write(f"**朝代：** {row['dynasty']}  |  **分类：** {row['category']}")
            st.info(row['full_text'])