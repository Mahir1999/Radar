import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Greedy AI v94.3", page_icon="🛡️", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .stButton>button { width: 100%; height: 48px; font-weight: bold; border-radius: 10px; }
    
    /* المربع الذهبي */
    .next-hit-card { background: #1a1a1a; border: 2px solid #39ff14; padding: 12px; border-radius: 15px; text-align: center; margin-bottom: 10px; }
    .quad-box { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 5px; }
    .quad-item { background: #002200; border: 1px solid #39ff14; padding: 6px; border-radius: 8px; color: white; font-weight: bold; font-size: 13px; }
    
    /* تنسيق الصف المدمج (تأمين + نمط) */
    .flex-container { display: flex; gap: 10px; margin-bottom: 10px; }
    .insurance-box { flex: 1; background: #001a33; border: 2px solid #00aaff; padding: 8px; border-radius: 12px; text-align: center; }
    .pattern-box { flex: 1.5; background: #111; border: 2px solid #444; padding: 8px; border-radius: 12px; text-align: center; }
    
    .stats-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 10px; }
    .stat-box { background: #111; padding: 8px; border-radius: 10px; text-align: center; border: 1px solid #333; font-size: 12px; }
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

# --- 1. العدادات ---
st.markdown(f'<div class="stats-grid"><div class="stat-box">🔄 الجولة: {total_h}</div><div class="stat-box" style="color:#39ff14">✅ فوز: {st.session_state.hits}</div><div class="stat-box" style="color:#ff4b4b">❌ خطأ: {st.session_state.misses}</div></div>', unsafe_allow_html=True)

# --- 2. المربع الذهبي ---
if total_h > 0:
    gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 9)}
    scores = {c: (hist[-15:].count(c) * 0.7 + (gaps[c] * 0.3)) for c in range(1, 9)}
    top_4 = sorted(scores, key=scores.get, reverse=True)[:4]
    insurance_slot = sorted(MEATS, key=lambda x: gaps[x], reverse=True)[0] if all(c in VEGGIES for c in top_4) else sorted(scores, key=scores.get, reverse=True)[4]
    st.session_state.current_preds = top_4 + [insurance_slot]
    
    st.markdown(f'<div class="next-hit-card"><div style="color:#39ff14; font-size:11px; font-weight:bold;">🎯 المربع الذهبي</div><div class="quad-box">{"".join([f'<div class="quad-item">{SYMBOLS[c].split()[0]}</div>' for c in top_4])}</div></div>', unsafe_allow_html=True)

    # --- 3. الصف المدمج (درع التأمين + شريط النمط) ---
    p_status = "ثابت ✅" if st.session_state.consecutive_misses < 2 else "متغير ⚠️"
    p_color = "#39ff14" if p_status == "ثابت ✅" else "#ff4b4b"
    gap_9 = (list(reversed(hist)).index(9) if 9 in hist else total_h)

    st.markdown(f"""
    <div class="flex-container">
        <div class="insurance-box">
            <div style="color:#00aaff; font-size:10px; font-weight:bold;">🛡️ تأمين</div>
            <div style="color:white; font-size:18px; font-weight:bold;">{SYMBOLS[insurance_slot].split()[0]}</div>
        </div>
        <div class="pattern-box">
            <div style="color:{p_color}; font-size:12px; font-weight:bold;">النمط: {p_status}</div>
            <div style="color:#888; font-size:10px;">🧠 {st.session_state.patterns_found} | 💰 {gap_9}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 4. سجل النتائج (بدون إطار) ---
r1, r2 = st.columns(5), st.columns(4)
for i, c in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[c].split()[0], key=f"btn_{c}"): register_result(c); st.rerun()
for i, c in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[c].split()[0], key=f"btn_{c}"): register_result(c); st.rerun()

# --- 5. أدوات التحكم ---
if st.button("↩️ تراجع"):
    if hist: st.session_state.history.pop(); st.rerun()
