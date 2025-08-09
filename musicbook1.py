import base64
from urllib.parse import urlparse
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Picture Jukebox", page_icon="🎵", layout="centered")

# ===== ユーザー指定（初期値） =====
DEFAULT_IMAGE_URL = "https://github.com/aki3note/musicbook1/blob/main/baackground.jpg"
DEFAULT_AUDIO_URL = "https://github.com/aki3note/musicbook1/blob/main/06.mp3"

# 盤面（この画像に合わせてだいたい良い感じに入る値。必要なら調整OK）
ROWS, COLS = 4, 4
GRID_BOUNDS = dict(top=16.5, left=4.5, width=91.0, height=77.0)  # % 単位
CELL_GAP = 2.0        # タイル間隔（%）
RADIUS = 12           # 角丸（デバッグ時の見た目用のみ）

# ---------- ヘルパ ----------
def to_raw_url(url: str) -> str:
    """GitHubの blob URL を Raw URL に変換（その他はそのまま）。"""
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        if parsed.netloc == "github.com" and "/blob/" in parsed.path:
            user_repo, branch_and_path = parsed.path.strip("/").split("/blob/", 1)
            return f"https://raw.githubusercontent.com/{user_repo}/{branch_and_path}"
        return url
    except Exception:
        return url

def read_image_as_data_uri(src: str) -> str:
    # URLはそのまま表示。ローカルファイルならBase64に。
    if src.startswith(("http://", "https://")):
        return src
    p = Path(src)
    mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
    data = p.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"

def gen_grid_hotspots(rows, cols, bounds, gap=0.0):
    top = bounds["top"]; left = bounds["left"]
    W = bounds["width"]; H = bounds["height"]
    cell_w = (W - gap*(cols-1)) / cols
    cell_h = (H - gap*(rows-1)) / rows

    spots = []
    idx = 0
    for r in range(rows):
        for c in range(cols):
            t = top + r * (cell_h + gap)
            l = left + c * (cell_w + gap)
            idx += 1
            spots.append({
                "label": f"{idx:02}",
                "top": round(t, 4), "left": round(l, 4),
                "width": round(cell_w, 4), "height": round(cell_h, 4),
            })
    return spots

# ---------- UI（サイドバー：画像＆16音源） ----------
st.sidebar.header("設定")
img_url = st.sidebar.text_input("画像URL（1枚絵）", value=DEFAULT_IMAGE_URL)
img_url_raw = to_raw_url(img_url)

st.sidebar.markdown("**音源URL（16個）** — 空欄は未設定（無音）")
audio_urls = []
default_audio_raw = to_raw_url(DEFAULT_AUDIO_URL)
for i in range(16):
    val = st.sidebar.text_input(f"{i+1:02}", value=default_audio_raw if i == 0 else "")
    audio_urls.append(to_raw_url(val.strip()))

debug = st.sidebar.toggle("領域を可視化（調整用）", value=False)

# ---------- ホットスポット作成 ----------
HOTSPOTS = gen_grid_hotspots(ROWS, COLS, GRID_BOUNDS, CELL_GAP)

# ---------- 埋め込みHTML ----------
img_src = read_image_as_data_uri(img_url_raw or DEFAULT_IMAGE_URL)

html = f"""
<div id="stage" style="position:relative; max-width: 720px; margin: 0 auto;">
  <img src="{img_src}" style="width:100%; display:block;" alt="board"/>
  <audio id="player"></audio>
"""
for i, s in enumerate(HOTSPOTS):
    audio = audio_urls[i] if i < len(audio_urls) else ""
    outline = "1px dashed rgba(0,0,0,.35)" if debug else "none"
    bg = "rgba(0,0,0,.06)" if debug else "transparent"
    html += f"""
  <button
    onclick="(function(){{
      var src = '{audio}';
      if(src && src.trim().length > 0){{
        var a = document.getElementById('player');
        a.src = src;
        a.play().catch(()=>{{}});
      }}
    }})()"
    title="{s['label']}"
    style="
      position:absolute;
      top:{s['top']}%;
      left:{s['left']}%;
      width:{s['width']}%;
      height:{s['height']}%;
      border-radius:{RADIUS}px;
      border:{outline};
      background:{bg};
      cursor:pointer;
      padding:0;
      outline:none;
    ">
  </button>
"""
html += "</div>"

st.components.v1.html(html, height=820, scrolling=False)

st.caption("ヒント：GitHubのURLは **blob** ではなく **raw**（このアプリが自動で変換）を使うと安定して再生できます。")
