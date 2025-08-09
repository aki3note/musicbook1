import base64
from urllib.parse import urlparse
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Picture Jukebox Fixed", page_icon="🎵", layout="centered")

# ===== 基本設定 =====
ROWS, COLS = 4, 4
GRID_BOUNDS = dict(top=16.5, left=4.5, width=91.0, height=77.0)  # % 単位
CELL_GAP = 2.0   # タイル間隔（%）
RADIUS = 12      # デバッグ時の角丸

# ===== ヘルパ =====
def to_raw_url(url: str) -> str:
    """GitHubの blob URL → raw URL"""
    if not url:
        return ""
    try:
        p = urlparse(url)
        if p.netloc == "github.com" and "/blob/" in p.path:
            user_repo, branch_and_path = p.path.strip("/").split("/blob/", 1)
            return f"https://raw.githubusercontent.com/{user_repo}/{branch_and_path}"
        return url
    except Exception:
        return url

def read_image_as_data_uri(src: str) -> str:
    """ローカル画像ならBase64化、URLならそのまま"""
    if src.startswith(("http://", "https://")):
        return src
    p = Path(src)
    mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"

def gen_grid_hotspots(rows, cols, bounds, gap=0.0):
    """均等配置のホットスポットを%単位で作る"""
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

# ===== 固定の画像・音源設定 =====
img_url = to_raw_url("https://github.com/aki3note/musicbook1/blob/main/baackground.jpg")

# 全部無音で初期化
audio_urls = [""] * 16
# 1番（インデックス0）
audio_urls[0] = to_raw_url("https://github.com/aki3note/musicbook1/blob/main/inu.wav")
# 2番（インデックス1）
audio_urls[1] = to_raw_url("https://github.com/aki3note/musicbook1/blob/main/donguri.wav")
# 6番（インデックス5）
audio_urls[5] = to_raw_url("https://github.com/aki3note/musicbook1/blob/main/06.mp3")
# 14番（インデックス13）
audio_urls[13] = to_raw_url("https://github.com/aki3note/musicbook1/blob/main/tanuki.wav")

# デバッグ枠を表示するか
debug = False

# ===== ホットスポット作成 =====
HOTSPOTS = gen_grid_hotspots(ROWS, COLS, GRID_BOUNDS, CELL_GAP)

# ===== HTML埋め込み =====
img_src = read_image_as_data_uri(img_url)
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
