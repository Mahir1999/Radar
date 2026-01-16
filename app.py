import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Greedy AI v96.9", page_icon="📊", layout="centered")

for key in ['history', 'hits', 'misses', 'cons_m', 'p_count', 'preds', 'action_hit', 'max_streak', 'cur_streak']:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ['history', 'preds', 'action_hit'] else 0

def register_result(code):
    is_hit = code in st.session_state.preds
    if is_hit:
        st.session_state.hits += 1
        st.session_state.cur_streak += 1
        st.session_state.max_streak = max(st.session_state.max_streak, st.session_state.cur_streak)
        if st.session_state.cons_m >= 2: st.session_state.p_count += 1
        st.session_state.cons_m = 0
    elif code != 9:
        st.session_state.misses += 1
        st.session_state.cons_m += 1
        st.session_state.cur_streak = 0
    st.session_state.history.append(code)
    st.session_state.action_hit.append(is_hit)

# --- CSS التنسيق الرباعي المزدوج ---
st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; }
    .main-card { background: #1a1a1a; border: 2px solid #39ff14; padding: 10px; border-radius: 12px; text-align: center; margin-bottom: 5px; }
    .quad-box { display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; margin-top: 5px; }
    .quad-item { background: #002200; border: 1px solid #39ff14; padding: 5px; border-radius: 6px; color: white; font-weight: bold; font-size: 14px; }
    .info-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; margin-bottom: 4px; }
    .info-box { background: #111; border: 1px solid #333; padding: 5px; border-radius: 6px; text-align: center; }
    .lbl { font-size: 7px; color: #888; font-weight: bold; }
    .val { font-size: 10px; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

SYMBOLS = {1: "🍅", 2: "🌽", 3: "🥕", 4: "🫑", 5: "🐔", 6: "🐑", 7: "🐟", 8: "🦐", 9: "💰"}
hist = st.session_state.history; total_h = len(hist)

# --- الصف العلوي (الأساسيات) ---
st.markdown(f'<div class="info-grid">'
            f'<div class="info-box"><span class="lbl">🔄 جولة</span><br><b class="val">{total_h}</b></div>'
            f'<div class="info-box"><span class="lbl" style="color:#39ff14">✅ فوز</span><br><b class="val">{st.session_state.hits}</b></div>'
            f'<div class="info-box"><span class="lbl" style="color:#ff4b4b">❌ خطأ</span><br><b class="val">{st.session_state.misses}</b></div>'
            f'<div class="info-box"><span class="lbl">📉 نمط</span><br><b class="val">{st.session_state.p_count}</b></div></div>', unsafe_allow_html=True)

# --- المربع الذهبي (الذاكرة العميقة) ---
recent_15 = hist[-15:]; gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 9)}
scores = {c: (recent_15.count(c) * 0.7 + (gaps[c] * 0.3)) * (1.0 if recent_15.count(c) > 1 else 0.2) for c in range(1, 9)}
top_4 = sorted(scores, key=scores.get, reverse=True)[:4]
st.session_state.preds = top_4 + [5] # تبسيط للتأمين

st.markdown(f'<div class="main-card"><div style="color:#39ff14; font-size:10px; font-weight:bold;">🎯 المربع الذهبي (ذاكرة عميقة 🧠)</div><div class="quad-box">{"".join([f'<div class="quad-item">{SYMBOLS[c]}</div>' for c in top_4])}</div></div>', unsafe_allow_html=True)

# --- الأزرار ---
r1, r2 = st.columns(5), st.columns(4)
for i, c in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[c], key=f"b_{c}"): register_result(c); st.rerun()
for i, c in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[c], key=f"b_{c}"): register_result(c); st.rerun()

# --- الصف السفلي 1 (الإحصائيات التحليلية) ---
gap_9 = (list(reversed(hist)).index(9) if 9 in hist else total_h)
wave = "🥩" if sum(1 for x in recent_15 if x in [5,6,7,8]) > 8 else "🥗"
st.markdown(f'<div class="info-grid">'
            f'<div class="info-box"><span class="lbl">💰 جكبوت</span><br><b class="val">{gap_9}</b></div>'
            f'<div class="info-box"><span class="lbl">📡 موجة</span><br><b class="val">{wave}</b></div>'
            f'<div class="info-box"><span class="lbl">🏆 سلسلة</span><br><b class="val">{st.session_state.max_streak}</b></div>'
            f'<div class="info-box"><span class="lbl">🧠 تنبؤ</span><br><b class="val">{"مستقر" if st.session_state.cons_m==0 else "قلق"}</b></div></div>', unsafe_allow_html=True)

# --- الصف السفلي 2 (الإشارات الحاسمة) ---
recent_10_hits = sum(1 for x in st.session_state.action_hit[-10:] if x)
scam = "آمن ✅" if recent_10_hits >= 4 or len(hist) < 10 else "غدر 🚨"
if "غدر" in scam: launch, clr = "STOP 🔴", "#ff4b4b"
elif recent_10_hits >= 5: launch, clr = "GO 🟢", "#39ff14"
else: launch, clr = "WAIT 🟡", "#ffaa00"

st.markdown(f'<div class="info-grid">'
            f'<div class="info-box" style="grid-column: span 2; border-color:{"#39ff14" if "آمن" in scam else "#ff4b4b"}"><span class="lbl">🚨 إنذار النظام</span><br><b class="val">{scam}</b></div>'
            f'<div class="info-box" style="grid-column: span 2; border-color:{clr}"><span class="lbl">🚥 إشارة الانطلاق</span><br><b class="val" style="color:{clr}">{launch}</b></div></div>', unsafe_allow_html=True)
