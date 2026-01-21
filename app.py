import streamlit as st

# --- 1. الإعدادات الأساسية ---
st.set_page_config(page_title="Greedy AI v99.9", page_icon="🏆", layout="centered")

# --- 2. تهيئة الذاكرة (لا ينقص شيء) ---
keys = ['history', 'hits', 'misses', 'cons_m', 'p_count', 'preds', 'action_hit', 'max_streak', 'cur_streak', 'balance', 'target']
for key in keys:
    if key not in st.session_state:
        if key in ['history', 'preds', 'action_hit']: st.session_state[key] = []
        elif key == 'balance': st.session_state[key] = 0
        else: st.session_state[key] = 0

SYMBOLS = {1: "🍅", 2: "🌽", 3: "🥕", 4: "🫑", 5: "🐔", 6: "🐑", 7: "🐟", 8: "🦐", 9: "💰"}
MULT = {1: 5, 2: 5, 3: 5, 4: 5, 5: 45, 6: 15, 7: 25, 8: 10, 9: 0}

# --- 3. وظيفة تسجيل النتائج (كاملة وبدون نقص) ---
def register_result(code, bq, bi):
    is_quad_hit = code in st.session_state.preds[:4]
    is_ins_hit = (len(st.session_state.preds) > 4 and code == st.session_state.preds[4])
    is_hit = is_quad_hit or is_ins_hit
    h = st.session_state.history
    
    # حساب الأنماط المتراكم
    if len(h) >= 2:
        last_pair = [h[-1], code]
        for i in range(len(h) - 1):
            if h[i:i+2] == last_pair:
                st.session_state.p_count += 1
                break
    
    # الحساب المالي (شرط الجولة 30)
    if len(h) >= 30:
        total_bet = (bq * 4) + bi
        win = (bq * MULT[code]) if is_quad_hit else ((bi * MULT[code]) if is_ins_hit else 0)
        st.session_state.balance += (win - total_bet)
    
    # الإحصائيات
    if is_hit:
        st.session_state.hits += 1; st.session_state.cur_streak += 1
        st.session_state.max_streak = max(st.session_state.max_streak, st.session_state.cur_streak); st.session_state.cons_m = 0
    elif code != 9:
        st.session_state.misses += 1; st.session_state.cons_m += 1; st.session_state.cur_streak = 0
    
    st.session_state.history.append(code)
    st.session_state.action_hit.append(is_hit)

# --- 4. محرك التوقعات ورادار التكيف ---
hist = st.session_state.history; total_h = len(hist)
shift_active = (len(st.session_state.action_hit) >= 3 and all(x is False for x in st.session_state.action_hit[-3:]) and total_h > 10)

if total_h == 0:
    st.session_state.preds = [1, 2, 3, 4, 5]
    probs = {i: 10 for i in range(1, 9)}
else:
    # تحليل القوة
    scores = {i: (hist[-15:].count(i) * 1.5 + (total_h - (list(reversed(hist)).index(i) if i in hist else total_h)) * 0.2) for i in range(1, 9)}
    if shift_active: # وضع التكيف
        for i in scores: 
            if i not in hist[-4:]: scores[i] *= 1.8
    
    top_sorted = sorted(scores, key=scores.get, reverse=True)
    st.session_state.preds = top_sorted[:4]
    
    # اختيار التأمين الذكي
    meat_opts = [5, 6, 7, 8]
    ins_slot = next((m for m in meat_opts if m not in st.session_state.preds), 5)
    st.session_state.preds.append(ins_slot)
    
    mx = max(scores.values()) if scores.values() else 1
    probs = {i: int((scores[i]/mx)*100) for i in range(1, 9)}

# --- 5. الواجهة الرسومية ---
st.markdown("""<style>
    .main-card { background: #1a1a1a; border: 2px solid #39ff14; padding: 10px; border-radius: 15px; text-align: center; }
    .finance-bar { display: flex; justify-content: space-between; background: #000; padding: 10px; border-radius: 10px; border: 1px solid #444; margin-bottom: 10px; }
    .mini-counter { background: #111; border: 1px solid #444; padding: 5px; border-radius: 6px; text-align: center; color: white; font-size: 11px; }
</style>""", unsafe_allow_html=True)

# الإدارة والرهان
with st.expander("💰 الإعدادات المالية والهدف", expanded=(total_h >= 30)):
    c1, c2, c3 = st.columns(3)
    cap = c1.number_input("الرصيد", value=4400)
    bq = c2.number_input("رهان المربع", value=50)
    bi = c3.number_input("رهان التأمين", value=100)
    if st.button("تصفير 🔄"): 
        for k in keys: st.session_state[k] = [] if k in ['history', 'preds', 'action_hit'] else 0
        st.rerun()

