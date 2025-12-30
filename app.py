import streamlit as st
import pandas as pd
import time

# ==========================================
# 1. Excelデータを読み込む関数
# ==========================================
@st.cache_data
def load_data():
    # Excelファイル名を指定（同じフォルダに置いてね！）
    df = pd.read_excel("valorant_questions.xlsx")
    return df

# ==========================================
# 2. 画面のデザイン設定
# ==========================================
st.set_page_config(page_title="VALORANT診断", page_icon="🔫")
st.title("🔫 VALORANT エージェント適性診断")
st.write("100問の質問から、あなたの適性ロールと性格を分析します！")
st.write("---")

# データ読み込み実行
try:
    df = load_data()
except Exception as e:
    st.error(f"Excelファイルが見つかりません！同じ場所に 'valorant_questions.xlsx' があるか確認してね。\nエラー内容: {e}")
    st.stop()

# ==========================================
# 3. 診断フォームの生成
# ==========================================
user_scores = {} # ここに点数を貯めていく

with st.form(key='my_form'):
    # Excelの行（質問）を1つずつ取り出して表示
    for index, row in df.iterrows():
        st.subheader(f"Q{index + 1}. {row['question']}")
        
        # 選択肢リストを作る（空欄のセルは除外する）
        options_dict = {}
        
        # A~Dの選択肢を確認
        for char in ['A', 'B', 'C', 'D']:
            opt_text = row.get(f'option_{char}') # 文言
            opt_score = row.get(f'score_{char}') # スコア文字列
            
            # 文言が入っている場合のみ選択肢に追加
            if pd.notna(opt_text) and str(opt_text).strip() != "":
                # 表示用に "選択肢の文言" をキー、"スコアデータ" を値にする
                options_dict[opt_text] = opt_score
        
        # ラジオボタン表示
        choice = st.radio(
            "直感で選んでください:",
            list(options_dict.keys()),
            key=f"q_{index}",
            index=None # 初期選択なし
        )

        # 選んだ選択肢のスコアデータを保存しておく
        if choice:
            user_scores[index] = options_dict[choice]

    st.write("")
    submit_btn = st.form_submit_button("診断結果を見る！")

# ==========================================
# 4. 結果判定ロジック
# ==========================================
if submit_btn:
    # 未回答チェック
    if len(user_scores) < len(df):
        st.warning("まだ回答していない質問があります！")
    else:
        # 集計開始！
        final_tally = {"Duelist": 0, "Initiator": 0, "Controller": 0, "Sentinel": 0}
        
        # プログレスバー演出
        bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            bar.progress(i + 1)
        
        # スコア計算
        for score_str in user_scores.values():
            # "Duelist:3, IQ:1" みたいな文字列を分解する
            if pd.isna(score_str): continue # データがない場合はスキップ
            
            items = str(score_str).split(",") # カンマで切る
            for item in items:
                try:
                    role, point = item.split(":") # コロンで切る
                    role = role.strip()
                    point = int(point)
                    
                    # 該当するロールに加点
                    if role in final_tally:
                        final_tally[role] += point
                    else:
                        # 定義していないパラメータ（IQとか）も一応数えておく
                        if role not in final_tally:
                            final_tally[role] = 0
                        final_tally[role] += point
                except:
                    pass # 書き方が間違ってたら無視

        # 一番高いスコアを探す
        best_role = max(final_tally, key=final_tally.get)
        
        # 結果表示
        st.success("分析完了！")
        st.balloons() # 風船を飛ばす演出
        
        st.header(f"あなたに向いているのは... 【{best_role}】 です！")
        
        # グラフ表示
        st.bar_chart(final_tally)
        
        # 詳細データの表示（デバッグ用）
        with st.expander("詳細スコアを見る"):
            st.write(final_tally)