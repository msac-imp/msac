# streamlit_app.py
# 高等学校「情報Ⅰ」教材
# 「Webページが表示されるまでの通信の流れ」体験学習アプリ

import time
import random
import re

import streamlit as st

# ============================================================
# ページ設定
# ============================================================
st.set_page_config(
    page_title="Webページが表示されるまで",
    page_icon="🌐",
    layout="wide",
)

# ============================================================
# 定数
# ============================================================
TOTAL_STEPS = 6

DNS_CORRECT_ANSWER = "93.184.216.34"
DNS_CHOICES = ["192.168.1.1", "93.184.216.34", "255.255.255.0"]

PACKETS = [
    {"num": 1, "content": "<html><head>", "route": "PC → ルータA → ルータC → Webサーバ"},
    {"num": 2, "content": "<title>学校</title>", "route": "PC → ルータB → ルータC → Webサーバ"},
    {"num": 3, "content": "</head>", "route": "PC → ルータA → ルータD → Webサーバ"},
    {"num": 4, "content": "<body>ようこそ</body>", "route": "PC → ルータB → ルータD → Webサーバ"},
]
# 到着順（送信順とは異なる順番）
ARRIVAL_ORDER = [2, 4, 1, 3]

STATUS_TABLE = [
    ("200 OK", "正常に取得できた"),
    ("404 Not Found", "指定されたページが見つからない"),
    ("500 Internal Server Error", "Webサーバ内部でエラーが発生した"),
]

LEARNING_POINTS = {
    1: "URLは、プロトコル、ドメイン名、パスなどから構成されています。",
    2: "DNSは、ドメイン名をIPアドレスへ変換します。",
    3: "HTTPリクエストは、Webサーバへデータを要求するメッセージです。",
    4: "データはパケットに分割され、ネットワーク上を送られます。",
    5: "ステータスコードを見ると、Webサーバの処理結果が分かります。",
    6: "ブラウザは、HTML、CSS、画像などを解析してWebページを表示します。",
}

FLOW_STAGES = ["利用者PC", "DNSサーバ", "インターネット", "Webサーバ", "ブラウザ表示"]

# STEPごとに、どの機器を強調表示するか（0〜4のインデックス、複数可）
STEP_TO_ACTIVE_STAGE = {
    1: [0],
    2: [0, 1],
    3: [0, 2, 3],
    4: [2],
    5: [3, 2, 0],
    6: [0, 4],
}


