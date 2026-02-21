import streamlit as st
import requests
import json
import base64
from datetime import datetime

st.set_page_config(page_title="استديو مهووس الذكي", page_icon="🌟", layout="wide")

GOOGLE_KEY = st.secrets.get("GOOGLE_KEY", "AIzaSyBmXzIylxNEJWRNVZuLCVu8Xdg6ORF2QD8")
LUMA_KEY   = st.secrets.get("LUMA_KEY",   "luma-f801b085-d342-4e6a-b9ff-6aa21ba4b99c-8235cf57-8e12-4387-bbb1-8d999b766219")
GEMINI_MODEL = "gemini-2.0-flash"
IMAGEN_MODEL = "imagen-4.0-generate-001"
MAHWOUS_DNA  = "Photorealistic 3D animated character Mahwous, Gulf Arab perfume expert, neatly styled dark hair, groomed beard, warm brown eyes, luxury black suit with gold tie, cinematic lighting, Pixar Disney 3D style"
LUMA_BASE = "https://api.lumalabs.ai/dream-machine/v1"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;800;900&family=Cinzel:wght@700;900&display=swap');
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:#05080F!important;color:#C8D8F0!important;font-family:'Tajawal',sans-serif!important;direction:rtl}
[data-testid="stSidebar"]{background:#080D18!important;border-left:1px solid rgba(100,160,255,.15)}
[data-testid="stHeader"]{background:transparent!important}
h1,h2,h3{color:#6EB4FF!important;font-family:'Cinzel',serif!important}
#MainMenu,footer,[data-testid="stToolbar"]{visibility:hidden}
[data-baseweb="tab-list"]{background:#0D1525!important;border-radius:12px;padding:4px;gap:4px}
[data-baseweb="tab"]{color:rgba(200,216,240,.45)!important;font-family:'Tajawal',sans-serif!important;font-weight:700!important;border-radius:8px!important}
[aria-selected="true"][data-baseweb="tab"]{background:linear-gradient(135deg,#1A5FBF,#4A9FFF)!important;color:#fff!important}
textarea,.stTextInput input,.stTextArea textarea{background:#0D1525!important;border:1px solid rgba(100,160,255,.25)!important;color:#C8D8F0!important;border-radius:10px!important;font-family:'Tajawal',sans-serif!important}
.stButton>button{background:linear-gradient(135deg,#0A3A8A,#2A7FFF)!important;color:#fff!important;font-weight:800!important;border:none!important;border-radius:10px!important;width:100%!important;font-family:'Tajawal',sans-serif!important;box-shadow:0 4px 20px rgba(42,127,255,.3)!important}
.stButton>button:hover{box-shadow:0 6px 28px rgba(42,127,255,.5)!important}
.stDownloadButton>button{background:rgba(100,160,255,.1)!important;color:#6EB4FF!important;border:1px solid rgba(100,160,255,.3)!important;border-radius:10px!important;font-family:'Tajawal',sans-serif!important;font-weight:700!important}
[data-baseweb="select"]>div{background:#0D1525!important;border-color:rgba(100,160,255,.25)!important}
.gc{background:#0D1525;border:1px solid rgba(100,160,255,.18);border-radius:14px;padding:18px 20px;margin-bottom:14px}
.gcr{background:#0D1525;border:1px solid rgba(100,160,255,.12);border-radius:14px;padding:16px 20px;margin-bottom:12px;border-right:4px solid #2A7FFF}
.sl{font-size:.65rem;font-weight:800;letter-spacing:.2em;text-transform:uppercase;color:rgba(110,180,255,.65);padding-right:10px;border-right:3px solid #1A5FBF;margin-bottom:10px;display:block}
.sb{text-align:center;background:#0D1525;border:1px solid rgba(100,160,255,.2);border-radius:12px;padding:12px;margin:5px 0}
.sn{font-family:'Cinzel',serif;font-size:1.5rem;color:#6EB4FF;font-weight:900;display:block}
.slb{font-size:.62rem;color:rgba(200,216,240,.35);letter-spacing:.1em;text-transform:uppercase}
</style>
""", unsafe_allow_html=True)

# Session State
for k,v in dict(analysis=None,images={},job_id=None,job_status=None,video_url=None,history=[],video_prompt="").items():
    if k not in st.session_state: st.session_state[k]=v

# ── API helpers ──────────────────────────────────────────────────────────────
def call_gemini(brief):
    system='''أنت المدير الإبداعي لاستديو مهووس.
أجب فقط بـ JSON object واحد (ليس array) بهذا الشكل بالضبط بدون أي نص إضافي:
{"perfume":"اسم العطر","story":"القصة الجذابة بالعربية","scenario":[{"shot":1,"title":"عنوان","desc":"وصف المشهد","audio":"الصوت أو الحوار","movement":"حركة الكاميرا","prompt_en":"cinematic english luma prompt"},{"shot":2,"title":"عنوان","desc":"وصف","audio":"صوت","movement":"حركة","prompt_en":"prompt"},{"shot":3,"title":"عنوان","desc":"وصف","audio":"صوت","movement":"حركة","prompt_en":"prompt"}]}
مهم جداً: الجواب يجب أن يكون object وليس array.'''
    r=requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GOOGLE_KEY}",
        json={"contents":[{"parts":[{"text":f"الفكرة: {brief}"}]}],"systemInstruction":{"parts":[{"text":system}]},
              "generationConfig":{"responseMimeType":"application/json","temperature":0.9}},timeout=60)
    r.raise_for_status()
    data=r.json()
    if "error" in data: raise Exception(data["error"]["message"])
    parsed = json.loads(data["candidates"][0]["content"]["parts"][0]["text"])
    # Fix: if Gemini returns a list, take first element
    if isinstance(parsed, list):
        parsed = parsed[0] if parsed else {}
    # Fix: ensure required keys exist
    if "perfume" not in parsed:
        raise Exception("استجابة Gemini غير صحيحة - حاول مرة أخرى")
    return parsed

def call_imagen(prompt):
    r=requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{IMAGEN_MODEL}:predict?key={GOOGLE_KEY}",
        json={"instances":[{"prompt":f"{prompt}. Cinematic luxury 4K perfume advertisement."}],"parameters":{"sampleCount":1}},timeout=90)
    r.raise_for_status()
    data=r.json()
    if "error" in data: raise Exception(data["error"]["message"])
    return "data:image/png;base64,"+data["predictions"][0]["bytesBase64Encoded"]

def luma_create(prompt,char_url="",prod_url=""):
    headers={"Authorization":f"Bearer {LUMA_KEY}","Content-Type":"application/json"}
    body={"prompt":f"{prompt}. {MAHWOUS_DNA}. Ultra HD cinematic luxury perfume ad.","aspect_ratio":"9:16"}
    if char_url or prod_url:
        kf={}
        if char_url: kf["frame0"]={"type":"image","url":char_url}
        if prod_url: kf["frame1"]={"type":"image","url":prod_url}
        body["keyframes"]=kf
    r=requests.post(f"{LUMA_BASE}/generations",json=body,headers=headers,timeout=30)
    r.raise_for_status()
    data=r.json()
    if "id" not in data: raise Exception(str(data))
    return data["id"]

def luma_poll(job_id):
    r=requests.get(f"{LUMA_BASE}/generations/{job_id}",headers={"Authorization":f"Bearer {LUMA_KEY}"},timeout=20)
    r.raise_for_status()
    return r.json()

def luma_list(limit=8):
    try:
        r=requests.get(f"{LUMA_BASE}/generations?limit={limit}",headers={"Authorization":f"Bearer {LUMA_KEY}"},timeout=20)
        data=r.json()
        return data if isinstance(data,list) else data.get("generations",[])
    except: return []

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<div style='text-align:center;padding:18px 0 12px'>
    <div style='width:58px;height:58px;background:#2A7FFF;border-radius:16px;display:inline-flex;align-items:center;justify-content:center;font-size:1.7rem;font-weight:900;color:#000;box-shadow:0 0 24px rgba(42,127,255,.45)'>م</div>
    <div style='font-family:Cinzel,serif;color:#6EB4FF;font-weight:700;font-size:.95rem;margin-top:10px'>استديو مهووس الذكي</div>
    <div style='font-size:.58rem;opacity:.35;letter-spacing:.18em;margin-top:3px'>MAHWOUS AI STUDIO · 2026</div></div>""",unsafe_allow_html=True)
    st.markdown("---")
    c1,c2=st.columns(2)
    with c1: st.markdown(f'<div class="sb"><span class="sn">{len(st.session_state.history)}</span><span class="slb">حملات</span></div>',unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="sb"><span class="sn">{"✅" if st.session_state.video_url else "—"}</span><span class="slb">فيديو</span></div>',unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<span class="sl">🔑 مفاتيح API</span>',unsafe_allow_html=True)
    gk=st.text_input("Google AI Key",value=GOOGLE_KEY,type="password")
    lk=st.text_input("Luma AI Key",value=LUMA_KEY,type="password")
    if gk: GOOGLE_KEY=gk
    if lk: LUMA_KEY=lk
    st.markdown("---")
    if st.button("🗑️ مسح الجلسة"):
        for k in ["analysis","images","job_id","job_status","video_url","video_prompt"]:
            st.session_state[k]=None if k!="images" else {}
        st.rerun()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""<div style='padding:8px 0 16px;border-bottom:1px solid rgba(100,160,255,.12);margin-bottom:22px'>
<h1 style='font-size:1.5rem;margin:0'>استديو مهووس الذكي 🌟</h1>
<p style='font-size:.7rem;color:rgba(200,216,240,.35);letter-spacing:.15em;margin:4px 0 0'>GEMINI 2.0 · IMAGEN 4.0 · LUMA RAY 2.0</p></div>""",unsafe_allow_html=True)

tab1,tab2,tab3,tab4=st.tabs(["🧠 العقل المبدع","🖼️ صور الحملة","🎬 الفيديو","📜 السيناريو"])

# ══ TAB 1: العقل المبدع ══════════════════════════════════════════════════════
with tab1:
    L,R=st.columns([1,1.4],gap="large")
    with L:
        st.markdown('<span class="sl">💡 فكرتك</span>',unsafe_allow_html=True)
        brief=st.text_area("الفكرة",height=130,label_visibility="collapsed",placeholder="مثال: أريد فيديو لعطر شتوي فاخر يوحي بالغموض في لندن الليلية...")
        st.markdown('<span class="sl" style="margin-top:10px">⚡ أفكار سريعة</span>',unsafe_allow_html=True)
        for idea in ["عطر عود ملكي — ليلة ذهبية في دبي","عطر زهري — صباح باريسي رومانسي","عطر مسكي — داخل رولز رويس ليلاً","عطر خشبي — صحراء نجد عند الغروب"]:
            if st.button(f"✦  {idea}",key=f"i_{idea[:6]}"):
                st.session_state["_b"]=idea; st.rerun()
        if "_b" in st.session_state: brief=st.session_state.pop("_b")
        if st.button("🧠  تحليل الفكرة وإنشاء القصة  (Gemini)"):
            if not brief.strip(): st.warning("أدخل فكرة أولاً ⚠️")
            else:
                with st.spinner("🌀 جيمني يفكر..."):
                    try:
                        r=call_gemini(brief)
                        st.session_state.analysis=r
                        st.session_state.history.append({"brief":brief,"perfume":r.get("perfume",""),"time":datetime.now().strftime("%H:%M")})
                        if r.get("scenario"): st.session_state.video_prompt=r["scenario"][0].get("prompt_en","")
                        st.success("✅ تم! انتقل لأي تبويب")
                    except Exception as e: st.error(f"❌ خطأ Gemini: {e}")
    with R:
        st.markdown('<span class="sl">✨ نتيجة جيمني</span>',unsafe_allow_html=True)
        a=st.session_state.analysis
        if not a:
            st.markdown('<div style="border:2px dashed rgba(100,160,255,.12);border-radius:18px;padding:60px;text-align:center;opacity:.28"><div style="font-size:3rem;margin-bottom:12px">🧠</div><div style="font-weight:700">انتظار الإبداع...</div></div>',unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="gc"><div style="font-size:.6rem;color:rgba(110,180,255,.6);letter-spacing:.2em;text-transform:uppercase;margin-bottom:5px">العطر المقترح</div><div style="font-size:1.5rem;font-weight:900;color:#fff">{a.get("perfume","")}</div></div>',unsafe_allow_html=True)
            st.markdown(f'<div class="gc"><div style="font-size:.6rem;color:rgba(110,180,255,.6);letter-spacing:.2em;text-transform:uppercase;margin-bottom:8px">📖 القصة والهوك</div><div style="font-style:italic;font-size:.85rem;line-height:1.75;border-right:3px solid #2A7FFF;padding-right:12px;color:rgba(200,216,240,.85)">{a.get("story","")}</div></div>',unsafe_allow_html=True)
            sc=a.get("scenario",[])
            if sc:
                rows="".join(f'<div style="display:flex;gap:12px;align-items:flex-start;padding:8px 0;border-bottom:1px solid rgba(255,255,255,.04)"><div style="width:30px;height:30px;background:#2A7FFF;border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:900;color:#000;flex-shrink:0;font-size:.85rem">{s["shot"]}</div><div><div style="font-weight:700;font-size:.82rem;color:#fff">{s.get("title","")}</div><div style="font-size:.73rem;color:rgba(200,216,240,.5);margin-top:2px">{s.get("desc","")[:80]}...</div></div></div>' for s in sc)
                st.markdown(f'<div class="gc"><div style="font-size:.6rem;color:rgba(110,180,255,.6);letter-spacing:.2em;text-transform:uppercase;margin-bottom:10px">🎬 السيناريو ({len(sc)} لقطات)</div>{rows}</div>',unsafe_allow_html=True)

# ══ TAB 2: صور الحملة ════════════════════════════════════════════════════════
with tab2:
    a=st.session_state.analysis
    if not a: st.info("💡 ابدأ بتحليل فكرة في تبويب **العقل المبدع** أولاً")
    else:
        L,R=st.columns([1,1.5],gap="large")
        with L:
            st.markdown(f'<div class="gc"><span class="sl">العطر</span><div style="font-size:1rem;font-weight:800;color:#fff">{a.get("perfume","")}</div></div>',unsafe_allow_html=True)
            st.markdown('<span class="sl">⚙️ بروبت الصورة</span>',unsafe_allow_html=True)
            custom=st.text_area("بروبت",value=f"{MAHWOUS_DNA}. {a.get('perfume','')} luxury perfume.",height=90,label_visibility="collapsed")
            if st.button("🎨  توليد 3 صور للمنصات  (Imagen 4.0)"):
                imgs={}; bar=st.progress(0,text="جاري التوليد...")
                for i,(key,extra,lbl) in enumerate([("ig","square 1:1","Instagram"),("snap","vertical portrait 9:16","Snapchat"),("x","horizontal wide 16:9","Twitter")]):
                    bar.progress((i+1)*30,text=f"⏳ {lbl}...")
                    try: imgs[key]=call_imagen(f"{custom}. {extra} format.")
                    except Exception as e: st.error(f"❌ {lbl}: {e}")
                bar.progress(100,text="✅ تم!")
                st.session_state.images=imgs; st.rerun()
        with R:
            st.markdown('<span class="sl">🖼️ الصور</span>',unsafe_allow_html=True)
            imgs=st.session_state.images
            if not imgs:
                st.markdown('<div style="border:2px dashed rgba(100,160,255,.1);border-radius:14px;padding:60px;text-align:center;opacity:.25"><div style="font-size:2.5rem">🖼️</div><div style="margin-top:8px">الصور ستظهر هنا</div></div>',unsafe_allow_html=True)
            else:
                for key,lbl in [("ig","Instagram (1:1)"),("snap","Snapchat (9:16)"),("x","Twitter (16:9)")]:
                    if imgs.get(key):
                        st.markdown(f"**{lbl}**")
                        st.image(imgs[key],use_container_width=True)
                        st.download_button(f"⬇️ تحميل {lbl}",data=base64.b64decode(imgs[key].split(",")[1]),file_name=f"mahwous_{key}.png",mime="image/png",key=f"dl_{key}")

# ══ TAB 3: الفيديو ═══════════════════════════════════════════════════════════
with tab3:
    L,R=st.columns([1,1.4],gap="large")
    with L:
        st.markdown('<span class="sl">🎬 إعدادات الفيديو</span>',unsafe_allow_html=True)
        vp=st.text_area("البروبت (إنجليزي أفضل)",value=st.session_state.video_prompt,height=110,placeholder="Mahwous holds a golden perfume bottle, cinematic close-up, golden smoke swirls...")
        c1,c2=st.columns(2)
        with c1: cu=st.text_input("رابط صورة مهووس",placeholder="https://...")
        with c2: pu=st.text_input("رابط صورة العطر",placeholder="https://...")
        if st.button("🎥  إنشاء فيديو Luma Ray 2.0"):
            if not vp.strip(): st.warning("أدخل البروبت أولاً ⚠️")
            else:
                with st.spinner("🚀 جاري الإرسال إلى Luma..."):
                    try:
                        jid=luma_create(vp,cu.strip(),pu.strip())
                        st.session_state.job_id=jid; st.session_state.job_status="dreaming"; st.session_state.video_url=None
                        st.success(f"✅ تم الإرسال! انتظر 2-3 دقائق ثم اضغط تحديث")
                        st.code(jid,language=None)
                    except Exception as e: st.error(f"❌ خطأ Luma: {e}")
        if st.session_state.job_id:
            st.markdown("---")
            st.markdown('<span class="sl">📡 حالة الفيديو</span>',unsafe_allow_html=True)
            status=st.session_state.job_status or "unknown"
            color={"completed":"#50C878","failed":"#FF7070","dreaming":"#C87AFF"}.get(status,"#FFAA3C")
            icon={"completed":"✅","failed":"❌","dreaming":"🌀"}.get(status,"❓")
            label={"completed":"مكتمل!","failed":"فشل التوليد","dreaming":"جاري التوليد..."}.get(status,"غير معروف")
            st.markdown(f'<div style="text-align:center;background:#0D1525;border-radius:12px;padding:16px;border:1px solid rgba(100,160,255,.15)"><div style="font-size:2rem;margin-bottom:6px">{icon}</div><div style="font-weight:800;color:{color}">{label}</div><div style="font-size:.62rem;opacity:.35;margin-top:4px;direction:ltr">{st.session_state.job_id}</div></div>',unsafe_allow_html=True)
            if st.button("🔄  تحديث الحالة"):
                with st.spinner("جاري الفحص..."):
                    try:
                        data=luma_poll(st.session_state.job_id)
                        st.session_state.job_status=data.get("state","unknown")
                        if data.get("state")=="completed": st.session_state.video_url=data.get("assets",{}).get("video")
                        if data.get("state")=="failed": st.error("❌ فشل التوليد في Luma")
                        st.rerun()
                    except Exception as e: st.error(f"❌ {e}")
            st.caption("⏱️ الفيديو يحتاج 2-4 دقائق — اضغط تحديث كل دقيقة")
        a=st.session_state.analysis
        if a and a.get("scenario"):
            st.markdown("---")
            st.markdown('<span class="sl">⚡ لقطات جاهزة</span>',unsafe_allow_html=True)
            for s in a["scenario"]:
                if st.button(f"لقطة {s['shot']}: {s.get('title','')}",key=f"sh_{s['shot']}"):
                    st.session_state.video_prompt=s.get("prompt_en",s.get("desc","")); st.rerun()
        st.markdown("---")
        if st.button("📂  عرض الفيديوهات السابقة"):
            with st.spinner("جاري الجلب..."): gens=luma_list()
            for g in gens:
                gid=str(g.get("id",""))[:20]; gst=g.get("state","")
                gurl=g.get("assets",{}).get("video","") if isinstance(g.get("assets"),dict) else ""
                color="#50C878" if gst=="completed" else "#FFAA3C"
                link=f'<a href="{gurl}" target="_blank" style="color:#6EB4FF;font-size:.65rem">▶ مشاهدة</a>' if gurl else ""
                st.markdown(f'<div class="gc" style="padding:10px 14px;margin-bottom:6px"><div style="display:flex;justify-content:space-between;align-items:center"><code style="font-size:.68rem;color:rgba(200,216,240,.6)">{gid}...</code><span style="font-size:.65rem;color:{color};font-weight:700">{gst}</span></div>{link}</div>',unsafe_allow_html=True)
    with R:
        st.markdown('<span class="sl">📺 عرض الفيديو</span>',unsafe_allow_html=True)
        if st.session_state.video_url:
            st.video(st.session_state.video_url)
            st.markdown(f'<div style="text-align:center;margin-top:10px"><a href="{st.session_state.video_url}" target="_blank" style="background:#2A7FFF;color:#fff;padding:11px 28px;border-radius:10px;font-weight:800;text-decoration:none;font-size:.88rem">⬇️ تحميل الفيديو</a></div>',unsafe_allow_html=True)
        else:
            st.markdown('<div style="border:2px dashed rgba(100,160,255,.1);border-radius:18px;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:12px;opacity:.22;padding:80px 0"><div style="font-size:3.5rem">🎬</div><div style="font-weight:700;font-size:1rem">Cinema View</div><div style="font-size:.72rem">الفيديو يظهر هنا بعد الاكتمال</div></div>',unsafe_allow_html=True)

# ══ TAB 4: السيناريو ══════════════════════════════════════════════════════════
with tab4:
    a=st.session_state.analysis
    if not a:
        st.markdown('<div style="text-align:center;padding:60px;opacity:.28"><div style="font-size:3rem;margin-bottom:12px">📜</div><div style="font-weight:700">أدخل فكرتك في العقل المبدع أولاً</div></div>',unsafe_allow_html=True)
    else:
        _,C,_=st.columns([0.5,2,0.5])
        with C:
            st.markdown(f'<div class="gc" style="margin-bottom:22px"><div style="font-size:1.4rem;font-weight:900;color:#fff;margin-bottom:8px">{a.get("perfume","")}</div><div style="font-style:italic;font-size:.84rem;color:rgba(200,216,240,.65);line-height:1.75">{a.get("story","")}</div></div>',unsafe_allow_html=True)
            for s in a.get("scenario",[]):
                pen=f'<div style="background:rgba(180,100,255,.07);border-radius:8px;padding:8px 12px;direction:ltr;text-align:left;font-size:.72rem;color:rgba(180,100,255,.8);margin-bottom:10px">🤖 {s.get("prompt_en","")}</div>' if s.get("prompt_en") else ""
                st.markdown(f'''<div class="gcr"><div style="display:flex;gap:16px;align-items:flex-start">
                <div style="width:40px;height:40px;background:#2A7FFF;border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:900;color:#000;font-size:1.1rem;flex-shrink:0">{s.get("shot","")}</div>
                <div style="flex:1"><div style="font-weight:800;color:#A0D4FF;margin-bottom:6px">{s.get("title","")}</div>
                <div style="font-size:.83rem;color:rgba(200,216,240,.7);line-height:1.65;margin-bottom:10px">{s.get("desc","")}</div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px">
                <div style="background:rgba(0,0,0,.35);border-radius:8px;padding:8px 12px"><div style="font-size:.58rem;color:#6EB4FF;font-weight:700;margin-bottom:4px">🎙️ الصوت</div><div style="font-size:.75rem;font-style:italic;color:rgba(200,216,240,.55)">{s.get("audio","")}</div></div>
                <div style="background:rgba(0,0,0,.35);border-radius:8px;padding:8px 12px"><div style="font-size:.58rem;color:#6EB4FF;font-weight:700;margin-bottom:4px">📷 الكاميرا</div><div style="font-size:.75rem;color:rgba(200,216,240,.55)">{s.get("movement","")}</div></div>
                </div>{pen}</div></div></div>''',unsafe_allow_html=True)
                if st.button(f"🎬  توليد فيديو اللقطة {s.get('shot','')}",key=f"sv_{s.get('shot','')}"):
                    st.session_state.video_prompt=s.get("prompt_en",s.get("desc","")); st.rerun()
            st.markdown("---")
            st.markdown('<span class="sl">📤 تصدير</span>',unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1:
                st.download_button("⬇️ JSON",data=json.dumps(a,ensure_ascii=False,indent=2),file_name=f"mahwous_{datetime.now().strftime('%Y%m%d_%H%M')}.json",mime="application/json")
            with c2:
                md=f"# {a.get('perfume','')}\n\n{a.get('story','')}\n\n"+"".join(f"## لقطة {s.get('shot','')}: {s.get('title','')}\n\n{s.get('desc','')}\n\n**الصوت:** {s.get('audio','')}\n\n**الكاميرا:** {s.get('movement','')}\n\n---\n\n" for s in a.get("scenario",[]))
                st.download_button("⬇️ Markdown",data=md,file_name=f"mahwous_{datetime.now().strftime('%Y%m%d_%H%M')}.md",mime="text/markdown")

st.markdown('<div style="text-align:center;padding:30px 0 10px;font-size:.55rem;letter-spacing:.3em;text-transform:uppercase;opacity:.18;direction:ltr">MAHWOUS AI INTELLIGENCE STUDIO · 2026 · GEMINI · IMAGEN · LUMA RAY</div>',unsafe_allow_html=True)
