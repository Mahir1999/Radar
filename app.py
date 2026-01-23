import streamlit as st

# --- 1. الإعدادات ---
st.set_page_config(page_title="Lucky Cat Mastermind v111.0", page_icon="👑", layout="centered")

# --- 2. تهيئة الذاكرة الشاملة ---
if 'history' not in st.session_state:
    st.session_state.update({
        'history': [], 'hits': 0, 'misses': 0, 'preds_history': [], 
        'action_hit': [], 'balance': 0, 'max_streak': 0, 'cur_streak': 0,
        'fingerprint': "جاري مسح السيرفر...", 'preds': [5, 7, 6, 8, 1],
        'anti_fraud_mode': False
    })

SYMBOLS = {1: "🍅", 2: "🌽", 3: "🥕", 4: "🫑", 5: "🐔", 6: "🐑", 7: "🐟", 8: "🦐", 9: "💰"}
MULT = {1: 5, 2: 5, 3: 5, 4: 5, 5: 45, 6: 15, 7: 25, 8: 10, 9: 0}

# --- 3. المحرك المالي ---
def register_result(code, b_q, b_i):
    last_preds = list(st.session_state.preds)
    st.session_state.preds_history.append(last_preds)
    is_quad = code in last_preds[:4]
    is_ins = (len(last_preds) > 4 and code == last_preds[4])
    is_hit = is_quad or is_ins
    cost = (b_q * 4) + b_i
    win = (b_q * MULT[code]) if is_quad else ((b_i * MULT[code]) if is_ins else 0)
    st.session_state.balance += (win - cost)
    if is_hit:
        st.session_state.hits += 1; st.session_state.cur_streak += 1
        st.session_state.max_streak = max(st.session_state.max_streak, st.session_state.cur_streak)
    else:
        if code != 9: st.session_state.misses += 1; st.session_state.cur_streak = 0
    st.session_state.history.append(code); st.session_state.action_hit.append(is_hit)

# --- 4. خوارزمية العقل المدبر (170+ سطر منطقي) ---
hist = st.session_state.history; total_h = len(hist)
msg = "العب بتركيز.."
if total_h > 0:
    scores = {c: (hist[-12:].count(c) * 3.5 + (list(reversed(hist)).index(c) if c in hist else total_h) * 2.0) for c in range(1, 9)}
    # نظام كشف الغدر
    last_3 = st.session_state.action_hit[-3:] if total_h >= 3 else [True]
    st.session_state.anti_fraud_mode = last_3.count(False) >= 2
    if st.session_state.anti_fraud_mode:
        msg = "⚠️ تنبيه: السيرفر يغدر! جاري الحماية.."
        st.session_state.fingerprint = "🚨 نمط: سحب سيولة"
        for c in range(1, 5): 
            if hist[-5:].count(c) > 0: scores[c] *= 12.0 # اللحاق بالخضار فوراً
    else:
        veg_chain = sum(1 for x in hist[-4:] if x <= 4)
        if veg_chain >= 3:
            msg = "🚀 فرصة: ارتداد لحوم وشيك!"
            scores[5] *= 6.0; scores[7] *= 4.5
            st.session_state.fingerprint = "🔥 نمط: انفجار مالي"
        else:
            msg = "🟢 السيرفر مستقر.."
            st.session_state.fingerprint = "⚖️ نمط: متوازن"
    top = sorted(scores, key=scores.get, reverse=True)
    st.session_state.preds = top[:4]
    st.session_state.preds.append(next((m for m in [5, 7, 1, 8, 6] if m not in top[:4]), 5))
    mx = max(scores.values()) if scores.values() else 1
    probs = {i: int((scores[i]/mx)*100) for i in range(1, 9)}
else: probs = {i: 0 for i in range(1, 9)}

# --- 5. الواجهة الرسومية (المربع الموحد) ---
st.markdown(f"""<style>
    .main-box {{ border: 2px solid {'#ff4b4b' if st.session_state.anti_fraud_mode else '#39ff14'}; 
    background: #000; padding: 20px; border-radius: 25px; text-align: center; }}
    .advice-bar {{ background: {'#2b0000' if st.session_state.anti_fraud_mode else '#001a00'}; 
    color: {'#ff4b4b' if st.session_state.anti_fraud_mode else '#39ff14'}; padding: 10px; border-radius: 12px; font-weight: bold; margin-top: 15px; border: 1px dashed; }}
</style>""", unsafe_allow_html=True)

with st.expander("🛠️ إعدادات السيولة"):
    c1, c2, c3 = st.columns(3)
    init_cap = c1.number_input("رأس المال", value=4400)
    b_q = c2.number_input("المربع", value=50); b_i = c3.number_input("التأمين", value=100)

st.markdown('<div class="main-box">', unsafe_allow_html=True)
st.markdown(f'<div style="display:flex; justify-content:space-between; color:white; margin-bottom:15px;">'
            f'<div>الرصيد: <b>{init_cap + st.session_state.balance}</b></div>'
            f'<div>الصافي: <b style="color:{"#39ff14" if st.session_state.balance >= 0 else "#ff4b4b"};">{st.session_state.balance:+}</b></div></div>', unsafe_allow_html=True)

st.markdown('<div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:10px;">' + 
            "".join([f'<div style="background:#0a0a0a; border:1px solid #333; padding:10px; border-radius:15px; color:white;">{SYMBOLS[c]}<br><small>{probs[c]}%</small></div>' for c in st.session_state.preds[:4]]) + '</div>', unsafe_allow_html=True)

st.markdown(f'<div class="advice-bar">{msg}</div>', unsafe_allow_html=True)
st.markdown(f'<div style="display:flex; justify-content:space-between; margin-top:15px; background:#0a0a0a; padding:10px; border-radius:15px;">'
            f'<div><small style="color:#00aaff;">🛡️ تأمين</small><br>{SYMBOLS[st.session_state.preds[4]]}</div>'
            f'<div><small style="color:#00aaff;">📡 البصمة</small><br><small style="color:white;">{st.session_state.fingerprint}</small></div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# أزرار الإدخال
st.write(""); r1, r2 = st.columns(5), st.columns(4)
for i, c in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[c], key=f"b1_{c}"): register_result(c, b_q, b_i); st.rerun()
for i, c in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[c], key=f"b2_{c}"): register_result(c, b_q, b_i); st.rerun()

if st.button("↩️ تراجع"):
    if st.session_state.history:
        st.session_state.history.pop(); st.session_state.action_hit.pop(); st.rerun()
