import streamlit as st
import pandas as pd
import time
import random

# ==========================================
# 1. データ読み込み
# ==========================================
@st.cache_data
def load_data():
    # GitHub上のExcelファイルを読み込む
    df = pd.read_excel("valorant_questions.xlsx")
    return df

st.set_page_config(page_title="VALORANT 性格 × 適性診断 100", page_icon="🔫")
st.title("🔫 VALORANT 性格 × 適性診断 100")

try:
    df = load_data()
except Exception as e:
    st.error("Excelファイルが読み込めません。GitHubにファイルがあるか確認してください。")
    st.stop()

# ==========================================
# 🎁 【修正】一撃で診断結果を出すデバッグ機能
# ==========================================
if st.button("🧪 【デバッグ用】ランダムな回答で今すぐ結果を見る"):
    st.session_state["debug_results"] = True
    # ランダムに回答を生成して保存
    debug_scores = []
    for index, row in df.iterrows():
        opts = [row.get(f'score_{c}') for c in ['A', 'B', 'C', 'D'] if pd.notna(row.get(f'option_{c}'))]
        debug_scores.append(random.choice(opts))
    st.session_state["debug_scores"] = debug_scores

# ==========================================
# 2. メインの診断フォーム
# ==========================================
user_answers = {}

# デバッグボタンが押されていない時だけフォームを表示
if "debug_results" not in st.session_state:
    with st.form(key='diagnosis_form'):
        for index, row in df.iterrows():
            st.subheader(f"Q{index + 1}. {row['question']}")
            
            options_dict = {}
            for char in ['A', 'B', 'C', 'D']:
                opt_text = row.get(f'option_{char}')
                opt_score = row.get(f'score_{char}')
                if pd.notna(opt_text) and str(opt_text).strip() != "":
                    options_dict[opt_text] = opt_score
            
            choice = st.radio("選択してください:", list(options_dict.keys()), key=f"q_{index}", index=None)
            if choice:
                user_answers[index] = options_dict[choice]

        st.write("---")
        submit_btn = st.form_submit_button("診断結果を解析する")
else:
    # デバッグモードの時は解析ボタンが押されたことにする
    submit_btn = True
    user_answers = {i: v for i, v in enumerate(st.session_state["debug_scores"])}

# ==========================================
# 3. 性格分析ロジック
# ==========================================
if submit_btn:
    if len(user_answers) < len(df):
        st.warning(f"まだ回答していない質問があります！（現在 {len(user_answers)} / {len(df)} 問）")
    else:
        tally = {"Duelist": 0, "Initiator": 0, "Controller": 0, "Sentinel": 0,
                 "Aggro": 0, "Logic": 0, "Stoic": 0, "Teamwork": 0}
        
        for score_str in user_answers.values():
            if pd.isna(score_str): continue
            for item in str(score_str).split(","):
                try:
                    k, v = item.split(":")
                    k = k.strip()
                    if k in tally: tally[k] += int(val)
                except: pass

        # 演出
        st.write("性格成分を抽出中...")
        bar = st.progress(0)
        for i in range(100):
            time.sleep(0.005) # デバッグなので少し速めに
            bar.progress(i + 1)
        st.balloons()

        # MBTI判定
        m = ""
        m += "A" if tally["Aggro"] >= 5 else "P"
        m += "L" if tally["Logic"] >= 5 else "I"
        m += "S" if tally["Stoic"] >= 5 else "E"
        m += "T" if tally["Teamwork"] >= 5 else "C"

        roles = {k: v for k, v in tally.items() if k in ["Duelist", "Initiator", "Controller", "Sentinel"]}
        best_role = max(roles, key=roles.get)

        st.header(f"あなたのタイプは... **{m} 型**")
        st.subheader(f"適性ロール: **{best_role}**")
        
        # タイトル
        titles = {"ALST": "冷静な戦術指揮官", "AIST": "本能で動くエース", "PLST": "完璧主義の守護神", "PIET": "心優しいサポーター"}
        st.info(f"あなたは... **「{titles.get(m, '個性豊かなエージェント')}」** です！")
        
        if st.button("もう一度診断する"):
            del st.session_state["debug_results"]
            st.rerun()