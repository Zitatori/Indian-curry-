import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.set_page_config(page_title="Spice Shelf → Indian Dishes", page_icon="🫙", layout="wide")

DATA_DIR = Path("data")
RECIPES_CSV = DATA_DIR / "recipes.csv"
SPICES_CSV = DATA_DIR / "spices.csv"

SHELF_COLS = 6
CARD_COLS = 3

@st.cache_data
def load_data():
    if not RECIPES_CSV.exists() or not SPICES_CSV.exists():
        st.error("❌ データファイルが見つかりません。\n`data/recipes.csv` と `data/spices.csv` を配置してください。")
        st.stop()

    recipes = pd.read_csv(RECIPES_CSV)
    recipes["spices"] = recipes["spices"].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
    spices = pd.read_csv(SPICES_CSV)
    return recipes, spices

def jar_card(spice_name, alias="", color="#eee", key=""):
    st.markdown(f"""
    <div style="
        border-radius: 18px; padding: 10px 10px 6px 10px;
        border: 1px solid #e6e6e6; background: #fff;
        box-shadow: 0 1px 3px rgba(0,0,0,.05); text-align:center;
        ">
        <div style="font-size: 42px;">🫙</div>
        <div style="font-weight:700; margin-top:6px;">{spice_name}</div>
        <div style="font-size:12px; color:#666;">{alias}</div>
        <div style="height:10px; border-radius:5px; margin:8px 0; background:{color};"></div>
    </div>
    """, unsafe_allow_html=True)
    return st.button(f"＋ {spice_name} を入れる", key=key, use_container_width=True)

def tag(text, bg):
    st.markdown(
        f'<span style="display:inline-block;background:{bg};border-radius:6px;padding:4px 8px;margin-right:6px;font-size:12px;">{text}</span>',
        unsafe_allow_html=True,
    )

def main():
    recipes, spices = load_data()

    if "basket" not in st.session_state:
        st.session_state.basket = []
    if "show_results" not in st.session_state:
        st.session_state.show_results = False

    st.title("🫙 Spice Shelf → Indian Dishes")
    st.caption("棚からスパイスを選んで、自分の入れ物に入れよう。選んだスパイスを使う代表料理を表示します。")

    shelf, basket = st.columns([2, 1])

    # ---- スパイス棚 ----
    with shelf:
        st.subheader("スパイス棚")
        grid = st.columns(SHELF_COLS)
        for i, row in spices.reset_index(drop=True).iterrows():
            with grid[i % SHELF_COLS]:
                added = jar_card(row["spice_name"], row.get("alias",""), row.get("color","#eee"), key=f"jar_{i}")
                if added:
                    s = row["spice_name"]
                    if s not in st.session_state.basket:
                        st.session_state.basket.append(s)
                        st.toast(f"Added: {s}", icon="✅")

    # ---- 自分の入れ物 ----
    with basket:
        st.subheader("自分の入れ物")
        if st.session_state.basket:
            st.write(", ".join(st.session_state.basket))
            if st.button("🗑 クリア", use_container_width=True):
                st.session_state.basket = []
                st.session_state.show_results = False
                st.rerun()
            if st.button("🔍 このスパイスで検索", use_container_width=True, type="primary"):
                st.session_state.show_results = True
        else:
            st.info("棚からスパイスを入れてください。")

    st.divider()

    if st.session_state.show_results:
        picked = st.session_state.basket
        df = recipes.copy()
        if picked:
            df = df[df["spices"].apply(lambda lst: all(sp in lst for sp in picked))]

        st.subheader(f"検索結果 ({len(df)} 件)")
        if df.empty:
            st.info("該当する料理がありません。")
            return

        cols = st.columns(CARD_COLS)
        for i, row in df.reset_index(drop=True).iterrows():
            with cols[i % CARD_COLS]:
                with st.container(border=True):
                    if isinstance(row.get("image_url",""), str) and row["image_url"].startswith("http"):
                        st.image(row["image_url"], use_column_width=True)
                    st.markdown(f"### {row['dish_name']}")
                    tag(row["region"], "#f0f7ff")
                    tag(row["category"], "#fff3e0")
                    tag(row["heat"], "#ffecec")
                    st.caption("Spices: " + ", ".join(row["spices"]))
                    if isinstance(row.get("wiki_url",""), str) and row["wiki_url"].startswith("http"):
                        st.link_button("Wikipediaで詳しく", row["wiki_url"], use_container_width=True)

if __name__ == "__main__":
    main()