# شريط الحالة المالية
st.markdown(f'<div class="finance-bar">'
            f'<div><small style="color:#777;">الرصيد</small><br><b>{cap + st.session_state.balance}</b></div>'
            f'<div><small style="color:#777;">الربح (بعد ج 30)</small><br><b style="color:{"#39ff14" if st.session_state.balance >= 0 else "#ff4b4b"}">{st.session_state.balance:+}</b></div>'
            f'<div><small style="color:#777;">الوضع</small><br><b style="color:#ffaa00;">{"نشط ✅" if total_h >= 30 else "إحماء ⏳"}</b></div></div>', unsafe_allow_html=True)

# المربع الذهبي وشريط القوة
st.markdown(f'<div class="main-card"><div style="color:#39ff14; font-size:10px; font-weight:bold;">🎯 المربع الذهبي والاحتمالات</div><div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:5px; margin-top:5px;">' + 
    "".join([f'<div style="background:#002200; border:1px solid #39ff14; padding:5px; border-radius:8px;">{SYMBOLS[c]}<div style="font-size:8px;">{probs[c]}%</div><div style="height:3px; background:#39ff14; width:{probs[c]}%; border-radius:2px;"></div></div>' for c in st.session_state.preds[:4]]) + 
    '</div></div>', unsafe_allow_html=True)

# التأمين وآخر 5
ins = st.session_state.preds[4]; last_5 = "".join([f'<span style="margin-left:4px;">{SYMBOLS[c]}</span>' for c in hist[-5:]])
st.markdown(f'<div style="display:flex; gap:8px; margin: 10px 0;"><div style="width:75px; background:#111; border:1px solid #00aaff; border-radius:10px; text-align:center;"><small style="color:#00aaff; font-size:9px;">🛡️ تأمين</small><br><span style="font-size:18px;">{SYMBOLS[ins]}</span></div><div style="flex:1; background:#111; border-radius:10px; border:1px solid #333; display:flex; align-items:center; justify-content:center; font-size:22px;">{last_5 if last_5 else "..."}</div></div>', unsafe_allow_html=True)

# أزرار الرموز
r1, r2 = st.columns(5), st.columns(4)
for i, c in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[c], key=f"r1_{c}"): register_result(c, bq, bi); st.rerun()
for i, c in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[c], key=f"r2_{c}"): register_result(c, bq, bi); st.rerun()

# الرادار السفلي
r10 = sum(1 for x in st.session_state.action_hit[-10:] if x)
scam = "آمن ✅" if r10 >= 4 or total_h < 10 else "غدر 🚨"
trnd = "مستقر ✅" if not shift_active else "تكيف 🌀"
sig = "STOP 🔴" if (scam == "غدر 🚨" or shift_active) else ("GO 🟢" if r10 >= 5 else "WAIT 🟡")

st.markdown(f'<div style="display:grid; grid-template-columns: repeat(4, 1fr); gap: 4px; margin-bottom: 8px;">'
            f'<div class="mini-counter">📡 {trnd}</div><div class="mini-counter">🚨 {scam}</div>'
            f'<div class="mini-counter">🏆 {st.session_state.max_streak}</div><div class="mini-counter">🚥 {sig}</div></div>', unsafe_allow_html=True)

# التراجع والعدادات (بجانب بعض)
c1, c2, c3, c4 = st.columns([0.8, 1, 1, 1])
if c1.button("↩️"): 
    if st.session_state.history: st.session_state.history.pop(); st.session_state.action_hit.pop(); st.rerun()
c2.markdown(f'<div class="mini-counter">🔄 جولة<br>{total_h}</div>', unsafe_allow_html=True)
c3.markdown(f'<div class="mini-counter" style="color:#39ff14;">✅ صح<br>{st.session_state.hits}</div>', unsafe_allow_html=True)
c4.markdown(f'<div class="mini-counter" style="color:#ff4b4b;">❌ خطأ<br>{st.session_state.misses}</div>', unsafe_allow_html=True)

# رادار النمط النهائي
p_msg, p_clr = ("نمط عميق ✅", "#39ff14") if any(hist[i:i+3] == hist[-3:] for i in range(len(hist)-4)) else ("تحليل مستمر", "#777")
st.markdown(f'<div style="background:#0a0a0a; border:1px dashed {p_clr}; padding:5px; border-radius:8px; font-size:10px; color:{p_clr}; text-align:center; font-weight:bold; margin-top:5px;">🔍 {p_msg} | 📉 {st.session_state.p_count} نمط محفوظ</div>', unsafe_allow_html=True)
