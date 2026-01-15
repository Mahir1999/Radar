import streamlit as st

# --- إعدادات الصفحة وحفظ البيانات ---
st.set_page_config(page_title="Greedy AI v96.1", page_icon="📈", layout="centered")

# تأكيد حفظ الأرقام (Memory Management)
for key in ['history', 'hits', 'misses', 'cons_m', 'p_count', 'preds', 'action_hit', 'max_streak', 'cur_streak']:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ['history', 'preds', 'action_hit'] else 0

# --- منطق تسجيل النتائج ---
def register_result(code):
    is_hit = code in st.session_state.preds
    if is_hit:
        st.session_state.hits += 1
        st.session_state.cur_streak += 1
        if st.session_state.cur_streak > st.session_state.max_streak:
            st.session_state.max_streak = st.session_state.cur_streak
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

# --- التنسيق (CSS) ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    .stButton>button { width: 100%; height: 42px; font-weight: bold; border-radius: 8px; font-size: 13px; }
    .main-card { background: #1a1a1a; border: 2px solid #39ff14; padding: 10px; border-radius: 15px; text-align: center; margin-bottom: 8px; }
    .quad-box { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 5px; }
    .quad-item { background: #002200; border: 1px solid #39ff14; padding: 6px; border-radius: 8px; color: white; font-weight: bold; font-size: 11px; }
    
    /* الصف الرباعي المدمج */
    .mini-grid { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 4px; margin-bottom: 8px; }
    .mini-box { background: #111; border: 1px solid #333; padding: 4px; border-radius: 6px; text-align: center; }
    
    /* صف التنبؤ والسلسلة */
    .pro-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 6px; margin-top: 8px; }
    .pro-box { background: #0a0a0a; border: 1px solid #444; padding: 6px; border-radius: 10px; text-align: center; }
    
    .lbl { font-size: 8px; color: #777; font-weight: bold; text-transform: uppercase; }
    .val { font-size: 11px; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

SYMBOLS = {1: "🍅", 2: "🌽", 3: "🥕", 4: "🫑", 5: "🐔", 6: "🐑", 7: "🐟", 8: "🦐", 9: "💰"}
hist = st.session_state.history
total_h = len(hist)

# --- 1. العدادات العلوية ---
p_status = "ثابت ✅" if st.session_state.cons_m < 2 else "متغير ⚠️"
st.markdown(f'<div style="display:grid; grid-template-columns: 1fr 1fr 1fr 1.2fr; gap:4px; margin-bottom:8px;">'
            f'<div class="mini-box"><span class="lbl">🔄 جولة</span><br><b class="val">{total_h}</b></div>'
            f'<div class="mini-box"><span class="lbl" style="color:#39ff14">✅ فوز</span><br><b class="val">{st.session_state.hits}</b></div>'
            f'<div class="mini-box"><span class="lbl" style="color:#ff4b4b">❌ خطأ</span><br><b class="val">{st.session_state.misses}</b></div>'
            f'<div class="mini-box"><span class="lbl">📉 النمط</span><br><b class="val" style="color:{"#39ff14" if "✅" in p_status else "#ff4b4b"}">{p_status}</b></div></div>', unsafe_allow_html=True)

# --- 2. المربع الذهبي ---
if total_h >= 0:
    gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 9)}
    recent_15 = hist[-15:]
    scores = {c: (recent_15.count(c) * 0.7 + (gaps[c] * 0.3)) for c in range(1, 9)}
    top_4 = sorted(scores, key=scores.get, reverse=True)[:4]
    ins_slot = sorted([5,6,7,8], key=lambda x: gaps[x], reverse=True)[0] if all(c in [1,2,3,4] for c in top_4) else sorted(scores, key=scores.get, reverse=True)[4]
    st.session_state.preds = top_4 + [ins_slot]
    
    st.markdown(f'<div class="main-card"><div style="color:#39ff14; font-size:10px; font-weight:bold;">🎯 المربع الذهبي</div><div class="quad-box">{"".join([f'<div class="quad-item">{SYMBOLS[c]}</div>' for c in top_4])}</div></div>', unsafe_allow_html=True)

    # --- 3. التأمين وتاريخ آخر 5 ---
    last_5_html = "".join([f'<span style="margin-left:3px;">{SYMBOLS[c]}</span>' for c in hist[-5:]])
    conf = min(95, 40 + (gaps[ins_slot] * 2))
    st.markdown(f'<div style="display:flex; gap:6px; margin-bottom:8px;">'
                f'<div class="mini-box" style="width:70px; border-color:#00aaff;"><span class="lbl" style="color:#00aaff">🛡️ {conf}%</span><br><span style="font-size:16px;">{SYMBOLS[ins_slot]}</span></div>'
                f'<div class="mini-box" style="flex:1; display:flex; justify-content:center; align-items:center; font-size:18px;">{last_5_html if last_5_html else "..."}</div></div>', unsafe_allow_html=True)

# --- 4. الأزرار ---
r1, r2 = st.columns(5), st.columns(4)
for i, c in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[c], key=f"b_{c}"): register_result(c); st.rerun()
for i, c in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[c], key=f"b_{c}"): register_result(c); st.rerun()

# --- 5. الصف الرباعي المدمج (الرهان، ملوك الموجة، الجاكبوت، الأنماط) ---
gap_9 = (list(reversed(hist)).index(9) if 9 in hist else total_h)
meat_count = sum(1 for x in recent_15 if x in [5,6,7,8])
wave_icon = "🥩" if meat_count > 8 else ("🥗" if meat_count < 7 else "🔄")
adv_txt = "💸" if st.session_state.hits > st.session_state.misses + 5 else ("⚠️" if st.session_state.cons_m >= 2 else "⚖️")

st.markdown(f"""
<div class="mini-grid">
    <div class="mini-box"><span class="lbl">💰 جكبوت</span><br><b class="val">{gap_9}</b></div>
    <div class="mini-box"><span class="lbl">📡 موجة</span><br><b class="val">{wave_icon}</b></div>
    <div class="mini-box"><span class="lbl">🧠 أنماط</span><br><b class="val">{st.session_state.p_count}</b></div>
    <div class="mini-box"><span class="lbl">💵 رهان</span><br><b class="val">{adv_txt}</b></div>
</div>
""", unsafe_allow_html=True)

# --- 6. صف التنبؤ والسلسلة (الأفكار الجديدة) ---
trend_val = "مستقر ✅" if st.session_state.cons_m == 0 else "قلق 🧨"
trend_clr = "#39ff14" if st.session_state.cons_m == 0 else "#ffaa00"

st.markdown(f"""
<div class="pro-grid">
    <div class="pro-box" style="border-color:{trend_clr}"><span class="lbl">📡 تنبؤ الموجة</span><br><b class="val" style="color:{trend_clr}">{trend_val}</b></div>
    <div class="pro-box" style="border-color:#39ff14"><span class="lbl">🏆 أفضل سلسلة</span><br><b class="val" style="color:#39ff14">{st.session_state.max_streak}</b></div>
</div>
""", unsafe_allow_html=True)

# --- 7. رادار الكثافة وزر تراجع ---
c1, c2 = st.columns([1, 2])
if c1.button("↩️"): undo_last()
if total_h > 0:
    top_3 = sorted({SYMBOLS[c]: recent_15.count(c) for c in range(1, 9)}.items(), key=lambda x: x[1], reverse=True)[:3]
    radar = " ".join([f"{k}:{v}" for k, v in top_3])
    c2.markdown(f'<div style="background:#0a0a0a; border:1px dashed #39ff14; padding:4px; border-radius:8px; font-size:9px; color:#39ff14; text-align:center;">📡 {radar}</div>', unsafe_allow_html=True)
