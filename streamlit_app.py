import streamlit as st

st.set_page_config(
    page_title="Webページが届くまで",
    page_icon="🌐",
    layout="wide",
)

# ----------------------------------------------------------------------------
# データ定義
# ----------------------------------------------------------------------------
STEPS = [
    {
        "no": 1,
        "actor": "CLIENT → DNS",
        "title": "ドメイン名の問い合わせ",
        "text": "クライアントは、URLからドメイン名を取り出し、Webページの"
                "IPアドレスをDNSサーバに問い合わせる。",
        "path": "client_to_dns",
    },
    {
        "no": 2,
        "actor": "DNS → CLIENT",
        "title": "IPアドレスの通知",
        "text": "DNSサーバは、調べたIPアドレスをクライアントに通知する。",
        "path": "dns_to_client",
    },
    {
        "no": 3,
        "actor": "CLIENT → ROUTER",
        "title": "リクエストパケットの送信",
        "text": "クライアントは、閲覧したいWebページのURLのファイル名に、"
                "WebサーバのIPアドレスと送信元のIPアドレスなどを添付し、"
                "パケットとして送信する。",
        "path": "client_to_router",
    },
    {
        "no": 4,
        "actor": "ROUTER → SERVER",
        "title": "ルータによる中継",
        "text": "インターネット上にあるルータは、パケットを次々と中継して"
                "目的のWebサーバに届ける。",
        "path": "router_to_server",
    },
    {
        "no": 5,
        "actor": "SERVER → ROUTER",
        "title": "レスポンスの分割送信",
        "text": "Webサーバは、Webページのデータをいくつかのパケットに"
                "分割してインターネット上に送信する。",
        "path": "server_to_router",
    },
    {
        "no": 6,
        "actor": "ROUTER → CLIENT",
        "title": "ページデータの到着",
        "text": "Webページのデータは、ルータを次々と経由してクライアントに"
                "届けられる。",
        "path": "router_to_client",
    },
]

# ----------------------------------------------------------------------------
# セッション状態
# ----------------------------------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = 1

def go_to(n: int) -> None:
    st.session_state.step = max(1, min(6, n))

