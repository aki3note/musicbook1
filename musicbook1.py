import base64
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Picture Jukebox", page_icon="🎵", layout="centered")

# =========================
# 設定（ここを差し替え）
# =========================

# 1枚絵（ローカルorURL）— ローカルは同ディレクトリに置く想定
BACKGROUND_IMAGE = "baackground.jpg"  # 例: "images/board.png" / "https://.../board.png"

# まずは 4x4 の規則的レイアウトを自動生成する場合
ROWS, COLS = 4, 4
# 画像内でグリッドが占める外枠（百分率）。上・左・幅・高さ
# ↓この画像ならだいたい盤面の内側に合うよう仮置きしています。必要に応じて調整してください。
GRID_BOUNDS = dict(top=16.5, left=4.5, width=91.0, height=77.0)

# 自動生成したホットスポットのサイズ・間隔（％）
CELL_GAP = 2.0      # タイル同士のすき間（横縦とも）
RADIUS = 12         # 見える枠の角丸（デバッグ用）

# ▶ 後で1枚ずつ微調整したい場合は、下の HOTSPOTS_CUSTOM を使う
# （top/left/width/height は全て画像に対する％。audio は mp3/ogg のURL）
HOTSPOTS_CUSTOM = [
    # {"label": "1", "audio": "https://raw.githubusercontent.com/you/repo/main/sounds/01.mp3",
    #  "top": 18.0, "left": 6.0, "width": 20.0, "height": 17.0},
]

# デフォルト音源（未設定のときに入る値）
DEFAULT_AUDIO = None  # "https://raw.githubusercontent.com/you/repo/main/sounds/blank.mp3"

# =========================
# ここから下はいじらなくてOK
# =========================

def read_image_as_data_uri(src: str) -> str:
    if src.startswith("http://") or src.startswith("https://"):
        return src  # 直接URLで表示（CORS問題がある場合はローカル→Base64に）
    p = Path(src)
    mime = "image/png" if p.suffix.lower() in [".png"] else "image/jpeg"
    data = p.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"

def gen_grid_hotspots(rows, cols, bounds, gap=0.0):
    """均等な矩形ホットスポットを%で生成。"""
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
                "audio": DEFAULT_AUDIO,   # 後で差し替え
                "top": round(t, 4),
                "left": round(l, 4),
                "width": round(cell_w, 4),
                "height": round(cell_h, 4),
            })
    return spots

# 使うホットスポットを決定
HOTSPOTS = HOTSPOTS_CUSTOM if HOTSPOTS_CUSTOM else gen_grid_hotspots(
    ROWS, COLS, GRID_BOUNDS, CELL_GAP
)

# デバッグ表示（領域の枠線を表示）
debug = st.toggle("領域を可視化（調整用）", value=False, help="ONにすると透明ボタンの枠が見えます")

# 背景画像を data URI か URL として取得
img_src = read_image_as_data_uri(BACKGROUND_IMAGE)

# HTMLを埋め込み（絶対配置の透明ボタン＋audio）
html = f"""
<div id="stage" style="position:relative; max-width: 720px; margin: 0 auto;">
  <img src="{img_src}" style="width:100%; display:block;" alt="board"/>

  <!-- オーディオプレイヤー（画面外） -->
  <audio id="player"></audio>

  <!-- ホットスポット群 -->
"""
for i, s in enumerate(HOTSPOTS):
    audio = (s.get("audio") or "")  # 空文字なら無音
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
    title="{s.get('label','')}"
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

with st.expander("🔧 使い方メモ（音の割り当て・座標の調整）"):
    st.markdown("""
- **音源URLは Raw URL** を使ってください  
  例）`https://raw.githubusercontent.com/<user>/<repo>/main/sounds/01.mp3`
- まずは `GRID_BOUNDS` と `ROWS/COLS/CELL_GAP` でおおまかに合わせ、
  細かく合わせたいタイルだけ `HOTSPOTS_CUSTOM` に手で1件ずつ書きます。
- `top/left/width/height` は **画像に対する％** です。  
  可視化トグルをONにすると、枠線が出て位置合わせがしやすくなります。
""")
