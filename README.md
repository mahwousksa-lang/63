# 🌟 استديو مهووس الذكي

> تطبيق Streamlit عربي لإنشاء فيديوهات عطور احترافية بالذكاء الاصطناعي

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)

---

## ✨ المميزات

| الميزة | الوصف |
|--------|-------|
| 🧠 العقل المبدع | تحليل الأفكار وإنشاء قصص وسيناريوهات بـ Gemini 2.5 |
| 🖼️ صور الحملة | توليد صور متعددة المقاسات بـ Imagen 4.0 (Instagram · Snapchat · Twitter) |
| 🎬 محرك الفيديو | إنشاء فيديوهات سينمائية بـ Luma Ray 2.0 |
| 📜 السيناريو | عرض وتصدير السيناريو بصيغتي JSON و Markdown |

---

## 🚀 التشغيل المحلي

```bash
# 1. Clone المشروع
git clone https://github.com/YOUR_USERNAME/mahwous-ai-studio.git
cd mahwous-ai-studio

# 2. تثبيت المكتبات
pip install -r requirements.txt

# 3. إعداد مفاتيح API
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# ثم عدّل الملف وضع مفاتيحك

# 4. تشغيل التطبيق
streamlit run app.py
```

---

## 🔑 مفاتيح API المطلوبة

| المفتاح | المصدر |
|---------|--------|
| `GOOGLE_KEY` | [Google AI Studio](https://aistudio.google.com) |
| `LUMA_KEY` | [Luma AI](https://lumalabs.ai) |

### إعداد على Streamlit Cloud
1. ارفع المشروع على GitHub
2. اذهب إلى [share.streamlit.io](https://share.streamlit.io)
3. في **Settings → Secrets** أضف:

```toml
GOOGLE_KEY = "AIzaSy..."
LUMA_KEY   = "luma-..."
```

---

## 🏗️ هيكل المشروع

```
mahwous-ai-studio/
├── app.py                    # التطبيق الرئيسي
├── requirements.txt          # المكتبات المطلوبة
├── .gitignore
├── .streamlit/
│   └── secrets.toml.example  # نموذج إعداد المفاتيح
└── README.md
```

---

## 🎭 شخصية مهووس

> Photorealistic 3D animated character 'Mahwous', Gulf Arab perfume expert,
> neatly styled dark hair, groomed beard, warm brown eyes, wearing luxury black
> suit with gold tie. High-end cinematic lighting. Pixar/Disney 3D style.

يمكنك تخصيص DNA الشخصية من الشريط الجانبي في التطبيق.

---

## 📡 APIs المستخدمة

- **Google Gemini 2.5 Flash** — توليد النصوص والسيناريوهات
- **Google Imagen 4.0** — توليد الصور
- **Luma Ray 2.0** — توليد الفيديوهات

---

<div align="center">
  <strong>Mahwous AI Intelligence Studio · 2026</strong>
</div>
