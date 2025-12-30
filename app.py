import streamlit as st
import pandas as pd
import time

# ==========================================
# 1. データ読み込み
# ==========================================
@st.cache_data
def load_data():
    # Excelファイルを読み込む
    df = pd.read_excel("valorant_questions.xlsx")
    return df

st.set_page_config(page_title="VALORANT 性格 × 適性診断 100", page_icon="🔫")
st.title("🔫 VALORANT 性格 × 適性診断 100")
st.write("あなたのプレイスタイルと性格を100問の質問から精密に分析します。")

try:
    df = load_data()
except Exception as e:
    st.error("Excelファイルが読み込めません。GitHubにファイルがあるか確認してください。")
    st.stop()

# ==========================================
# 2. 診断フォーム
# ==========================================
user_answers = {}

# デバッグ機能は削除しました。直接フォームを表示します。
with st.form(key='diagnosis_form'):
    for index, row in df.iterrows():
        st.subheader(f"Q{index + 1}. {row['question']}")
        
        options_dict = {}
        for char in ['A', 'B', 'C', 'D']:
            opt_text = row.get(f'option_{char}')
            opt_score = row.get(f'score_{char}')
            if pd.notna(opt_text) and str(opt_text).strip() != "":
                options_dict[opt_text] = opt_score
        
        # ラジオボタンで選択
        choice = st.radio("選択:", list(options_dict.keys()), key=f"q_{index}", index=None)
        
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
        # スコア集計用
        tally = {"Duelist": 0, "Initiator": 0, "Controller": 0, "Sentinel": 0,
                 "Aggro": 0, "Logic": 0, "Stoic": 0, "Teamwork": 0}
        
        for score_str in user_answers.values():
            if pd.isna(score_str) or score_str == "": continue
            # score_X に入っている "Duelist:1,Aggro:1" 形式を分解
            for item in str(score_str).split(","):
                try:
                    k, v = item.split(":")
                    key = k.strip()
                    if key in tally:
                        tally[key] += int(v)
                except:
                    pass

        # 解析中アニメーション
        st.write("性格成分を抽出中...")
        bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01) # 本番用は少しだけ余韻を持たせる
            bar.progress(i + 1)
        st.balloons()

        # MBTI判定 (各軸のスコアが一定以上ならアルファベットを付与)
        m = ""
        m += "A" if tally["Aggro"] >= 5 else "P"
        m += "L" if tally["Logic"] >= 5 else "I"
        m += "S" if tally["Stoic"] >= 5 else "E"
        m += "T" if tally["Teamwork"] >= 5 else "C"

        # 最もスコアの高いロールを決定
        roles = {k: v for k, v in tally.items() if k in ["Duelist", "Initiator", "Controller", "Sentinel"]}
        best_role = max(roles, key=roles.get)

        # 16種類の詳細データ
        results_data = {
            "ALST": {"title": "冷静な戦術指揮官", "desc": "論理と冷静さを兼ね備えた、チームの脳。無駄なデスを嫌い、確実な勝機を待てるプロフェッショナル。"},
            "ALSC": {"title": "孤高の天才軍師", "desc": "味方すら利用して勝利を掴む、圧倒的な個。自分の立ち回りに絶対的な自信を持っており、裏取りやクラッチで輝きます。"},
            "ALET": {"title": "理論武装した情熱家", "desc": "戦術を重視しつつも、ここぞという場面では熱い叫びと共にチームを鼓舞する。理論と情熱のハイブリッドプレイヤー。"},
            "ALEC": {"title": "計算された破壊屋", "desc": "敵の配置を読み切り、最も効果的なタイミングで暴れまわる。理性的に敵を絶望させる、効率的なアタッカー。"},
            "AIST": {"title": "本能で動くエース", "desc": "理屈じゃない。一瞬の隙を見逃さず、フィジカルと直感で戦況をぶち壊す。あなたのエントリーが勝利への合図です。"},
            "AISC": {"title": "野生の狩人", "desc": "予測不能な動きで敵の背後を取り、一人でサイトを壊滅させる。誰にも縛られない、自由奔放なプレイスタイル。"},
            "AIET": {"title": "熱き突撃隊長", "desc": "直感を信じて最前線へ飛び込み、勢いで味方を引っ張っていく。あなたのポジティブなエネルギーが逆転劇を生みます。"},
            "AIEC": {"title": "暴走する破壊神", "desc": "考える前に体が動く。圧倒的な攻撃意欲で敵を蹂躙し、試合のテンポを一人で支配する、生粋の戦闘狂。"},
            "PLST": {"title": "完璧主義の守護神", "desc": "徹底したセットアップと守備で、敵に指一本触れさせない。あなたが守るサイトは、敵にとっての終着駅です。"},
            "PLSC": {"title": "冷徹な影の支配者", "desc": "敵を罠にハメて倒すことに喜びを感じるタイプ。自分は安全圏から、敵をいたぶるような立ち回りが得意。"},
            "PLET": {"title": "盤面の教育者", "desc": "冷静に守りつつも、味方への適切な指示を欠かさない。チーム全体のレベルを底上げする、頼れるベテラン気質。"},
            "PLEC": {"title": "職人気質の仕事人", "desc": "黙々と自分の役割をこなし、気づけば勝利に貢献している。派手さはないが、チームに欠かせない屋台骨。"},
            "PIST": {"title": "静かなる暗殺者", "desc": "目立たず、騒がず、しかし確実に重要な一人を仕留める。忍者のような立ち回りで、敵の計算を狂わせます。"},
            "PISC": {"title": "マイペースな仕事師", "desc": "周囲の状況に左右されず、自分のやりたいプレイを貫く。独特なリズムで戦い、予想外のクラッチを見せる。"},
            "PIET": {"title": "心優しいサポーター", "desc": "味方の動きを察知し、最高のタイミングで支援を送る。あなたのカバーがチームを崩壊から守っています。"},
            "PIEC": {"title": "感性豊かなムードメーカー", "desc": "理屈抜きの楽しさを追求し、チームの雰囲気を最高にする。あなたのプレイ一つで、場がパッと明るくなります。"}
        }

        res = results_data.get(m, {"title": "変幻自在なエージェント", "desc": "特定の型にはまらない、バランスの取れたプレイヤー。"})

        # --- 結果表示エリア ---
        st.header(f"あなたのタイプ: {m}型")
        st.subheader(f"適性ロール: {best_role}")
        st.info(f"あなたは... **「{res['title']}」** です！")
        st.write(res["desc"])

        st.write("---")
        # Discord共有用コピーエリア
        st.write("### 💬 Discord共有用テキスト")
        copy_text = f"**【VALORANT性格診断結果】**\n🛡️ タイプ: {res['title']} ({m}型)\n🔫 適性ロール: {best_role}\n📝 分析: {res['desc']}\n#VALORANT性格診断100"
        st.code(copy_text, language=None)
        st.caption("クリックでコピーしてDiscordに貼り付けてね！")

        if st.button("もう一度診断する"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()