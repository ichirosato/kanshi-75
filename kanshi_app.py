import streamlit as st
import pandas as pd
import random

# --- 1. ページ設定（スマホ・横並び最適化） ---
st.set_page_config(page_title="汉诗 75 首", layout="centered")

st.markdown("""
    <style>
    /* ボタンを強制的に横並びにする設定 */
    [data-testid="column"] {
        width: 32% !important;
        flex: 1 1 30% !important;
        min-width: 30% !important;
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 5px !important;
    }
    .stButton button { 
        width: 100%; 
        height: 3em; 
        font-size: 0.9rem !important; 
        padding: 0px !important;
        margin-bottom: 0px; 
    }
    /* 出題ボックスを少しコンパクトに */
    .poem-box { 
        background-color: #f8f9fa; 
        padding: 15px; 
        border-radius: 12px; 
        text-align: center; 
        border: 1px solid #e9ecef; 
        margin-bottom: 10px; 
    }
    h1 { text-align: center; font-size: 1.5rem !important; margin-bottom: 0.5rem; }
    h3 { text-align: center; font-size: 1.8rem !important; color: #2E4053; margin: 5px 0; }
    /* 余計な余白を削る */
    .block-container { padding-top: 2rem !important; padding-bottom: 1rem !important; }
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
st.sidebar.header("🎯 学习范围")
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
if selected_author: filtered_df = filtered_df[filtered_author := filtered_df["author"].isin(selected_author)]
if selected_tags:
    def check_tags(c):
        norm = str(c).replace("，", ",").replace("、", ",").replace("·", ",").replace("/", ",")
        tags = [t.strip() for t in norm.split(",") if t.strip()]
        return any(t in tags for t in selected_tags)
    filtered_df = filtered_df[filtered_df["category"].apply(check_tags)]

# --- 5. メイン：出題システム ---
if 'current_poem' not in st.session_state: st.session_state.current_poem = None
if 'hint_level' not in st.session_state: st.session_state.hint_level = 0

if st.button("✨ 随机抽题 (Next)"):
    if not filtered_df.empty:
        st.session_state.current_poem = filtered_df.sample(1).iloc[0]
        st.session_state.hint_level = 0
    else: st.error("没有符合条件的诗。")

if st.session_state.current_poem is not None:
    p = st.session_state.current_poem
    st.markdown('<div class="poem-box">', unsafe_allow_html=True)
    st.markdown(f"### {p['title']}")
    if st.session_state.hint_level >= 1: st.write(f"[{p['dynasty']}] {p['author']}")
    if st.session_state.hint_level >= 2: st.info(p['phrase_1'])
    if st.session_state.hint_level >= 3: st.success(p['full_text'])
    st.markdown('</div>', unsafe_allow_html=True)

    # 3つのボタンを横並びに固定
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💡提示"):
            if st.session_state.hint_level < 3: st.session_state.hint_level += 1
    with col2:
        if st.button("📖答案"): st.session_state.hint_level = 3
    with col3:
        if st.button("✅会了"): st.balloons()

# --- 6. 一覧表示（コンパクト版） ---
st.divider()
st.subheader(f"📚 一览 ({len(filtered_df)}首)")
for index, row in filtered_df.iterrows():
    with st.expander(f"{row['id']}. {row['title']} - {row['author']}"):
        st.write(f"[{row['dynasty']}] {row['category']}")
        st.info(row['full_text'])