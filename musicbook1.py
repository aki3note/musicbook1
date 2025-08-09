import io
from pathlib import Path
from typing import List, Tuple

import streamlit as st
from PIL import Image

st.set_page_config(page_title="Picture Jukebox", page_icon="🎵", layout="wide")


# =========================
# 設定（ここを後で差し替え）
# =========================

# 4x4 グリッド想定（必要なら変更可）
ROWS, COLS = 4, 4

# 合成画像のパス（デモ用）。あなたの画像URL/相対パスに差し替えてOK
# 例: Path("assets/sprite.png") や "https://github.com/aki3note/musicbook1/blob/main/baackground.jpg?raw=true"
COMPOSITE_IMAGE = Path("baackground.jpg")  # このチャットに添付された画像名

# 音源URL（左上→右下の順で16コ）。あとでGitHubのmp3/oggに差し替えてください
AUDIO_URLS = [
    None, None, None, None,
    None, None, None, None,
    None, None, None, None,
    None, None, None, None,
]
# 例:
# AUDIO_URLS = [
#   "https://raw.githubusercontent.com/you/repo/main/sounds/01.mp3",
#   "https://raw.githubusercontent.com/you/repo/main/sounds/02.mp3",
#   ...
# ]


# 画像の中で「タイルが並ぶ領域」を切り出す枠（上, 右, 下, 左）px
# 不要なら None（画像全体を等分）
GRID_BOUNDS: Tuple[int, int, int, int] | None = None
# 例: 上下左右に余白が多い場合 → GRID_BOUNDS = (220, 90, 120, 90)


# =========================
# ここから下は基本いじらなくてOK
# =========================

def load_image(src: str | Path) -> Image.Image:
    """画像を読み込み（URL/ローカル両対応）。"""
    src = str(src)
    if src.startswith("http://") or src.startswith("https://"):
        import urllib.request
        with urllib.request.urlopen(src) as resp:
            return Image.open(io.BytesIO(resp.read())).convert("RGBA")
    else:
        return Image.open(src).convert("RGBA")


def crop_grid(img: Image.Image, rows: int, cols: int,
              bounds: Tuple[int, int, int, int] | None = None) -> List[Image.Image]:
    """画像を rows×cols で等分し、PIL Image のリストを返す。bounds で内側領域を指定可能。"""
    W, H = img.size
    if bounds:
        top, right, bottom, left = bounds
        x0, y0 = left, top
        x1, y1 = W - right, H - bottom
    else:
        x0, y0, x1, y1 = 0, 0, W, H

    grid_w = x1 - x0
    grid_h = y1 - y0
    tile_w = grid_w / cols
    tile_h = grid_h / rows

    tiles = []
    for r in range(rows):
        for c in range(cols):
            lx = int(x0 + c * tile_w)
            ty = int(y0 + r * tile_h)
            rx = int(x0 + (c + 1) * tile_w)
            by = int(y0 + (r + 1) * tile_h)
            tiles.append(img.crop((lx, ty, rx, by)))
    return tiles


# 再生用の状態
if "play_src" not in st.session_state:
    st.session_state.play_src = None

st.title("🎵 画像タップで音を鳴らす（ブランク版）")
st.caption("4×4の各タイルを押すと対応する音源を再生します。画像・音源は後でGitHubのURLに差し替えてOK。")

# 背景画像の読み込み & 分割
try:
    sprite = load_image(COMPOSITE_IMAGE)
except Exception as e:
    st.error(f"画像の読み込みに失敗しました: {e}")
    st.stop()

tiles = crop_grid(sprite, ROWS, COLS, GRID_BOUNDS)

# スタイル：画像角丸＆ボタンをフル幅に
st.markdown("""
<style>
.tile-img { border-radius: 14px; }
.stButton>button { width:100%; border-radius: 12px; padding:.5rem .75rem; }
.audio-hidden { height:0; overflow:hidden; }
</style>
""", unsafe_allow_html=True)

# グリッド描画（画像→ボタンの順）
idx = 0
for _ in range(ROWS):
    cols = st.columns(COLS, vertical_alignment="center")
    for c in cols:
        with c:
            # 画像表示
            c.image(tiles[idx], use_container_width=True, output_format="PNG")
            # ボタン（画像そのものを押せるように下にワイドなボタンを置く）
            clicked = st.button("　", key=f"btn_{idx}")  # 見た目を空白に
            if clicked:
                # 音源をセット（None の場合は無音）
                st.session_state.play_src = AUDIO_URLS[idx]
        idx += 1

# 再生（1度のインタラクションで最後に押したものだけ）
def autoplay(src: str | None):
    if not src:
        return
    st.markdown(
        f"""
        <div class="audio-hidden">
            <audio autoplay>
                <source src="{src}">
            </audio>
        </div>
        """,
        unsafe_allow_html=True
    )

autoplay(st.session_state.play_src)

with st.expander("🔧 セットアップ手順（超簡単）"):
    st.markdown("""
1. 合成画像（4×4並び）を `COMPOSITE_IMAGE` に指定。URLでもOK。  
2. 各タイルに対応する音源URLを **左上→右下** の順で `AUDIO_URLS` に並べます。  
   - GitHubのRaw URL推奨（`https://raw.githubusercontent.com/.../sounds/xx.mp3`）  
3. 画像の外周に大きな余白がある場合は `GRID_BOUNDS = (上, 右, 下, 左)` を設定すると
   その内側をキレイに等分できます。  
4. 列/行数を変える場合は `ROWS, COLS` を調整してください。
    """)

