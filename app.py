import streamlit as st

# --- 1. الإعدادات الأساسية (من v99.6 الأصلية) ---
st.set_page_config(page_title="Greedy AI v104.0", page_icon="💎", layout="centered")

# --- 2. تهيئة الذاكرة المفصلة (لضمان بقاء الأسطر كما هي) ---
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'hits' not in st.session_state:
    st.session_state['hits'] = 0
if 'misses' not in st.session_state:
    st.session_state['misses'] = 0
if 'cons_m' not in st.session_state:
    st.session_state['cons_m'] = 0
if 'p_count' not in st.session_state:
    st.session_state['p_count'] = 0
if 'preds' not in st.session_state:
    st.session_state['preds'] = [1, 2, 3, 4, 5]
if 'action_hit' not in st.session_state:
    st.session_state['action_hit'] = []
if 'max_streak' not in st.session_state:
    st.session_state['max_streak'] = 0
if 'cur_streak' not in st.session_state:
    st.session_state['cur_streak'] = 0
if 'balance' not in st.session_state:
    st.session_state['balance'] = 0
if 'target' not in st.session_state:
    st.session_state['target'] = 1000
if 'fingerprint' not in st.session_state:
    st.session_state['fingerprint'] = "تحليل البصمة..."

SYMBOLS = {1: "🍅", 2: "🌽", 3: "🥕", 4: "🫑", 5: "🐔", 6: "🐑", 7: "🐟", 8: "🦐", 9: "💰"}
MULT = {1: 5, 2: 5, 3: 5, 4: 5, 5: 45, 6: 15, 7: 25, 8: 10, 9: 0}

# --- 3. المحرك المفصل (Logic) ---
def register_result(code, bet_q, bet_i):
    h = st.session_state.history
    is_quad_hit = code in st.session_state.preds[:4]
    is_ins_hit = (len(st.session_state.preds) > 4 and code == st.session_state.preds[4])
    is_hit = is_quad_hit or is_ins_hit
    
    # ميزة البصمة (المضافة حديثاً بشكل مفصل)
    if len(h) > 10:
        meat_count = 0
        for x in h[-10:]:
            if x >= 5:
                meat_count += 1
        ratio = meat_count / 10
        if ratio > 0.6:
            st.session_state.fingerprint = "بصمة: لحوم مكثفة 🍖"
        elif ratio < 0.3:
            st.session_state.fingerprint = "بصمة: هدوء خضار 🥗"
        else:
            st.session_state.fingerprint = "بصمة: سيرفر متوازن ⚖️"

    # حساب الأنماط (البحث التاريخي المفصل)
    if len(h) >= 2:
        last_pair = [h[-1], code]
        for i in range(len(h) - 1):
            if h[i:i+2] == last_pair:
                st.session_state.p_count += 1
                break
    
    # تفعيل الحساب المالي بعد الجولة 30 (بشكل مفصل)
    if len(h) >= 30:
        total_bet = (bet_q * 4) + bet_i
        if is_quad_hit:
            win_amount = bet_q * MULT[code]
        elif is_ins_hit:
            win_amount = bet_i * MULT[code]
        else:
            win_amount = 0
        st.session_state.balance += (win_amount - total_bet)
    
    # تحديث العدادات الإحصائية
    if is_hit:
        st.session_state.hits += 1
        st.session_state.cur_streak += 1
        if st.session_state.cur_streak > st.session_state.max_streak:
            st.session_state.max_streak = st.session_state.cur_streak
        st.session_state.cons_m = 0
    else:
        if code != 9:
            st.session_state.misses += 1
            st.session_state.cons_m += 1
            st.session_state.cur_streak = 0
    
    st.session_state.history.append(code)
    st.session_state.action_hit.append(is_hit)

# --- 4. محرك التوقعات (v99.6 + الميزان الرقمي) ---
hist = st.session_state.history
total_h = len(hist)
shift_active = False
if len(st.session_state.action_hit) >= 3:
    if all(x is False for x in st.session_state.action_hit[-3:]) and total_h > 10:
        shift_active = True

if total_h == 0:
    st.session_state.preds = [1, 2, 3, 4, 5]
    probs = {i: 10 for i in range(1, 9)}
else:
    recent_15 = hist[-15:]
    scores = {}
    for c in range(1, 9):
        if c in hist:
            gap = list(reversed(hist)).index(c)
        else:
            gap = total_h
        scores[c] = (recent_15.count(c) * 0.7 + (gap * 0.3))
    
    # الميزان الرقمي المتوازن (المفصل)
    if hist[-1] >= 5:
        for i in range(5, 9):
            scores[i] = scores[i] * 0.6 
        for i in range(1, 5):
            scores[i] = scores[i] * 1.4 

    top_sorted = sorted(scores, key=scores.get, reverse=True)
    st.session_state.preds = top_sorted[:4]
    
    meat_opts = [5, 6, 7, 8]
    ins_slot = 5
    for m in meat_opts:
        if m not in st.session_state.preds:
            ins_slot = m
            break
    st.session_state.preds.append(ins_slot)
    
    mx = max(scores.values()) if scores.values() else 1
    probs = {i: int((scores[i]/mx)*100) for i in range(1, 9)}

