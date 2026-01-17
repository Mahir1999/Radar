import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Greedy AI v98.0", page_icon="💰", layout="centered")

# --- تهيئة الذاكرة والحسابات المالية ---
for key in ['history', 'hits', 'misses', 'cons_m', 'p_count', 'preds', 'action_hit', 'max_streak', 'cur_streak', 'balance', 'total_profit']:
    if key not in st.session_state:
        if key == 'history' or key == 'preds' or key == 'action_hit': st.session_state[key] = []
        else: st.session_state[key] = 0

# --- معاملات الربح (Multipliers) ---
MULT = {1: 5, 2: 5, 3: 5, 4: 5, 5: 45, 6: 15, 7: 25, 8: 10, 9: 0}

# --- منطق الحساب المالي والتسجيل ---
def register_result(code, bet_quad, bet_ins):
    is_quad_hit = code in st.session_state.preds[:4]
    is_ins_hit = code == st.session_state.preds[4]
    
    total_bet = (bet_quad * 4) + bet_ins
    win_amount = 0
    
    if is_quad_hit:
        win_amount = bet_quad * MULT[code]
    elif is_ins_hit:
        win_amount = bet_ins * MULT[code]
        
    st.session_state.balance += (win_amount - total_bet)
    st.session_state.total_profit = st.session_state.balance
    
    # التسجيل الإحصائي المعتاد (بدون تغيير)
    is_hit = is_quad_hit or is_ins_hit
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

