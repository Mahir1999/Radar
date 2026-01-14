import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Greedy AI v98.0 - Grid Master", page_icon="🔮", layout="centered")

st.markdown("""
    <style>
    /* الإطار الأخضر الموحد (المستطيل الكبير) */
    .unified-master-box {
        background: rgba(0, 0, 0, 0.8);
        border: 2px solid #39ff14;
        border-radius: 15px;
        padding: 15px;
        margin-top: 15px;
        box-shadow: 0 0 15px rgba(57, 255, 20, 0.2);
    }

    /* تقسيم الشبكة داخل الإطار */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr); /* 3 أعمدة متساوية */
        gap: 10px;
    }

    /* تصميم الأزرار كمستطيلات خضراء */
    div.stButton > button {
        background-color: #002200 !important;
        color: #39ff14 !important;
        border: 1px solid #39ff14 !important;
        border-radius: 8px !important;
        width: 100% !important;
        height: 50px !important;
        font-size: 20px !important;
        font-weight: bold !important;
        transition: 0.2s;
    }

    div.stButton > button:hover {
        background-color: #39ff14 !important;
        color: black !important;
        box-shadow: 0 0 10px #39ff14;
    }

    .last-result-banner { background: #1a1a1a; padding: 10px; border-radius: 10px; border-right: 5px solid #39ff14; text-align: center; margin-bottom: 10px; color: #39ff14; font-weight: bold; font-size: 18px; }
    .next-hit-card { background: linear-gradient(135deg, #1a1a1a 0%, #000 100%); border: 2px solid #39ff14; padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 10px; }
    .insurance-card { background: linear-gradient(135deg, #001a33 0%, #000 100%); border: 2px solid #00aaff; padding: 10px; border-radius: 15px; text-align: center; margin-bottom: 15px; }
    .stats-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 10px; }
    .stat-box { background: #111; padding: 8px; border-radius: 10px; text-align: center; border: 1px solid #333; font-size: 12px; }
    .omni-metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }
    .metric-card { background: #0a0a0a; border: 1px dashed #444; padding: 10px; border-radius: 10px; text-align: center; font-size: 11px; }
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

# --- العدادات وتحليل الموجة ---
st.markdown(f'<div class="stats-grid"><div class="stat-box">🔄 الجولة: {total_h}</div><div class="stat-box" style="color:#39ff14">✅ فوز: {st.session_state.hits}</div><div class="stat-box" style="color:#ff4b4b">❌ خطأ: {st.session_state.misses}</div></div>', unsafe_allow_html=True)

# --- التوقعات (المربع الذهبي + درع التأمين) ---
if total_h > 0:
    gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 9)}
    scores = {c: (hist[-15:].count(c) * 0.7 + (gaps[c] * 0.3)) for c in range(1, 9)}
    top_4 = sorted(scores, key=scores.get, reverse=True)[:4]
    insurance_slot = sorted(MEATS, key=lambda x: gaps[x], reverse=True)[0] if all(c in VEGGIES for c in top_4) else sorted(scores, key=scores.get, reverse=True)[4]
    st.session_state.current_preds = top_4 + [insurance_slot]
    
    st.markdown(f'<div class="next-hit-card"><div style="color:#39ff14; font-size:12px; font-weight:bold;">🎯 المربع الذهبي</div><div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-top:10px;">' + 
                "".join([f'<div style="background:#002200; border:1px solid #39ff14; padding:8px; border-radius:8px;">{SYMBOLS[c]}</div>' for c in top_4]) + 
                '</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="insurance-card"><div style="color:#00aaff; font-size:12px; font-weight:bold;">🛡️ درع التأمين</div><div style="font-size:24px; margin-top:5px;">{SYMBOLS[insurance_slot]}</div></div>', unsafe_allow_html=True)

# --- سجل النتيجة (المربع الواحد المطلوب بتوزيع شبكي) ---
st.markdown('<div class="unified-master-box">', unsafe_allow_html=True)
st.write("<div style='color:#39ff14; font-size:12px; font-weight:bold; margin-bottom:10px; text-align:center;'>🔘 سجل النتيجة</div>", unsafe_allow_html=True)

# عرض الرموز في شبكة 3x3 داخل الإطار
st.markdown('<div class="grid-container">', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
# ترتيب الرموز بشكل منظم داخل الأعمدة
for i, code in enumerate([5, 7, 6, 8, 9, 1, 2, 3, 4]):
    with [col1, col2, col3][i % 3]:
        if st.button(SYMBOLS[code], key=f"btn_{code}"):
            register_result(code)
            st.rerun()
st.markdown('</div></div>', unsafe_allow_html=True)

# --- معلومات إضافية وأزرار التحكم ---
if hist:
    st.markdown(f'<div class="last-result-banner">⏮️ الأخيرة: {SYMBOLS[hist[-1]]}</div>', unsafe_allow_html=True)
    
c1, c2 = st.columns(2)
if c1.button("↩️ تراجع"):
    if hist: st.session_state.history.pop(); st.rerun()
if c2.button("🗑️ مسح"):
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

st.markdown(f'<div style="text-align:center; font-size:11px; margin-top:10px; color:#888;">🧠 الأنماط المكتشفة: {st.session_state.patterns_found} | جكبوت غائب منذ: {(list(reversed(hist)).index(9) if 9 in hist else total_h)}</div>', unsafe_allow_html=True)
