# -*- coding: utf-8 -*-
"""
ネットワーク・クエスト ～失われたWebページを取り戻せ～

高等学校「情報Ⅰ」向け教材アプリ
「Webページが表示されるまでの通信の流れ」を
ロールプレイングゲーム形式で体験的に学習できるStreamlitアプリです。

※ 本アプリは教材用のシミュレーションです。
   実際のインターネット通信・DNS問い合わせ・外部サイトへのアクセスは行いません。
   東京ディズニーリゾートの公式ロゴ・キャラクター・写真・文章・画面デザインは
   一切使用・複製していません（教材用の例としてURL文字列のみを表示しています）。
"""

import time
import random
import streamlit as st

# =========================================================
# 基本設定
# =========================================================
st.set_page_config(
    page_title="ネットワーク・クエスト",
    page_icon="🗝️",
    layout="wide",
)

TARGET_URL = "https://www.tokyodisneyresort.jp/"

# エリア（ワールドマップ）の定義
AREAS = [
    {"name": "はじまりの街", "emoji": "🏘"},
    {"name": "URL解析の森", "emoji": "📜"},
    {"name": "DNSの塔", "emoji": "🔮"},
    {"name": "Webサーバ城", "emoji": "🏰"},
    {"name": "パケット迷宮", "emoji": "🌐"},
    {"name": "ブラウザ神殿", "emoji": "🪞"},
]

# 通信キーの定義（インデックスはSTEP番号-1に対応）
NET_KEYS = [
    {"name": "入力のキー", "emoji": "🔑"},
    {"name": "URL解析のキー", "emoji": "🗝️"},
    {"name": "DNSのキー", "emoji": "🔐"},
    {"name": "HTTPのキー", "emoji": "📯"},
    {"name": "パケットのキー", "emoji": "🧩"},
    {"name": "ブラウザのキー", "emoji": "🪄"},
]

# アイテムの定義
ITEMS_INFO = {
    "プロトコルの書": {
        "emoji": "📘",
        "text": "プロトコルは、コンピュータ同士が通信するときの決まりです。\n"
                 "HTTPSでは、通信内容を暗号化して安全にデータをやり取りします。",
    },
    "ドメイン地図": {
        "emoji": "🗺",
        "text": "ドメイン名は、Webサイトの場所を人間に分かりやすく表した名前です。",
    },
    "DNSクリスタル": {
        "emoji": "🔮",
        "text": "DNSは、ドメイン名をコンピュータが通信に使うIPアドレスへ変換します。",
    },
    "HTTPの巻物": {
        "emoji": "📜",
        "text": "ブラウザは、HTTPリクエストを使ってWebサーバへデータを要求します。",
    },
    "パケットバッグ": {
        "emoji": "🎒",
        "text": "データは小さなパケットに分けて送られ、受信側で元の順番に戻されます。",
    },
    "ブラウザの鏡": {
        "emoji": "🪞",
        "text": "ブラウザは、HTML、CSS、画像などを解析してWebページを表示します。",
    },
}

# 職業の定義
JOBS = {
    "ネットワーク剣士": {
        "emoji": "⚔️",
        "desc": "通信経路を切り開く勇者",
    },
    "DNS魔法使い": {
        "emoji": "🪄",
        "desc": "名前とIPアドレスを結び付ける魔法使い",
    },
    "ブラウザ探検家": {
        "emoji": "🧭",
        "desc": "Webページの完成を目指す冒険者",
    },
}

EXP_TABLE = {1: 20, 2: 30, 3: 30, 4: 40, 5: 50, 6: 60}
EXP_PER_LEVEL = 100


