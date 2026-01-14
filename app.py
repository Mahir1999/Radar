import streamlit as st

# --- إعدادات الصفحة وحفظ البيانات ---
st.set_page_config(page_title="Greedy AI v96.0", page_icon="🏆", layout="centered")

# تأكيد حفظ الأرقام كما طلبت في تعليماتك
for key in ['history', 'hits', 'misses', 'cons_m', 'p_count', 'preds', 'action_hit', 'goal', 'bank']:
    if key not in st.session_state:
        st.session_state[key] = [] if key in ['history', 'preds', 'action_hit'] else 0

# --- منطق تسجيل النتائج المطور ---
def register_result(code):
    is_hit = code in st.session_state.preds
    if is_hit:
        st.session_state.hits += 1
        if st.session_state.cons_m >= 2: st.session_state.p_count += 1
        st.session_state.cons_m = 0
    elif code != 9:
        st.session_state.misses += 1
        st.session_state.cons_m += 1
    
    st.session_state.history.append(code)
    st.session_state.action_hit.append(is_hit)

def undo_last():
    if st.session_state.history:
        st.session_state.history.pop()
        last_hit = st.session_state.action_hit.pop()
        if last_hit: st.session_state.hits -= 1
        else: 
            st.session_state.misses -= 1
            st.session_state.cons_m -= 1
        st.rerun()

