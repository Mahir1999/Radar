import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Greedy AI v98.1", page_icon="💎", layout="centered")

# --- تهيئة الذاكرة (تأكد من وجود كل المفاتيح) ---
keys = ['history', 'hits', 'misses', 'cons_m', 'p_count', 'preds', 'action_hit', 'max_streak', 'cur_streak', 'balance']
for key in keys:
    if key not in st.session_state:
        if key in ['history', 'preds', 'action_hit']: st.session_state[key] = []
        else: st.session_state[key] = 0

# --- معاملات الربح ---
MULT = {1: 5, 2: 5, 3: 5, 4: 5, 5: 45, 6: 15, 7: 25, 8: 10, 9: 0}
SYMBOLS = {1: "🍅", 2: "🌽", 3: "🥕", 4: "🫑", 5: "🐔", 6: "🐑", 7: "🐟", 8: "🦐", 9: "💰"}

# --- وظيفة تسجيل النتائج ---
def register_result(code, bet_quad, bet_ins):
    # الحساب المالي
    is_quad_hit = code in st.session_state.preds[:4]
    is_ins_hit = (len(st.session_state.preds) > 4 and code == st.session_state.preds[4])
    
    total_bet = (bet_quad * 4) + bet_ins
    win_amount = (bet_quad * MULT[code]) if is_quad_hit else ((bet_ins * MULT[code]) if is_ins_hit else 0)
    st.session_state.balance += (win_amount - total_bet)
    
    # التسجيل الإحصائي
    is_hit = is_quad_hit or is_ins_hit
    if is_hit:
        st.session_state.hits += 1
        st.session_state.cur_streak += 1
        st.session_state.max_streak = max(st.session_state.max_streak, st.session_state.cur_streak)
        st.session_state.cons_m = 0
    elif code != 9:
        st.session_state.misses += 1
        st.session_state.cons_m += 1
        st.session_state.cur_streak = 0
    
    st.session_state.history.append(code)
    st.session_state.action_hit.append(is_hit)

# --- منطق التوقعات (يجب تشغيله قبل العرض) ---
hist = st.session_state.history
total_h = len(hist)
if total_h == 0:
    st.session_state.preds = [1, 2, 3, 4, 5] # توقعات افتراضية للبداية
else:
    recent_15 = hist[-15:]; gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 9)}
    scores = {c: (recent_15.count(c) * 0.7 + (gaps[c] * 0.3)) * (1.0 if recent_15.count(c) > 1 else 0.2) for c in range(1, 9)}
    if st.session_state.cur_streak >= 4:
        for sym in hist[-2:]: 
            if sym in scores: scores[sym] *= 0.6
    top_4 = sorted(scores, key=scores.get, reverse=True)[:4]
    meat_options = [5, 6, 7, 8]; ins_slot = 5
    for meat in meat_options:
        if meat not in top_4: ins_slot = meat; break
    st.session_state.preds = top_4 + [ins_slot]

