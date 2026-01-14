import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Greedy AI v97.0 - FlexBoard", page_icon="🔮", layout="centered")

st.markdown("""
    <style>
    /* منع انهيار العناصر وجعلها في إطار واحد */
    .unified-grid {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 10px;
        background: linear-gradient(135deg, #1a1a1a 0%, #000 100%);
        border: 2px solid #39ff14;
        padding: 15px;
        border-radius: 15px;
        margin-top: 10px;
    }
    
    /* إلغاء تصميم أزرار ستريمليت الافتراضي */
    div.stButton > button {
        background-color: #002200 !important;
        color: white !important;
        border: 1px solid #39ff14 !important;
        border-radius: 10px !important;
        width: 60px !important;
        height: 60px !important;
        font-size: 24px !important;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: 0.3s;
    }
    
    div.stButton > button:hover {
        transform: scale(1.1);
        border-color: #ffffff !important;
        box-shadow: 0 0 10px #39ff14;
    }

    .last-result-banner { background: #1a1a1a; padding: 10px; border-radius: 10px; border-right: 5px solid #39ff14; text-align: center; margin-bottom: 10px; color: #39ff14; font-weight: bold; font-size: 18px; }
    .next-hit-card { background: linear-gradient(135deg, #1a1a1a 0%, #000 100%); border: 2px solid #39ff14; padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 10px; }
    .insurance-card { background: linear-gradient(135deg, #001a33 0%, #000 100%); border: 2px solid #00aaff; padding: 10px; border-radius: 15px; text-align: center; margin-bottom: 15px; }
    .quad-box { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
    .quad-item { background: #002200; border: 1px solid #39ff14; padding: 8px; border-radius: 8px; color: white; font-weight: bold; }
    .stats-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 10px; }
    .stat-box { background: #111; padding: 8px; border-radius: 10px; text-align: center; border: 1px solid #333; font-size: 12px; }
    .omni-metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }
    .metric-card { background: #0a0a0a; border: 1px dashed #444; padding: 10px; border-radius: 10px; text-align: center; font-size: 11px; }
    .pattern-pulse { padding: 5px; border-radius: 5px; font-weight: bold; }
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

# --- 1. العدادات ---
st.markdown(f'<div class="stats-grid"><div class="stat-box">🔄 الجولة: {total_h}</div><div class="stat-box" style="color:#39ff14">✅ فوز: {st.session_state.hits}</div><div class="stat-box" style="color:#ff4b4b">❌ خطأ: {st.session_state.misses}</div></div>', unsafe_allow_html=True)

# --- 2. رادار الموجة والميزان ---
st.markdown(f'<div class="omni-metrics"><div class="metric-card">🌊 الموجة: <span style="color:#39ff14">{"FIRE 🔥" if st.session_state.consecutive_misses==0 else "امتصاص"}</span></div><div class="metric-card">⚖️ ضغط السيرفر: <b>{"ممتلئ" if st.session_state.misses > st.session_state.hits else "متوازن"}</b></div></div>', unsafe_allow_html=True)

# --- 3. المربع الذهبي ودرع التأمين ---
if total_h > 0:
    gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 9)}
    scores = {c: (hist[-15:].count(c) * 0.7 + (gaps[c] * 0.3)) for c in range(1, 9)}
    top_4 = sorted(scores, key=scores.get, reverse=True)[:4]
    insurance_slot = sorted(MEATS, key=lambda x: gaps[x], reverse=True)[0] if all(c in VEGGIES for c in top_4) else sorted(scores, key=scores.get, reverse=True)[4]
    st.session_state.current_preds = top_4 + [insurance_slot]
    
    st.markdown(f'<div class="next-hit-card"><div style="color:#39ff14; font-size:12px; font-weight:bold;">🎯 المربع الذهبي</div><div class="quad-box">{"".join([f'<div class="quad-item">{SYMBOLS[c]}</div>' for c in top_4])}</div></div><div class="insurance-card"><div style="color:#00aaff; font-size:12px; font-weight:bold;">🛡️ درع التأمين</div><div style="font-size:24px; margin-top:5px;">{SYMBOLS[insurance_slot]}</div></div>', unsafe_allow_html=True)

# --- 4. حالة النمط والجكبوت ---
p_status = "ثابت ✅" if st.session_state.consecutive_misses < 2 else "متغير ⚠️"
st.markdown(f'<div style="text-align:center; font-size:11px; margin-bottom:10px;">🧠 الأنماط: {st.session_state.patterns_found} | <span class="pattern-pulse" style="background:#222; color:white;">الحالة: {p_status}</span></div>', unsafe_allow_html=True)

if hist:
    st.markdown(f'<div class="last-result-banner">⏮️ الأخيرة: {SYMBOLS[hist[-1]]}</div>', unsafe_allow_html=True)

# --- 5. سجل النتيجة (المربع الواحد المطلوب) ---
st.markdown('<div class="unified-grid">', unsafe_allow_html=True)
# عرض الرموز كأزرار متراصة داخل نفس الإطار
for code in [5, 7, 6, 8, 9, 1, 2, 3, 4]:
    if st.button(SYMBOLS[code], key=f"btn_{code}"):
        register_result(code)
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- أزرار الإدارة ---
c1, c2 = st.columns(2)
if c1.button("↩️ تراجع"):
    if hist: st.session_state.history.pop(); st.rerun()
if c2.button("🗑️ مسح"):
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()