# ============================================================
# session_state 初期化
# ============================================================
def init_state():
    """アプリで使用するsession_stateの初期値をまとめて設定する"""
    defaults = {
        "step": 1,
        "url": "https://www.example.com/index.html",
        "url_parsed": False,
        "protocol": "",
        "domain": "",
        "path": "",
        "log": [],
        "dns_answer": None,
        "dns_correct": False,
        "http_sent": False,
        "packet_sent": False,
        "packet_arranged": False,
        "server_response_mode": "正常な応答にする",
        "server_response_code": None,
        "server_response_done": False,
        "render_stage": 1,
        "render_done": False,
        "paused": False,
        "speed": "普通",
        "animation_running": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_all():
    """学習内容をすべて初期化してSTEP1へ戻す"""
    st.session_state.step = 1
    st.session_state.url = "https://www.example.com/index.html"
    st.session_state.url_parsed = False
    st.session_state.protocol = ""
    st.session_state.domain = ""
    st.session_state.path = ""
    st.session_state.log = []
    st.session_state.dns_answer = None
    st.session_state.dns_correct = False
    st.session_state.http_sent = False
    st.session_state.packet_sent = False
    st.session_state.packet_arranged = False
    st.session_state.server_response_mode = "正常な応答にする"
    st.session_state.server_response_code = None
    st.session_state.server_response_done = False
    st.session_state.render_stage = 1
    st.session_state.render_done = False
    st.session_state.paused = False
    st.session_state.animation_running = False


# ============================================================
# 共通ユーティリティ関数
# ============================================================
def add_log(message: str):
    """通信ログに重複しないようメッセージを追加する（自動採番）"""
    existing_messages = [line.split(". ", 1)[1] for line in st.session_state.log if ". " in line]
    if message in existing_messages:
        return
    number = len(st.session_state.log) + 1
    st.session_state.log.append(f"{number}. {message}")


def get_delay(base_seconds: float) -> float:
    """通信速度の選択に応じて待ち時間を調整する"""
    speed = st.session_state.get("speed", "普通")
    factor = {"遅い": 1.8, "普通": 1.0, "速い": 0.4}.get(speed, 1.0)
    return round(base_seconds * factor, 2)


def is_paused() -> bool:
    """一時停止中かどうかを判定する"""
    return st.session_state.get("paused", False)


def parse_url(raw_url: str):
    """URLをプロトコル・ドメイン名・パスに分解する"""
    url = (raw_url or "").strip()

    if url == "":
        url = "https://www.example.com/index.html"

    # プロトコルが省略されている場合は https:// を補う
    if not re.match(r"^[a-zA-Z]+://", url):
        url = "https://" + url

    match = re.match(r"^(https?://)([^/]+)(/.*)?$", url)
    if not match:
        # 解析できない場合は初期値にフォールバック
        return "https://", "www.example.com", "/index.html"

    protocol = match.group(1)
    domain = match.group(2)
    path = match.group(3) if match.group(3) else "/"

    return protocol, domain, path


def go_next_step():
    if st.session_state.step < TOTAL_STEPS:
        st.session_state.step += 1


def go_prev_step():
    if st.session_state.step > 1:
        st.session_state.step -= 1


def can_go_next() -> bool:
    """現在のSTEPの必要な操作が完了しているかどうか"""
    step = st.session_state.step
    if step == 1:
        return st.session_state.url_parsed
    if step == 2:
        return st.session_state.dns_correct
    if step == 3:
        return st.session_state.http_sent
    if step == 4:
        return st.session_state.packet_arranged
    if step == 5:
        return st.session_state.server_response_done and st.session_state.server_response_code == 200
    if step == 6:
        return st.session_state.render_done
    return False


# ============================================================
# CSS（デザイン）
# ============================================================
def inject_css():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #f4f9ff;
        }
        .main-title {
            font-size: 2.1rem;
            font-weight: 800;
            color: #1a4fa3;
            margin-bottom: 0.1rem;
        }
        .sub-title {
            font-size: 1.05rem;
            color: #33608f;
            margin-bottom: 1.2rem;
        }
        .card {
            background-color: #ffffff;
            border-radius: 16px;
            padding: 16px 18px;
            box-shadow: 0 3px 10px rgba(30, 80, 160, 0.12);
            margin-bottom: 14px;
            border: 1px solid #dce8fb;
        }
        .card-blue { background-color: #e8f1ff; }
        .card-green { background-color: #e9fbef; }
        .card-yellow { background-color: #fff9e6; }
        .card-pink { background-color: #ffeef3; }
        .card-purple { background-color: #f2ecff; }

        .step-badge {
            display: inline-block;
            background-color: #1a4fa3;
            color: #ffffff;
            border-radius: 999px;
            padding: 4px 14px;
            font-weight: 700;
            font-size: 0.9rem;
            margin-bottom: 10px;
        }

        .flow-box {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            background-color: #ffffff;
            border-radius: 16px;
            padding: 14px 10px;
            box-shadow: 0 3px 10px rgba(30, 80, 160, 0.10);
            margin-bottom: 18px;
        }
        .flow-node {
            flex: 1;
            min-width: 90px;
            text-align: center;
            padding: 10px 6px;
            margin: 4px;
            border-radius: 12px;
            color: #9fb3cc;
            background-color: #f3f6fb;
            font-size: 0.85rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .flow-node-active {
            color: #ffffff;
            background-color: #1a4fa3;
            box-shadow: 0 4px 10px rgba(26, 79, 163, 0.45);
            border: 2px solid #0f3474;
            transform: scale(1.05);
        }
        .flow-arrow {
            font-size: 1.3rem;
            color: #9fb3cc;
            padding: 0 2px;
        }

        .log-box {
            background-color: #0b1f3a;
            color: #eaf3ff;
            border-radius: 14px;
            padding: 14px 16px;
            height: 260px;
            overflow-y: auto;
            font-family: "Consolas", "Courier New", monospace;
            font-size: 0.85rem;
            line-height: 1.6;
        }

        .browser-frame {
            border: 2px solid #b9cdf0;
            border-radius: 14px;
            background-color: #ffffff;
            padding: 14px;
            min-height: 160px;
        }

        .packet-card {
            display: inline-block;
            background-color: #eef4ff;
            border: 2px solid #1a4fa3;
            border-radius: 10px;
            padding: 8px 12px;
            margin: 4px;
            font-family: monospace;
            font-size: 0.85rem;
        }

        .error-box {
            background-color: #ffe3e3;
            border-left: 6px solid #d1433f;
            border-radius: 10px;
            padding: 12px 14px;
            color: #7a1f1c;
            font-weight: 600;
        }
        .success-box {
            background-color: #e1f7e6;
            border-left: 6px solid #2f9e44;
            border-radius: 10px;
            padding: 12px 14px;
            color: #1e5c2c;
            font-weight: 600;
        }
        .warn-box {
            background-color: #fff3cd;
            border-left: 6px solid #e0a800;
            border-radius: 10px;
            padding: 12px 14px;
            color: #6b5300;
            font-weight: 600;
        }

        .school-site {
            background-color: #eef5ff;
            border-radius: 14px;
            padding: 18px;
        }
        .school-site h1 {
            color: #1a4fa3;
        }
        .school-card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 10px 14px;
            margin: 8px 0;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        }
        .school-btn {
            display: inline-block;
            background-color: #1a4fa3;
            color: white;
            padding: 6px 16px;
            border-radius: 8px;
            font-weight: 600;
            margin-top: 6px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 全体の通信フロー表示（画面上部）
# ============================================================
def show_flow():
    active_indexes = STEP_TO_ACTIVE_STAGE.get(st.session_state.step, [])
    icons = ["💻", "📡", "🌐", "🖥", "🧭"]

    html = '<div class="flow-box">'
    for i, (icon, name) in enumerate(zip(icons, FLOW_STAGES)):
        css_class = "flow-node flow-node-active" if i in active_indexes else "flow-node"
        html += f'<div class="{css_class}">{icon}<br>{name}</div>'
        if i < len(FLOW_STAGES) - 1:
            html += '<div class="flow-arrow">➡</div>'
    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


# ============================================================
# サイドバー
# ============================================================
def render_sidebar():
    st.sidebar.header("⚙️ 学習コントロール")

    st.sidebar.text_input("URLを入力してください", key="url")

    st.sidebar.selectbox("通信速度", ["遅い", "普通", "速い"], key="speed")

    st.sidebar.markdown(f"### 現在のSTEP：{st.session_state.step} / {TOTAL_STEPS}")
    st.sidebar.progress(st.session_state.step / TOTAL_STEPS)

    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("⬅ 戻る", use_container_width=True):
            go_prev_step()
            st.rerun()
    with col2:
        next_disabled = not can_go_next()
        if st.button("次へ ➡", use_container_width=True, disabled=next_disabled):
            go_next_step()
            st.rerun()

    pause_label = "再開 ▶" if st.session_state.paused else "⏸ 一時停止"
    if st.sidebar.button(pause_label, use_container_width=True):
        st.session_state.paused = not st.session_state.paused
        st.rerun()

    if st.sidebar.button("🔄 リセット", use_container_width=True):
        reset_all()
        st.rerun()

    if st.session_state.paused:
        st.sidebar.info("通信シミュレーションを一時停止しています。")


# ============================================================
# 右カラム：通信ログ・学習ポイント・Webページ表示
# ============================================================
def render_right_column(webpage_placeholder_content=None):
    st.markdown('<div class="card"><b>📜 通信ログ</b></div>', unsafe_allow_html=True)
    log_html = "<br>".join(st.session_state.log) if st.session_state.log else "（まだログはありません）"
    st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)

    st.markdown('<div class="card card-yellow"><b>💡 現在の学習ポイント</b><br>' +
                LEARNING_POINTS.get(st.session_state.step, "") + '</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><b>🖥 Webページの表示結果</b></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="browser-frame">', unsafe_allow_html=True)
        if webpage_placeholder_content:
            webpage_placeholder_content()
        else:
            st.caption("まだWebページは表示されていません。学習を進めましょう。")
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# STEP1 URLを分解する
# ============================================================
def step1():
    st.markdown('<span class="step-badge">STEP 1</span>', unsafe_allow_html=True)
    st.subheader("URLを分解する")

    st.write("入力されたURLを、プロトコル・ドメイン名・パスの3つの要素に分けて確認しましょう。")

    if st.button("🔍 通信開始", key="step1_start"):
        protocol, domain, path = parse_url(st.session_state.url)
        st.session_state.protocol = protocol
        st.session_state.domain = domain
        st.session_state.path = path
        st.session_state.url_parsed = True
        add_log("URLを解析しました。")
        add_log("プロトコル、ドメイン名、パスを確認しました。")
        st.success("URLの解析が完了しました。")

    if not st.session_state.url or st.session_state.url.strip() == "":
        st.info("URLが空欄です。初期値（https://www.example.com/index.html）を使用します。")

    if st.session_state.url_parsed:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f'<div class="card card-blue"><b>プロトコル</b><br>'
                f'<span style="font-size:1.3rem;">{st.session_state.protocol}</span></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div class="card card-green"><b>ドメイン名</b><br>'
                f'<span style="font-size:1.3rem;">{st.session_state.domain}</span></div>',
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f'<div class="card card-pink"><b>パス</b><br>'
                f'<span style="font-size:1.3rem;">{st.session_state.path}</span></div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <div class="card">
            <b>📘 解説</b><br>
            プロトコルは、コンピュータ同士が通信するときの決まりです。<br><br>
            ドメイン名は、接続先を人間に分かりやすく表した名前です。<br><br>
            パスは、Webサーバ内にあるファイルやページの場所を表します。
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.warning("「通信開始」ボタンを押して、URLを解析してください。")


# ============================================================
# STEP2 DNSでIPアドレスを調べる
# ============================================================
def step2():
    st.markdown('<span class="step-badge">STEP 2</span>', unsafe_allow_html=True)
    st.subheader("DNSでIPアドレスを調べる")

    domain = st.session_state.domain or "www.example.com"
    st.write(f"問題：**{domain}** のIPアドレスはどれでしょうか。")

    answer = st.radio("選択肢", DNS_CHOICES, key="dns_radio")

    if st.button("✅ 回答する", key="step2_answer"):
        st.session_state.dns_answer = answer
        if answer == DNS_CORRECT_ANSWER:
            st.session_state.dns_correct = True
            add_log("DNSサーバへ問い合わせました。")
            add_log("ドメイン名に対応するIPアドレスを取得しました。")
            add_log(f"取得したIPアドレス：{DNS_CORRECT_ANSWER}")
        else:
            st.session_state.dns_correct = False

    if st.session_state.dns_answer is not None:
        if st.session_state.dns_correct:
            st.markdown(
                '<div class="success-box">正解です。<br>DNSサーバがドメイン名をIPアドレスに変換しました。</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="error-box">もう一度考えてみましょう。<br>'
                'DNSは、ドメイン名に対応するIPアドレスを調べる仕組みです。</div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <div class="card">
        <b>📘 学習ポイント</b><br>
        コンピュータ同士の通信では、ドメイン名ではなくIPアドレスを使って接続先を識別します。<br><br>
        DNSは、人間が覚えやすいドメイン名を、コンピュータが通信に使うIPアドレスへ変換します。
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.dns_correct:
        st.info("正解するまでは、次のSTEPへ進めません。")


# ============================================================
# STEP3 HTTPリクエストを送る
# ============================================================
def step3():
    st.markdown('<span class="step-badge">STEP 3</span>', unsafe_allow_html=True)
    st.subheader("HTTPリクエストを送る")

    domain = st.session_state.domain or "www.example.com"
    path = st.session_state.path or "/index.html"

    st.code(f"GET {path} HTTP/1.1\nHost: {domain}", language="text")

    st.markdown(
        """
        <div class="card">
        <b>📘 解説</b><br>
        GETは、Webサーバに「指定したファイルを送ってください」と依頼する命令です。<br><br>
        ブラウザは、HTTPという通信の決まりに従って、Webサーバへリクエストを送信します。
        </div>
        """,
        unsafe_allow_html=True,
    )

    if is_paused():
        st.warning("通信シミュレーションを一時停止しています。再開してから送信してください。")

    if st.button("📤 GETリクエストを送信", key="step3_send", disabled=is_paused()):
        run_http_animation(domain, path)


def run_http_animation(domain, path):
    steps_text = [
        "WebサーバのIPアドレスを確認しています…",
        "Webサーバへ接続しています…",
        "HTTPリクエストを作成しています…",
        "GETリクエストを送信しています…",
        "送信完了しました。",
    ]
    progress = st.progress(0)
    status_area = st.empty()

    with st.status("HTTP通信を実行中…", expanded=True) as status:
        for i, text in enumerate(steps_text):
            if is_paused():
                st.warning("一時停止中のため、処理を中断しました。再開後にもう一度お試しください。")
                status.update(label="一時停止中", state="error")
                return
            status_area.info(text)
            time.sleep(get_delay(0.5))
            progress.progress((i + 1) / len(steps_text))
        status.update(label="通信完了", state="complete")

    st.success("Webサーバへの接続とGETリクエストの送信が完了しました。")

    st.session_state.http_sent = True
    add_log("Webサーバへ接続しました。")
    add_log("HTTP GETリクエストを作成しました。")
    add_log("HTTP GETリクエストを送信しました。")


# ============================================================
# STEP4 パケット通信を体験する
# ============================================================
def step4():
    st.markdown('<span class="step-badge">STEP 4</span>', unsafe_allow_html=True)
    st.subheader("パケット通信を体験する")

    st.write("HTMLデータは、次の4つのパケットに分割されて送信されます。")

    cols = st.columns(4)
    for i, packet in enumerate(PACKETS):
        with cols[i]:
            st.markdown(
                f'<div class="packet-card"><b>パケット{packet["num"]}</b><br>{packet["content"]}<br>'
                f'<small>{packet["route"]}</small></div>',
                unsafe_allow_html=True,
            )

    if is_paused():
        st.warning("通信シミュレーションを一時停止しています。再開してから送信してください。")

    if st.button("📦 パケットを送信", key="step4_send", disabled=is_paused()):
        run_packet_animation()

    st.markdown(
        """
        <div class="card">
        <b>📘 解説</b><br>
        大きなデータは、小さなパケットに分けて送られます。<br><br>
        パケットは、それぞれ異なる経路を通ることがあります。<br><br>
        到着する順番が変わっても、受信側がパケット番号を確認し、正しい順番に戻します。
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.packet_arranged:
        order_text = " → ".join([f"パケット{p}" for p in sorted(ARRIVAL_ORDER)])
        st.markdown(
            f'<div class="success-box">{order_text}<br>データを正しい順番に組み立てました。</div>',
            unsafe_allow_html=True,
        )


def run_packet_animation():
    add_log("HTMLデータを4つのパケットに分割しました。")

    progress = st.progress(0)
    status_area = st.empty()
    arrival_area = st.empty()

    total = len(ARRIVAL_ORDER)
    arrived_display = []

    with st.status("パケットをネットワーク上へ送信中…", expanded=True) as status:
        for i, packet_num in enumerate(ARRIVAL_ORDER):
            if is_paused():
                st.warning("一時停止中のため、処理を中断しました。再開後にもう一度お試しください。")
                status.update(label="一時停止中", state="error")
                return
            status_area.info(f"パケット{packet_num} が届きました。")
            arrived_display.append(packet_num)
            arrival_area.write("到着順： " + " → ".join([f"パケット{n}" for n in arrived_display]))
            time.sleep(get_delay(0.6))
            progress.progress((i + 1) / total)
        status.update(label="全パケットが到着", state="complete")

    add_log("パケットをネットワーク上へ送信しました。")
    add_log("パケットが異なる順番で到着しました。")

    st.info("受信側でパケット番号を確認し、正しい順番に組み立て直します…")
    time.sleep(get_delay(0.6))

    st.session_state.packet_sent = True
    st.session_state.packet_arranged = True
    add_log("パケットを正しい順番に組み立てました。")


# ============================================================
# STEP5 Webサーバの応答を確認する
# ============================================================
def step5():
    st.markdown('<span class="step-badge">STEP 5</span>', unsafe_allow_html=True)
    st.subheader("Webサーバの応答を確認する")

    st.radio(
        "応答方法を選択してください",
        ["正常な応答にする", "ランダムにする"],
        key="server_response_mode",
    )

    if is_paused():
        st.warning("通信シミュレーションを一時停止しています。再開してから受信してください。")

    button_label = "📥 サーバの応答を受信"
    if st.session_state.server_response_done and st.session_state.server_response_code != 200:
        button_label = "🔁 もう一度応答を受信する"

    if st.button(button_label, key="step5_receive", disabled=is_paused()):
        if st.session_state.server_response_mode == "正常な応答にする":
            code = 200
        else:
            code = random.choice([200, 404, 500])

        st.session_state.server_response_code = code
        st.session_state.server_response_done = True

        if code == 200:
            add_log("Webサーバから200 OKを受信しました。")
            add_log("HTML、CSS、画像などのデータを受信します。")
        elif code == 404:
            add_log("Webサーバから404 Not Foundを受信しました。")
            add_log("指定されたページが見つかりませんでした。")
        else:
            add_log("Webサーバから500 Internal Server Errorを受信しました。")
            add_log("Webサーバ内部でエラーが発生しました。")

    code = st.session_state.server_response_code
    if code == 200:
        st.markdown(
            '<div class="success-box">200 OK：正常にWebページのデータを取得できました。</div>',
            unsafe_allow_html=True,
        )
    elif code == 404:
        st.markdown(
            '<div class="error-box">404 Not Found：指定されたページが見つかりません。</div>',
            unsafe_allow_html=True,
        )
    elif code == 500:
        st.markdown(
            '<div class="warn-box">500 Internal Server Error：Webサーバ内部でエラーが発生しました。</div>',
            unsafe_allow_html=True,
        )

    st.markdown("#### 📊 ステータスコードの意味")
    st.table({"ステータスコード": [s[0] for s in STATUS_TABLE], "意味": [s[1] for s in STATUS_TABLE]})

    if code in (404, 500):
        st.info("200 OKを受信すると、次のSTEPへ進めるようになります。")


def render_webpage_step5():
    code = st.session_state.server_response_code
    if code == 404:
        st.markdown(
            '<div style="text-align:center;"><h1>404</h1><p>ページが見つかりません</p></div>',
            unsafe_allow_html=True,
        )
    elif code == 500:
        st.markdown(
            '<div style="text-align:center;"><h1>500</h1><p>サーバエラーが発生しました</p></div>',
            unsafe_allow_html=True,
        )
    elif code == 200:
        st.caption("データを受信しました。STEP6でWebページを描画します。")


# ============================================================
# STEP6 ブラウザがWebページを描画する
# ============================================================
def step6():
    st.markdown('<span class="step-badge">STEP 6</span>', unsafe_allow_html=True)
    st.subheader("ブラウザがWebページを描画する")

    stage_names = ["HTMLのみ", "CSSを適用", "画像を表示", "完成したWebページ"]
    st.write(f"現在の描画段階：**第{st.session_state.render_stage}段階（{stage_names[st.session_state.render_stage - 1]}）**")

    if is_paused():
        st.warning("通信シミュレーションを一時停止しています。再開してから進めてください。")

    if st.session_state.render_stage < 4:
        if st.button("🎨 次の描画段階へ", key="step6_next_stage", disabled=is_paused()):
            with st.spinner("描画処理中…"):
                time.sleep(get_delay(0.5))
            advance_render_stage()
            st.rerun()
    else:
        if not st.session_state.render_done:
            st.session_state.render_done = True
            add_log("ブラウザがHTML、CSS、画像を組み立てました。")
            add_log("Webページの描画が完了しました。")
        st.success("Webページの表示が完了しました。")

    st.markdown(
        """
        <div class="card">
        <b>📘 解説</b><br>
        ブラウザは、HTMLでページの構造を作ります。<br><br>
        次にCSSで文字の色や配置などの見た目を整えます。<br><br>
        最後に画像などを追加し、Webページを完成させます。
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.render_done:
        st.markdown("## ✅ 通信完了")
        render_summary_flowchart()


def advance_render_stage():
    stage = st.session_state.render_stage
    if stage == 1:
        add_log("HTMLを読み込みました。")
        add_log("Webページの構造を作成しました。")
    elif stage == 2:
        add_log("CSSを読み込みました。")
        add_log("Webページの見た目を整えました。")
    elif stage == 3:
        add_log("画像データを読み込みました。")
        add_log("Webページに画像を表示しました。")
    st.session_state.render_stage = min(stage + 1, 4)


def render_webpage_step6():
    stage = st.session_state.render_stage

    if stage == 1:
        st.markdown(
            """
            学校Webサイト

            ようこそ、学校Webサイトへ。

            お知らせ

            行事予定
            """
        )
    elif stage == 2:
        st.markdown(
            """
            <div class="school-site">
            <h3>学校Webサイト</h3>
            <p>ようこそ、学校Webサイトへ。</p>
            <div class="school-card">お知らせ</div>
            <div class="school-card">行事予定</div>
            <div class="school-btn">詳しく見る</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif stage == 3:
        st.markdown(
            """
            <div class="school-site">
            <h3>🏫 学校Webサイト 📚</h3>
            <p>ようこそ、学校Webサイトへ。🎓</p>
            <div class="school-card">お知らせ</div>
            <div class="school-card">行事予定</div>
            <div class="school-btn">詳しく見る</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="school-site">
            <h1>🏫 学校Webサイト</h1>
            <p><i>学び・つながり・未来へ</i></p>
            <p>ようこそ、学校Webサイトへ。</p>
            <div class="school-card">
            <b>📢 お知らせ</b><br>
            ・学校説明会を開催します<br>
            ・文化祭の日程が決まりました
            </div>
            <div class="school-card">
            <b>📅 行事予定</b><br>
            ・体育祭<br>
            ・文化祭<br>
            ・修学旅行
            </div>
            <div class="school-btn">🎓 詳しく見る</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_summary_flowchart():
    flow_items = [
        "URLを入力",
        "URLを解析",
        "DNSサーバへ問い合わせ",
        "IPアドレスを取得",
        "Webサーバへ接続",
        "HTTP GETリクエストを送信",
        "Webサーバから応答",
        "HTML・CSS・画像を受信",
        "パケットを正しい順番に組み立てる",
        "ブラウザがデータを解析",
        "Webページの表示完了",
    ]
    html = '<div class="card" style="text-align:center;">'
    for i, item in enumerate(flow_items):
        html += f"<div>{item}</div>"
        if i < len(flow_items) - 1:
            html += "<div>↓</div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    st.markdown(
        """
        <div class="card card-blue">
        Webページは、URLを入力するとDNSでIPアドレスを調べ、WebサーバへHTTPリクエストを送ることでデータを取得します。<br><br>
        受信したHTML、CSS、画像などのデータをブラウザが解析して組み立てることで、Webページが画面に表示されます。
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🔁 もう一度最初から学習する", key="restart_button"):
        reset_all()
        st.rerun()


# ============================================================
# 右カラムのWebページ表示内容を決定する
# ============================================================
def right_webpage_renderer():
    step = st.session_state.step
    if step == 5 and st.session_state.server_response_done:
        render_webpage_step5()
    elif step == 6:
        render_webpage_step6()
    elif step > 5 and st.session_state.get("server_response_code") == 200:
        render_webpage_step6()
    else:
        st.caption("まだWebページは表示されていません。学習を進めましょう。")


# ============================================================
# メイン処理
# ============================================================
def main():
    init_state()
    inject_css()

    st.markdown('<div class="main-title">🌐 Webページが表示されるまで</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">URLを入力してからWebページが表示されるまでの通信を、操作しながら学習しよう</div>',
        unsafe_allow_html=True,
    )

    render_sidebar()
    show_flow()

    left_col, right_col = st.columns([1.3, 1])

    with left_col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        step = st.session_state.step
        if step == 1:
            step1()
        elif step == 2:
            step2()
        elif step == 3:
            step3()
        elif step == 4:
            step4()
        elif step == 5:
            step5()
        elif step == 6:
            step6()
        else:
            st.session_state.step = 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:
        render_right_column(webpage_placeholder_content=right_webpage_renderer)


if __name__ == "__main__":
    main()