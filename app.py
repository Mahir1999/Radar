import streamlit as st

# --- إعدادات الصفحة وحفظ البيانات ---
st.set_page_config(page_title="Greedy AI v99.0", page_icon="🏆", layout="centered")

keys = ['history', 'hits', 'misses', 'cons_m', 'p_count', 'preds', 'action_hit', 'max_streak', 'cur_streak', 'balance', 'target']
for key in keys:
    if key not in st.session_state:
        if key in ['history', 'preds', 'action_hit']: st.session_state[key] = []
        elif key == 'target': st.session_state[key] = 500 # الهدف الافتراضي
        else: st.session_state[key] = 0

MULT = {1: 5, 2: 5, 3: 5, 4: 5, 5: 45, 6: 15, 7: 25, 8: 10, 9: 0}
SYMBOLS = {1: "🍅", 2: "🌽", 3: "🥕", 4: "🫑", 5: "🐔", 6: "🐑", 7: "🐟", 8: "🦐", 9: "💰"}

# --- وظيفة تسجيل النتائج ---
def register_result(code, bet_quad, bet_ins):
    is_quad_hit = code in st.session_state.preds[:4]
    is_ins_hit = (len(st.session_state.preds) > 4 and code == st.session_state.preds[4])
    h = st.session_state.history
    if len(h) >= 2 and h[-2:] == h[:-2][-2:]: st.session_state.p_count += 1
    if len(h) >= 30:
        total_bet = (bet_quad * 4) + bet_ins
        win_amount = (bet_quad * MULT[code]) if is_quad_hit else ((bet_ins * MULT[code]) if is_ins_hit else 0)
        st.session_state.balance += (win_amount - total_bet)
    is_hit = is_quad_hit or is_ins_hit
    if is_hit:
        st.session_state.hits += 1; st.session_state.cur_streak += 1
        st.session_state.max_streak = max(st.session_state.max_streak, st.session_state.cur_streak)
        st.session_state.cons_m = 0
    elif code != 9:
        st.session_state.misses += 1; st.session_state.cons_m += 1; st.session_state.cur_streak = 0
    st.session_state.history.append(code); st.session_state.action_hit.append(is_hit)

# --- محرك التوقعات وتحليل الاحتمالات ---
hist = st.session_state.history; total_h = len(hist)
shift_active = (len(st.session_state.action_hit) >= 3 and all(x is False for x in st.session_state.action_hit[-3:]) and total_h > 10)
probs = {c: 10 for c in range(1, 9)} # افتراضي

if total_h == 0:
    st.session_state.preds = [1, 2, 3, 4, 5]
else:
    recent_15 = hist[-15:]; gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 9)}
    scores = {c: (recent_15.count(c) * 0.7 + (gaps[c] * 0.3)) * (1.0 if recent_15.count(c) > 1 else 0.2) for c in range(1, 9)}
    if shift_active:
        for c in scores:
            if c not in recent_15[-3:]: scores[c] *= 1.5
    if st.session_state.cur_streak >= 4:
        for sym in hist[-2:]: 
            if sym in scores: scores[sym] *= 0.6
    top_sorted = sorted(scores, key=scores.get, reverse=True)
    st.session_state.preds = top_sorted[:4]
    meat_options = [5, 6, 7, 8]; ins_slot = 5
    for meat in meat_options:
        if meat not in st.session_state.preds: ins_slot = meat; break
    st.session_state.preds.append(ins_slot)
    # حساب النسب المئوية للقوة
    max_s = max(scores.values()) if scores.values() else 1
    probs = {c: int((scores[c]/max_s)*100) for c in range(1, 9)}

