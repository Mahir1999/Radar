import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Greedy AI v99.0", page_icon="🛡️", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    
    /* إطار لوحة الأزرار الموحد - يمنع الانهيار العمودي */
    .icon-grid-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 8px;
        background: rgba(0, 0, 0, 0.9);
        border: 2px solid #39ff14;
        padding: 15px;
        border-radius: 15px;
        margin-top: 10px;
    }

    /* تصميم الأزرار كمستطيلات صغيرة داخل الإطار */
    div.stButton > button {
        background-color: #001a00 !important;
        color: white !important;
        border: 1px solid #39ff14 !important;
        border-radius: 8px !important;
        min-width: 60px !important;
        height: 50px !important;
        font-size: 22px !important;
    }

    .status-bar { 
        background: #111; 
        padding: 8px; 
        border-radius: 10px; 
        text-align: center; 
        margin-bottom: 10px; 
        border: 1px solid #333;
    }
    .pattern-pulse { padding: 4px 10px; border-radius: 5px; font-weight: bold; font-size: 12px; }
    .next-hit-card { background: #1a1a1a; border: 2px solid #39ff14; padding: 10px; border-radius: 15px; text-align: center; margin-bottom: 10px; }
    .insurance-card { background: #001a33; border: 2px solid #00aaff; padding: 10px; border-radius: 15px; text-align: center; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

SYMBOLS = {1: "🍅", 2: "🌽", 3: "🥕", 4: "🫑", 5: "🐔", 6: "🐑", 7: "🐟", 8: "🦐", 9: "💰"}
VEGGIES, MEATS = [1, 2, 3, 4], [5, 6, 7, 8]

if 'history' not in st.session_state: st.session_state.history = []
if 'hits' not in st.session_state: st.session_state.hits = 0
if 'misses' not in st.session_state: st.session_state.misses = 0
if 'consecutive_misses' not in st.session_state: st.session_state.consecutive_misses = 0
if 'patterns_found' not in st.session_state: st.session_state.patterns_found = 0
if 'current_preds' not in st.session_state: st.session_state.current_preds = []

def register_result(code):
    if st.session_state.current_preds:
        if code in st.session_state.current_preds:
            st.session_state.hits += 1
            st.session_state.consecutive_misses = 0
        elif code != 9:
            st.session_state.misses += 1
            st.session_state.consecutive_misses += 1
            if st.session_state.consecutive_misses >= 2: st.session_state.patterns_found += 1
    st.session_state.history.append(code)

hist = st.session_state.history
total_h = len(hist)

# --- العدادات العلوية ---
st.write(f"<div style='display:flex; justify-content:space-around; font-size:14px; margin-bottom:10px;'><span>🔄 جولة: {total_h}</span><span style='color:#39ff14'>✅ فوز: {st.session_state.hits}</span><span style='color:#ff4b4b'>❌ خطأ: {st.session_state.misses}</span></div>", unsafe_allow_html=True)

# --- المربع الذهبي ودرع التأمين ---
if total_h > 0:
    gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 9)}
    scores = {c: (hist[-15:].count(c) * 0.7 + (gaps[c] * 0.3)) for c in range(1, 9)}
    top_4 = sorted(scores, key=scores.get, reverse=True)[:4]
    insurance_slot = sorted(MEATS, key=lambda x: gaps[x], reverse=True)[0] if all(c in VEGGIES for c in top_4) else sorted(scores, key=scores.get, reverse=True)[4]
    st.session_state.current_preds = top_4 + [insurance_slot]
    
    st.markdown(f'<div class="next-hit-card"><div style="color:#39ff14; font-size:11px;">🎯 المربع الذهبي</div><div style="display:flex; justify-content:center; gap:10px; margin-top:5px; font-size:20px;">' + "".join([f'<div>{SYMBOLS[c]}</div>' for c in top_4]) + '</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="insurance-card"><div style="color:#00aaff; font-size:11px;">🛡️ درع التأمين</div><div style="font-size:22px;">{SYMBOLS[insurance_slot]}</div></div>', unsafe_allow_html=True)

# --- استعادة شريط حالة النمط والأنماط (الميزة التي اختفت) ---
p_status = "ثابت ✅" if st.session_state.consecutive_misses < 2 else "متغير ⚠️"
p_bg = "#003300" if p_status == "ثابت ✅" else "#331a00"
gap_9 = (list(reversed(hist)).index(9) if 9 in hist else total_h)

st.markdown(f"""
<div class="status-bar">
    <span style="font-size:11px; color:#aaa;">🧠 أنماط: {st.session_state.patterns_found} | 💰 جكبوت: {gap_9}</span><br>
    <span class="pattern-pulse" style="background:{p_bg}; color:white;">حالة النمط: {p_status}</span>
</div>
""", unsafe_allow_html=True)

# --- لوحة تسجيل النتيجة (المربع الواحد المطلوب) ---
st.markdown('<div class="icon-grid-container">', unsafe_allow_html=True)
# عرض الرموز في صفوف عرضية (3 في كل صف)
cols = st.columns(3)
icons_order = [5, 7, 6, 8, 9, 1, 2, 3, 4]
for i, code in enumerate(icons_order):
    with cols[i % 3]:
        if st.button(SYMBOLS[code], key=f"btn_{code}"):
            register_result(code)
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- أزرار التحكم السفلى ---
st.write("")
c1, c2 = st.columns(2)
with c1:
    if st.button("↩️ تراجع"):
        if hist: st.session_state.history.pop(); st.rerun()
with c2:
    if st.button("🗑️ مسح"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
