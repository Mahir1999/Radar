import streamlit as st

# --- إعدادات الصفحة وحفظ البيانات ---
st.set_page_config(page_title="Greedy AI v96.5", page_icon="📱", layout="centered")

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
        st.session_state.history.pop(); st.session_state.action_hit.pop()
        # تقليل العدادات بناءً على آخر فعل (تبسيط للمساحة)
        st.rerun()

# --- التنسيق (CSS) ---
st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; }
    .main-card { background: #1a1a1a; border: 2px solid #39ff14; padding: 10px; border-radius: 15px; text-align: center; margin-bottom: 5px; }
    .quad-box { display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; margin-top: 5px; }
    .quad-item { background: #002200; border: 1px solid #39ff14; padding: 5px; border-radius: 8px; color: white; font-weight: bold; font-size: 11px; }
    
    /* نظام التمرير الأفقي للأزرار */
    .scroll-container {
        display: flex;
        overflow-x: auto;
        white-space: nowrap;
        gap: 8px;
        padding: 10px 5px;
        scrollbar-width: none; /* Firefox */
    }
    .scroll-container::-webkit-scrollbar { display: none; } /* Chrome/Safari */
    
    .scroll-btn {
        flex: 0 0 auto;
        width: 50px;
        height: 50px;
        background: #222;
        border: 2px solid #444;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        cursor: pointer;
    }
    
    .mini-grid { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 4px; margin-bottom: 5px; }
    .mini-box { background: #111; border: 1px solid #333; padding: 4px; border-radius: 6px; text-align: center; }
    .pro-grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 4px; margin-bottom: 5px; }
    .pro-box { background: #0a0a0a; border: 1px solid #444; padding: 5px; border-radius: 8px; text-align: center; }
    .lbl { font-size: 7px; color: #777; font-weight: bold; }
    .val { font-size: 10px; color: white; font-weight: bold; }
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

# --- 2. المربع الذهبي (المفلتر) ---
recent_15 = hist[-15:]; gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 9)}
scores = {c: (recent_15.count(c) * 0.7 + (gaps[c] * 0.3)) * (1.0 if recent_15.count(c) > 1 else 0.2) for c in range(1, 9)}
top_4 = sorted(scores, key=scores.get, reverse=True)[:4]
st.session_state.preds = top_4 + [sorted(scores, key=scores.get, reverse=True)[4]]

items_html = "".join([f'<div class="quad-item">{SYMBOLS[c]}</div>' for c in top_4])
st.markdown(f'<div class="main-card"><div style="color:#39ff14; font-size:10px; font-weight:bold;">🎯 المربع الذهبي (مفلتر 🛡️)</div><div class="quad-box">{items_html}</div></div>', unsafe_allow_html=True)

# --- 3. صف الحماية الثلاثي ---
scam_status = "آمن ✅" if sum(1 for x in st.session_state.action_hit[-10:] if x) >= 4 or len(hist) < 10 else "غدر 🚨"
st.markdown(f'<div class="pro-grid-3">'
            f'<div class="pro-box"><span class="lbl">📡 تنبؤ</span><br><b class="val">{"مستقر ✅" if st.session_state.cons_m == 0 else "قلق 🧨"}</b></div>'
            f'<div class="pro-box" style="border-color:{"#39ff14" if "✅" in scam_status else "#ff4b4b"}"><span class="lbl">🚨 إنذار</span><br><b class="val">{scam_status}</b></div>'
            f'<div class="pro-box"><span class="lbl">🏆 سلسلة</span><br><b class="val">{st.session_state.max_streak}</b></div></div>', unsafe_allow_html=True)

# --- 4. نظام أزرار التمرير الأفقي (الميزة الجديدة) ---
st.markdown('<p class="lbl" style="text-align:center; margin:0;">⬅️ اسحب لاختيار الرمز ➡️</p>', unsafe_allow_html=True)
cols = st.columns([1,1,1,1,1,1,1,1,1])
# لتمثيل التمرير في Streamlit نستخدم توزيع الأعمدة أو الحاويات
with st.container():
    h_scroll = st.columns(9)
    order = [5,6,7,8,1,2,3,4,9] # اللحوم أولاً لسهولة الوصول
    for i, c in enumerate(order):
        if h_scroll[i].button(SYMBOLS[c], key=f"scr_{c}"):
            register_result(c); st.rerun()

# --- 5. رادار الكثافة وزر التراجع ---
c1, c2 = st.columns([1, 3])
if c1.button("↩️"): undo_last()
if total_h > 0:
    top_3 = sorted({SYMBOLS[c]: recent_15.count(c) for c in range(1, 9)}.items(), key=lambda x: x[1], reverse=True)[:3]
    radar = " ".join([f"{k}:{v}" for k, v in top_3])
    c2.markdown(f'<div style="background:#0a0a0a; border:1px dashed #39ff14; padding:4px; border-radius:8px; font-size:10px; color:#39ff14; text-align:center;">📡 {radar}</div>', unsafe_allow_html=True)
