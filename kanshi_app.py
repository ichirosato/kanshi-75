import streamlit as st
import pandas as pd
import random

# --- 1. ページ設定（スマホ最適化） ---
st.set_page_config(page_title="汉诗 75 首", layout="centered") # centeredでスマホで見やすく

# 文字サイズを大きく、ボタンを押しやすくする魔法のCSS
st.markdown("""
    <style>
    .stButton button { width: 100%; height: 3em; font-size: 1.2rem !important; margin-bottom: 10px; }
    .poem-box { background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
    .hint-text { color: #555; font-size: 0.9rem; margin-top: 5px; }
    h1 { text-align: center; font-size: 1.8rem !important; }
    h3 { text-align: center; font-size: 2.2rem !important; color: #2E4053; }
    /* スマホで表がはみ出さないように隠す設定 */
    .stDataFrame { font-size: 0.8rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("诵读经典：汉诗 75 首")

# --- 2. データの読み込み ---
@st.cache_data
def load_data():
    df = pd.read_csv("kanshi_data.csv")
    df["category"] = df["category"].fillna("")
    # 5首ずつの「段階（Level）」を自動計算
    df["level"] = ((df["id"] - 1) // 5) + 1
    return df

df = load_data()

# --- 3. サイドバー：強力な絞り込み機能 ---
st.sidebar.header("🎯 学习范围 (Range)")

# ① 段階（レベル）で絞り込む
max_level = int(df["level"].max())
selected_levels = st.sidebar.multiselect(
    "选择阶段 (1-15阶段)", 
    options=list(range(1, max_level + 1)),
    default=[1, 2, 3], # 最初は1-3段階を選択状態に
    help="5首ずつ区切った学習ユニットです"
)

# ② カテゴリ・作者・時代で絞り込む（アコーディオンでスッキリ）
with st.sidebar.expander("更多筛选 (More Filters)"):
    # 時代
    dynasties = sorted(df["dynasty"].unique())
    selected_dynasty = multiselect_dynasty = st.multiselect("按朝代 (Dynasty)", options=dynasties)
    
    # 作者
    authors = sorted(df["author"].unique())
    selected_author = st.multiselect("按作者 (Author)", options=authors)
    
    # タグ
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
    st.session_state.hint_level = 0 # 0:題名のみ, 1:作者追加, 2:第一句追加...

st.write(f"当前范围内共有 **{len(filtered_df)}** 首诗")

if st.button("✨ 随机抽题 (Next Poem)"):
    if not filtered_df.empty:
        st.session_state.current_poem = filtered_df.sample(1).iloc[0]
        st.session_state.hint_level = 0 # ヒントをリセット
    else:
        st.error("没有符合条件的诗。")

# 問題表示エリア
if st.session_state.current_poem is not None:
    p = st.session_state.current_poem
    
    st.markdown('<div class="poem-box">', unsafe_allow_html=True)
    
    # ヒント段階に応じた表示
    st.markdown(f"### {p['title']}") # 常にタイトルは表示
    
    if st.session_state.hint_level >= 1:
        st.write(f"作者：[{p['dynasty']}] {p['author']}")
    
    if st.session_state.hint_level >= 2:
        st.info(f"第一句：{p['phrase_1']}")
        
    if st.session_state.hint_level >= 3:
        st.success(f"全文：\n\n{p['full_text']}")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # ヒントボタン（スマホで押しやすいよう並べる）
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💡 提示 (Hint)"):
            if st.session_state.hint_level < 3:
                st.session_state.hint_level += 1
    with col2:
        if st.button("✅ 会了！ (Mastered)"):
            st.balloons() # お祝いの風船

# --- 6. 一覧表示（アコーディオンに隠してスマホで見やすく） ---
with st.expander("📚 查看诗词一览 (View List)"):
    st.table(filtered_df[["id", "title", "author", "category"]]) # シンプルな表に

st.divider()
st.caption("小学部分汉诗75首学习助手")