# --- التنسيق (CSS) ---
st.markdown(f"""
    <style>
    .block-container {{ padding-top: 1rem; }}
    .stButton>button {{ width: 100%; height: 45px; font-weight: bold; border-radius: 8px; font-size: 13px; }}
    .main-card {{ background: #1a1a1a; border: 2px solid #39ff14; padding: 10px; border-radius: 15px; text-align: center; margin-bottom: 10px; }}
    .quad-box {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 5px; }}
    .quad-item {{ background: #002200; border: 1px solid #39ff14; padding: 6px; border-radius: 8px; color: white; font-weight: bold; font-size: 12px; }}
    
    /* مصفوفة الأدوات الجديدة */
    .tool-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px; }}
    .tool-box {{ background: #111; border: 1px solid #444; padding: 8px; border-radius: 10px; text-align: center; }}
    .stat-text {{ font-size: 10px; color: #888; font-weight: bold; }}
    .val-text {{ font-size: 13px; color: white; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

SYMBOLS = {1: "🍅", 2: "🌽", 3: "🥕", 4: "🫑", 5: "🐔", 6: "🐑", 7: "🐟", 8: "🦐", 9: "💰"}
hist = st.session_state.history
total_h = len(hist)

# --- 1. العدادات العلوية ---
p_status = "ثابت ✅" if st.session_state.cons_m < 2 else "متغير ⚠️"
st.markdown(f'<div style="display:grid; grid-template-columns: 1fr 1fr 1fr 1.2fr; gap:5px; margin-bottom:10px;">'
            f'<div class="tool-box"><span class="stat-text">🔄 جولة</span><br><b class="val-text">{total_h}</b></div>'
            f'<div class="tool-box"><span class="stat-text" style="color:#39ff14">✅ فوز</span><br><b class="val-text">{st.session_state.hits}</b></div>'
            f'<div class="tool-box"><span class="stat-text" style="color:#ff4b4b">❌ خطأ</span><br><b class="val-text">{st.session_state.misses}</b></div>'
            f'<div class="tool-box"><span class="stat-text">📉 النمط</span><br><b class="val-text" style="color:{"#39ff14" if "✅" in p_status else "#ff4b4b"}">{p_status}</b></div></div>', unsafe_allow_html=True)

# --- 2. المربع الذهبي ---
if total_h >= 0:
    gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 9)}
    recent_15 = hist[-15:]
    scores = {c: (recent_15.count(c) * 0.7 + (gaps[c] * 0.3)) for c in range(1, 9)}
    top_4 = sorted(scores, key=scores.get, reverse=True)[:4]
    ins_slot = sorted([5,6,7,8], key=lambda x: gaps[x], reverse=True)[0] if all(c in [1,2,3,4] for c in top_4) else sorted(scores, key=scores.get, reverse=True)[4]
    st.session_state.preds = top_4 + [ins_slot]
    
    st.markdown(f'<div class="main-card"><div style="color:#39ff14; font-size:11px; font-weight:bold;">🎯 المربع الذهبي</div><div class="quad-box">{"".join([f'<div class="quad-item">{SYMBOLS[c]}</div>' for c in top_4])}</div></div>', unsafe_allow_html=True)

    # --- 3. الصف المدمج (تأمين + تاريخ) ---
    last_5 = "".join([f'<div style="background:#222; border:1px solid #39ff14; padding:2px 6px; border-radius:4px; margin-left:4px;">{SYMBOLS[c]}</div>' for c in hist[-5:]])
    st.markdown(f'<div style="display:flex; gap:8px; margin-bottom:10px; align-items:center;">'
                f'<div class="tool-box" style="width:80px; border-color:#00aaff;"><span class="stat-text" style="color:#00aaff">🛡️ تأمين</span><br><span style="font-size:18px;">{SYMBOLS[ins_slot]}</span></div>'
                f'<div class="tool-box" style="flex:1; display:flex; justify-content:center; align-items:center;">{last_5 if last_5 else "..."}</div></div>', unsafe_allow_html=True)

# --- 4. أزرار التحكم ---
r1, r2 = st.columns(5), st.columns(4)
for i, c in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[c], key=f"b_{c}"): register_result(c); st.rerun()
for i, c in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[c], key=f"b_{c}"): register_result(c); st.rerun()

# --- 5. مصفوفة الأدوات الاحترافية الجديدة ---
gap_9 = (list(reversed(hist)).index(9) if 9 in hist else total_h)
# حساب مستشار الرهان
adv_color = "#39ff14" if st.session_state.hits > st.session_state.misses else "#ff4b4b"
adv_text = "ارفع 💸" if st.session_state.hits > st.session_state.misses + 5 else ("حذر ⚠️" if st.session_state.cons_m >= 2 else "عادي ⚖️")
# حساب المجموعات
meat_count = sum(1 for x in recent_15 if x in [5,6,7,8])
wave_text = "🥩 لحوم" if meat_count > 8 else ("🥗 خضار" if meat_count < 7 else "🔄 مختلط")

st.markdown(f"""
<div class="tool-grid">
    <div class="tool-box"><span class="stat-text">💰 الجاكبوت</span><br><b class="val-text" style="color:{"#ff4b4b" if gap_9 > 80 else "#39ff14"}">{gap_9} جولة</b></div>
    <div class="tool-box"><span class="stat-text">📡 ملك الموجة</span><br><b class="val-text">{wave_text}</b></div>
    <div class="tool-box"><span class="stat-text">🧠 الأنماط</span><br><b class="val-text">{st.session_state.p_count} نمط</b></div>
    <div class="tool-box" style="border-color:{adv_color}"><span class="stat-text">💵 الرهان</span><br><b class="val-text" style="color:{adv_color}">{adv_text}</b></div>
</div>
""", unsafe_allow_html=True)

# --- 6. رادار ملوك الموجة وزر التراجع ---
c1, c2 = st.columns([1, 2])
if c1.button("↩️ تراجع"): undo_last()
if total_h > 0:
    top_3 = sorted({SYMBOLS[c]: recent_15.count(c) for c in range(1, 9)}.items(), key=lambda x: x[1], reverse=True)[:3]
    radar = " ".join([f"{k}:{v}" for k, v in top_3])
    c2.markdown(f'<div style="background:#0a0a0a; border:1px dashed #39ff14; padding:5px; border-radius:8px; font-size:10px; color:#39ff14; text-align:center;">📡 الكثافة: {radar}</div>', unsafe_allow_html=True)