# --- التنسيق (CSS) ---
st.markdown("""
    <style>
    .main-card { background: #1a1a1a; border: 2px solid #39ff14; padding: 10px; border-radius: 15px; text-align: center; margin-bottom: 8px; }
    .quad-box { display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; margin-top: 5px; }
    .quad-item { background: #002200; border: 1px solid #39ff14; padding: 6px; border-radius: 8px; color: white; font-weight: bold; }
    .finance-bar { display: flex; justify-content: space-between; background: #000; padding: 8px; border-radius: 10px; border: 1px solid #444; margin-bottom: 8px; }
    .mini-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; margin-bottom: 8px; }
    .mini-box { background: #111; border: 1px solid #333; padding: 4px; border-radius: 6px; text-align: center; }
    .pro-grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 3px; margin-top: 8px; }
    .pro-box { background: #0a0a0a; border: 1px solid #444; padding: 4px; border-radius: 6px; text-align: center; }
    .lbl { font-size: 8px; color: #777; font-weight: bold; }
    .val { font-size: 10px; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. الإدارة المالية ---
with st.expander("💰 إعدادات المحفظة والرهان", expanded=False):
    c_cap, c_q, c_i = st.columns(3)
    capital = c_cap.number_input("رأس المال", value=1000)
    bet_q = c_q.number_input("رهان المربع", value=10)
    bet_i = c_i.number_input("رهان التأمين", value=5)
    if st.button("تصفير الكل 🔄"):
        for key in keys:
            if key in ['history', 'preds', 'action_hit']: st.session_state[key] = []
            else: st.session_state[key] = 0
        st.rerun()

# --- 2. العدادات العلوية ---
st.markdown(f'<div class="mini-grid">'
            f'<div class="mini-box"><span class="lbl">🔄 جولة</span><br><b class="val">{total_h}</b></div>'
            f'<div class="mini-box"><span class="lbl" style="color:#39ff14">✅ صح</span><br><b class="val">{st.session_state.hits}</b></div>'
            f'<div class="mini-box"><span class="lbl" style="color:#ff4b4b">❌ خطأ</span><br><b class="val">{st.session_state.misses}</b></div>'
            f'<div class="mini-box"><span class="lbl">📉 نمط</span><br><b class="val">{st.session_state.p_count}</b></div></div>', unsafe_allow_html=True)

# --- 3. شريط الحالة المالية ---
p_color = "#39ff14" if st.session_state.balance >= 0 else "#ff4b4b"
st.markdown(f'<div class="finance-bar">'
            f'<div style="text-align:center"><span class="lbl">الرصيد</span><br><b style="color:white; font-size:12px;">{capital + st.session_state.balance}</b></div>'
            f'<div style="text-align:center"><span class="lbl">الربح</span><br><b style="color:{p_color}; font-size:12px;">{st.session_state.balance:+}</b></div></div>', unsafe_allow_html=True)

# --- 4. المربع الذهبي ---
t4 = st.session_state.preds[:4]
st.markdown(f'<div class="main-card"><div style="color:#39ff14; font-size:10px; font-weight:bold;">🎯 المربع الذهبي</div><div class="quad-box">{"".join([f'<div class="quad-item">{SYMBOLS[c]}</div>' for c in t4])}</div></div>', unsafe_allow_html=True)

# --- 5. التأمين وآخر 5 ---
ins = st.session_state.preds[4] if len(st.session_state.preds) > 4 else 5
last_5 = "".join([f'<span style="margin-left:3px;">{SYMBOLS[c]}</span>' for c in hist[-5:]])
st.markdown(f'<div style="display:flex; gap:6px; margin-bottom:8px;"><div style="width:70px; background:#111; border:1px solid #00aaff; border-radius:8px; text-align:center;"><span class="lbl" style="color:#00aaff">🛡️ تأمين</span><br><span style="font-size:16px;">{SYMBOLS[ins]}</span></div>'
            f'<div style="flex:1; background:#111; border-radius:8px; display:flex; justify-content:center; align-items:center; font-size:18px; border:1px solid #333;">{last_5 if last_5 else "..."}</div></div>', unsafe_allow_html=True)

# --- 6. الأزرار ---
r1, r2 = st.columns(5), st.columns(4)
for i, c in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[c], key=f"b_{c}"): register_result(c, bet_q, bet_i); st.rerun()
for i, c in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[c], key=f"b_{c}"): register_result(c, bet_q, bet_i); st.rerun()

# --- 7. الصف الرباعي ---
r10 = sum(1 for x in st.session_state.action_hit[-10:] if x)
scam = "آمن ✅" if r10 >= 4 or total_h < 10 else "غدر 🚨"
trnd = "مستقر ✅" if st.session_state.cons_m == 0 else "قلق 🧨"
sig = "WAIT 🟡"
if scam == "غدر 🚨" or st.session_state.cons_m > 2: sig = "STOP 🔴"
elif r10 >= 5 and trnd == "مستقر ✅": sig = "GO 🟢"

st.markdown(f'<div class="pro-grid-4"><div class="pro-box"><span class="lbl">📡 تنبؤ</span><br><b class="val">{trnd}</b></div><div class="pro-box"><span class="lbl">🚨 إنذار</span><br><b class="val">{scam}</b></div><div class="pro-box"><span class="lbl">🏆 سلسلة</span><br><b class="val">{st.session_state.max_streak}</b></div><div class="pro-box"><span class="lbl">🚥 إشارة</span><br><b class="val">{sig}</b></div></div>', unsafe_allow_html=True)

# --- 8. رادار النمط ---
def find_p(h):
    if len(h) < 3: return "انتظار البيانات..", "#777"
    l3, l2 = h[-3:], h[-2:]
    for i in range(len(h)-4):
        if h[i:i+3] == l3: return "نمط عميق (3) موجود ✅", "#39ff14"
    for i in range(len(h)-3):
        if h[i:i+2] == l2: return "نمط ثنائي (2) موجود ✅", "#ffaa00"
    return "نمط جديد 🆕", "#ff4b4b"

p_msg, p_clr = find_p(hist)
c1, c2 = st.columns([1, 2.5])
if c1.button("↩️"): 
    if st.session_state.history: st.session_state.history.pop(); st.session_state.action_hit.pop(); st.rerun()
c2.markdown(f'<div style="background:#0a0a0a; border:1px dashed {p_clr}; padding:5px; border-radius:8px; font-size:9px; color:{p_clr}; text-align:center; font-weight:bold;">🔍 {p_msg}</div>', unsafe_allow_html=True)
