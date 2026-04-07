import streamlit as st
import pandas as pd
import random

# 1. ページ設定（タイトルなど）
st.set_page_config(page_title="汉诗背诵助手", layout="wide")
st.title("诵读经典：汉诗 75 首背诵")

# 2. データの読み込み
@st.cache_data
def load_data():
    # CSVを読み込む
    df = pd.read_csv("kanshi_data.csv")
    # カテゴリが空欄(NaN)だとエラーになるので、空の文字を入れておく
    df["category"] = df["category"].fillna("")
    return df

df = load_data()

# 3. サイドバー：フィルター（絞り込み）の設定
st.sidebar.header("设置 (Settings)")

# --- 作者で絞り込むためのリスト作成 ---
authors = sorted(df["author"].unique())
selected_author = st.sidebar.multiselect("按作者筛选 (Filter by Author)", options=authors)

# --- カテゴリー（タグ）をバラバラに分解してリスト化 ---
all_tags = []
for cat in df["category"]:
    if cat:
        # いろいろな区切り記号（，、・· /）をすべて「,」に置き換えてから分割する
        normalized = str(cat).replace("，", ",").replace("、", ",").replace("・", ",").replace("·", ",").replace("/", ",")
        tags = [t.strip() for t in normalized.split(",") if t.strip()]
        all_tags.extend(tags)

# 重複を削ってアルファベット順に並べる
unique_tags = sorted(list(set(all_tags)))
selected_tags = st.sidebar.multiselect("按标签筛选 (Filter by Tags)", options=unique_tags)

# 4. フィルターを実行する（データの中身を絞る）
filtered_df = df.copy()

# 作者が選ばれていたら絞り込む
if selected_author:
    filtered_df = filtered_df[filtered_df["author"].isin(selected_author)]

# タグが選ばれていたら絞り込む（「いずれかのタグが含まれるか」を判定）
if selected_tags:
    def check_tags(cat_str):
        if not cat_str: return False
        # 判定時も同じように記号を統一して分割
        norm = str(cat_str).replace("，", ",").replace("、", ",").replace("・", ",").replace("·", ",").replace("/", ",")
        poem_tags = [t.strip() for t in norm.split(",") if t.strip()]
        # ユーザーが選んだタグが、詩のタグの中に1つでもあるか？
        return any(t in poem_tags for t in selected_tags)
    
    filtered_df = filtered_df[filtered_df["category"].apply(check_tags)]

# 5. メイン画面：ランダム出題部分
st.subheader("🎯 抽题挑战")

# 現在の問題を記憶しておくための仕組み
if 'current_poem' not in st.session_state:
    st.session_state.current_poem = None

# 「換一首」ボタンが押されたらランダムに1つ選ぶ
if st.button("换一首 (Next Poem)"):
    if not filtered_df.empty:
        st.session_state.current_poem = filtered_df.sample(1).iloc[0]
    else:
        st.warning("没有符合条件的诗词。 (No poems match your filter)")

# 問題が表示されている場合の処理
if st.session_state.current_poem is not None:
    poem = st.session_state.current_poem
    
    # 毎回「タイトル」か「第一句」のどちらかをランダムでヒントにする
    hint_type = random.choice(["title", "phrase_1"])
    label = "标题 (Title)" if hint_type == "title" else "第一句 (First Line)"
    
    st.info(f"请根据 **{label}** 回忆全文：")
    st.markdown(f"### {poem[hint_type]}")
    
    # 折りたたみの中に答えを隠す
    with st.expander("点击查看全文 (Show Full Text)"):
        st.write(f"**标题：** {poem['title']}")
        st.write(f"**作者：** [{poem['dynasty']}] {poem['author']}")
        st.write(f"**分类：** {poem['category']}")
        st.success(poem['full_text'])

# 6. 画面下部：全データの一覧表示
st.divider()
st.subheader("📚 汉诗全集 (All Poems)")
# width="stretch" を使うことで画面いっぱいに広がる
st.dataframe(filtered_df, width="stretch")
# おまけ：文字サイズを大きくする設定（一番最後に追加）
st.markdown("""
    <style>
    .stMarkdown h3 {
        font-size: 40px !important;
        font-weight: bold;
        color: #2E4053;
        text-align: center;
    }
    .stAlert p {
        font-size: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)