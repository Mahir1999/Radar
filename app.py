import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Greedy AI v94.5", page_icon="🛡️", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .stButton>button { width: 100%; height: 48px; font-weight: bold; border-radius: 10px; }
    
    /* المربع الذهبي */
    .next-hit-card { background: #1a1a1a; border: 2px solid #39ff14; padding: 12px; border-radius: 15px; text-align: center; margin-bottom: 10px; }
    .quad-box { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 5px; }
    .quad-item { background: #002200; border: 1px solid #39ff14; padding: 6px; border-radius: 8px; color: white; font-weight: bold; font-size: 13px; }
    
    /* الصف العلوي الرباعي */
    .stats-grid-4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1.2fr; gap: 6px; margin-bottom: 10px; }
    .stat-box-v2 { background: #111; padding: 8px 4px; border-radius: 10px; text-align: center; border: 1px solid #333; font-size: 11px; }
    
    /* الصف الأوسط الثنائي (تأمين + الأخيرة) */
    .info-row-dual { display: flex; gap: 10px; margin-bottom: 15px; }
    .info-box-dual { flex: 1; padding: 10px; border-radius: 12px; text-align: center; }
    .insurance-style { background: #001a33; border: 2px solid #00aaff; }
    .last-style { background: #1a1a1a; border: 2px solid #39ff14; }
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

# --- حساب التوقعات ---
if total_h > 0:
    gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 9)}
    scores = {c: (hist[-15:].count(c) * 0.7 + (gaps[c] * 0.3)) for c in range(1, 9)}
    top_4 = sorted(scores, key=scores.get, reverse=True)[:4]
    insurance_slot = sorted(MEATS, key=lambda x: gaps[x], reverse=True)[0] if all(c in VEGGIES for c in top_4) else sorted(scores, key=scores.get, reverse=True)[4]
    st.session_state.current_preds = top_4 + [insurance_slot]
    
    # 1. الصف العلوي الرباعي (تم نقل النمط هنا)
    p_status = "ثابت ✅" if st.session_state.consecutive_misses < 2 else "متغير ⚠️"
    p_color = "#39ff14" if p_status == "ثابت ✅" else "#ff4b4b"
    
    st.markdown(f"""
    <div class="stats-grid-4">
        <div class="stat-box-v2">🔄 جولة<br><b>{total_h}</b></div>
        <div class="stat-box-v2" style="color:#39ff14">✅ فوز<br><b>{st.session_state.hits}</b></div>
        <div class="stat-box-v2" style="color:#ff4b4b">❌ خطأ<br><b>{st.session_state.misses}</b></div>
        <div class="stat-box-v2" style="border-color:{p_color}">📉 النمط<br><b style="color:{p_color}">{p_status}</b></div>
    </div>
    """, unsafe_allow_html=True)

    # 2. المربع الذهبي
    st.markdown(f'<div class="next-hit-card"><div style="color:#39ff14; font-size:11px; font-weight:bold;">🎯 المربع الذهبي</div><div class="quad-box">{"".join([f'<div class="quad-item">{SYMBOLS[c].split()[0]}</div>' for c in top_4])}</div></div>', unsafe_allow_html=True)

    # 3. الصف الأوسط الثنائي (تأمين + الأخيرة بمساحة كاملة)
    last_res = SYMBOLS[hist[-1]].split()[0] if hist else "---"
    st.markdown(f"""
    <div class="info-row-dual">
        <div class="info-box-dual insurance-style">
            <div style="color:#00aaff; font-size:10px; font-weight:bold;">🛡️ درع التأمين</div>
            <div style="color:white; font-size:22px; font-weight:bold;">{SYMBOLS[insurance_slot].split()[0]}</div>
        </div>
        <div class="info-box-dual last-style">
            <div style="color:#39ff14; font-size:10px; font-weight:bold;">⏮️ العنصر الأخير</div>
            <div style="color:white; font-size:22px; font-weight:bold;">{last_res}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 4. سجل النتائج (الأزرار) ---
r1, r2 = st.columns(5), st.columns(4)
for i, c in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[c].split()[0], key=f"btn_{c}"): register_result(c); st.rerun()
for i, c in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[c].split()[0], key=f"btn_{c}"): register_result(c); st.rerun()

# --- 5. العدادات السفلية والتحكم ---
gap_9 = (list(reversed(hist)).index(9) if 9 in hist else total_h)
st.markdown(f'<div style="text-align:center; font-size:10px; color:#666; margin-bottom:5px;">🧠 أنماط: {st.session_state.patterns_found} | 💰 جكبوت: {gap_9}</div>', unsafe_allow_html=True)

if st.button("↩️ تراجع"):
    if hist: st.session_state.history.pop(); st.rerun()