# --- التنسيق (CSS) ---
st.markdown("""
    <style>
    .main-card { background: #1a1a1a; border: 2px solid #39ff14; padding: 10px; border-radius: 15px; text-align: center; margin-bottom: 8px; }
    .quad-box { display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; margin-top: 5px; }
    .quad-item { background: #002200; border: 1px solid #39ff14; padding: 4px; border-radius: 8px; color: white; }
    .prob-bar { height: 4px; background: #39ff14; margin-top: 3px; border-radius: 2px; }
    .finance-bar { display: flex; justify-content: space-between; background: #000; padding: 8px; border-radius: 10px; border: 1px solid #444; margin-bottom: 8px; }
    .mini-box { background: #111; border: 1px solid #333; padding: 4px; border-radius: 6px; text-align: center; }
    .pro-box { background: #0a0a0a; border: 1px solid #444; padding: 4px; border-radius: 6px; text-align: center; }
    .lbl { font-size: 8px; color: #777; font-weight: bold; }
    .val { font-size: 10px; color: white; font-weight: bold; }
    .target-met { background: #d4af37 !important; border-color: #fff !important; color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. الإدارة والهدف اليومي ---
with st.expander("💰 إعدادات الرهان والهدف", expanded=(total_h >= 30)):
    c1, c2, c3, c4 = st.columns(4)
    capital = c1.number_input("رأس المال", value=1000)
    bet_q = c2.number_input("رهان المربع", value=10)
    bet_i = c3.number_input("التأمين", value=5)
    st.session_state.target = c4.number_input("الهدف 🏁", value=500)
    if st.button("تصفير الكل 🔄"):
        for k in keys:
            if k in ['history', 'preds', 'action_hit']: st.session_state[k] = []
            else: st.session_state[k] = 0
        st.rerun()

# --- 2. محلل التكرار (Heatmap) ---
if total_h > 0:
    st.markdown('<div class="lbl" style="text-align:center">🔥 توزيع التكرار الحالي</div>', unsafe_allow_html=True)
    cols = st.columns(8)
    for i in range(1, 9):
        count = hist.count(i)
        opacity = min(1.0, count/10) if count > 0 else 0.1
        cols[i-1].markdown(f'<div style="background:rgba(57,255,20,{opacity}); border-radius:4px; text-align:center; font-size:12px;">{SYMBOLS[i]}<br><span style="font-size:8px;">{count}</span></div>', unsafe_allow_html=True)

# --- 3. حالة الربح والهدف ---
is_target_met = st.session_state.balance >= st.session_state.target and total_h >= 30
target_class = "target-met" if is_target_met else ""
if is_target_met: st.balloons(); st.success("🎉 تم تحقيق الهدف اليومي! أنصح بالانسحاب.")

st.markdown(f'<div class="finance-bar {target_class}">'
            f'<div style="text-align:center"><span class="lbl">الرصيد</span><br><b style="font-size:12px;">{capital + st.session_state.balance}</b></div>'
            f'<div style="text-align:center"><span class="lbl">الربح الصافي</span><br><b style="font-size:12px;">{st.session_state.balance:+}</b></div>'
            f'<div style="text-align:center"><span class="lbl">الهدف</span><br><b style="font-size:12px;">{st.session_state.target}</b></div></div>', unsafe_allow_html=True)

# --- 4. المربع الذهبي مع شريط القوة ---
st.markdown(f'<div class="main-card"><div style="color:#39ff14; font-size:10px; font-weight:bold;">🎯 المربع الذهبي (قوة الاحتمال)</div><div class="quad-box">' + 
    "".join([f'<div class="quad-item">{SYMBOLS[c]}<div class="lbl">{probs[c]}%</div><div class="prob-bar" style="width:{probs[c]}%"></div></div>' for c in st.session_state.preds[:4]]) + 
    '</div></div>', unsafe_allow_html=True)

# --- 5. بقية العناصر (التأمين، الأزرار، الرادار، التراجع) ---
ins = st.session_state.preds[4]; last_5 = "".join([f'<span style="margin-left:3px;">{SYMBOLS[c]}</span>' for c in hist[-5:]])
st.markdown(f'<div style="display:flex; gap:6px; margin-bottom:8px;"><div style="width:70px; background:#111; border:1px solid #00aaff; border-radius:8px; text-align:center;"><span class="lbl" style="color:#00aaff">🛡️ تأمين</span><br><span style="font-size:16px;">{SYMBOLS[ins]}</span></div><div style="flex:1; background:#111; border-radius:8px; display:flex; justify-content:center; align-items:center; font-size:18px; border:1px solid #333;">{last_5 if last_5 else "..."}</div></div>', unsafe_allow_html=True)

r1, r2 = st.columns(5), st.columns(4)
for i, c in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[c], key=f"b_{c}"): register_result(c, bet_quad=bet_q, bet_ins=bet_i); st.rerun()
for i, c in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[c], key=f"b_{c}"): register_result(c, bet_quad=bet_q, bet_ins=bet_i); st.rerun()

r10 = sum(1 for x in st.session_state.action_hit[-10:] if x)
scam = "آمن ✅" if r10 >= 4 or total_h < 10 else "غدر 🚨"
trnd = "مستقر ✅" if not shift_active else "تكيف 🌀"
sig = "WAIT 🟡"
if scam == "غدر 🚨" or st.session_state.cons_m > 2 or shift_active: sig = "STOP 🔴"
elif r10 >= 5 and not shift_active: sig = "GO 🟢"

st.markdown(f'<div style="display:grid; grid-template-columns: repeat(4, 1fr); gap: 3px; margin-top: 8px;">'
            f'<div class="pro-box"><span class="lbl">📡 تنبؤ</span><br><b class="val">{trnd}</b></div>'
            f'<div class="pro-box"><span class="lbl">🚨 إنذار</span><br><b class="val">{scam}</b></div>'
            f'<div class="pro-box"><span class="lbl">🏆 سلسلة</span><br><b class="val">{st.session_state.max_streak}</b></div>'
            f'<div class="pro-box"><span class="lbl">🚥 إشارة</span><br><b class="val">{sig}</b></div></div>', unsafe_allow_html=True)

p_msg, p_clr = ("انتظار البيانات..", "#777") if total_h < 3 else (("نمط عميق (3) ✅", "#39ff14") if any(hist[i:i+3] == hist[-3:] for i in range(len(hist)-4)) else (("نمط ثنائي (2) ✅", "#ffaa00") if any(hist[i:i+2] == hist[-2:] for i in range(len(hist)-3)) else ("نمط جديد 🆕", "#ff4b4b")))
c1, c2 = st.columns([1, 2.5])
if c1.button("↩️"): 
    if st.session_state.history: st.session_state.history.pop(); st.session_state.action_hit.pop(); st.rerun()
c2.markdown(f'<div style="background:#0a0a0a; border:1px dashed {p_clr}; padding:5px; border-radius:8px; font-size:9px; color:{p_clr}; text-align:center; font-weight:bold;">🔍 {p_msg} | 📉 {st.session_state.p_count} نمط</div>', unsafe_allow_html=True)
