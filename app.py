import streamlit as st
import pandas as pd
import time

# ==========================================
# 1. データ読み込み
# ==========================================
@st.cache_data
def load_data():
    df = pd.read_excel("valorant_questions.xlsx")
    return df

st.set_page_config(page_title="VALORANT 性格 × 適性診断 100", page_icon="🔫")
st.title("🔫 VALORANT 性格 × 適性診断 100")
st.write("あなたのプレイスタイルと性格をMBTI風に精密分析します。")

try:
    df = load_data()
except Exception as e:
    st.error("Excelファイルが読み込めません。GitHubにファイルがあるか確認してください。")
    st.stop()

# ==========================================
# 2. 診断フォーム
# ==========================================
user_scores = {}

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
            user_scores[index] = options_dict[choice]

    st.write("---")
    submit_btn = st.form_submit_button("診断結果を解析する")

# ==========================================
# 3. 性格分析ロジック
# ==========================================
if submit_btn:
    if len(user_scores) < len(df):
        st.warning(f"まだ回答していない質問があります！（現在 {len(user_scores)} / {len(df)} 問）")
    else:
        # スコア集計
        tally = {
            # ロール
            "Duelist": 0, "Initiator": 0, "Controller": 0, "Sentinel": 0,
            # 性格軸（プラスとマイナスで判定）
            "Aggro": 0,    # 積極性 (Aggressive vs Passive)
            "Logic": 0,    # 思考法 (Logical vs Intuitive)
            "Stoic": 0,    # 精神性 (Stoic vs Emotional)
            "Teamwork": 0  # 連帯感 (Team-Player vs Solo-Carry)
        }
        
        for score_str in user_scores.values():
            if pd.isna(score_str): continue
            items = str(score_str).split(",")
            for item in items:
                try:
                    key, val = item.split(":")
                    key = key.strip()
                    val = int(val)
                    if key in tally:
                        tally[key] += val
                except: pass

        # 演出
        st.write("性格成分を抽出中...")
        bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            bar.progress(i + 1)
        st.balloons()

        # --- MBTI風 4文字コード作成 ---
        mbti_code = ""
        mbti_desc = []

        # 1. 積極性
        if tally["Aggro"] >= 5:
            mbti_code += "A"
            mbti_desc.append("【A】Aggressive（超攻撃的）")
        else:
            mbti_code += "P"
            mbti_desc.append("【P】Passive（慎重派）")

        # 2. 思考法
        if tally["Logic"] >= 5:
            mbti_code += "L"
            mbti_desc.append("【L】Logical（理論派）")
        else:
            mbti_code += "I"
            mbti_desc.append("【I】Intuitive（直感派）")

        # 3. 精神性
        if tally["Stoic"] >= 5:
            mbti_code += "S"
            mbti_desc.append("【S】Stoic（冷静沈着）")
        else:
            mbti_code += "E"
            mbti_desc.append("【E】Emotional (情熱的)")

        # 4. 連帯感
        if tally["Teamwork"] >= 5:
            mbti_code += "T"
            mbti_desc.append("【T】Team-Player（協力重視）")
        else:
            mbti_code += "C"
            mbti_desc.append("【C】Solo-Carry（圧倒的主人公）")

        # ロール決定
        roles = {k: v for k, v in tally.items() if k in ["Duelist", "Initiator", "Controller", "Sentinel"]}
        best_role = max(roles, key=roles.get)

        # 結果表示
        st.header(f"あなたのタイプは... **{mbti_code} 型**")
        st.subheader(f"適性ロール: **{best_role}**")
        st.write("---")
        
        st.write("### 📊 性格分析レポート")
        for desc in mbti_desc:
            st.write(desc)
        
        # 二つ名の生成（例）
        titles = {
            "ALST": "冷静な戦術指揮官",
            "AIST": "本能で動くエース",
            "PLST": "完璧主義の守護神",
            "PIET": "心優しいサポーター"
        }
        title = titles.get(mbti_code, "個性豊かなエージェント")
        st.info(f"あなたは... **「{title}」** です！")

        with st.expander("詳細スコアを確認する"):
            st.write(tally)