# =========================================================
# CSS（デザインは1か所にまとめる）
# =========================================================
def inject_css():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #0b0f2b 0%, #1a1440 60%, #241a4d 100%);
        }
        .parchment-card {
            background: linear-gradient(180deg, #f5ecd7 0%, #ecdcb8 100%);
            border: 2px solid #b8860b;
            border-radius: 16px;
            padding: 18px 22px;
            margin-bottom: 14px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.35);
            color: #3b2b12;
        }
        .parchment-card h1, .parchment-card h2, .parchment-card h3,
        .parchment-card h4, .parchment-card p, .parchment-card li,
        .parchment-card span, .parchment-card div {
            color: #3b2b12;
        }
        .rpg-title {
            text-align: center;
            font-size: 40px;
            font-weight: 900;
            color: #ffd76a;
            text-shadow: 2px 2px 6px rgba(0,0,0,0.6);
            margin-bottom: 0px;
        }
        .rpg-subtitle {
            text-align: center;
            font-size: 18px;
            color: #d8c6ff;
            margin-top: 4px;
            margin-bottom: 20px;
        }
        .badge-card {
            border-radius: 14px;
            padding: 10px 8px;
            text-align: center;
            font-size: 14px;
            font-weight: 700;
            box-shadow: 0 3px 8px rgba(0,0,0,0.3);
        }
        .key-obtained {
            background: linear-gradient(180deg, #ffe27a, #d9a441);
            color: #3b2b12;
            border: 2px solid #ffd76a;
        }
        .key-locked {
            background: #3a3a4a;
            color: #9a9aae;
            border: 2px solid #55556a;
        }
        .map-current {
            background: linear-gradient(180deg, #ffe27a, #d9a441);
            color: #3b2b12;
            border-radius: 14px;
            padding: 10px 6px;
            text-align: center;
            font-weight: 800;
            box-shadow: 0 0 14px 4px rgba(255, 215, 106, 0.7);
        }
        .map-cleared {
            background: linear-gradient(180deg, #9be79b, #4caf50);
            color: #123312;
            border-radius: 14px;
            padding: 10px 6px;
            text-align: center;
            font-weight: 700;
        }
        .map-locked {
            background: #2c2c40;
            color: #8888a0;
            border-radius: 14px;
            padding: 10px 6px;
            text-align: center;
            font-weight: 700;
        }
        .url-proto {
            background: #2a6fdb; color: white; padding: 8px 12px;
            border-radius: 10px; font-weight: 800; display: inline-block;
            margin: 4px;
        }
        .url-domain {
            background: #2fa84f; color: white; padding: 8px 12px;
            border-radius: 10px; font-weight: 800; display: inline-block;
            margin: 4px;
        }
        .url-path {
            background: #e08a2c; color: white; padding: 8px 12px;
            border-radius: 10px; font-weight: 800; display: inline-block;
            margin: 4px;
        }
        .log-box {
            background: #0c0c1a;
            color: #f0f0f0;
            border-radius: 12px;
            padding: 14px;
            height: 260px;
            overflow-y: auto;
            font-family: "Courier New", monospace;
            font-size: 13px;
            border: 1px solid #4a4a6a;
        }
        .npc-box {
            background: rgba(255,255,255,0.08);
            border-left: 5px solid #ffd76a;
            border-radius: 8px;
            padding: 10px 14px;
            margin-bottom: 10px;
            color: #f0eaff;
        }
        .final-page {
            background: #ffffff;
            border-radius: 14px;
            padding: 20px;
            color: #222;
            border: 3px solid #b8860b;
        }
        .final-page-card {
            background: #fdf6e3;
            border-radius: 10px;
            padding: 10px 14px;
            margin-bottom: 10px;
            border: 1px solid #e0c98a;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# session_state 初期化（関数化）
# =========================================================
def init_session_state():
    defaults = {
        "game_started": False,
        "player_name": "",
        "job": "ネットワーク剣士",
        "level": 1,
        "exp": 0,
        "hp": 100,
        "current_area": 0,       # 0〜5（AREASのインデックス）
        "step_cleared": [False] * 6,
        "keys_obtained": [],
        "items_obtained": [],
        "adventure_log": [],
        "paused": False,
        "speed": "普通",
        "input_url": TARGET_URL,
        "step1_opened": False,
        "url_broken": False,
        "url_quiz_correct": [None, None, None],
        "dns_quiz_correct": None,
        "dns_query_done": False,
        "http_choice_correct": False,
        "http_sent": False,
        "packet_order_correct": False,
        "packet_sent": False,
        "step6_random_mode": False,
        "status_code": None,
        "render_stage": 0,
        "page_complete": False,
        "show_clear_screen": False,
        "levelup_flag": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# =========================================================
# 各種処理関数
# =========================================================
def add_log(message: str):
    """冒険の記録にログを追加する（重複は追加しない）"""
    if message not in st.session_state.adventure_log:
        st.session_state.adventure_log.append(message)


def add_exp(amount: int):
    """経験値を加算し、必要ならレベルアップさせる"""
    st.session_state.exp += amount
    while st.session_state.exp >= EXP_PER_LEVEL:
        st.session_state.exp -= EXP_PER_LEVEL
        st.session_state.level += 1
        st.session_state.levelup_flag = True


def take_damage(amount: int = 5):
    """HPを減らす。0以下になったら妖精が助けてくれる演出を出す"""
    st.session_state.hp -= amount
    if st.session_state.hp <= 0:
        st.session_state.hp = 30
        st.warning("通信の妖精が助けてくれました。\n\nもう一度、学習ポイントを確認して挑戦しましょう。")
    if st.session_state.hp < 0:
        st.session_state.hp = 0


def add_item(item_name: str):
    """アイテムを獲得する（重複しない）"""
    if item_name not in st.session_state.items_obtained:
        st.session_state.items_obtained.append(item_name)
        st.success(f"「{item_name}」を手に入れた！")


def add_key(step_index: int):
    """通信キーを獲得する（重複しない）。step_indexは0始まり"""
    key_name = NET_KEYS[step_index]["name"]
    if key_name not in st.session_state.keys_obtained:
        st.session_state.keys_obtained.append(key_name)


def clear_step(step_index: int, exp_amount: int):
    """STEPクリア処理をまとめて行う（重複防止つき）"""
    if not st.session_state.step_cleared[step_index]:
        st.session_state.step_cleared[step_index] = True
        add_exp(exp_amount)
        add_key(step_index)


def show_levelup_effect():
    """レベルアップ演出"""
    if st.session_state.levelup_flag:
        st.balloons()
        st.markdown(
            """
            <div class="parchment-card" style="text-align:center;">
                <h2>✨ LEVEL UP！ ✨</h2>
                <p>通信士としての力が高まりました。</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.session_state.levelup_flag = False


def reset_game():
    """ゲーム状態をすべて初期化する"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()


# =========================================================
# サイドバー
# =========================================================
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🧙 プレイヤー情報")
        job_info = JOBS.get(st.session_state.job, JOBS["ネットワーク剣士"])
        st.markdown(f"**{job_info['emoji']} {st.session_state.player_name or '名もなき冒険者'}**")
        st.caption(f"{job_info['emoji']} {st.session_state.job}｜{job_info['desc']}")

        st.markdown(f"**レベル：{st.session_state.level}**")

        st.markdown("HP")
        hp_ratio = max(0, min(100, st.session_state.hp)) / 100
        st.progress(hp_ratio, text=f"{st.session_state.hp} / 100")

        st.markdown("EXP")
        exp_ratio = max(0, min(EXP_PER_LEVEL, st.session_state.exp)) / EXP_PER_LEVEL
        st.progress(exp_ratio, text=f"{st.session_state.exp} / {EXP_PER_LEVEL}")

        current_area_name = AREAS[st.session_state.current_area]["name"]
        st.markdown(f"📍 現在地：**{current_area_name}**")

        st.markdown("### 🔑 通信キー")
        for k in NET_KEYS:
            obtained = k["name"] in st.session_state.keys_obtained
            mark = "✅" if obtained else "🔒"
            st.markdown(f"{mark} {k['emoji']} {k['name']}")

        st.markdown("### 🎒 所持アイテム")
        if st.session_state.items_obtained:
            for item in st.session_state.items_obtained:
                emoji = ITEMS_INFO.get(item, {}).get("emoji", "🎁")
                st.markdown(f"{emoji} {item}")
        else:
            st.caption("まだ何も持っていません")

        st.markdown("### 📶 通信速度")
        st.session_state.speed = st.selectbox(
            "通信速度", ["遅い", "普通", "速い"],
            index=["遅い", "普通", "速い"].index(st.session_state.speed),
            label_visibility="collapsed",
        )

        st.markdown("---")
        col_back, col_next = st.columns(2)
        with col_back:
            if st.button("⬅ 戻る", use_container_width=True, disabled=(st.session_state.current_area == 0)):
                st.session_state.current_area = max(0, st.session_state.current_area - 1)
                st.rerun()
        with col_next:
            can_advance = (
                st.session_state.current_area < 5
                and st.session_state.step_cleared[st.session_state.current_area]
            )
            if st.button("次へ ➡", use_container_width=True, disabled=not can_advance):
                st.session_state.current_area = min(5, st.session_state.current_area + 1)
                st.rerun()

        pause_label = "▶ 再開" if st.session_state.paused else "⏸ 一時停止"
        if st.button(pause_label, use_container_width=True):
            st.session_state.paused = not st.session_state.paused
            st.rerun()

        if st.button("🔄 リセット", use_container_width=True):
            st.session_state["_show_reset_confirm"] = True

        if st.session_state.get("_show_reset_confirm", False):
            st.warning("本当にリセットしますか？すべての記録が失われます。")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("はい", key="reset_yes", use_container_width=True):
                    reset_game()
                    st.rerun()
            with c2:
                if st.button("いいえ", key="reset_no", use_container_width=True):
                    st.session_state["_show_reset_confirm"] = False
                    st.rerun()


# =========================================================
# ワールドマップ
# =========================================================
def render_world_map():
    cols = st.columns(6)
    for i, area in enumerate(AREAS):
        with cols[i]:
            if i == st.session_state.current_area:
                css_class = "map-current"
                mark = "📍"
            elif st.session_state.step_cleared[i]:
                css_class = "map-cleared"
                mark = "✅"
            else:
                css_class = "map-locked"
                mark = "🔒"
            st.markdown(
                f'<div class="{css_class}">{mark}<br>{area["emoji"]}<br>{area["name"]}</div>',
                unsafe_allow_html=True,
            )


# =========================================================
# タイトル画面
# =========================================================
def show_title_screen():
    st.markdown('<div class="rpg-title">🗝️ ネットワーク・クエスト</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="rpg-subtitle">～失われたWebページを取り戻せ～<br>通信の仕組みを学びながら、Webページ表示の冒険に出発しよう</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="parchment-card">
        <p>ネットワーク王国では、Webページのデータが行方不明になる事件が起きていた。</p>
        <p>君の使命は、通信の6つのエリアを攻略し、失われたWebページを取り戻すことだ。</p>
        <p>URLを入力し、通信の冒険を始めよう。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("プレイヤー名を入力してください", value=st.session_state.player_name, max_chars=20)
    with col2:
        job = st.selectbox("職業を選択してください", list(JOBS.keys()),
                            index=list(JOBS.keys()).index(st.session_state.job))

    job_info = JOBS[job]
    st.markdown(
        f'<div class="npc-box">{job_info["emoji"]} <b>{job}</b><br>{job_info["desc"]}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### 職業一覧")
    jcols = st.columns(3)
    for (jname, jinfo), col in zip(JOBS.items(), jcols):
        with col:
            st.markdown(
                f'<div class="parchment-card" style="text-align:center;">'
                f'{jinfo["emoji"]}<br><b>{jname}</b><br><span style="font-size:13px;">{jinfo["desc"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    if st.button("⚔ 冒険を始める", type="primary", use_container_width=True):
        player_name = name.strip() if name.strip() else "名もなき冒険者"
        st.session_state.player_name = player_name
        st.session_state.job = job
        st.session_state.game_started = True
        st.rerun()


# =========================================================
# STEP1 はじまりの街
# =========================================================
def show_step1():
    st.markdown(
        """
        <div class="parchment-card">
        <h3>ミッション1　伝説のURLを入力せよ</h3>
        <div class="npc-box">🧙 通信の賢者<br>「Webページを探すためには、まず目的地を表すURLが必要じゃ。」</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    url = st.text_input("🌐 ブラウザのアドレスバー", value=st.session_state.input_url)
    st.session_state.input_url = url if url else TARGET_URL

    if st.button("🚪 ページを開く", type="primary"):
        st.session_state.step1_opened = True
        add_log("ブラウザにURLが入力されました。")
        add_log("Webページ表示の処理を開始しました。")

    if st.session_state.step1_opened:
        st.info(
            "ブラウザがURLを受け取りました。\n\n"
            "しかし、まだWebページは表示されていません。\n\n"
            "通信の冒険は、ここから始まります。"
        )

        if not st.session_state.step_cleared[0]:
            clear_step(0, EXP_TABLE[1])
            add_item_placeholder = NET_KEYS[0]["name"]
            st.success(f"ミッションクリア！\n\n「{add_item_placeholder}」を手に入れた！")
        else:
            st.success("このミッションはすでにクリア済みです。")

        with st.expander("📖 学習ポイント"):
            st.write("URLは、インターネット上にあるWebページの場所を表します。")


# =========================================================
# STEP2 URL解析の森
# =========================================================
def show_step2():
    st.markdown(
        """
        <div class="parchment-card">
        <h3>ミッション2　URLの3つの紋章を見つけ出せ</h3>
        <div class="npc-box">🧝 URLの精霊<br>「このURLには、3つの大切な情報が隠されています。」</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.code(TARGET_URL, language="text")

    if st.button("🔍 URLを分解する"):
        st.session_state.url_broken = True

    if st.session_state.url_broken:
        st.markdown(
            """
            <div style="text-align:center; margin:14px 0;">
                <span class="url-proto">https://</span>
                <span class="url-domain">www.tokyodisneyresort.jp</span>
                <span class="url-path">/</span>
            </div>
            <div style="text-align:center; font-size:13px; color:#d8c6ff;">
                プロトコル　　　　　　　　　　ドメイン名　　　　　　　　　パス
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("📘 プロトコル（https://）とは"):
            st.write(
                "プロトコルは、コンピュータ同士が通信するときの決まりです。\n\n"
                "HTTPSでは、通信内容を暗号化して安全にデータをやり取りします。"
            )
        with st.expander("🗺 ドメイン名（www.tokyodisneyresort.jp）とは"):
            st.write("ドメイン名は、Webサイトの場所を人間に分かりやすく表した名前です。")
        with st.expander("📄 パス（/）とは"):
            st.write(
                "パスは、Webサーバ内のページやファイルの場所を表します。\n\n"
                "「/」はトップページを表します。"
            )

        st.markdown("---")
        st.markdown(
            """
            <div class="npc-box">👾 URLスライムが現れた！<br>正しい名前を選んで、3つの紋章を取り戻そう。</div>
            """,
            unsafe_allow_html=True,
        )

        options = ["選択してください", "プロトコル", "ドメイン名", "パス"]
        q1 = st.selectbox("問題1：https:// は何？", options, key="q1_select")
        q2 = st.selectbox("問題2：www.tokyodisneyresort.jp は何？", options, key="q2_select")
        q3 = st.selectbox("問題3：/ は何？", options, key="q3_select")

        if st.button("⚔ 回答する"):
            answers = [q1 == "プロトコル", q2 == "ドメイン名", q3 == "パス"]
            st.session_state.url_quiz_correct = answers
            if all(answers):
                st.success("URLスライムを倒した！\n\nURLの3つの紋章を取り戻しました。")
                if not st.session_state.step_cleared[1]:
                    clear_step(1, EXP_TABLE[2])
                    add_item("プロトコルの書")
                    add_item("ドメイン地図")
                    add_log("URLをプロトコル、ドメイン名、パスに分解しました。")
            else:
                take_damage(5)
                st.error("URLスライムの反撃を受けた！")
                st.info(
                    "ヒント：\n\n"
                    "通信の決まりがプロトコルです。\n\n"
                    "Webサイトの名前がドメイン名です。\n\n"
                    "サーバ内の場所がパスです。"
                )

        if st.session_state.step_cleared[1]:
            st.success("このミッションはクリア済みです。")
            with st.expander("📖 学習ポイント"):
                st.write("URLを見ると、通信方法、接続先のWebサイト、ページの場所が分かります。")


# =========================================================
# STEP3 DNSの塔
# =========================================================
def show_step3():
    st.markdown(
        """
        <div class="parchment-card">
        <h3>ミッション3　ドメイン名をIPアドレスに変換せよ</h3>
        <div class="npc-box">🧙‍♂️ DNSの魔法使い<br>「ドメイン名だけでは、Webサーバへたどり着けない。」</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("ドメイン名をIPアドレスに変換する仕組みはどれでしょうか。")
    choice = st.radio("選択肢", ["選択してください", "DNS", "HTML", "CSS"], key="dns_choice")

    if st.button("🔎 回答する", key="dns_answer_btn"):
        if choice == "DNS":
            st.session_state.dns_quiz_correct = True
            st.success("正解！ドメイン名の秘密を見破った！")
        else:
            st.session_state.dns_quiz_correct = False
            take_damage(5)
            st.error("不正解…塔の力に押し返された！")
            st.info("ヒント：ドメイン名をコンピュータ用の住所（IPアドレス）に変換する仕組みです。")

    if st.session_state.dns_quiz_correct:
        if st.button("🔮 DNS魔法を使う"):
            st.session_state.dns_query_done = True

        if st.session_state.dns_query_done:
            steps_text = [
                "① DNSサーバへ問い合わせる…",
                "② ドメイン名を確認する…",
                "③ IPアドレスを探す…",
                "④ IPアドレスを受け取った！",
            ]
            for line in steps_text:
                st.write(line)

            st.markdown(
                """
                <div class="parchment-card" style="text-align:center;">
                🔮 DNS変換魔法！<br><br>
                www.tokyodisneyresort.jp<br>
                　↓<br>
                <b>203.0.113.10</b>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption("※このIPアドレスは教材用の例です。実際の東京ディズニーリゾートのIPアドレスではありません。")

            if not st.session_state.step_cleared[2]:
                clear_step(2, EXP_TABLE[3])
                add_item("DNSクリスタル")
                add_log("DNSサーバへ問い合わせました。")
                add_log("ドメイン名に対応する教材用IPアドレスを取得しました。")

            if st.session_state.step_cleared[2]:
                st.success("このミッションはクリア済みです。")
                with st.expander("📖 学習ポイント"):
                    st.write("DNSは、ドメイン名をコンピュータが通信に使うIPアドレスへ変換します。")


# =========================================================
# STEP4 Webサーバ城
# =========================================================
def show_step4():
    st.markdown(
        """
        <div class="parchment-card">
        <h3>ミッション4　HTTPの巻物を使って城門を開け</h3>
        <div class="npc-box">🛡 サーバの門番<br>「正しいリクエストを送らなければ、城門は開かない。」</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.code("GET / HTTP/1.1\nHost: www.tokyodisneyresort.jp", language="http")

    st.write("正しいコマンドカードを選んでください。")
    cols = st.columns(3)
    commands = ["GET", "SAVE", "DELETE"]
    chosen = None
    for cmd, col in zip(commands, cols):
        with col:
            if st.button(f"📜 {cmd}", key=f"cmd_{cmd}", use_container_width=True):
                chosen = cmd

    if chosen is not None:
        if chosen == "GET":
            st.session_state.http_choice_correct = True
            st.success("正しいコマンドだ！城門の鍵が反応した！")
        else:
            take_damage(5)
            st.error("城門はびくともしない…！")
            st.info("ヒント：GETはデータを送ってもらうための命令です。")

    if st.session_state.http_choice_correct:
        if st.button("📯 GETリクエストを送信する"):
            st.session_state.http_sent = True

        if st.session_state.http_sent:
            for line in [
                "① IPアドレスを確認…",
                "② Webサーバへ接続…",
                "③ HTTPリクエストを作成…",
                "④ GETリクエストを送信！",
                "⑤ サーバがリクエストを受信しました。",
            ]:
                st.write(line)

            st.markdown(
                """
                <div class="parchment-card" style="text-align:center;">
                📜 HTTPの巻物を使用！<br><br>
                <code>GET / HTTP/1.1</code><br><br>
                城門が開きました。
                </div>
                """,
                unsafe_allow_html=True,
            )

            if not st.session_state.step_cleared[3]:
                clear_step(3, EXP_TABLE[4])
                add_item("HTTPの巻物")
                add_log("Webサーバへ接続しました。")
                add_log("HTTP GETリクエストを送信しました。")

            if st.session_state.step_cleared[3]:
                st.success("このミッションはクリア済みです。")
                with st.expander("📖 学習ポイント"):
                    st.write("ブラウザは、HTTPリクエストを使ってWebサーバへデータを要求します。")


# =========================================================
# STEP5 パケット迷宮
# =========================================================
PACKETS = [
    "<html><head>",
    "<title>テーマパーク案内",
    "</title></head>",
    "<body>夢の一日へようこそ",
]


def show_step5():
    st.markdown(
        """
        <div class="parchment-card">
        <h3>ミッション5　散らばったパケットを正しく並べ直せ</h3>
        <div class="npc-box">🐉 パケットドラゴン<br>「データをばらばらにしてやったぞ！」</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("📤 パケットを送信する"):
        st.session_state.packet_sent = True

    if st.session_state.packet_sent:
        st.write("パケットが異なる経路を通って届いた…")
        routes = [
            "パケット1：Webサーバ → ルータA → ルータC → 利用者PC",
            "パケット2：Webサーバ → ルータB → ルータC → 利用者PC",
            "パケット3：Webサーバ → ルータA → ルータD → 利用者PC",
            "パケット4：Webサーバ → ルータB → ルータD → 利用者PC",
        ]
        for r in routes:
            st.write(r)
        st.caption("到着順：パケット2 → パケット4 → パケット1 → パケット3")

        st.write("正しい順番（パケット1→2→3→4）になるように、内容を並び替えよう。")
        shuffled_display = {
            "パケット2": PACKETS[1],
            "パケット4": PACKETS[3],
            "パケット1": PACKETS[0],
            "パケット3": PACKETS[2],
        }
        for name, content in shuffled_display.items():
            st.code(f"{name}: {content}", language="text")

        order_options = ["パケット1", "パケット2", "パケット3", "パケット4"]
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            p1 = st.selectbox("1番目", order_options, key="p1")
        with c2:
            p2 = st.selectbox("2番目", order_options, key="p2")
        with c3:
            p3 = st.selectbox("3番目", order_options, key="p3")
        with c4:
            p4 = st.selectbox("4番目", order_options, key="p4")

        if st.button("🧩 パケットを組み立てる"):
            user_order = [p1, p2, p3, p4]
            correct_order = ["パケット1", "パケット2", "パケット3", "パケット4"]
            if user_order == correct_order:
                st.session_state.packet_order_correct = True
                st.success("パケットドラゴンを倒した！\n\nデータが元の順番に戻りました。")
                st.code("".join(PACKETS), language="html")

                if not st.session_state.step_cleared[4]:
                    clear_step(4, EXP_TABLE[5])
                    add_item("パケットバッグ")
                    add_log("Webページのデータをパケットに分割しました。")
                    add_log("パケットが異なる経路を通って到着しました。")
                    add_log("パケットを正しい順番に組み立てました。")
            else:
                take_damage(5)
                st.error("パケットドラゴンの反撃だ！順番が違うようだ…")
                st.info("ヒント：パケット番号を確認しよう。")

        if st.session_state.step_cleared[4]:
            st.success("このミッションはクリア済みです。")
            with st.expander("📖 学習ポイント"):
                st.write("データは小さなパケットに分けて送られ、受信側で元の順番に戻されます。")


# =========================================================
# STEP6 ブラウザ神殿（最終ミッション＆最終ボス戦）
# =========================================================
def show_step6():
    st.markdown(
        """
        <div class="parchment-card">
        <h3>最終ミッション　失われたWebページを復活させよ</h3>
        <div class="npc-box">👑 ブラウザ王<br>「6つの通信キーをそろえた者だけが、Webページを完成させられる。」</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    all_keys_ready = len(st.session_state.keys_obtained) >= 6
    if not all_keys_ready:
        st.warning("まだ通信キーがそろっていません。前のエリアに戻って集めましょう。")
        return

    st.success("6つの通信キーがそろっている！ブラウザ王が門を開いた。")

    st.session_state.step6_random_mode = st.checkbox(
        "サーバの応答をランダムにする（教員向けオプション）",
        value=st.session_state.step6_random_mode,
    )

    if st.session_state.status_code is None:
        if st.button("📡 Webサーバへリクエストを送る"):
            if st.session_state.step6_random_mode:
                st.session_state.status_code = random.choice(["200", "404", "500"])
            else:
                st.session_state.status_code = "200"

    if st.session_state.status_code == "404":
        st.error("404 Not Found\n\n目的のページが見つかりません。")
        if st.button("🔁 再挑戦する", key="retry_404"):
            st.session_state.status_code = None
        return

    if st.session_state.status_code == "500":
        st.error("500 Internal Server Error\n\nWebサーバ内部で問題が発生しました。")
        if st.button("🔁 再挑戦する", key="retry_500"):
            st.session_state.status_code = None
        return

    if st.session_state.status_code == "200":
        st.success("200 OK\n\nWebページのデータを正常に取得しました。")
        add_log("Webサーバから200 OKを受信しました。")

        st.markdown("---")
        st.markdown(
            """
            <div class="npc-box">🌑 未描画の魔王<br>
            「HTML、CSS、画像を別々にして、Webページを表示できなくしてやった！」</div>
            """,
            unsafe_allow_html=True,
        )

        stage_labels = ["第1形態：HTML", "第2形態：CSS", "第3形態：画像と装飾", "第4形態：完成"]
        current_stage = st.session_state.render_stage
        st.write(f"現在の形態：{min(current_stage + 1, 4)} / 4")

        if current_stage < 4:
            if st.button("🖌 描画する"):
                st.session_state.render_stage += 1
                st.rerun()

        # 各形態の表示
        if st.session_state.render_stage >= 1:
            st.markdown(
                """
                <div class="parchment-card">
                <h4>テーマパーク案内</h4>
                <p>夢の一日へようこそ</p>
                <p><b>お知らせ</b></p>
                <p><b>施設案内</b></p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption("HTMLの力で、ページの構造が現れた！")
            add_log("HTMLを読み込みました。")

        if st.session_state.render_stage >= 2:
            st.markdown(
                """
                <div style="background:#1a3a5c; border:3px solid #ffd76a; border-radius:14px;
                            padding:16px; color:white;">
                <h4 style="color:#ffd76a;">テーマパーク案内</h4>
                <p>夢の一日へようこそ</p>
                <div style="background:white; color:#222; border-radius:10px; padding:10px; margin-top:6px;">
                お知らせ / 施設案内カード
                </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption("CSSの力で、ページの見た目が整った！")
            add_log("CSSを読み込みました。")

        if st.session_state.render_stage >= 3:
            st.markdown(
                """
                <div style="background:#1a3a5c; border:3px solid #ffd76a; border-radius:14px;
                            padding:16px; color:white; text-align:center;">
                🏰 ✨ 🎡 🎠 ✨<br>
                <h4 style="color:#ffd76a;">テーマパーク案内</h4>
                <p>夢の一日へようこそ</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption("画像と装飾の力で、ページが華やかになった！")
            add_log("画像や装飾を読み込みました。")

        if st.session_state.render_stage >= 4:
            st.markdown(
                """
                <div class="final-page">
                <h2>🏰 テーマパーク案内</h2>
                <h4>夢と冒険の一日へ</h4>
                <p>ようこそ、テーマパーク案内ページへ。</p>
                <div class="final-page-card">
                <b>本日のお知らせ</b>
                <ul><li>開園時間をご確認ください</li><li>イベント情報を公開しました</li></ul>
                </div>
                <div class="final-page-card">
                <b>施設案内</b>
                <ul><li>アトラクション</li><li>レストラン</li><li>ショップ</li></ul>
                </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.success("未描画の魔王を倒した！\n\nWebページの表示に成功しました。")
            add_log("Webページの表示に成功しました。")

            if not st.session_state.step_cleared[5]:
                clear_step(5, EXP_TABLE[6])
                add_item("ブラウザの鏡")
                st.session_state.page_complete = True

            if st.button("🏆 ゲームクリア画面を見る", type="primary"):
                st.session_state.show_clear_screen = True
                st.rerun()

            with st.expander("📖 学習ポイント"):
                st.write("ブラウザは、HTML、CSS、画像などを解析してWebページを表示します。")


# =========================================================
# ゲームクリア画面
# =========================================================
def show_clear_screen():
    st.markdown('<div class="rpg-title">🎉 QUEST CLEAR！ 🎉</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="rpg-subtitle">失われたWebページを取り戻しました！</div>',
        unsafe_allow_html=True,
    )
    st.balloons()

    job_info = JOBS.get(st.session_state.job, JOBS["ネットワーク剣士"])
    st.markdown(
        f"""
        <div class="parchment-card">
        <h3>最終結果</h3>
        <p>プレイヤー名：{st.session_state.player_name}</p>
        <p>職業：{job_info['emoji']} {st.session_state.job}</p>
        <p>最終レベル：{st.session_state.level}</p>
        <p>残りHP：{st.session_state.hp} / 100</p>
        <p>獲得した通信キー：{'、'.join(st.session_state.keys_obtained)}</p>
        <p>獲得したアイテム：{'、'.join(st.session_state.items_obtained)}</p>
        </div>
        <div class="parchment-card" style="text-align:center;">
        <h4>称号</h4>
        <p style="font-size:20px;">🏅 ネットワーク王国の通信勇者</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### 🧭 通信の流れ　まとめ")
    flow = [
        "URLを入力", "URLをプロトコル・ドメイン名・パスに分解", "DNSサーバへ問い合わせ",
        "IPアドレスを取得", "Webサーバへ接続", "HTTP GETリクエストを送信",
        "Webページのデータを受信", "データをパケットに分割して送信",
        "パケットを正しい順番に組み立てる", "HTML・CSS・画像を読み込む",
        "ブラウザがWebページを表示",
    ]
    st.markdown(" 　↓\n".join([f"**{s}**" for s in flow]))

    st.markdown(
        """
        <div class="parchment-card">
        <p>Webページを表示するとき、ブラウザは最初にURLを確認します。</p>
        <p>DNSを使ってドメイン名に対応するIPアドレスを調べ、WebサーバへHTTPリクエストを送信します。</p>
        <p>Webサーバから受信したHTML、CSS、画像などのデータを、ブラウザが解析して組み立てることで、
        Webページが表示されます。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🔄 もう一度冒険する", type="primary", use_container_width=True):
        reset_game()
        st.rerun()


# =========================================================
# 右側パネル：通信ログ・学習ポイント・アイテム・Webページ結果
# =========================================================
def render_right_panel():
    st.markdown("### 📝 冒険の記録")
    log_html = "<div class='log-box'>"
    if st.session_state.adventure_log:
        for i, line in enumerate(st.session_state.adventure_log, start=1):
            log_html += f"{i}. {line}<br>"
    else:
        log_html += "まだ記録がありません。"
    log_html += "</div>"
    st.markdown(log_html, unsafe_allow_html=True)

    st.markdown("### 🎒 獲得アイテム一覧")
    if st.session_state.items_obtained:
        for item in st.session_state.items_obtained:
            info = ITEMS_INFO.get(item, {})
            with st.expander(f"{info.get('emoji', '🎁')} {item}"):
                st.write(info.get("text", ""))
    else:
        st.caption("まだアイテムを持っていません。")

    if st.session_state.render_stage >= 4:
        st.markdown("### 🌐 Webページ表示結果")
        st.success("Webページの表示に成功しました！")


# =========================================================
# メイン処理
# =========================================================
def main():
    inject_css()
    init_session_state()

    if not st.session_state.game_started:
        show_title_screen()
        return

    if st.session_state.show_clear_screen:
        render_sidebar()
        show_clear_screen()
        return

    render_sidebar()

    st.markdown('<div class="rpg-title" style="font-size:28px;">🗝️ ネットワーク・クエスト</div>', unsafe_allow_html=True)
    render_world_map()

    if st.session_state.paused:
        st.info("冒険を一時停止しています。")
        return

    show_levelup_effect()

    left_col, right_col = st.columns([2, 1])

    with left_col:
        step_funcs = [show_step1, show_step2, show_step3, show_step4, show_step5, show_step6]
        step_funcs[st.session_state.current_area]()

    with right_col:
        render_right_panel()


if __name__ == "__main__":
    main()