import streamlit as st
import pandas as pd
import random

# --- 1. ページ設定 ---
st.set_page_config(page_title="汉诗 75 首", layout="centered")

# 【魔法のCSS】これを追加することで、ボタンの隙間と横並びを強制します
st.markdown("""
    <style>
    /* カラムを強制的に横並び(flex)にする */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: space-between !important;
        gap: 5px !important;
    }
    /* 各カラムを3等分にする */
    div[data-testid="column"] {
        flex: 1 1 30% !important;
        min-width: 30% !important;
        max-width: 33% !important;
    }
    /* ボタンの文字サイズと余白をスマホに最適化 */
    .stButton button {
        width: 100% !important;
        font-size: 0.95rem !important;
        padding: 0 !important;
        height: 3.2em !important;
        white-space: nowrap !important;
    }
    /* 問題ボックスをスリムに */
    .poem-box { 
        background-color: #f8f9fa; 
        padding: 15px; 
        border-radius: 12px; 
        text-align: center; 
        border: 1px solid #e9ecef; 
        margin-bottom: 10px;
    }
    h3 { margin: 5px 0 !important; font-size: 1.6rem !important; }
    .block-container { padding: 1.5rem 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("诵读经典：汉詩 75")

# --- 2. データの読み込み ---
@st.cache_data
def load_data():
    df = pd.read_csv("kanshi_data.csv")
    df["category"] = df["category"].fillna("")
    df["level"] = ((df["id"] - 1) // 5) + 1
    return df

df = load_data()

# --- 3. フィルター機能（サイドバー） ---
st.sidebar.header("🎯 范围设定")
max_level = int(df["level"].max())
selected_levels = st.sidebar.multiselect("阶段 (Level)", options=list(range(1, max_level + 1)), default=[1, 2, 3])

with st.sidebar.expander("更多筛选"):
    selected_dynasty = st.multiselect("朝代", options=sorted(df["dynasty"].unique()))
    selected_author = st.multiselect("作者", options=sorted(df["author"].unique()))
    all_tags = []
    for cat in df["category"]:
        normalized = str(cat).replace("，", ",").replace("、", ",").replace("·", ",").replace("/", ",")
        all_tags.extend([t.strip() for t in normalized.split(",") if t.strip()])
    selected_tags = st.multiselect("标签", options=sorted(list(set(all_tags))))

# --- 4. フィルター実行 ---
filtered_df = df.copy()
if selected_levels: filtered_df = filtered_df[filtered_df["level"].isin(selected_levels)]
if selected_dynasty: filtered_df = filtered_df[filtered_df["dynasty"].isin(selected_dynasty)]
if selected_author: filtered_df = filtered_df[filtered_df["author"].isin(selected_author)]
if selected_tags:
    def check_tags(c):
        norm = str(c).replace("，", ",").replace("、", ",").replace("·", ",").replace("/", ",")
        tags = [t.strip() for t in norm.split(",") if t.strip()]
        return any(t in tags for t in selected_tags)
    filtered_df = filtered_df[filtered_df["category"].apply(check_tags)]

# --- 5. 出題システム ---
if 'current_poem' not in st.session_state: st.session_state.current_poem = None
if 'hint_level' not in st.session_state: st.session_state.hint_level = 0

if st.button("✨ 随机抽题 (Next)"):
    if not filtered_df.empty:
        st.session_state.current_poem = filtered_df.sample(1).iloc[0]
        st.session_state.hint_level = 0
    else: st.error("没有符合条件。")

if st.session_state.current_poem is not None:
    p = st.session_state.current_poem
    st.markdown('<div class="poem-box">', unsafe_allow_html=True)
    st.markdown(f"### {p['title']}")
    if st.session_state.hint_level >= 1: st.write(f"[{p['dynasty']}] {p['author']}")
    if st.session_state.hint_level >= 2: st.info(p['phrase_1'])
    if st.session_state.hint_level >= 3: st.success(p['full_text'])
    st.markdown('</div>', unsafe_allow_html=True)

    # 3カラム配置（CSSで強制的に横並び）
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💡提示"):
            if st.session_state.hint_level < 3: st.session_state.hint_level += 1
    with col2:
        if st.button("📖答案"): st.session_state.hint_level = 3
    with col3:
        if st.button("✅会了"): st.balloons()

# --- 6. 一覧表示 ---
st.divider()
st.subheader(f"📚 一览 ({len(filtered_df)}首)")
for index, row in filtered_df.iterrows():
    with st.expander(f"{row['id']}. {row['title']} - {row['author']}"):
        st.write(f"[{row['dynasty']}] {row['category']}")
        st.info(row['full_text'])