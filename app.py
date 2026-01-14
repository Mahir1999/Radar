import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Greedy AI v94.0 - Restore", page_icon="🛡️", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .stButton>button { width: 100%; height: 48px; font-weight: bold; border-radius: 10px; }
    .last-result-banner { background: #1a1a1a; padding: 10px; border-radius: 10px; border-right: 5px solid #39ff14; text-align: center; margin-bottom: 10px; color: #39ff14; font-weight: bold; font-size: 18px; }
    .timeline-container { display: flex; gap: 5px; margin-bottom: 15px; padding: 8px; background: #0e1117; border-radius: 8px; overflow-x: auto; }
    .timeline-item { padding: 4px 10px; background: #262730; border-radius: 6px; font-size: 13px; white-space: nowrap; color: #eee; }
    .next-hit-card { background: linear-gradient(135deg, #1a1a1a 0%, #000 100%); border: 2px solid #39ff14; padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 10px; }
    .insurance-card { background: linear-gradient(135deg, #001a33 0%, #000 100%); border: 2px solid #00aaff; padding: 10px; border-radius: 15px; text-align: center; margin-bottom: 15px; }
    .quad-box { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
    .quad-item { background: #002200; border: 1px solid #39ff14; padding: 8px; border-radius: 8px; color: white; font-weight: bold; font-size: 14px;}
    .stats-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 10px; }
    .stat-box { background: #111; padding: 8px; border-radius: 10px; text-align: center; border: 1px solid #333; font-size: 12px; }
    .omni-metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }
    .metric-card { background: #0a0a0a; border: 1px dashed #444; padding: 10px; border-radius: 10px; text-align: center; font-size: 11px; }
    .compact-frame { border: 2px solid #444; padding: 15px; border-radius: 15px; background: #0e1117; margin-top: 10px; }
    .pattern-pulse { padding: 5px; border-radius: 5px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

SYMBOLS = {1: "🍅 طماطم", 2: "🌽 ذرة", 3: "🥕 جزر", 4: "🫑 فلفل", 5: "🐔 دجاجة", 6: "🐑 خروف", 7: "🐟 سمك", 8: "🦐 روبيان", 9: "💰 جكبوت"}
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

# --- مستشار الانسحاب ---
if total_h > 20 and st.session_state.consecutive_misses >= 3:
    st.error("🚨 مستشار الانسحاب: السيرفر في وضع استرداد، خذ حذرك!")

# --- 1. العدادات ---
st.markdown(f"""
<div class="stats-grid">
    <div class="stat-box">🔄 الجولة: <b>{total_h}</b></div>
    <div class="stat-box" style="color:#39ff14">✅ فوز: <b>{st.session_state.hits}</b></div>
    <div class="stat-box" style="color:#ff4b4b">❌ خطأ: <b>{st.session_state.misses}</b></div>
</div>
""", unsafe_allow_html=True)

# --- 2. رادار الموجة والميزان ---
st.markdown(f"""
<div class="omni-metrics">
    <div class="metric-card">🌊 الموجة: <span style="color:#39ff14">{"FIRE 🔥" if st.session_state.consecutive_misses==0 else "امتصاص"}</span></div>
    <div class="metric-card">⚖️ ضغط السيرفر: <b>{"ممتلئ" if st.session_state.misses > st.session_state.hits else "متوازن"}</b></div>
</div>
""", unsafe_allow_html=True)

# --- 3. المربع الذهبي ودرع التأمين ---
if total_h > 0:
    gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 9)}
    scores = {c: (hist[-15:].count(c) * 0.7 + (gaps[c] * 0.3)) for c in range(1, 9)}
    top_4 = sorted(scores, key=scores.get, reverse=True)[:4]
    insurance_slot = sorted(MEATS, key=lambda x: gaps[x], reverse=True)[0] if all(c in VEGGIES for c in top_4) else sorted(scores, key=scores.get, reverse=True)[4]
    st.session_state.current_preds = top_4 + [insurance_slot]
    
    st.markdown(f"""
    <div class="next-hit-card">
        <div style="color:#39ff14; font-size:12px; font-weight:bold;">🎯 المربع الذهبي</div>
        <div class="quad-box">{"".join([f'<div class="quad-item">{"⏳ " if gaps[c] > 15 else ""}{SYMBOLS[c].split()[0]}</div>' for c in top_4])}</div>
    </div>
    <div class="insurance-card">
        <div style="color:#00aaff; font-size:12px; font-weight:bold;">🛡️ درع التأمين</div>
        <div style="color:white; font-size:20px; font-weight:bold;">{SYMBOLS[insurance_slot].split()[0]}</div>
    </div>
    """, unsafe_allow_html=True)

# --- شريط الجكبوت والأنماط (v94 المميز) ---
gap_9 = (list(reversed(hist)).index(9) if 9 in hist else total_h)
p_status = "ثابت ✅" if st.session_state.consecutive_misses < 2 else "متغير ⚠️"
p_bg = "#003300" if p_status == "ثابت ✅" else "#331a00"

st.markdown(f"""
<div style="text-align:center; font-size:11px; margin-bottom:10px;">
    💰 جكبوت غائب: {gap_9} | 
    🧠 الأنماط: <b>{st.session_state.patterns_found}</b> | 
    <span class="pattern-pulse" style="background:{p_bg}; color:white;">حالة النمط: {p_status}</span>
</div>
""", unsafe_allow_html=True)

# --- شريط النتائج والتحكم ---
if hist:
    st.markdown(f'<div class="last-result-banner">⏮️ الأخيرة: {SYMBOLS[hist[-1]].split()[0]}</div>', unsafe_allow_html=True)
st.markdown('<div class="compact-frame">', unsafe_allow_html=True)
r1, r2 = st.columns(5), st.columns(4)
for i, c in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[c].split()[0], key=f"btn_{c}"): register_result(c); st.rerun()
for i, c in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[c].split()[0], key=f"btn_{c}"): register_result(c); st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

if st.button("↩️ تراجع"):
    if hist: st.session_state.history.pop(); st.rerun()
