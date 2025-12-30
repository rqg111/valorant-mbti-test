import streamlit as st
import pandas as pd
import time
import random

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

try:
    df = load_data()
except Exception as e:
    st.error("Excelファイルが読み込めません。GitHubにファイルがあるか確認してください。")
    st.stop()

# ==========================================
# 🎁 デバッグ機能
# ==========================================
if st.button("🧪 【デバッグ用】ランダムな回答で今すぐ結果を見る"):
    st.session_state["debug_results"] = True
    debug_scores = []
    for index, row in df.iterrows():
        opts = [row.get(f'score_{c}') for c in ['A', 'B', 'C', 'D'] if pd.notna(row.get(f'option_{c}'))]
        if opts:
            debug_scores.append(random.choice(opts))
        else:
            debug_scores.append("")
    st.session_state["debug_scores"] = debug_scores

# ==========================================
# 2. メインの診断フォーム
# ==========================================
user_answers = {}

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
        
        submit_btn = st.form_submit_button("診断結果を解析する")
else:
    submit_btn = True
    user_answers = {i: v for i, v in enumerate(st.session_state["debug_scores"])}

# ==========================================
# 3. 性格分析・詳細解説ロジック
# ==========================================
if submit_btn:
    if len(user_answers) < len(df):
        st.warning(f"まだ回答していない質問があります！（現在 {len(user_answers)} / {len(df)} 問）")
    else:
        tally = {"Duelist": 0, "Initiator": 0, "Controller": 0, "Sentinel": 0,
                 "Aggro": 0, "Logic": 0, "Stoic": 0, "Teamwork": 0}
        
        for score_str in user_answers.values():
            if pd.isna(score_str) or score_str == "": continue
            for item in str(score_str).split(","):
                try:
                    k, v = item.split(":")
                    key = k.strip()
                    if key in tally:
                        tally[key] += int(v)
                except:
                    pass

        st.write("性格成分を抽出中...")
        bar = st.progress(0)
        for i in range(100):
            time.sleep(0.005)
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

        # 結果表示
        st.header(f"あなたのタイプは... **{m} 型**")
        st.subheader(f"適性ロール: **{best_role}**")

        # --- 性格別詳細データ（16種類コンプリート） ---
        results_data = {
            "ALST": {"title": "冷静な戦術指揮官", "desc": "論理と冷静さを兼ね備えた、チームの脳。無駄なデスを嫌い、確実な勝機を待てるプロフェッショナル。", "advice": "時として「理屈に合わない強気な勝負」が必要な場面もあります。直感を信じてみて。"},
            "ALSC": {"title": "孤高の天才軍師", "desc": "味方すら利用して勝利を掴む、圧倒的な個。自分の立ち回りに絶対的な自信を持っており、裏取りやクラッチで輝きます。", "advice": "味方との連携を少し意識するだけで、あなたの生存率はさらに上がり、より恐ろしい存在になります。"},
            "ALET": {"title": "理論武装した情熱家", "desc": "戦術を重視しつつも、ここぞという場面では熱い叫びと共にチームを鼓舞する。理論と情熱のハイブリッドプレイヤー。", "advice": "感情が乗りすぎると報告が雑になりがち。熱い時こそ、正確なHP報告を忘れずに！"},
            "ALEC": {"title": "計算された破壊屋", "desc": "敵の配置を読み切り、最も効果的なタイミングで暴れまわる。理性的に敵を絶望させる、効率的なアタッカー。", "advice": "一人で壊しすぎて、味方がカバーに入れないことが。強引に行く時はピンを鳴らして！"},
            "AIST": {"title": "本能で動くエース", "desc": "理屈じゃない。一瞬の隙を見逃さず、フィジカルと直感で戦況をぶち壊す。あなたのエントリーが勝利への合図です。", "advice": "エイムが不調な時は、スキルの定点を一つでも覚えていると、チームに貢献しやすくなります。"},
            "AISC": {"title": "野生の狩人", "desc": "予測不能な動きで敵の背後を取り、一人でサイトを壊滅させる。誰にも縛られない、自由奔放なプレイスタイル。", "advice": "孤立しがちなので、死んだ後に武器を拾ってくれる味方が近くにいるか確認しておくとGOOD。"},
            "AIET": {"title": "熱き突撃隊長", "desc": "直感を信じて最前線へ飛び込み、勢いで味方を引っ張っていく。あなたのポジティブなエネルギーが逆転劇を生みます。", "advice": "勢い余って「トロール」にならないよう注意。味方の準備が整ったか一瞬だけ待ってみて。"},
            "AIEC": {"title": "暴走する破壊神", "desc": "考える前に体が動く。圧倒的な攻撃意欲で敵を蹂躙し、試合のテンポを一人で支配する、生粋の戦闘狂。", "advice": "デスした後の「なんで今ので死ぬの？」は禁物。自分の勇姿を称えて、次へ切り替えよう！"},
            "PLST": {"title": "完璧主義の守護神", "desc": "徹底したセットアップと守備で、敵に指一本触れさせない。あなたが守るサイトは、敵にとっての終着駅です。", "advice": "守りは神ですが、攻めの時に後ろに居すぎかも。たまにはデュエリストの背中を全力で追って。"},
            "PLSC": {"title": "冷徹な影の支配者", "desc": "敵を罠にハメて倒すことに喜びを感じるタイプ。自分は安全圏から、敵をいたぶるような立ち回りが得意。", "advice": "敵から一番ヘイトを買うタイプです。煽られても動じないその心、大切にしてください。"},
            "PLET": {"title": "盤面の教育者", "desc": "冷静に守りつつも、味方への適切な指示を欠かさない。チーム全体のレベルを底上げする、頼れるベテラン気質。", "advice": "指示が強くなりすぎて「軍隊」にならないよう、褒める言葉を2倍に増やしてみましょう。"},
            "PLEC": {"title": "職人気質の仕事人", "desc": "黙々と自分の役割をこなし、気づけば勝利に貢献している。派手さはないが、チームに欠かせない屋台骨。", "advice": "あなたの凄さは玄人にしか伝わりません。たまには派手なスキンを買って目立ってみる？"},
            "PIST": {"title": "静かなる暗殺者", "desc": "目立たず、騒がず、しかし確実に重要な一人を仕留める。忍者のような立ち回りで、敵の計算を狂わせます。", "advice": "存在感が消えすぎて味方からも忘れられることが。たまにはボイスチャットで生存確認を！"},
            "PISC": {"title": "マイペースな仕事師", "desc": "周囲の状況に左右されず、自分のやりたいプレイを貫く。独特なリズムで戦い、予想外のクラッチを見せる。", "advice": "味方の構成に合わせるフリをして、結局好きなキャラを選ぶ癖、バレてますよ！"},
            "PIET": {"title": "心優しいサポーター", "desc": "味方の動きを察知し、最高のタイミングで支援を送る。あなたのカバーがチームを崩壊から守っています。", "advice": "謙虚すぎるのが玉にキズ。たまには強気に「俺がやる！」と宣言して、武器を買いましょう。"},
            "PIEC": {"title": "感性豊かなムードメーカー", "desc": "理屈抜きの楽しさを追求し、チームの雰囲気を最高にする。あなたのプレイ一つで、場がパッと明るくなります。", "advice": "負けていても楽しそうにできる才能は唯一無二。そのままのあなたでいてください。"}
        }

        res = results_data.get(m, {
            "title": "変幻自在なエージェント",
            "desc": "特定の型にはまらない、バランスの取れたプレイヤー。どんな状況でもチームの穴を埋めることができます。",
            "advice": "自分の得意な「武器」を一つ絞ると、さらにランクが上がりやすくなります。"
        })

        st.info(f"あなたは... **「{res['title']}」** です！")
        st.write("### 📝 分析レポート")
        st.write(res["desc"])
        st.write("### 💡 ランクアップへのアドバイス")
        st.success(res["advice"])

        if st.button("もう一度診断する"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()