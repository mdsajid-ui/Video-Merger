"""
Automated Video Merger Studio
DV Analytics

Run with: streamlit run app.py
"""

import os
import io
import shutil
import tempfile
import subprocess
from datetime import datetime

import streamlit as st

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

def get_ffmpeg_binary():
    cmd = shutil.which("ffmpeg")
    if cmd:
        return cmd
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    return "ffmpeg"

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Page configuration & Modern Theme
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="DV Analytics — Video Merger Studio",
    page_icon="🎬",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Login gate — Interactive Lamp Theme
# ---------------------------------------------------------------------------
def login():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        #MainMenu, footer, [data-testid="stHeader"], [data-testid="stToolbar"] { display:none !important; }
        html, body, [class*="css"] { font-family:'Inter',sans-serif; }
        .stApp { background:#0b0b09; min-height:100vh; color:#fff; }
        .block-container { max-width:1080px !important; padding:6vh 28px 30px !important; }
        .lamp-heading { text-align:center; margin-bottom:34px; }
        .lamp-heading h1 { margin:0; color:#f7f7f3; font-size:clamp(32px,4.5vw,54px); letter-spacing:-2px; font-weight:500; }
        .lamp-heading h1 span { color:#ffe000; font-weight:600; }
        .lamp-heading p { color:#88877f; margin:10px 0 0; font-size:14px; letter-spacing:.06em; text-transform:uppercase; }
        [data-testid="stHorizontalBlock"] { align-items:center; gap:3rem; }
        .lamp-stage { height:470px; position:relative; overflow:hidden; }
        .lamp-glow { position:absolute; width:390px; height:390px; left:50%; top:77px; transform:translateX(-50%); background:radial-gradient(ellipse at 50% 15%,rgba(255,225,92,.42),rgba(255,212,55,.12) 43%,transparent 70%); filter:blur(5px); animation:breathe 3s ease-in-out infinite; transition:opacity .35s ease; }
        .light-cone { position:absolute; left:50%; top:126px; transform:translateX(-50%); width:330px; height:285px; background:linear-gradient(100deg,transparent 3%,rgba(255,226,116,.30) 48%,rgba(255,240,162,.17) 75%,transparent 97%); clip-path:polygon(39% 0,61% 0,100% 100%,0 100%); filter:blur(2px); transition:opacity .35s ease; }
        .lamp-stage.lamp-off .lamp-glow, .lamp-stage.lamp-off .light-cone, .lamp-stage.lamp-off .fly { opacity:0 !important; animation:none; }
        .lamp-stage.lamp-off .shade { border-bottom-color:#25251f; box-shadow:none; }
        .shade { position:absolute; z-index:3; left:50%; top:94px; transform:translateX(-50%); width:155px; height:55px; border-radius:80px 80px 10px 10px; background:linear-gradient(#080807,#181711); border-bottom:5px solid #5f5633; box-shadow:0 8px 28px rgba(255,220,65,.33); }
        .stem { position:absolute; z-index:3; left:calc(50% - 3px); top:146px; width:6px; height:239px; background:linear-gradient(90deg,#171714,#75705c,#151513); }
        .base { position:absolute; z-index:4; left:50%; top:382px; transform:translateX(-50%); width:142px; height:12px; border-radius:50%; background:#11110f; box-shadow:0 3px 12px #000; }
        .cord { position:absolute; z-index:4; left:calc(50% + 51px); top:136px; width:2px; height:75px; background:#93865c; transform-origin:top; animation:sway 3.2s ease-in-out infinite; }
        .cord:after { content:''; position:absolute; left:-5px; bottom:-12px; width:12px; height:17px; border-radius:50%; background:#cbb96f; box-shadow:inset 2px 0 4px #746a42; }
        .fly { position:absolute; z-index:5; width:5px; height:5px; border-radius:50%; background:#fff26a; box-shadow:0 0 5px #fff400,0 0 12px #d4ff00; animation:float 5s ease-in-out infinite; }
        .f1{left:16%;top:17%;}.f2{left:77%;top:25%;animation-delay:-1s}.f3{left:25%;top:70%;animation-delay:-2.2s}.f4{left:83%;top:74%;animation-delay:-3.4s}.f5{left:67%;top:51%;animation-delay:-4s}
        [data-testid="stForm"] { background:linear-gradient(145deg,rgba(35,35,32,.98),rgba(23,23,21,.96)); border:1px solid #3c3b35; border-radius:22px; padding:32px 30px 26px; box-shadow:0 25px 65px rgba(0,0,0,.55),inset 0 1px rgba(255,255,255,.04); }
        .card-head h2 { margin:0; font-size:30px; color:#fff; letter-spacing:-1px; }
        .card-head p { margin:7px 0 22px; color:#8f8e87; font-size:13px; }
        .stTextInput label { color:#b9b8b1 !important; font-size:12px !important; font-weight:600 !important; }
        .stTextInput [data-baseweb="input"], .stTextInput [data-baseweb="base-input"], .stTextInput input { background-color:#151513 !important; border-color:#292925 !important; }
        .stTextInput [data-baseweb="input"] { border:1px solid #292925 !important; border-radius:10px !important; min-height:49px; }
        .stTextInput [data-baseweb="input"]:focus-within { border-color:#ffe000 !important; box-shadow:0 0 0 2px rgba(255,224,0,.12) !important; }
        .stTextInput input { color:#ffe76a !important; -webkit-text-fill-color:#ffe76a !important; caret-color:#ffe000 !important; opacity:1 !important; }
        .stTextInput input::placeholder { color:#565650 !important; }
        [data-testid="stToggle"] { max-width:180px; margin:0 auto -8px; }
        [data-testid="stToggle"] label p { color:#d8d6c8 !important; font-size:13px !important; font-weight:600 !important; }
        .login-actions { display:flex; justify-content:space-between; color:#77766f; font-size:12px; margin:0 2px 13px; }
        [data-testid="stFormSubmitButton"] button { width:100%; min-height:50px; border:0; border-radius:10px; background:#ffe000; color:#13130f; font-size:15px; font-weight:800; box-shadow:0 8px 22px rgba(255,224,0,.18); transition:.2s; }
        [data-testid="stFormSubmitButton"] button:hover { background:#ffea3b; color:#000; transform:translateY(-1px); box-shadow:0 11px 28px rgba(255,224,0,.27); }
        .secure-note { text-align:center; color:#62615b; font-size:11px; margin-top:18px; }
        .login-footer { text-align:center; color:#4f4e49; font-size:11px; margin-top:28px; }
        @keyframes breathe{50%{opacity:.72;transform:translateX(-50%) scale(.96)}}
        @keyframes sway{50%{transform:rotate(3deg)}}
        @keyframes float{0%,100%{transform:translate(0,0);opacity:.35}50%{transform:translate(18px,-24px);opacity:1}}
        @media(max-width:760px){.block-container{padding:30px 18px !important}.lamp-heading{margin-bottom:8px}.lamp-stage{height:280px}.shade{top:35px}.lamp-glow{top:20px;height:270px}.light-cone{top:67px;height:190px;width:260px}.stem{top:87px;height:150px}.base{top:234px}.cord{top:77px}.lamp-heading h1{font-size:35px}[data-testid="stHorizontalBlock"]{gap:.5rem}[data-testid="stForm"]{padding:26px 20px 22px}}
        </style>
        <div class="lamp-heading"><h1>Video Merger <span>Studio</span></h1><p>DV Analytics · Secure Sign In</p></div>
        """,
        unsafe_allow_html=True,
    )

    lamp_col, form_col = st.columns([1.12, 1], gap="large")
    with lamp_col:
        lamp_on = st.toggle("Turn on lamp", value=True, key="login_lamp_on")
        lamp_state = "lamp-on" if lamp_on else "lamp-off"
        st.markdown(
            f'''<div class="lamp-stage {lamp_state}"><div class="lamp-glow"></div><div class="light-cone"></div><div class="shade"></div><div class="stem"></div><div class="base"></div><div class="cord"></div><i class="fly f1"></i><i class="fly f2"></i><i class="fly f3"></i><i class="fly f4"></i><i class="fly f5"></i></div>''',
            unsafe_allow_html=True,
        )

    with form_col:
        with st.form("login_form", clear_on_submit=False):
            st.markdown(
                '<div class="card-head"><h2>Welcome Back</h2><p>Sign in to access Video Merger Studio</p></div>',
                unsafe_allow_html=True,
            )
            username = st.text_input("USERNAME", placeholder="Enter your username", key="login_username")
            password = st.text_input("PASSWORD", type="password", placeholder="Enter your password", key="login_password")
            st.markdown(
                '<div class="login-actions"><span>✓ &nbsp;Secure session</span><span>Authorized access only</span></div>',
                unsafe_allow_html=True,
            )
            submitted = st.form_submit_button("Sign In", use_container_width=True)
            st.markdown('<div class="secure-note">🔒 Your connection is protected</div>', unsafe_allow_html=True)

    if submitted:
        valid_username = os.environ.get("APP_USERNAME", "")
        valid_password = os.environ.get("APP_PASSWORD", "")

        # If credentials are not set in environment/secrets, allow default admin/admin or any input
        if not valid_username or not valid_password:
            st.session_state["logged_in"] = True
            st.rerun()
        elif username == valid_username and password == valid_password:
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("❌ Invalid username or password")

    st.markdown('<div class="login-footer">© 2026 DV Analytics · Video Merger Suite</div>', unsafe_allow_html=True)
    return st.session_state.get("logged_in", False)


if not st.session_state.get("logged_in", False):
    login()
    st.stop()

# ---------------------------------------------------------------------------
# Dashboard UI Styles & Branding
# ---------------------------------------------------------------------------
NAVY = "#0B1B4D"
NAVY_DEEP = "#060F30"
RED = "#EF233C"
ACCENT = "#5B6CF7"
ACCENT_2 = "#8A5CFF"
GOLD = "#D4AF37"
BG = "#F4F5FB"
CARD = "#FFFFFF"
BORDER = "#E7E9F6"
MUTED = "#6B7188"

st.markdown(
    f"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
        .stApp {{
            background:
                radial-gradient(1000px 500px at 100% -5%, {ACCENT}14, transparent 55%),
                radial-gradient(800px 500px at -5% 10%, {GOLD}10, transparent 50%),
                {BG};
        }}
        #MainMenu, footer, header[data-testid="stHeader"] {{ visibility: hidden; }}

        /* ---------- Hero ---------- */
        .dv-hero {{
            position: relative; overflow: hidden;
            background: radial-gradient(130% 180% at 0% 0%, {ACCENT_2}3d 0%, transparent 45%),
                        radial-gradient(120% 160% at 100% 100%, {RED}26 0%, transparent 40%),
                        linear-gradient(120deg, {NAVY} 0%, {NAVY_DEEP} 100%);
            padding: 32px 36px; border-radius: 22px; margin-bottom: 28px;
            display: flex; align-items: center; justify-content: space-between; gap: 18px;
            box-shadow: 0 20px 45px -18px rgba(11,27,77,0.55);
            border: 1px solid rgba(255,255,255,.08);
        }}
        .dv-hero-left {{ display: flex; align-items: center; gap: 18px; }}
        .dv-hero .mark {{
            width: 54px; height: 54px; border-radius: 15px; flex-shrink: 0;
            background: linear-gradient(135deg, {RED}, #ff7a7a);
            display: flex; align-items: center; justify-content: center;
            color: white; font-weight: 800; font-size: 20px; letter-spacing: -1px;
            font-family: 'Poppins', sans-serif;
            box-shadow: 0 8px 20px -4px {RED}aa, inset 0 1px 0 rgba(255,255,255,.25);
        }}
        .dv-hero h1 {{
            color: white; font-size: 24px; margin: 0; font-family: 'Poppins', sans-serif; font-weight: 700;
            letter-spacing: -.3px;
        }}
        .dv-hero p {{ color: #B7BEEF; font-size: 13px; margin: 4px 0 0; }}
        .dv-hero-pill {{
            display: flex; align-items: center; gap: 8px; color: #EAF0FF; font-size: 12.5px;
            font-weight: 600; padding: 8px 14px; border-radius: 999px;
            background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.14);
            backdrop-filter: blur(8px); white-space: nowrap;
        }}
        .dv-hero-pill .dot {{
            width: 7px; height: 7px; border-radius: 50%; background: #34d399;
            box-shadow: 0 0 0 3px rgba(52,211,153,.25);
        }}

        /* ---------- Glass cards ---------- */
        .dv-card {{
            background: linear-gradient(180deg, rgba(255,255,255,.95), rgba(255,255,255,.82));
            border: 1px solid {BORDER}; border-radius: 18px;
            padding: 24px 26px; margin-bottom: 20px;
            box-shadow: 0 8px 24px -14px rgba(11,27,77,0.14);
            backdrop-filter: blur(10px);
            transition: box-shadow .2s ease;
        }}
        .dv-card:hover {{ box-shadow: 0 14px 34px -16px rgba(11,27,77,0.20); }}
        .dv-section-title {{
            font-family: 'Poppins', sans-serif; font-weight: 700; font-size: 17.5px;
            color: {NAVY}; margin-bottom: 2px; display: flex; align-items: center; gap: 8px;
        }}
        .dv-section-title:before {{
            content: ""; display: inline-block; width: 6px; height: 18px; border-radius: 4px;
            background: linear-gradient(180deg, {ACCENT}, {RED});
        }}
        .dv-section-sub {{ color: {MUTED}; font-size: 13px; margin: 4px 0 16px 14px; }}

        /* ---------- Clip item in list ---------- */
        .dv-clip-item {{
            display: flex; align-items: center; justify-content: space-between;
            padding: 12px 16px; border-radius: 12px; margin-bottom: 8px;
            background: #ffffff; border: 1px solid {BORDER};
            box-shadow: 0 2px 8px rgba(11,27,77,0.04);
        }}
        .dv-clip-left {{ display: flex; align-items: center; gap: 12px; }}
        .dv-clip-badge {{
            width: 28px; height: 28px; border-radius: 8px;
            background: linear-gradient(135deg, {NAVY}, {ACCENT});
            color: white; font-weight: 700; font-size: 13px;
            display: flex; align-items: center; justify-content: center;
        }}
        .dv-clip-name {{ font-weight: 600; font-size: 14px; color: {NAVY}; }}
        .dv-clip-size {{ color: {MUTED}; font-size: 12.5px; }}

        /* ---------- Buttons ---------- */
        .stButton>button {{
            background: linear-gradient(135deg, {NAVY} 0%, {ACCENT} 55%, {ACCENT_2} 130%);
            background-size: 200% auto;
            color: white !important; border-radius: 12px; font-weight: 700; border: none;
            padding: 0.72em 1.6em; font-family: 'Poppins', sans-serif; font-size: 15px;
            box-shadow: 0 10px 24px -8px {NAVY}77;
            transition: all .22s ease;
        }}
        .stButton>button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 16px 32px -10px {NAVY}99;
            color: white !important;
        }}
        .stDownloadButton>button {{
            background: linear-gradient(135deg, {RED} 0%, #FF8A3D 100%) !important;
            color: white !important; border: none !important; border-radius: 12px !important;
            font-weight: 700 !important; font-family: 'Poppins', sans-serif !important; font-size: 15px !important;
            padding: 0.75em 1.8em !important;
            box-shadow: 0 10px 24px -8px {RED}99 !important;
            float: right !important;
        }}
        .stDownloadButton>button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 16px 32px -10px {RED}dd !important;
            color: white !important;
        }}

        /* ---------- Sidebar ---------- */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {NAVY_DEEP}, {NAVY}) !important;
        }}
        section[data-testid="stSidebar"] * {{ color: #EAF0FF !important; }}
        section[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,.12) !important; }}
    </style>

    <div class="dv-hero">
        <div class="dv-hero-left">
            <div class="mark">DV</div>
            <div>
                <h1>Video Merger Studio</h1>
                <p>Fast, lossless multi-clip video stitching and high-definition rendering</p>
            </div>
        </div>
        <div class="dv-hero-pill">
            <span class="dot"></span> Engine Ready
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar Settings & Info
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎬 Video Studio Controls")
    st.caption("Configure global video stitching settings")
    st.markdown("---")

    mode = st.radio(
        "Merge Strategy",
        ["Instant Stream Copy (Fastest)", "Smart Re-encode (Maximum Compatibility)"],
        index=0,
        help="Stream Copy stitches without re-encoding in seconds if resolution matches.",
    )

    quality_preset = st.selectbox(
        "Re-encode Quality (If applicable)",
        ["Balanced (720p - Recommended)", "High (1080p Full HD)", "Fast (480p)"],
        index=0,
    )

    st.markdown("---")
    st.markdown("### 📊 Session Info")
    st.info("System Engine: **FFmpeg Multi-thread**\nOutput Format: **MP4 (H.264 / AAC)**")

    if st.button("🚪 Log Out", use_container_width=True):
        st.session_state["logged_in"] = False
        st.rerun()

# ---------------------------------------------------------------------------
# Main Workflow
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="dv-card">
        <div class="dv-section-title">Step 1: Upload Video Clips</div>
        <div class="dv-section-sub">Select two or more video clips (MP4, MOV, MKV, WebM, AVI) to merge together.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_files = st.file_uploader(
    "Choose video files",
    type=["mp4", "mov", "mkv", "webm", "avi"],
    accept_multiple_files=True,
    label_visibility="collapsed",
)

if uploaded_files:
    # Summary Metrics
    total_size_mb = sum([f.size for f in uploaded_files]) / (1024 * 1024)
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Clips", f"{len(uploaded_files)} clips")
    with m2:
        st.metric("Combined File Size", f"{total_size_mb:.1f} MB")
    with m3:
        st.metric("Output Format", "MP4 Container")

    st.markdown(
        """
        <div class="dv-card">
            <div class="dv-section-title">Step 2: Clips in Merge Order</div>
            <div class="dv-section-sub">Videos will be joined in the exact order listed below.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for idx, f in enumerate(uploaded_files, start=1):
        fsize_mb = f.size / (1024 * 1024)
        st.markdown(
            f"""
            <div class="dv-clip-item">
                <div class="dv-clip-left">
                    <div class="dv-clip-badge">{idx}</div>
                    <div>
                        <div class="dv-clip-name">{f.name}</div>
                        <div class="dv-clip-size">{fsize_mb:.1f} MB</div>
                    </div>
                </div>
                <div style="color:#10b981; font-size:13px; font-weight:600;">✓ Ready</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    merge_col, _ = st.columns([1, 1])
    with merge_col:
        start_merge = st.button("🎬 Merge Clips Now", use_container_width=True)

    if start_merge:
        if len(uploaded_files) < 2:
            st.warning("⚠️ Please select at least 2 video clips to merge.")
        else:
            with st.spinner("Processing videos with FFmpeg engine..."):
                prog_bar = st.progress(10)
                temp_dir = tempfile.mkdtemp(prefix="video_merger_")
                try:
                    file_paths = []
                    for i, f in enumerate(uploaded_files):
                        ext = os.path.splitext(f.name)[1] or ".mp4"
                        clip_path = os.path.join(temp_dir, f"clip_{i}{ext}")
                        with open(clip_path, "wb") as out_f:
                            out_f.write(f.getvalue())
                        file_paths.append(clip_path)

                    prog_bar.progress(40)

                    # Create concat list
                    list_path = os.path.join(temp_dir, "concat_list.txt")
                    with open(list_path, "w", encoding="utf-8") as lf:
                        for p in file_paths:
                            clean_p = p.replace("\\", "/")
                            lf.write(f"file '{clean_p}'\n")

                    output_path = os.path.join(temp_dir, "merged_output.mp4")
                    prog_bar.progress(60)

                    # Check strategy
                    used_fast = False
                    ffmpeg_bin = get_ffmpeg_binary()
                    if "Instant" in mode:
                        cmd = [
                            ffmpeg_bin, "-y",
                            "-f", "concat",
                            "-safe", "0",
                            "-i", list_path,
                            "-c", "copy",
                            "-movflags", "+faststart",
                            output_path,
                        ]
                        res = subprocess.run(cmd, capture_output=True, text=True)
                        if res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                            used_fast = True

                    # Fallback or Re-encode mode
                    if not used_fast:
                        prog_bar.progress(70)
                        # Build scale dimensions based on quality preset
                        scale_opt = "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2"
                        if "1080p" in quality_preset:
                            scale_opt = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2"
                        elif "480p" in quality_preset:
                            scale_opt = "scale=854:480:force_original_aspect_ratio=decrease,pad=854:480:(ow-iw)/2:(oh-ih)/2"

                        cmd = [
                            ffmpeg_bin, "-y",
                            "-f", "concat",
                            "-safe", "0",
                            "-i", list_path,
                            "-vf", scale_opt,
                            "-c:v", "libx264",
                            "-preset", "veryfast",
                            "-crf", "23",
                            "-c:a", "aac",
                            "-b:a", "192k",
                            "-movflags", "+faststart",
                            output_path,
                        ]
                        subprocess.run(cmd, check=True)

                    prog_bar.progress(100)

                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        out_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                        with open(output_path, "rb") as out_file:
                            merged_bytes = out_file.read()

                        st.success(
                            f"🎉 Merged {len(uploaded_files)} clips successfully! "
                            f"({'Instant Stream Copy' if used_fast else 'Re-encoded Quality'} · {out_size_mb:.1f} MB)"
                        )

                        # Output Section with Video Player & Right-aligned Download Button
                        st.markdown(
                            """
                            <div class="dv-card">
                                <div class="dv-section-title">Step 3: Preview & Download</div>
                                <div class="dv-section-sub">Your merged video is ready. Preview below or download directly to your computer.</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        # Action row with download button right-aligned
                        dl_col1, dl_col2 = st.columns([1, 1])
                        with dl_col2:
                            st.download_button(
                                label="⬇ Download Merged Video (merged.mp4)",
                                data=merged_bytes,
                                file_name="merged.mp4",
                                mime="video/mp4",
                                use_container_width=True,
                            )

                        st.video(merged_bytes)

                except Exception as e:
                    st.error(f"❌ Video merging failed: {str(e)}")
                finally:
                    shutil.rmtree(temp_dir, ignore_errors=True)
else:
    st.info("💡 Upload two or more video files above to get started!")
