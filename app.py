import streamlit as st
import requests
import json
import time
import base64
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="استديو مهووس الذكي",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded",
)

MAHWOUS_DNA = (
    "Photorealistic 3D animated character 'Mahwous', Gulf Arab perfume expert, "
    "neatly styled dark hair, groomed beard, warm brown eyes, wearing luxury black suit "
    "with gold tie. High-end cinematic lighting. Pixar/Disney 3D style."
)

GEMINI_MODEL = "gemini-2.5-flash-preview-05-20"
IMAGEN_MODEL = "imagen-4.0-generate-001"
LUMA_BASE    = "https://api.lumalabs.ai/dream-machine/v1"

# Keys from st.secrets OR hardcoded fallback
def get_key(name, fallback=""):
    try:
        return st.secrets[name]
    except Exception:
        return fallback

GOOGLE_KEY = get_key("GOOGLE_KEY", "AIzaSyBmXzIylxNEJWRNVZuLCVu8Xdg6ORF2QD8")
LUMA_KEY   = get_key("LUMA_KEY",   "luma-f801b085-d342-4e6a-b9ff-6aa21ba4b99c-8235cf57-8e12-4387-bbb1-8d999b766219")

# ─────────────────────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800;900&family=Cinzel:wght@700;900&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #0E0B08 !important;
    color: #E0D0B0 !important;
    font-family: 'Tajawal', sans-serif !important;
    direction: rtl;
}
[data-testid="stSidebar"] {
    background: #12100A !important;
    border-left: 1px solid rgba(212,175,55,0.2);
    border-right: none !important;
}
[data-testid="stHeader"] { background: transparent !important; }
h1,h2,h3 { font-family: 'Cinzel', serif !important; color: #D4AF37 !important; }

/* Tabs */
[data-baseweb="tab-list"] { background: #1A1612 !important; border-radius: 12px; padding: 4px; gap: 4px; }
[data-baseweb="tab"] { color: rgba(224,208,176,0.5) !important; font-family: 'Tajawal',sans-serif !important;
    font-weight: 700 !important; border-radius: 8px !important; }
[aria-selected="true"][data-baseweb="tab"] { background: #D4AF37 !important; color: #000 !important; }
[data-baseweb="tab-panel"] { background: transparent !important; }

/* Inputs */
textarea, input[type="text"], input[type="password"], .stTextInput input {
    background: #1A1612 !important; border: 1px solid rgba(212,175,55,0.25) !important;
    color: #E0D0B0 !important; border-radius: 10px !important;
    font-family: 'Tajawal', sans-serif !important; direction: rtl;
}
textarea:focus, .stTextInput input:focus { border-color: #D4AF37 !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #8A6415, #D4AF37) !important;
    color: #000 !important; font-family: 'Tajawal', sans-serif !important;
    font-weight: 800 !important; border: none !important; border-radius: 10px !important;
    padding: 10px 20px !important; width: 100%;
    transition: transform .15s, box-shadow .15s;
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(212,175,55,0.25) !important; }

/* Cards */
.card {
    background: #1A1612; border: 1px solid rgba(212,175,55,0.2);
    border-radius: 16px; padding: 18px 20px; margin: 6px 0;
    transition: border-color .2s, box-shadow .2s;
}
.card:hover { border-color: #D4AF37; box-shadow: 0 4px 20px rgba(212,175,55,0.1); }
.card-title { font-weight: 800; font-size: 1rem; color: #fff; margin-bottom: 6px; }
.card-body  { font-size: 0.82rem; color: rgba(224,208,176,0.6); line-height: 1.6; }

/* Tag pills */
.tag { display:inline-block; font-size:.65rem; font-weight:700; padding:3px 10px;
    border-radius:20px; margin:3px 2px; border:1px solid; }
.tg { color:#D4AF37; border-color:rgba(212,175,55,.4); background:rgba(212,175,55,.08); }
.tp { color:#C87AFF; border-color:rgba(180,100,255,.4); background:rgba(180,100,255,.08); }
.tn { color:#50C878; border-color:rgba(80,200,120,.4); background:rgba(80,200,120,.08); }
.tr { color:#FF7070; border-color:rgba(255,100,100,.4); background:rgba(255,100,100,.08); }

/* Shot card */
.shot-card {
    background: #1A1612; border: 1px solid rgba(212,175,55,0.15);
    border-radius: 14px; padding: 16px 20px; margin: 10px 0;
    border-right: 4px solid #D4AF37;
}
.shot-num { font-family:'Cinzel',serif; font-size:1.4rem; color:#D4AF37; font-weight:900; }
.shot-title { font-weight:800; font-size:.95rem; color:#fff; margin:6px 0 4px; }
.shot-text  { font-size:.8rem; color:rgba(224,208,176,.65); line-height:1.6; }
.shot-meta  { background:#0E0B08; border-radius:8px; padding:8px 12px; margin-top:8px;
    font-size:.75rem; color:rgba(224,208,176,.5); }

/* Status */
.status-box {
    background: #1A1612; border-radius:12px; padding:14px 18px;
    text-align:center; border:1px dashed rgba(212,175,55,0.3);
}
.status-icon { font-size:2rem; margin-bottom:6px; }
.status-text { font-weight:700; font-size:.85rem; }

/* Sidebar stat */
.stat-box { text-align:center; background:#1A1612; border:1px solid rgba(212,175,55,0.2);
    border-radius:12px; padding:14px; margin:6px 0; }
.stat-num { font-family:'Cinzel',serif; font-size:1.6rem; color:#D4AF37; font-weight:900; }
.stat-lbl { font-size:.65rem; color:rgba(224,208,176,.4); letter-spacing:.1em; text-transform:uppercase; }

/* Section label */
.sec-label { font-size:.7rem; font-weight:800; letter-spacing:.2em; text-transform:uppercase;
    color:rgba(212,175,55,.6); padding-right:10px; border-right:3px solid #8A6415; margin-bottom:10px; }

/* Divider */
hr { border-color: rgba(212,175,55,0.12) !important; }

/* Hide Streamlit branding */
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
for k, v in {
    "analysis": None,
    "social_images": {"ig": None, "snap": None, "x": None},
    "video_url": None,
    "video_job_id": None,
    "video_status": None,
    "history": [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────────────────────────────────────
# API HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def call_gemini(user_prompt: str) -> dict | None:
    system = """أنت المدير الإبداعي لـ 'استديو مهووس الذكي'. بناءً على الفكرة المقدمة:
1. اقترح عطراً فاخراً مناسباً
2. اكتب قصة/هوك جذابة
3. أنشئ سيناريو سينمائي من 3 لقطات
4. قدم بروبت صور دقيق بالإنجليزية لمهووس وللعطر

أجب فقط بـ JSON بهذا الشكل:
{
  "perfume": "اسم العطر",
  "story": "القصة/الهوك بالعربية",
  "scenario": [
    {"shot": 1, "title": "عنوان اللقطة", "desc": "وصف المشهد", "audio": "الصوت/الحوار", "movement": "حركة الكاميرا", "prompt_en": "english video prompt for Luma"}
  ],
  "char_prompt": "english prompt for Mahwous character image",
  "prod_prompt": "english prompt for perfume product image",
  "social_prompt": "english prompt for luxury perfume social media ad"
}"""
    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GOOGLE_KEY}",
            json={
                "contents": [{"parts": [{"text": user_prompt}]}],
                "systemInstruction": {"parts": [{"text": system}]},
                "generationConfig": {"responseMimeType": "application/json", "temperature": 1.0},
            },
            timeout=60,
        )
        raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(raw)
    except Exception as e:
        st.error(f"❌ خطأ في Gemini: {e}")
        return None


def call_imagen(prompt: str) -> str | None:
    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{IMAGEN_MODEL}:predict?key={GOOGLE_KEY}",
            json={
                "instances": [{"prompt": prompt + ". 4K cinematic luxury perfume advertisement. Professional photography."}],
                "parameters": {"sampleCount": 1},
            },
            timeout=90,
        )
        data = r.json()
        b64 = data["predictions"][0]["bytesBase64Encoded"]
        return f"data:image/png;base64,{b64}"
    except Exception as e:
        st.error(f"❌ خطأ في Imagen: {e}")
        return None


def create_luma_video(prompt: str, char_url: str = None, prod_url: str = None) -> str | None:
    """Submit a Luma Ray generation job and return job ID."""
    headers = {"Authorization": f"Bearer {LUMA_KEY}", "Content-Type": "application/json"}
    full_prompt = f"{prompt}. {MAHWOUS_DNA}. Cinematic luxury perfume advertisement. Ultra HD."

    body: dict = {"prompt": full_prompt, "aspect_ratio": "9:16", "loop": False}

    # Attach keyframes if image URLs provided
    if char_url or prod_url:
        keyframes: dict = {}
        if char_url:
            keyframes["frame0"] = {"type": "image", "url": char_url}
        if prod_url:
            keyframes["frame1"] = {"type": "image", "url": prod_url}
        body["keyframes"] = keyframes

    try:
        r = requests.post(f"{LUMA_BASE}/generations", json=body, headers=headers, timeout=30)
        data = r.json()
        return data.get("id")
    except Exception as e:
        st.error(f"❌ خطأ في Luma: {e}")
        return None


def poll_luma_video(job_id: str) -> dict:
    """Poll Luma job status. Returns dict with status + video_url."""
    headers = {"Authorization": f"Bearer {LUMA_KEY}"}
    try:
        r = requests.get(f"{LUMA_BASE}/generations/{job_id}", headers=headers, timeout=20)
        data = r.json()
        status = data.get("state", "unknown")
        url = None
        if status == "completed":
            url = data.get("assets", {}).get("video")
        return {"status": status, "url": url, "raw": data}
    except Exception as e:
        return {"status": "error", "url": None, "error": str(e)}


def list_luma_generations(limit: int = 10) -> list:
    headers = {"Authorization": f"Bearer {LUMA_KEY}"}
    try:
        r = requests.get(f"{LUMA_BASE}/generations?limit={limit}", headers=headers, timeout=20)
        return r.json().get("generations", [])
    except Exception:
        return []


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:20px 0 10px'>
      <div style='width:60px;height:60px;background:#D4AF37;border-radius:16px;
           display:inline-flex;align-items:center;justify-content:center;
           font-family:Cinzel,serif;font-size:1.8rem;font-weight:900;color:#000;
           box-shadow:0 0 30px rgba(212,175,55,.5)'>م</div>
      <div style='font-family:Cinzel,serif;font-size:1rem;color:#D4AF37;font-weight:700;margin-top:10px'>
        استديو مهووس الذكي
      </div>
      <div style='font-size:.62rem;opacity:.35;letter-spacing:.2em;margin-top:2px'>
        MAHWOUS AI STUDIO · 2026
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Stats
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""<div class="stat-box">
            <div class="stat-num">{len(st.session_state.history)}</div>
            <div class="stat-lbl">حملات</div></div>""", unsafe_allow_html=True)
    with col2:
        has_video = "✅" if st.session_state.video_url else "—"
        st.markdown(f"""<div class="stat-box">
            <div class="stat-num">{has_video}</div>
            <div class="stat-lbl">فيديو</div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="sec-label">🔑 مفاتيح API</div>', unsafe_allow_html=True)

    google_key = st.text_input("Google AI Key", value=GOOGLE_KEY, type="password", key="gk")
    luma_key   = st.text_input("Luma AI Key",   value=LUMA_KEY,   type="password", key="lk")

    if google_key: globals()["GOOGLE_KEY"] = google_key
    if luma_key:   globals()["LUMA_KEY"]   = luma_key

    st.markdown("---")
    st.markdown('<div class="sec-label">📋 DNA مهووس</div>', unsafe_allow_html=True)
    dna = st.text_area("شخصية مهووس", value=MAHWOUS_DNA, height=100)
    if dna: globals()["MAHWOUS_DNA"] = dna

    st.markdown("---")
    if st.button("🗑️ مسح الجلسة"):
        for k in ["analysis","social_images","video_url","video_job_id","video_status"]:
            st.session_state[k] = None if "images" not in k else {"ig":None,"snap":None,"x":None}
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding:10px 0 4px;border-bottom:1px solid rgba(212,175,55,0.15);margin-bottom:20px'>
  <h1 style='font-size:1.7rem;margin:0'>استديو مهووس الذكي 🌟</h1>
  <p style='font-size:.75rem;color:rgba(224,208,176,.4);letter-spacing:.15em;margin:4px 0 0;
    font-family:Tajawal,sans-serif'>
    GEMINI 2.5 · IMAGEN 4.0 · LUMA RAY 2.0
  </p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🧠 العقل المبدع",
    "🖼️ صور الحملة",
    "🎬 المحرك السينمائي",
    "📜 السيناريو",
])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — CREATIVE BRAIN
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    col_in, col_out = st.columns([1, 1.3], gap="large")

    with col_in:
        st.markdown('<div class="sec-label">💡 فكرتك</div>', unsafe_allow_html=True)
        brief = st.text_area(
            "اكتب فكرة الفيديو",
            placeholder="مثال: أريد فيديو لعطر شتوي ثقيل يوحي بالفخامة والغموض في لندن الليلية...",
            height=150,
            label_visibility="collapsed",
        )

        # Quick idea buttons
        st.markdown('<div style="font-size:.7rem;opacity:.5;margin:8px 0 4px">⚡ أفكار سريعة</div>', unsafe_allow_html=True)
        ideas = [
            "عطر عود ملكي — ليلة ذهبية في دبي",
            "عطر زهري — صباح باريسي رومانسي",
            "عطر مسكي — لقطة داخل رولز رويس",
            "عطر خشبي — صحراء نجد عند الغروب",
        ]
        for idea in ideas:
            if st.button(f"✦ {idea}", key=f"idea_{idea[:10]}"):
                st.session_state["quick_idea"] = idea
                st.rerun()

        if "quick_idea" in st.session_state:
            brief = st.session_state.pop("quick_idea")

        analyze_btn = st.button("🧠 تحليل الفكرة وإنشاء القصة (Gemini)")

        if analyze_btn:
            if not brief.strip():
                st.warning("⚠️ أدخل فكرة أولاً")
            else:
                with st.spinner("🌀 جيمني يفكر..."):
                    result = call_gemini(brief)
                if result:
                    st.session_state.analysis = result
                    st.session_state.history.append({
                        "brief": brief,
                        "perfume": result.get("perfume",""),
                        "time": datetime.now().strftime("%H:%M"),
                    })
                    st.success("✅ تم! انتقل لتبويب السيناريو أو الصور")
                    st.rerun()

    with col_out:
        st.markdown('<div class="sec-label">✨ نتيجة جيمني</div>', unsafe_allow_html=True)
        if not st.session_state.analysis:
            st.markdown("""
            <div style='border:2px dashed rgba(212,175,55,0.15);border-radius:20px;
                padding:50px;text-align:center;opacity:.3'>
              <div style='font-size:3rem;margin-bottom:12px'>🧠</div>
              <div style='font-family:Cinzel,serif;font-size:1rem'>انتظار الإبداع...</div>
            </div>""", unsafe_allow_html=True)
        else:
            a = st.session_state.analysis
            # Perfume name
            st.markdown(f"""
            <div class="card">
              <div style='font-size:.65rem;color:rgba(212,175,55,.6);letter-spacing:.2em;text-transform:uppercase;margin-bottom:6px'>العطر المقترح</div>
              <div style='font-family:Cinzel,serif;font-size:1.6rem;color:#fff;font-weight:900'>{a.get('perfume','')}</div>
              <span class="tag tg">بواسطة Gemini 2.5</span>
            </div>""", unsafe_allow_html=True)

            # Story
            st.markdown(f"""
            <div class="card">
              <div class="card-title">📖 القصة والهوك</div>
              <div class="card-body" style='font-style:italic;border-right:3px solid #D4AF37;padding-right:12px'>
                {a.get('story','')}
              </div>
            </div>""", unsafe_allow_html=True)

            # Scenario preview
            scenario = a.get("scenario", [])
            st.markdown(f"""
            <div class="card">
              <div class="card-title">🎬 السيناريو ({len(scenario)} لقطات)</div>
              <div class="card-body">
                {'  ·  '.join([f"لقطة {s['shot']}: {s.get('title','')}" for s in scenario])}
              </div>
              <div style='margin-top:8px'>
                <span class="tag tn">سيناريو جاهز</span>
                <span class="tag tp">بروبتات جاهزة</span>
              </div>
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — IMAGE GENERATION
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    if not st.session_state.analysis:
        st.info("💡 ابدأ بتحليل فكرتك في تبويب **العقل المبدع** أولاً")
    else:
        a = st.session_state.analysis
        col_ctrl, col_prev = st.columns([1, 1.5], gap="large")

        with col_ctrl:
            st.markdown('<div class="sec-label">⚙️ إعدادات الصور</div>', unsafe_allow_html=True)

            img_type = st.radio(
                "نوع الصورة",
                ["🎭 مهووس + العطر (هوية البراند)", "🌟 صور السوشال ميديا"],
                label_visibility="collapsed",
            )

            custom_prompt = st.text_area(
                "تعديل البروبت (اختياري)",
                value=a.get("social_prompt", "") if "سوشال" in img_type else a.get("char_prompt",""),
                height=100,
            )

            platform = st.selectbox(
                "المنصة",
                ["Instagram (1:1)", "Snapchat (9:16)", "Twitter/X (16:9)"],
            ) if "سوشال" in img_type else None

            if st.button("🎨 توليد الصورة الآن (Imagen 4.0)"):
                prompt = custom_prompt or a.get("social_prompt", a.get("char_prompt",""))
                if "مهووس" in img_type:
                    prompt = f"{MAHWOUS_DNA}. {a.get('char_prompt','')}. {prompt}"
                with st.spinner("🎨 Imagen يرسم..."):
                    img_data = call_imagen(prompt)
                if img_data:
                    key = "ig"
                    if platform and "Snap" in platform: key = "snap"
                    elif platform and "Twitter" in platform: key = "x"
                    st.session_state.social_images[key] = img_data
                    st.success("✅ تم توليد الصورة!")
                    st.rerun()

            st.markdown("---")
            st.markdown('<div class="sec-label">🚀 توليد كل منصات</div>', unsafe_allow_html=True)
            if st.button("⚡ توليد الثلاث منصات دفعة واحدة"):
                base_prompt = a.get("social_prompt", "")
                with st.spinner("⚡ جاري توليد 3 صور..."):
                    for key, extra in [("ig","square 1:1"), ("snap","vertical 9:16 portrait"), ("x","horizontal 16:9 landscape")]:
                        img = call_imagen(f"{base_prompt}. {extra} format.")
                        if img:
                            st.session_state.social_images[key] = img
                st.success("✅ تم توليد صور المنصات الثلاث!")
                st.rerun()

        with col_prev:
            st.markdown('<div class="sec-label">🖼️ معاينة الصور</div>', unsafe_allow_html=True)
            imgs = st.session_state.social_images
            labels = [("ig","Instagram (1:1)"), ("snap","Snapchat (9:16)"), ("x","Twitter/X (16:9)")]

            any_img = any(imgs[k] for k, _ in labels)
            if not any_img:
                st.markdown("""
                <div style='border:2px dashed rgba(212,175,55,0.12);border-radius:16px;
                    padding:60px;text-align:center;opacity:.3'>
                  <div style='font-size:2.5rem'>🖼️</div>
                  <div style='margin-top:8px;font-size:.85rem'>الصور ستظهر هنا</div>
                </div>""", unsafe_allow_html=True)
            else:
                for k, label in labels:
                    if imgs[k]:
                        st.markdown(f"**{label}**")
                        st.image(imgs[k], use_container_width=True)
                        # Download
                        b64_clean = imgs[k].split(",")[1]
                        st.download_button(
                            f"⬇️ تحميل {label}",
                            data=base64.b64decode(b64_clean),
                            file_name=f"mahwous_{k}.png",
                            mime="image/png",
                            key=f"dl_{k}",
                        )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — VIDEO GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    col_v_left, col_v_right = st.columns([1, 1.4], gap="large")

    with col_v_left:
        st.markdown('<div class="sec-label">🎬 إعدادات الفيديو</div>', unsafe_allow_html=True)

        # Auto-fill from analysis
        default_prompt = ""
        if st.session_state.analysis:
            sc = st.session_state.analysis.get("scenario", [])
            if sc:
                default_prompt = sc[0].get("prompt_en", sc[0].get("desc", ""))

        video_prompt = st.text_area(
            "بروبت الفيديو (إنجليزي)",
            value=default_prompt,
            height=120,
            placeholder="Mahwous holds the perfume bottle, golden smoke swirls around him, cinematic luxury shot...",
        )

        st.markdown('<div style="font-size:.75rem;opacity:.5;margin:8px 0 4px">صور مرجعية (اختياري)</div>', unsafe_allow_html=True)
        char_url = st.text_input("رابط صورة مهووس", placeholder="https://...")
        prod_url = st.text_input("رابط صورة العطر",  placeholder="https://...")

        aspect = st.selectbox("نسبة العرض", ["9:16 (عمودي)", "16:9 (أفقي)", "1:1 (مربع)"])
        aspect_val = aspect.split(" ")[0]

        generate_btn = st.button("🎥 توليد فيديو Luma Ray 2.0")

        if generate_btn:
            if not video_prompt.strip():
                st.warning("⚠️ أدخل بروبت الفيديو")
            else:
                with st.spinner("🚀 جاري إرسال الطلب لـ Luma..."):
                    job_id = create_luma_video(
                        video_prompt,
                        char_url if char_url.strip() else None,
                        prod_url  if prod_url.strip()  else None,
                    )
                if job_id:
                    st.session_state.video_job_id = job_id
                    st.session_state.video_status = "dreaming"
                    st.session_state.video_url = None
                    st.success(f"✅ تم إرسال الطلب! Job ID: `{job_id}`")
                    st.rerun()

        # Poll status
        if st.session_state.video_job_id and not st.session_state.video_url:
            st.markdown("---")
            st.markdown('<div class="sec-label">📡 حالة الفيديو</div>', unsafe_allow_html=True)
            if st.button("🔄 تحديث الحالة"):
                with st.spinner("جاري الفحص..."):
                    result = poll_luma_video(st.session_state.video_job_id)
                st.session_state.video_status = result["status"]
                if result["url"]:
                    st.session_state.video_url = result["url"]
                    st.rerun()

            status_icons = {
                "dreaming": ("🌀","جاري التوليد...","#C87AFF"),
                "completed": ("✅","مكتمل!","#50C878"),
                "failed":    ("❌","فشل التوليد","#FF7070"),
                "unknown":   ("❓","حالة مجهولة","#FFAA3C"),
            }
            s = st.session_state.video_status or "unknown"
            icon, text, color = status_icons.get(s, status_icons["unknown"])
            st.markdown(f"""
            <div class="status-box">
              <div class="status-icon">{icon}</div>
              <div class="status-text" style='color:{color}'>{text}</div>
              <div style='font-size:.65rem;opacity:.4;margin-top:4px'>ID: {st.session_state.video_job_id}</div>
            </div>""", unsafe_allow_html=True)

        # Past jobs
        st.markdown("---")
        st.markdown('<div class="sec-label">📂 الفيديوهات السابقة</div>', unsafe_allow_html=True)
        if st.button("📂 تحميل الفيديوهات من Luma"):
            with st.spinner("جاري الجلب..."):
                gens = list_luma_generations(8)
            for g in gens:
                gid   = g.get("id","")[:16]
                gst   = g.get("state","")
                gurl  = g.get("assets",{}).get("video","")
                color = "#50C878" if gst == "completed" else "#FFAA3C"
                st.markdown(f"""
                <div class="card" style='padding:10px 14px'>
                  <div style='display:flex;justify-content:space-between;align-items:center'>
                    <div style='font-size:.72rem;color:#fff;font-weight:700'>{gid}...</div>
                    <span style='font-size:.6rem;color:{color};font-weight:700'>{gst}</span>
                  </div>
                  {'<a href="' + gurl + '" target="_blank" style="font-size:.65rem;color:#D4AF37">▶ مشاهدة / تحميل</a>' if gurl else ''}
                </div>""", unsafe_allow_html=True)

    with col_v_right:
        st.markdown('<div class="sec-label">📺 عرض الفيديو</div>', unsafe_allow_html=True)
        if st.session_state.video_url:
            st.video(st.session_state.video_url)
            st.markdown(f"""
            <div style='text-align:center;margin-top:10px'>
              <a href="{st.session_state.video_url}" target="_blank"
                 style='background:#D4AF37;color:#000;padding:10px 24px;border-radius:10px;
                 font-weight:800;text-decoration:none;font-family:Tajawal,sans-serif'>
                ⬇️ تحميل الفيديو
              </a>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='border:2px dashed rgba(212,175,55,0.12);border-radius:20px;
                aspect-ratio:9/16;max-height:500px;display:flex;align-items:center;
                justify-content:center;opacity:.25;flex-direction:column;gap:12px'>
              <div style='font-size:3rem'>🎬</div>
              <div style='font-family:Cinzel,serif;font-size:.9rem'>Cinema View</div>
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 — SCENARIO
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    if not st.session_state.analysis:
        st.info("💡 ابدأ بتحليل فكرتك في تبويب **العقل المبدع** أولاً")
    else:
        a = st.session_state.analysis
        sc = a.get("scenario", [])

        st.markdown(f"""
        <div class="card" style='margin-bottom:20px'>
          <div style='font-size:.65rem;color:rgba(212,175,55,.6);letter-spacing:.2em;margin-bottom:4px'>حملة</div>
          <div style='font-family:Cinzel,serif;font-size:1.4rem;color:#fff'>{a.get('perfume','')}</div>
          <div style='font-size:.8rem;color:rgba(224,208,176,.6);margin-top:6px;font-style:italic'>
            {a.get('story','')}
          </div>
        </div>""", unsafe_allow_html=True)

        for shot in sc:
            num   = shot.get("shot","")
            title = shot.get("title","")
            desc  = shot.get("desc","")
            audio = shot.get("audio","")
            move  = shot.get("movement","")
            pen   = shot.get("prompt_en","")

            st.markdown(f"""
            <div class="shot-card">
              <div style='display:flex;align-items:flex-start;gap:16px'>
                <div>
                  <div class="shot-num">{num}</div>
                </div>
                <div style='flex:1'>
                  <div class="shot-title">🎥 {title}</div>
                  <div class="shot-text">{desc}</div>
                  <div class="shot-meta">
                    🎙️ <strong>الصوت:</strong> {audio}<br>
                    📷 <strong>الكاميرا:</strong> {move}
                  </div>
                  {f'<div class="shot-meta" style="margin-top:6px;font-size:.7rem;direction:ltr;text-align:left;color:rgba(180,100,255,.8)">🤖 Luma Prompt: {pen}</div>' if pen else ''}
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

            if st.button(f"🎬 توليد فيديو اللقطة {num}", key=f"shot_btn_{num}"):
                prompt_to_use = pen or desc
                st.session_state.video_job_id = None
                st.session_state.video_url    = None
                with st.spinner(f"🚀 إرسال اللقطة {num} إلى Luma..."):
                    job_id = create_luma_video(prompt_to_use)
                if job_id:
                    st.session_state.video_job_id = job_id
                    st.session_state.video_status = "dreaming"
                    st.success(f"✅ تم! انتقل لتبويب 🎬 لمتابعة الحالة · Job: {job_id}")

        # Export
        st.markdown("---")
        st.markdown('<div class="sec-label">📤 تصدير السيناريو</div>', unsafe_allow_html=True)
        export_data = json.dumps(a, ensure_ascii=False, indent=2)
        st.download_button(
            "⬇️ تحميل السيناريو JSON",
            data=export_data,
            file_name=f"mahwous_scenario_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
        )

        md_content = f"# حملة: {a.get('perfume','')}\n\n**القصة:** {a.get('story','')}\n\n"
        for s in sc:
            md_content += f"## لقطة {s.get('shot','')}: {s.get('title','')}\n\n"
            md_content += f"**الوصف:** {s.get('desc','')}\n\n"
            md_content += f"**الصوت:** {s.get('audio','')}\n\n"
            md_content += f"**الكاميرا:** {s.get('movement','')}\n\n"
            if s.get('prompt_en'):
                md_content += f"**Luma Prompt:** `{s.get('prompt_en','')}`\n\n"
            md_content += "---\n\n"

        st.download_button(
            "⬇️ تحميل السيناريو Markdown",
            data=md_content,
            file_name=f"mahwous_scenario_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
        )


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:2rem 0 1rem;font-size:.6rem;letter-spacing:.3em;
   text-transform:uppercase;opacity:.2;font-family:Cinzel,serif;direction:ltr'>
  Mahwous AI Intelligence Studio · 2026 · Gemini 2.5 · Imagen 4.0 · Luma Ray 2.0
</div>""", unsafe_allow_html=True)
