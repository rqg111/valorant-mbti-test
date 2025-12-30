import streamlit as st
import pandas as pd
import time
import random

# ==========================================
# 1. データ読み込み
# ==========================================
@st.cache_data
def load_data():
    df = pd.read_excel("valorant_questions.xlsx")
    return df

st.set_page_config(page_title="VALORANT 性格 × 適性診断 100", page_icon="🔫")
st.title("🔫 VALORANT 性格 × 適性診断 100")

try:
    df = load_data()
except Exception as e:
    st.error("Excelファイルが読み込めません。")
    st.stop()

# ==========================================
# 🎁 【追加】一括回答機能
# ==========================================
if st.button("🧪 【デバッグ用】全問ランダムで回答を埋める"):
    for index, row in df.iterrows():
        options = []
        for char in ['A', 'B', 'C', 'D']:
            opt_text = row.get(f'option_{char}')
            if pd.notna(opt_text) and str(opt_text).strip() != "":
                options.append(opt_text)
        # ランダムに選択肢を選んでセッションに保存
        st.session_state[f"q_{index}"] = random.choice(options)
    st.success("全ての回答をランダムに埋めました！一番下の『診断結果を解析する』を押してください。")

# ==========================================
# 2. 診断フォーム
# ==========================================
user_answers = {}

with st.form(key='diagnosis_form'):
    for index, row in df.iterrows():
        st.subheader(f"Q{index + 1}. {row['question']}")
        
        options_dict = {}
        for char in ['A', 'B', 'C', 'D']:
            opt_text = row.get(f'option_{char}')
            opt_score = row.get(f'score_{char}')
            if pd.notna(opt_text) and str(opt_text).strip() != "":
                options_dict[opt_text] = opt_score
        
        # セッション状態から初期値を取得（デバッグ用）
        default_val = st.session_state.get(f"q_{index}", None)
        # ラジオボタンのindexを決定
        current_index = list(options_dict.keys()).index(default_val) if default_val in options_dict else None

        choice = st.radio(
            "選択してください:", 
            list(options_dict.keys()), 
            key=f"radio_{index}", # keyが重複しないように変更
            index=current_index
        )
        
        if choice:
            user_answers[index] = options_dict[choice]

    st.write("---")
    submit_btn = st.form_submit_button("診断結果を解析する")

# ==========================================
# 3. 性格分析ロジック
# ==========================================
if submit_btn:
    if len(user_answers) < len(df):
        st.warning(f"まだ回答していない質問があります！（現在 {len(user_answers)} / {len(df)} 問）")
    else:
        # スコア集計
        tally = {
            "Duelist": 0, "Initiator": 0, "Controller": 0, "Sentinel": 0,
            "Aggro": 0, "Logic": 0, "Stoic": 0, "Teamwork": 0
        }
        
        for score_str in user_answers.values():
            if pd.isna(score_str): continue
            items = str(score_str).split(",")
            for item in items:
                try:
                    key, val = item.split(":")
                    key = key.strip()
                    val = int(val)
                    if key in tally:
                        tally[key] += val
                    else:
                        if key not in tally: tally[key] = 0
                        tally[key] += val
                except: pass

        st.write("性格成分を抽出中...")
        bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            bar.progress(i + 1)
        st.balloons()

        # MBTI判定ロジック
        mbti_code = ""
        mbti_code += "A" if tally.get("Aggro", 0) >= 5 else "P"
        mbti_code += "L" if tally.get("Logic", 0) >= 5 else "I"
        mbti_code += "S" if tally.get("Stoic", 0) >= 5 else "E"
        mbti_code += "T" if tally.get("Teamwork", 0) >= 5 else "C"

        roles = {k: v for k, v in tally.items() if k in ["Duelist", "Initiator", "Controller", "Sentinel"]}
        best_role = max(roles, key=roles.get)

        st.header(f"あなたの診断コード: **{mbti_code}型**")
        st.subheader(f"適性ロール: **{best_role}**")
        
        # タイトルマッピング
        titles = {
            "ALST": "冷静な戦術指揮官", "AIST": "本能で動くエース",
            "PLST": "完璧主義の守護神", "PIET": "心優しいサポーター",
            "ALEC": "情熱的な破壊屋", "PIEC": "感性豊かなムードメーカー"
        }
        title = titles.get(mbti_code, "変幻自在なエージェント")
        st.info(f"あなたは... **「{title}」** です！")

        with st.expander("詳細スコア"):
            st.write(tally)