# --- التنسيق (CSS) ---
st.markdown("""
    <style>
    .stNumberInput>div>div>input { background: #0e1117; color: #39ff14; font-weight: bold; }
    .main-card { background: #1a1a1a; border: 2px solid #39ff14; padding: 10px; border-radius: 15px; text-align: center; margin-bottom: 8px; }
    .quad-box { display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; margin-top: 5px; }
    .quad-item { background: #002200; border: 1px solid #39ff14; padding: 6px; border-radius: 8px; color: white; font-weight: bold; }
    .finance-bar { display: flex; justify-content: space-between; background: #000; padding: 10px; border-radius: 10px; border: 1px solid #444; margin-bottom: 10px; }
    .pro-grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 3px; margin-top: 8px; }
    .pro-box { background: #0a0a0a; border: 1px solid #444; padding: 4px; border-radius: 6px; text-align: center; }
    .lbl { font-size: 7px; color: #777; font-weight: bold; }
    .val { font-size: 9px; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. مدخلات الإدارة المالية ---
with st.expander("💰 إعدادات المحفظة والرهان", expanded=True):
    col_cap, col_q, col_i = st.columns(3)
    capital = col_cap.number_input("رأس المال", value=1000)
    bet_q = col_q.number_input("رهان المربع", value=10)
    bet_i = col_i.number_input("رهان التأمين", value=5)
    if st.button("تصفير المحفظة 🔄"):
        st.session_state.balance = 0
        st.rerun()

# --- 2. شريط الحالة المالية ---
profit_color = "#39ff14" if st.session_state.balance >= 0 else "#ff4b4b"
st.markdown(f"""
<div class="finance-bar">
    <div style="text-align:center"><span class="lbl">الرصيد الحالي</span><br><b style="color:white; font-size:14px;">{capital + st.session_state.balance}</b></div>
    <div style="text-align:center"><span class="lbl">صافي الربح/الخسارة</span><br><b style="color:{profit_color}; font-size:14px;">{st.session_state.balance:+}</b></div>
</div>
""", unsafe_allow_html=True)

SYMBOLS = {1: "🍅", 2: "🌽", 3: "🥕", 4: "🫑", 5: "🐔", 6: "🐑", 7: "🐟", 8: "🦐", 9: "💰"}
hist = st.session_state.history; total_h = len(hist)

# --- المربع الذهبي (بميزاته السابقة) ---
if total_h > 0:
    recent_15 = hist[-15:]; gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 9)}
    scores = {c: (recent_15.count(c) * 0.7 + (gaps[c] * 0.3)) * (1.0 if recent_15.count(c) > 1 else 0.2) for c in range(1, 9)}
    if st.session_state.cur_streak >= 4:
        for sym in hist[-2:]: 
            if sym in scores: scores[sym] *= 0.6
    top_4 = sorted(scores, key=scores.get, reverse=True)[:4]
    meat_options = [5, 6, 7, 8]; ins_slot = sorted(scores, key=scores.get, reverse=True)[4]
    for meat in meat_options:
        if meat not in top_4: ins_slot = meat; break
    st.session_state.preds = top_4 + [ins_slot]
    st.markdown(f'<div class="main-card"><div style="color:#39ff14; font-size:10px; font-weight:bold;">🎯 المربع الذهبي (درع + محاكاة)</div><div class="quad-box">{"".join([f'<div class="quad-item">{SYMBOLS[c]}</div>' for c in top_4])}</div></div>', unsafe_allow_html=True)

# --- التأمين وآخر 5 ---
    last_5_html = "".join([f'<span style="margin-left:3px;">{SYMBOLS[c]}</span>' for c in hist[-5:]])
    st.markdown(f'<div style="display:flex; gap:6px; margin-bottom:8px;"><div class="mini-box" style="width:70px; border:1px solid #00aaff; border-radius:8px; text-align:center;"><span class="lbl" style="color:#00aaff">🛡️ تأمين</span><br><span style="font-size:16px;">{SYMBOLS[ins_slot]}</span></div>'
                f'<div style="flex:1; background:#111; border-radius:8px; display:flex; justify-content:center; align-items:center; font-size:18px;">{last_5_html if last_5_html else "..."}</div></div>', unsafe_allow_html=True)

# --- الأزرار ---
r1, r2 = st.columns(5), st.columns(4)
for i, c in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[c], key=f"b_{c}"): register_result(c, bet_q, bet_i); st.rerun()
for i, c in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[c], key=f"b_{c}"): register_result(c, bet_q, bet_i); st.rerun()

# --- الصف الرباعي والرادار ---
recent_10_hits = sum(1 for x in st.session_state.action_hit[-10:] if x)
scam_status = "آمن ✅" if recent_10_hits >= 4 or len(hist) < 10 else "غدر 🚨"
trend_val = "مستقر ✅" if st.session_state.cons_m == 0 else "قلق 🧨"
launch_sig = "WAIT 🟡"
if scam_status == "غدر 🚨" or st.session_state.cons_m > 2: launch_sig = "STOP 🔴"
elif recent_10_hits >= 5 and trend_val == "مستقر ✅": launch_sig = "GO 🟢"

st.markdown(f'<div class="pro-grid-4"><div class="pro-box"><span class="lbl">📡 تنبؤ</span><br><b class="val">{trend_val}</b></div><div class="pro-box"><span class="lbl">🚨 إنذار</span><br><b class="val">{scam_status}</b></div><div class="pro-box"><span class="lbl">🏆 سلسلة</span><br><b class="val">{st.session_state.max_streak}</b></div><div class="pro-box"><span class="lbl">🚥 الإشارة</span><br><b class="val">{launch_sig}</b></div></div>', unsafe_allow_html=True)

def find_flexible_pattern(h):
    if len(h) < 3: return "بيانات غير كافية ⏳", "#777"
    l3, l2 = h[-3:], h[-2:]
    for i in range(len(h)-4):
        if h[i:i+3] == l3: return "نمط عميق (3) موجود ✅", "#39ff14"
    for i in range(len(h)-3):
        if h[i:i+2] == l2: return "نمط ثنائي (2) موجود ✅", "#ffaa00"
    return "نمط جديد 🆕", "#ff4b4b"

pattern_msg, pattern_clr = find_flexible_pattern(hist)
c1, c2 = st.columns([1, 2.5])
if c1.button("↩️"): 
    if st.session_state.history: st.session_state.history.pop(); st.session_state.action_hit.pop(); st.rerun()
c2.markdown(f'<div style="background:#0a0a0a; border:1px dashed {pattern_clr}; padding:5.5px; border-radius:8px; font-size:10px; color:{pattern_clr}; text-align:center; font-weight:bold;">🔍 {pattern_msg}</div>', unsafe_allow_html=True)