# ----------------------------------------------------------------------------
# スタイル（すべてこのファイル内に完結）
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    :root{
        --ink:#e8edf5;
        --bg:#0b1220;
        --panel:#121b2e;
        --line:#2a3752;
        --amber:#f5a623;
        --cyan:#38bdf8;
        --dim:#5b6b8c;
    }
    .stApp{
        background:
            radial-gradient(circle at 15% 0%, #142038 0%, transparent 45%),
            radial-gradient(circle at 85% 100%, #14243a 0%, transparent 45%),
            var(--bg);
        color:var(--ink);
    }
    section[data-testid="stSidebar"]{
        background:#0e1626;
        border-right:1px solid var(--line);
    }
    .app-header{
        font-family:'Courier New', monospace;
        letter-spacing:.08em;
        color:var(--dim);
        font-size:.8rem;
        text-transform:uppercase;
        margin-bottom:.2rem;
    }
    .app-title{
        font-size:2.1rem;
        font-weight:800;
        margin:0 0 1.4rem 0;
        color:var(--ink);
    }
    .app-title span{color:var(--amber);}
    .step-card{
        background:var(--panel);
        border:1px solid var(--line);
        border-radius:10px;
        padding:1.4rem 1.6rem;
        margin-top:1rem;
    }
    .step-tag{
        display:inline-block;
        font-family:'Courier New', monospace;
        font-size:.75rem;
        letter-spacing:.1em;
        color:var(--bg);
        background:var(--amber);
        padding:.15rem .55rem;
        border-radius:4px;
        font-weight:700;
        margin-bottom:.6rem;
    }
    .step-heading{
        font-size:1.35rem;
        font-weight:700;
        margin:.1rem 0 .6rem 0;
    }
    .step-body{
        font-size:1.02rem;
        line-height:1.85;
        color:#c8d3e6;
    }
    .step-actor{
        font-family:'Courier New', monospace;
        color:var(--cyan);
        font-size:.85rem;
        letter-spacing:.05em;
        margin-bottom:.3rem;
    }
    .legend{
        font-family:'Courier New', monospace;
        font-size:.78rem;
        color:var(--dim);
        margin-top:.6rem;
    }
    .legend b{color:var(--amber);}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# SVG図の生成
# ----------------------------------------------------------------------------
def build_diagram(active_path: str) -> str:
    """ネットワーク構成図（クライアント／DNS／ルータ群／Webサーバ）をSVGで返す"""

    def edge_style(name: str):
        if name == active_path:
            return "var(--amber)", "4", "1"
        return "var(--dim)", "2", "0.35"

    c1, w1, o1 = edge_style("client_to_dns")
    c2, w2, o2 = edge_style("dns_to_client")
    c3, w3, o3 = edge_style("client_to_router")
    c4, w4, o4 = edge_style("router_to_server")
    c5, w5, o5 = edge_style("server_to_router")
    c6, w6, o6 = edge_style("router_to_client")

    def packet(path_id: str, color: str, active: bool, dur="1.6s"):
        if not active:
            return ""
        return f"""
        <circle r="7" fill="{color}">
          <animateMotion dur="{dur}" repeatCount="indefinite">
            <mpath href="#{path_id}"/>
          </animateMotion>
        </circle>
        """

    svg = f"""
    <svg viewBox="0 0 980 460" xmlns="http://www.w3.org/2000/svg"
         style="width:100%;height:auto;font-family:'Courier New',monospace;">
      <defs>
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3"
                orient="auto" markerUnits="strokeWidth">
          <path d="M0,0 L0,6 L9,3 z" fill="context-stroke"/>
        </marker>
      </defs>

      <!-- DNSサーバ -->
      <path id="p_c2d" d="M170,330 L170,120" fill="none"/>
      <path id="p_d2c" d="M210,120 L210,330" fill="none"/>
      <line x1="170" y1="330" x2="170" y2="120" stroke="{c1}" stroke-width="{w1}"
            stroke-opacity="{o1}" stroke-dasharray="{ '0' if active_path=='client_to_dns' else '6,6'}"
            marker-end="url(#arrow)"/>
      <line x1="210" y1="120" x2="210" y2="330" stroke="{c2}" stroke-width="{w2}"
            stroke-opacity="{o2}" stroke-dasharray="{ '0' if active_path=='dns_to_client' else '6,6'}"
            marker-end="url(#arrow)"/>
      {packet('p_c2d', c1, active_path=='client_to_dns')}
      {packet('p_d2c', c2, active_path=='dns_to_client')}

      <rect x="110" y="40" width="160" height="70" rx="10" fill="#182338" stroke="{c1 if active_path in ('client_to_dns','dns_to_client') else 'var(--line)'}" stroke-width="2"/>
      <text x="190" y="70" text-anchor="middle" fill="var(--ink)" font-size="15" font-weight="700">DNSサーバ</text>
      <text x="190" y="92" text-anchor="middle" fill="var(--dim)" font-size="11">名前解決</text>

      <!-- クライアント -->
      <rect x="40" y="330" width="150" height="80" rx="10" fill="#182338" stroke="var(--cyan)" stroke-width="2"/>
      <text x="115" y="365" text-anchor="middle" fill="var(--ink)" font-size="15" font-weight="700">クライアント</text>
      <text x="115" y="388" text-anchor="middle" fill="var(--dim)" font-size="11">ブラウザ</text>

      <!-- ルータ群（雲） -->
      <ellipse cx="500" cy="230" rx="230" ry="120" fill="#101a2c" stroke="var(--line)" stroke-width="2"/>
      <text x="500" y="140" text-anchor="middle" fill="var(--dim)" font-size="12">インターネット（ルータが中継）</text>
      <g fill="#20304e" stroke="var(--line)" stroke-width="1.5">
        <rect x="400" y="200" width="60" height="34" rx="6"/>
        <rect x="480" y="250" width="60" height="34" rx="6"/>
        <rect x="560" y="190" width="60" height="34" rx="6"/>
      </g>
      <g fill="var(--dim)" font-size="10" text-anchor="middle">
        <text x="430" y="221">router</text>
        <text x="510" y="271">router</text>
        <text x="590" y="211">router</text>
      </g>

      <!-- クライアント〜ルータ群 -->
      <path id="p_c2r" d="M195,370 L400,300" fill="none"/>
      <path id="p_r2c" d="M400,320 L195,390" fill="none"/>
      <line x1="195" y1="370" x2="400" y2="300" stroke="{c3}" stroke-width="{w3}"
            stroke-opacity="{o3}" stroke-dasharray="{ '0' if active_path=='client_to_router' else '6,6'}"
            marker-end="url(#arrow)"/>
      <line x1="400" y1="320" x2="195" y2="390" stroke="{c6}" stroke-width="{w6}"
            stroke-opacity="{o6}" stroke-dasharray="{ '0' if active_path=='router_to_client' else '6,6'}"
            marker-end="url(#arrow)"/>
      {packet('p_c2r', c3, active_path=='client_to_router')}
      {packet('p_r2c', c6, active_path=='router_to_client')}

      <!-- ルータ群〜Webサーバ -->
      <path id="p_r2s" d="M600,300 L800,370" fill="none"/>
      <path id="p_s2r" d="M800,390 L600,320" fill="none"/>
      <line x1="600" y1="300" x2="800" y2="370" stroke="{c4}" stroke-width="{w4}"
            stroke-opacity="{o4}" stroke-dasharray="{ '0' if active_path=='router_to_server' else '6,6'}"
            marker-end="url(#arrow)"/>
      <line x1="800" y1="390" x2="600" y2="320" stroke="{c5}" stroke-width="{w5}"
            stroke-opacity="{o5}" stroke-dasharray="{ '0' if active_path=='server_to_router' else '6,6'}"
            marker-end="url(#arrow)"/>
      {packet('p_r2s', c4, active_path=='router_to_server')}
      {packet('p_s2r', c5, active_path=='server_to_router')}

      <!-- Webサーバ -->
      <rect x="790" y="330" width="150" height="80" rx="10" fill="#182338" stroke="var(--amber)" stroke-width="2"/>
      <text x="865" y="365" text-anchor="middle" fill="var(--ink)" font-size="15" font-weight="700">Webサーバ</text>
      <text x="865" y="388" text-anchor="middle" fill="var(--dim)" font-size="11">Webページ提供</text>
    </svg>
    """
    return svg


# ----------------------------------------------------------------------------
# サイドバー：ステップ操作
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="app-header">STEP NAVIGATOR</div>', unsafe_allow_html=True)
    st.markdown("### 手順を選択")
    labels = [f"{s['no']}. {s['title']}" for s in STEPS]
    choice = st.radio(
        "手順",
        options=list(range(1, 7)),
        format_func=lambda n: labels[n - 1],
        index=st.session_state.step - 1,
        label_visibility="collapsed",
    )
    if choice != st.session_state.step:
        st.session_state.step = choice

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("◀ 前へ", use_container_width=True, disabled=st.session_state.step == 1):
            go_to(st.session_state.step - 1)
            st.rerun()
    with col_b:
        if st.button("次へ ▶", use_container_width=True, disabled=st.session_state.step == 6):
            go_to(st.session_state.step + 1)
            st.rerun()

    st.markdown("---")
    st.markdown(
        '<div class="legend">'
        "<b>橙色の実線</b> = 現在の通信<br>"
        "灰色の点線 = その他の経路"
        "</div>",
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------------
# メイン画面
# ----------------------------------------------------------------------------
st.markdown('<div class="app-header">HOW A WEB PAGE REACHES YOU</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-title">URLを入力してから<span>Webページが表示される</span>までの流れ</div>',
    unsafe_allow_html=True,
)

current = STEPS[st.session_state.step - 1]

st.markdown(build_diagram(current["path"]), unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="step-card">
        <div class="step-tag">STEP {current['no']} / 6</div>
        <div class="step-actor">{current['actor']}</div>
        <div class="step-heading">{current['title']}</div>
        <div class="step-body">{current['text']}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 全体プロセスの一覧（折りたたみ）
with st.expander("全6ステップをまとめて確認する"):
    for s in STEPS:
        marker = "👉" if s["no"] == current["no"] else "・"
        st.markdown(f"{marker} **STEP {s['no']}｜{s['title']}** — {s['text']}")