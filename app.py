import streamlit as st

# --- 1. الإعدادات والواجهة ---
st.set_page_config(page_title="Lucky Cat Radar PRO", page_icon="🎯", layout="centered")

# --- 2. تهيئة الذاكرة (Persistence) ---
if 'history' not in st.session_state:
    st.session_state.update({
        'history': [], 'hits': 0, 'misses': 0, 'preds_history': [], 
        'action_hit': [], 'balance': 0, 'cur_streak': 0, 'max_streak': 0,
        'fingerprint': "جاري تحليل الموجة...", 'preds': [5, 7, 6, 8, 1],
        'anti_fraud': False
    })

SYMBOLS = {1: "🍅", 2: "🌽", 3: "🥕", 4: "🫑", 5: "🐔", 6: "🐑", 7: "🐟", 8: "🦐", 9: "💰"}
MULT = {1: 5, 2: 5, 3: 5, 4: 5, 5: 45, 6: 15, 7: 25, 8: 10, 9: 0}

# --- 3. المحرك المالي ---
def register_result(code, b_q, b_i):
    last_preds = list(st.session_state.preds)
    st.session_state.preds_history.append(last_preds)
    is_q, is_i = code in last_preds[:4], (len(last_preds) > 4 and code == last_preds[4])
    cost = (b_q * 4) + b_i
    win = (b_q * MULT[code]) if is_q else ((b_i * MULT[code]) if is_i else 0)
    st.session_state.balance += (win - cost)
    if is_q or is_i:
        st.session_state.hits += 1; st.session_state.cur_streak += 1
        st.session_state.max_streak = max(st.session_state.max_streak, st.session_state.cur_streak)
    else:
        if code != 9: st.session_state.misses += 1; st.session_state.cur_streak = 0
    st.session_state.history.append(code); st.session_state.action_hit.append(is_q or is_i)

# --- 4. خوارزمية الرادار (Logic Engine) ---
hist = st.session_state.history; total_h = len(hist)
advice = "بانتظار البيانات.."
gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 9)}

if total_h > 0:
    # حساب النقاط بناءً على "البصمة الزمنية"
    scores = {c: (gaps[c] * 2.5 + hist[-15:].count(c) * 4.0) for c in range(1, 9)}
    
    # فحص "الغدر": خسارتين متتاليتين تحول النظام للحذر
    last_hits = st.session_state.action_hit[-2:] if total_h >= 2 else [True]
    st.session_state.anti_fraud = last_hits.count(False) >= 2
    
    if st.session_state.anti_fraud:
        advice = "⚠️ السيرفر يغدر! مربع (حماية) مكرر"
        for c in range(1, 5): scores[c] *= 10.0 # اللحاق بالخضار
    else:
        # كشف "الاستحقاق العالي"
        if gaps[5] > 40 or gaps[7] > 30:
            advice = "🔥 استحقاق عالي! ركز على اللحوم"
            scores[5] *= 5.0; scores[7] *= 4.0
        else:
            advice = "🟢 وضع مستقر: العب بتوازن"

    top = sorted(scores, key=scores.get, reverse=True)
    st.session_state.preds = top[:4]
    st.session_state.preds.append(next((m for m in [1, 8, 5, 7] if m not in top[:4]), 1))
    mx = max(scores.values()) if scores.values() else 1
    probs = {i: int((scores[i]/mx)*100) for i in range(1, 9)}
else: probs = {i: 0 for i in range(1, 9)}

# --- 5. واجهة المستخدم (CSS الموحد) ---
st.markdown(f"""<style>
    .master-box {{ border: 2px solid {'#ff4b4b' if st.session_state.anti_fraud else '#39ff14'}; 
    background: #000; padding: 20px; border-radius: 20px; text-align: center; color: white; }}
    .gap-card {{ background: #111; border: 1px solid #333; padding: 5px; border-radius: 8px; font-size: 11px; }}
</style>""", unsafe_allow_html=True)

with st.expander("💰 المبالغ والسيولة"):
    c1, c2, c3 = st.columns(3)
    wallet = c1.number_input("المحفظة", value=4400)
    bq = c2.number_input("المربع", value=50); bi = c3.number_input("التأمين", value=100)

st.markdown('<div class="master-box">', unsafe_allow_html=True)
st.markdown(f'<div style="display:flex; justify-content:space-between; margin-bottom:15px;">'
            f'<div>الرصيد: {wallet + st.session_state.balance}</div>'
            f'<div style="color:{"#39ff14" if st.session_state.balance >=0 else "#ff4b4b"};">الصافي: {st.session_state.balance:+}</div></div>', unsafe_allow_html=True)

# المربع الذهبي
st.markdown('<div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:10px;">' + 
            "".join([f'<div style="background:#0a0a0a; border:1px solid #39ff14; padding:10px; border-radius:12px;">{SYMBOLS[c]}<br>{probs[c]}%</div>' for c in st.session_state.preds[:4]]) + '</div>', unsafe_allow_html=True)

st.markdown(f'<div style="margin-top:15px; padding:10px; background:#222; border-radius:10px; font-weight:bold; color:{"#ff4b4b" if st.session_state.anti_fraud else "#39ff14"};">{advice}</div>', unsafe_allow_html=True)

# رادار الاستحقاق (أهم إضافة)
st.markdown('<div style="margin-top:15px; display:grid; grid-template-columns: repeat(4, 1fr); gap:5px;">' + 
            "".join([f'<div class="gap-card"><b>{SYMBOLS[c]}</b><br>{gaps[c]} جولة</div>' for c in [5, 7, 6, 8]]) + '</div>', unsafe_allow_html=True)

st.markdown(f'<div style="margin-top:10px; font-size:12px; color:#00aaff;">🛡️ تأمين: {SYMBOLS[st.session_state.preds[4]]} | سجل: {" ".join([SYMBOLS[x] for x in hist[-5:]])}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# أزرار الإدخال
st.write(""); r1, r2 = st.columns(5), st.columns(4)
for i, c in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[c], key=f"f1_{c}"): register_result(c, bq, bi); st.rerun()
for i, c in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[c], key=f"f2_{c}"): register_result(c, bq, bi); st.rerun()
