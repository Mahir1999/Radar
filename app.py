import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Greedy AI v90.0 - Fortress", page_icon="🛡️", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    .stButton>button { width: 100%; height: 40px; font-weight: bold; border-radius: 8px; font-size: 12px; padding: 0; }
    .last-result-banner { background: #1a1a1a; padding: 10px; border-radius: 10px; border-right: 5px solid #39ff14; text-align: center; margin-bottom: 10px; color: #39ff14; font-weight: bold; }
    .next-hit-card { background: linear-gradient(135deg, #1a1a1a 0%, #000 100%); border: 2px solid #39ff14; padding: 12px; border-radius: 15px; text-align: center; margin-bottom: 10px; }
    .quad-box { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 8px; }
    .quad-item { background: #002200; border: 1px solid #39ff14; padding: 6px; border-radius: 6px; color: white; font-size: 13px; font-weight: bold; }
    .stats-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5px; margin-bottom: 8px; }
    .stat-box { background: #111; padding: 8px; border-radius: 8px; text-align: center; border: 1px solid #333; font-size: 11px; }
    .compact-control-box { background: #161616; border: 1px solid #444; padding: 10px; border-radius: 12px; margin-top: 10px; }
    .advisor-alert { background: #330000; border: 1px solid #ff4b4b; color: #ff4b4b; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 10px; font-size: 13px; }
    </style>
    """, unsafe_allow_html=True)

SYMBOLS = {1: "🍅", 2: "🌽", 3: "🥕", 4: "🫑", 5: "🐔", 6: "🐑", 7: "🐟", 8: "🦐", 9: "💰"}

if 'history' not in st.session_state: st.session_state.history = []
if 'hits' not in st.session_state: st.session_state.hits = 0
if 'misses' not in st.session_state: st.session_state.misses = 0
if 'consecutive_misses' not in st.session_state: st.session_state.consecutive_misses = 0

def register_result(code):
    if st.session_state.get('current_preds'):
        if code in st.session_state.current_preds:
            st.session_state.hits += 1
            st.session_state.consecutive_misses = 0
        elif code != 9:
            st.session_state.misses += 1
            st.session_state.consecutive_misses += 1
    st.session_state.history.append(code)

hist = st.session_state.history
total_h = len(hist)

# --- 1. مستشار الانسحاب الذكي ---
if total_h > 20:
    win_rate = (st.session_state.hits / total_h) * 100
    if st.session_state.consecutive_misses >= 3 and win_rate > 50:
        st.markdown('<div class="advisor-alert">🚨 مستشار الانسحاب: السيرفر بدأ بالسحب! حافظ على أرباحك واخرج الآن.</div>', unsafe_allow_html=True)

# --- العدادات ---
st.markdown(f"""
<div class="stats-grid">
    <div class="stat-box">🔄 الجولة: {total_h}</div>
    <div class="stat-box" style="color:#39ff14">✅ صح: {st.session_state.hits}</div>
    <div class="stat-box" style="color:#ff4b4b">❌ خطأ: {st.session_state.misses}</div>
</div>
""", unsafe_allow_html=True)

# --- محرك التوقع (v90) ---
if total_h > 0:
    scores = {c: (hist[-20:].count(c) * 0.8 + hist.count(c) * 0.2) for c in range(1, 9)}
    top_4 = sorted(scores, key=scores.get, reverse=True)[:4]
    st.session_state.current_preds = top_4
    st.markdown(f"""
    <div class="next-hit-card">
        <div style="color:#39ff14; font-size:12px; font-weight:bold;">🎯 التوقعات القادمة</div>
        <div class="quad-box">
            {"".join([f'<div class="quad-item">{SYMBOLS[c]} {c}</div>' for c in top_4])}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- سجل النتيجة (الإطار الموحد الموفر للمساحة) ---
st.markdown('<div class="compact-control-box">', unsafe_allow_html=True)
st.write("<p style='text-align:center; font-size:12px; margin-bottom:5px;'>🔘 سجل النتيجة (إطار موحد)</p>", unsafe_allow_html=True)
row1 = st.columns(5)
row2 = st.columns(4)

for i, code in enumerate([5, 7, 6, 8, 9]):
    if row1[i].button(f"{SYMBOLS[code]}", key=f"btn_{code}"):
        register_result(code); st.rerun()
for i, code in enumerate([1, 2, 3, 4]):
    if row2[i].button(f"{SYMBOLS[code]}", key=f"btn_{code}"):
        register_result(code); st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- شريط التحكم السفلي ---
cols = st.columns(2)
if cols[0].button("↩️ تراجع"):
    if hist: st.session_state.history.pop(); st.rerun()
if cols[1].button("🗑️ مسح الجلسة"):
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()

if hist:
    st.markdown(f'<div class="last-result-banner">⏮️ الأخيرة: {SYMBOLS[hist[-1]]}</div>', unsafe_allow_html=True)
