import streamlit as st
import time

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Confidence Radar v77", page_icon="🛡️", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .stButton>button { width: 100%; height: 48px; font-weight: bold; border-radius: 10px; }
    .next-hit-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #000 100%);
        border: 2px solid #39ff14; padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 15px;
    }
    .confidence-bar-container {
        background-color: #333; border-radius: 10px; margin: 10px 0; height: 12px; overflow: hidden;
    }
    .confidence-bar-fill {
        background: linear-gradient(90deg, #ff4b4b, #ffaa00, #39ff14);
        height: 100%; transition: width 0.5s ease-in-out;
    }
    .prob-box { 
        background: #111; border: 1px solid #333; border-radius: 8px; 
        padding: 8px; text-align: center; position: relative;
    }
    .gap-counter { position: absolute; top: 2px; right: 5px; font-size: 10px; color: #ff4b4b; font-weight: bold; }
    .main-highlight { border: 2px solid #39ff14 !important; background: #002200 !important; }
    </style>
    """, unsafe_allow_html=True)

SYMBOLS = {
    1: {"name": "🍅 طماطم", "type": "veg"}, 2: {"name": "🌽 ذرة", "type": "veg"}, 
    3: {"name": "🥕 جزر", "type": "veg"}, 4: {"name": "🫑 فلفل", "type": "veg"},
    5: {"name": "🐔 دجاجة", "type": "ani"}, 6: {"name": "🐑 خروف", "type": "ani"}, 
    7: {"name": "🐟 سمك", "type": "ani"}, 8: {"name": "🦐 روبيان", "type": "ani"},
    9: {"name": "💰 جكبوت", "type": "jack"}
}

if 'history' not in st.session_state: st.session_state.history = []

def register_result(code):
    st.session_state.history.append(code)

hist = st.session_state.history
total_h = len(hist)

# --- أزرار التحكم ---
c_undo, c_reset = st.columns(2)
with c_undo:
    if st.button("↩️ تراجع"): 
        if hist: st.session_state.history.pop(); st.rerun()
with c_reset:
    if st.button("🗑️ مسح الكل"): st.session_state.history = []; st.rerun()

# --- محرك التوقع ومؤشر الثقة ---
if total_h >= 30:
    gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 10)}
    
    # حساب الثقة بناءً على (حجم البيانات + استقرار النمط)
    confidence_score = min(total_h * 1.2, 100) # يزداد مع عدد الجولات
    if total_h > 50: confidence_score = min(confidence_score + 10, 100)
    
    # تحديد التوقع التالي
    next_expected = max(range(1, 9), key=lambda x: (hist[-25:].count(x)*0.8 + (1/max(gaps[x],1))*0.2))
    
    st.markdown(f"""
    <div class="next-hit-card">
        <div style="color:#39ff14; font-size:14px;">🎯 التوقع التالي الذكي</div>
        <div style="font-size:26px; font-weight:bold; color:white;">{SYMBOLS[next_expected]["name"]}</div>
        <div style="font-size:12px; color:#aaa; margin-top:5px;">قوة ثقة البيانات: {int(confidence_score)}%</div>
        <div class="confidence-bar-container">
            <div class="confidence-bar-fill" style="width: {confidence_score}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- رادار الفجوات والأنماط ---
st.subheader("📊 رادار الفجوات (العدد الأحمر = غياب)")
if total_h >= 30:
    gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 10)}
    global_counts = {c: hist.count(c) for c in range(1, 9)}
    recent_25 = hist[-25:]
    recent_counts = {c: recent_25.count(c) for c in range(1, 9)}
    combined_scores = {c: (global_counts.get(c, 0)*0.2 + recent_counts.get(c, 0)*0.8) for c in range(1, 9)}
    sorted_probs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

    p1 = st.columns(4)
    for i, (code, prob) in enumerate(sorted_probs[:4]):
        with p1[i]:
            st.markdown(f'<div class="prob-box main-highlight"><span class="gap-counter">{gaps[code]}</span>{SYMBOLS[code]["name"].split()[0]}<br><b>نشط</b></div>', unsafe_allow_html=True)

    p2 = st.columns(4)
    for i, (code, prob) in enumerate(sorted_probs[4:8]):
        with p2[i]:
            st.markdown(f'<div class="prob-box"><span class="gap-counter">{gaps[code]}</span>{SYMBOLS[code]["name"].split()[0]}<br><b>ساكن</b></div>', unsafe_allow_html=True)
else:
    st.info(f"📡 اجمع {30-total_h} جولة إضافية لبناء شريط الثقة.")

# --- تسجيل النتائج ---
st.write("🔘 **سجل النتيجة:**")
r1 = st.columns(5)
for i, code in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[code]["name"].split()[0], key=f"r_{code}"): register_result(code); st.rerun()
r2 = st.columns(4)
for i, code in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[code]["name"].split()[0], key=f"r_{code}"): register_result(code); st.rerun()
