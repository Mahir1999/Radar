import streamlit as st
import time

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Pro Session Radar v74", page_icon="💎", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .stButton>button { width: 100%; height: 48px; font-weight: bold; border-radius: 10px; }
    .last-result-banner {
        background: #1a1a1a; padding: 10px; border-radius: 10px; border-right: 5px solid #39ff14;
        text-align: center; margin-bottom: 10px; color: #39ff14; font-weight: bold;
    }
    .jackpot-alert {
        background: linear-gradient(45deg, #4b0082, #000); border: 2px solid #ff00ff;
        padding: 10px; border-radius: 10px; text-align: center; color: #ff00ff;
        font-weight: bold; animation: pulse 1.5s infinite; margin-bottom: 10px;
    }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    .session-card {
        background: #111; border: 1px solid #333; padding: 10px; border-radius: 10px;
        display: flex; justify-content: space-around; margin-bottom: 15px; font-size: 14px;
    }
    .prob-box { 
        background: #111; border: 1px solid #333; border-radius: 8px; 
        padding: 8px; text-align: center; font-size: 12px;
    }
    .main-highlight { border: 2px solid #39ff14 !important; background: #002200 !important; }
    .category-box {
        background: #1a1a1a; border-radius: 10px; padding: 10px; margin-top: 5px; border: 1px dashed #444;
    }
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
if 'last_jackpot' not in st.session_state: st.session_state.last_jackpot = 0
if 'start_time' not in st.session_state: st.session_state.start_time = time.time()

def register_result(code):
    st.session_state.history.append(code)
    if code == 9: st.session_state.last_jackpot = len(st.session_state.history)

def undo_last():
    if st.session_state.history:
        removed = st.session_state.history.pop()
        if removed == 9:
            st.session_state.last_jackpot = 0
            for i, code in enumerate(st.session_state.history):
                if code == 9: st.session_state.last_jackpot = i + 1

hist = st.session_state.history
total_h = len(hist)

# --- مدير الجلسة ورادار الجكبوت ---
elapsed_min = int((time.time() - st.session_state.start_time) / 60)
st.markdown(f'<div class="session-card"><span>⏳ الوقت: <b>{elapsed_min} د</b></span><span>🎮 الجولات: <b>{total_h}</b></span><span>🛑 التركيز: <b>{"ممتاز" if elapsed_min < 30 else "تحتاج راحة"}</b></span></div>', unsafe_allow_html=True)

jack_gap = total_h - st.session_state.last_jackpot
if jack_gap > 80:
    st.markdown(f'<div class="jackpot-alert">⚡ رادار الجكبوت: غائب منذ {jack_gap} جولة! احتمال انفجاره مرتفع.</div>', unsafe_allow_html=True)

# --- أزرار التحكم ---
c_stat, c_undo, c_reset = st.columns([2, 1, 1])
with c_stat:
    if total_h < 30:
        st.write(f"📡 نضوج البيانات: {int((total_h/30)*100)}%")
        st.progress(total_h/30)
    else: st.success("✅ النظام مستقر")
with c_undo:
    if st.button("↩️ تراجع"): undo_last(); st.rerun()
with c_reset:
    if st.button("🗑️ مسح"): st.session_state.history = []; st.session_state.last_jackpot = 0; st.rerun()

# --- شريط التاريخ ---
if hist:
    st.markdown(f'<div class="last-result-banner">⏮️ الأخير: {SYMBOLS[hist[-1]]["name"]}</div>', unsafe_allow_html=True)
    timeline_html = '<div style="display:flex; overflow-x:auto; gap:5px; margin-bottom:15px;">'
    for code in reversed(hist[-12:]):
        timeline_html += f'<div style="background:#262730; padding:4px 10px; border-radius:6px; white-space:nowrap; color:#eee; font-size:13px;">{SYMBOLS[code]["name"].split()[0]}</div>'
    timeline_html += '</div>'
    st.markdown(timeline_html, unsafe_allow_html=True)

# --- محرك التوقعات (8 عناصر) ---
st.subheader("📊 تحليل النمط")
if total_h >= 30:
    global_counts = {c: hist.count(c) for c in range(1, 9)}
    recent_25 = hist[-25:]
    recent_counts = {c: recent_25.count(c) for c in range(1, 9)}
    combined_scores = {}
    for c in range(1, 9):
        score = (global_counts.get(c, 0) * 0.2) + (recent_counts.get(c, 0) * 0.8)
        combined_scores[c] = score
    sorted_probs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
    
    st.write("🔥 **الأقوى حالياً:**")
    p1 = st.columns(4)
    for i, (code, prob) in enumerate(sorted_probs[:4]):
        with p1[i]: st.markdown(f'<div class="prob-box main-highlight">{SYMBOLS[code]["name"].split()[0]}<br><b>نشط</b></div>', unsafe_allow_html=True)
    
    st.write("🛡️ **الاحتياط:**")
    p2 = st.columns(4)
    for i, (code, prob) in enumerate(sorted_probs[4:8]):
        with p2[i]: st.markdown(f'<div class="prob-box">{SYMBOLS[code]["name"].split()[0]}<br><b>ساكن</b></div>', unsafe_allow_html=True)

    # --- القسم الجديد: أفضل الخيارات حسب الفئة ---
    st.divider()
    st.write("🎯 **أفضل الخيارات حسب النوع:**")
    col_veg, col_ani = st.columns(2)
    
    # فلترة الخضروات والحيوانات
    veg_probs = [item for item in sorted_probs if SYMBOLS[item[0]]["type"] == "veg"]
    ani_probs = [item for item in sorted_probs if SYMBOLS[item[0]]["type"] == "ani"]
    
    with col_veg:
        st.markdown('<div class="category-box"><b>🥬 أقوى خضروات:</b><br>' + 
                    f'1. {SYMBOLS[veg_probs[0][0]]["name"]}<br>' +
                    f'2. {SYMBOLS[veg_probs[1][0]]["name"]}</div>', unsafe_allow_html=True)
    
    with col_ani:
        st.markdown('<div class="category-box"><b>🥩 أقوى حيوانات:</b><br>' + 
                    f'1. {SYMBOLS[ani_probs[0][0]]["name"]}<br>' +
                    f'2. {SYMBOLS[ani_probs[1][0]]["name"]}</div>', unsafe_allow_html=True)
else:
    st.info(f"📡 متبقي {30-total_h} جولة للتفعيل.")

# --- تسجيل النتائج ---
st.write("🔘 **سجل النتيجة:**")
r1 = st.columns(5)
for i, code in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[code]["name"].split()[0], key=f"r_{code}"): register_result(code); st.rerun()
r2 = st.columns(4)
for i, code in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[code]["name"].split()[0], key=f"r_{code}"): register_result(code); st.rerun()