# --- 5. الواجهة الرسومية (UI) ---
st.markdown("""<style>
    .main-box { background: #1a1a1a; border: 2px solid #39ff14; padding: 12px; border-radius: 15px; text-align: center; }
    .finance-bar { display: flex; justify-content: space-between; background: #000; padding: 8px; border-radius: 10px; border: 1px solid #444; margin: 8px 0; }
    .mini-card { background: #111; border: 1px solid #444; padding: 4px; border-radius: 6px; text-align: center; color: white; font-size: 11px; font-weight: bold; }
    .finger-tag { background: #001a33; color: #00aaff; border: 1px dashed #00aaff; border-radius: 5px; font-size: 10px; padding: 4px; margin-top: 5px; font-weight: bold; }
</style>""", unsafe_allow_html=True)

with st.expander("📊 الضبط المالي", expanded=(total_h < 31)):
    c1, c2, c3 = st.columns(3)
    capital = c1.number_input("المحفظة", value=4400)
    bet_q = c2.number_input("المربع", value=50)
    bet_i = c3.number_input("التأمين", value=100)

st.markdown(f'<div class="finance-bar">'
            f'<div><small style="color:#777;">الرصيد</small><br><b>{capital + st.session_state.balance}</b></div>'
            f'<div><small style="color:#777;">الربح الصافي</small><br><b style="color:{"#39ff14" if st.session_state.balance >= 0 else "#ff4b4b"}">{st.session_state.balance:+}</b></div>'
            f'<div><small style="color:#777;">الحالة</small><br><b style="color:#ffaa00;">{"نشط ✅" if total_h >= 30 else "إحماء ⏳"}</b></div></div>', unsafe_allow_html=True)

# المربع الذهبي
st.markdown(f'<div class="main-box"><div style="color:#39ff14; font-size:11px; font-weight:bold; margin-bottom:5px;">🎯 المربع الذهبي (Deep Analyze)</div>'
            f'<div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:6px;">' + 
            "".join([f'<div style="background:#002200; border:1px solid #39ff14; padding:5px; border-radius:8px;">{SYMBOLS[c]}<div style="font-size:8px;">{probs[c]}%</div></div>' for c in st.session_state.preds[:4]]) + 
            '</div>'
            f'<div class="finger-tag">{st.session_state.fingerprint}</div></div>', unsafe_allow_html=True)

# التأمين وآخر 5
ins = st.session_state.preds[4]
last_5 = ""
for c in hist[-5:]:
    last_5 += f'<span style="margin-left:4px;">{SYMBOLS[c]}</span>'

st.markdown(f'<div style="display:flex; gap:8px; margin: 10px 0;">'
            f'<div style="width:75px; background:#111; border:1px solid #00aaff; border-radius:10px; text-align:center;"><small style="color:#00aaff; font-size:9px;">🛡️ تأمين</small><br><span style="font-size:18px;">{SYMBOLS[ins]}</span></div>'
            f'<div style="flex:1; background:#111; border-radius:10px; border:1px solid #333; display:flex; align-items:center; justify-content:center; font-size:22px;">{last_5 if last_5 else "..."}</div></div>', unsafe_allow_html=True)

# الأزرار
r1, r2 = st.columns(5), st.columns(4)
for i, c in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[c], key=f"btn_{c}"):
        register_result(c, bet_q, bet_i)
        st.rerun()
for i, c in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[c], key=f"btn_{c}"):
        register_result(c, bet_q, bet_i)
        st.rerun()

# الرادار السفلي
hits_10 = sum(1 for x in st.session_state.action_hit[-10:] if x)
scam = "آمن ✅" if hits_10 >= 4 or total_h < 10 else "غدر 🚨"
trnd = "مستقر ✅" if not shift_active else "تكيف 🌀"
sig = "WAIT 🟡"
if scam == "غدر 🚨" or shift_active:
    sig = "STOP 🔴"
elif hits_10 >= 5:
    sig = "GO 🟢"

st.markdown(f'<div style="display:grid; grid-template-columns: repeat(4, 1fr); gap: 4px; margin-bottom: 8px;">'
            f'<div class="mini-card">📡 {trnd}</div><div class="mini-card">🚨 {scam}</div>'
            f'<div class="mini-card">🏆 {st.session_state.max_streak}</div><div class="mini-card">🚥 {sig}</div></div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns([0.8, 1, 1, 1])
if c1.button("↩️"): 
    if st.session_state.history:
        st.session_state.history.pop()
        st.session_state.action_hit.pop()
        st.rerun()
c2.markdown(f'<div class="mini-card">🔄 جولة<br>{total_h}</div>', unsafe_allow_html=True)
c3.markdown(f'<div class="mini-card" style="color:#39ff14;">✅ صح<br>{st.session_state.hits}</div>', unsafe_allow_html=True)
c4.markdown(f'<div class="mini-card" style="color:#ff4b4b;">❌ خطأ<br>{st.session_state.misses}</div>', unsafe_allow_html=True)

p_msg = "تحليل الذاكرة"
p_clr = "#777"
if any(hist[i:i+3] == hist[-3:] for i in range(len(hist)-4)):
    p_msg = "نمط مكتشف ✅"
    p_clr = "#39ff14"
st.markdown(f'<div style="background:#0a0a0a; border:1px dashed {p_clr}; padding:5px; border-radius:8px; font-size:10px; color:{p_clr}; text-align:center; font-weight:bold; margin-top:5px;">🔍 {p_msg} | 📉 {st.session_state.p_count} نمط محفوظ</div>', unsafe_allow_html=True)
