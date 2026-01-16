import streamlit as st

# --- إعدادات الصفحة وحفظ البيانات ---
st.set_page_config(page_title="Greedy AI v96.8", page_icon="🧠", layout="centered")

# تأكيد حفظ الأرقام 
for key in ['history', 'hits', 'misses', 'cons_m', 'p_count', 'preds', 'action_hit', 'max_streak', 'cur_streak']:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ['history', 'preds', 'action_hit'] else 0

# --- منطق تسجيل النتائج ---
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

def undo_last():
    if st.session_state.history:
        st.session_state.history.pop()
        last_hit = st.session_state.action_hit.pop()
        if last_hit: 
            st.session_state.hits -= 1
            st.session_state.cur_streak = max(0, st.session_state.cur_streak - 1)
        else: 
            st.session_state.misses -= 1
            st.session_state.cons_m -= 1
        st.rerun()

# --- خوارزمية الذاكرة العميقة (Deep Memory Search) ---
def get_deep_memory_weight(hist, current_symbol):
    if len(hist) < 3: return {}
    weights = {i: 0.0 for i in range(1, 9)}
    for i in range(len(hist) - 1):
        if hist[i] == current_symbol:
            next_sym = hist[i+1]
            if next_sym in weights:
                weights[next_sym] += 0.5 
    return weights

# --- التنسيق (CSS) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    .stButton>button { width: 100%; height: 45px; font-weight: bold; border-radius: 8px; font-size: 16px; }
    .main-card { background: #1a1a1a; border: 2px solid #39ff14; padding: 10px; border-radius: 15px; text-align: center; margin-bottom: 8px; }
    .quad-box { display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; margin-top: 5px; }
    .quad-item { background: #002200; border: 1px solid #39ff14; padding: 6px; border-radius: 8px; color: white; font-weight: bold; font-size: 14px; }
    .pro-grid-4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 3px; margin-top: 8px; }
    .pro-box { background: #0a0a0a; border: 1px solid #444; padding: 4px; border-radius: 6px; text-align: center; }
    .mini-grid { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 4px; margin-bottom: 8px; }
    .mini-box { background: #111; border: 1px solid #333; padding: 4px; border-radius: 6px; text-align: center; }
    .lbl { font-size: 7px; color: #777; font-weight: bold; }
    .val { font-size: 9px; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

SYMBOLS = {1: "🍅", 2: "🌽", 3: "🥕", 4: "🫑", 5: "🐔", 6: "🐑", 7: "🐟", 8: "🦐", 9: "💰"}
hist = st.session_state.history; total_h = len(hist)

# --- 1. العدادات العلوية ---
st.markdown(f'<div class="mini-grid">'
            f'<div class="mini-box"><span class="lbl">🔄 جولة</span><br><b class="val">{total_h}</b></div>'
            f'<div class="mini-box"><span class="lbl" style="color:#39ff14">✅ فوز</span><br><b class="val">{st.session_state.hits}</b></div>'
            f'<div class="mini-box"><span class="lbl" style="color:#ff4b4b">❌ خطأ</span><br><b class="val">{st.session_state.misses}</b></div>'
            f'<div class="mini-box"><span class="lbl">📉 نمط</span><br><b class="val">{st.session_state.p_count}</b></div></div>', unsafe_allow_html=True)

# --- 2. المربع الذهبي (ذاكرة عميقة 🧠) ---
if total_h > 0:
    recent_15 = hist[-15:]; gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 9)}
    base_scores = {c: (recent_15.count(c) * 0.7 + (gaps[c] * 0.3)) * (1.0 if recent_15.count(c) > 1 else 0.2) for c in range(1, 9)}
    deep_weights = get_deep_memory_weight(hist, hist[-1])
    for c in base_scores: base_scores[c] += deep_weights.get(c, 0)
    top_4 = sorted(base_scores, key=base_scores.get, reverse=True)[:4]
    st.session_state.preds = top_4 + [5]
    st.markdown(f'<div class="main-card"><div style="color:#39ff14; font-size:10px; font-weight:bold;">🎯 المربع الذهبي (ذاكرة عميقة 🧠)</div><div class="quad-box">{"".join([f'<div class="quad-item">{SYMBOLS[c]}</div>' for c in top_4])}</div></div>', unsafe_allow_html=True)

# --- 3. التأمين وآخر 5 ---
    last_5_html = "".join([f'<span style="margin-left:3px;">{SYMBOLS[c]}</span>' for c in hist[-5:]])
    st.markdown(f'<div style="display:flex; gap:6px; margin-bottom:8px;"><div class="mini-box" style="width:70px; border-color:#00aaff;"><span class="lbl" style="color:#00aaff">🛡️ تأمين</span><br><span style="font-size:16px;">{SYMBOLS[5]}</span></div>'
                f'<div class="mini-box" style="flex:1; display:flex; justify-content:center; align-items:center; font-size:18px;">{last_5_html if last_5_html else "..."}</div></div>', unsafe_allow_html=True)

# --- 4. الأزرار ---
r1, r2 = st.columns(5), st.columns(4)
for i, c in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[c], key=f"b_{c}"): register_result(c); st.rerun()
for i, c in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[c], key=f"b_{c}"): register_result(c); st.rerun()

# --- 5. منطق الإشارة 🚥 ---
recent_10_hits = sum(1 for x in st.session_state.action_hit[-10:] if x)
scam_status = "آمن ✅" if recent_10_hits >= 4 or len(hist) < 10 else "غدر 🚨"
trend_val = "مستقر ✅" if st.session_state.cons_m == 0 else "قلق 🧨"
if scam_status == "غدر 🚨" or st.session_state.cons_m > 2: launch_sig, sig_clr = "STOP 🔴", "#ff4b4b"
elif recent_10_hits >= 5 and trend_val == "مستقر ✅": launch_sig, sig_clr = "GO 🟢", "#39ff14"
else: launch_sig, sig_clr = "WAIT 🟡", "#ffaa00"

st.markdown(f"""
<div class="pro-grid-4">
    <div class="pro-box"><span class="lbl">📡 تنبؤ</span><br><b class="val" style="color:{"#39ff14" if "مستقر" in trend_val else "#ffaa00"}">{trend_val}</b></div>
    <div class="pro-box"><span class="lbl">🚨 إنذار</span><br><b class="val" style="color:{"#39ff14" if "آمن" in scam_status else "#ff4b4b"}">{scam_status}</b></div>
    <div class="pro-box"><span class="lbl">🏆 سلسلة</span><br><b class="val">{st.session_state.max_streak}</b></div>
    <div class="pro-box" style="border-color:{sig_clr}"><span class="lbl">🚥 الإشارة</span><br><b class="val" style="color:{sig_clr}">{launch_sig}</b></div>
</div>
""", unsafe_allow_html=True)

# --- 6. التراجع والرادار ---
c1, c2 = st.columns([1, 2])
if c1.button("↩️"): undo_last()
if total_h > 0:
    top_3 = sorted({SYMBOLS[c]: recent_15.count(c) for c in range(1, 9)}.items(), key=lambda x: x[1], reverse=True)[:3]
    radar = " ".join([f"{k}:{v}" for k, v in top_3]); c2.markdown(f'<div style="background:#0a0a0a; border:1px dashed #39ff14; padding:4px; border-radius:8px; font-size:10px; color:#39ff14; text-align:center;">📡 {radar}</div>', unsafe_allow_html=True)
