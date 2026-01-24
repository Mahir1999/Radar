import streamlit as st

# --- 1. الإعدادات ---
st.set_page_config(page_title="Neural Processor v116", page_icon="🧠", layout="centered")

# --- 2. الذاكرة الفولاذية ---
if 'history' not in st.session_state:
    st.session_state.update({
        'history': [], 'balance': 0, 'hits': 0, 'misses': 0,
        'action_hit': [], 'preds': [1, 5, 7, 2, 8]
    })

SYMBOLS = {1: "🍅", 2: "🌽", 3: "🥕", 4: "🫑", 5: "🐔", 6: "🐑", 7: "🐟", 8: "🦐", 9: "💰"}
MULT = {1: 5, 2: 5, 3: 5, 4: 5, 5: 45, 6: 15, 7: 25, 8: 10, 9: 0}

# --- 3. المحرك المالي ---
def register_result(code, b_q, b_i):
    lp = list(st.session_state.preds)
    is_q, is_i = code in lp[:4], (len(lp) > 4 and code == lp[4])
    win = (b_q * MULT[code]) if is_q else ((b_i * MULT[code]) if is_i else 0)
    st.session_state.balance += (win - (b_q * 4 + b_i))
    st.session_state.history.append(code)
    st.session_state.action_hit.append(is_q or is_i)
    if is_q or is_i: st.session_state.hits += 1
    else: st.session_state.misses += 1

# --- 4. خوارزمية المعالج العصبي (Deep Logic) ---
hist = st.session_state.history; total_h = len(hist)
advice = "تحليل النمط..."
bg_color = "#0e1117"

if total_h > 0:
    # حساب الأوزان بناءً على آخر 10 جولات
    recent = hist[-10:]
    weights = {c: (recent.count(c) * 5 + (list(reversed(hist)).index(c) if c in hist else total_h)) for c in range(1, 9)}
    
    # تصحيح المسار الفوري
    if st.session_state.action_hit and not st.session_state.action_hit[-1]:
        advice = "⚠️ تصحيح مسار: السيرفر غير النمط"
        # إذا خسرنا، نميل لتغطية الرموز الأكثر تكراراً حالياً
        top = sorted(weights, key=weights.get, reverse=True)
    else:
        advice = "✅ النمط مستقر: تابع الهجوم"
        top = sorted(weights, key=weights.get, reverse=True)

    st.session_state.preds = top[:4]
    # التأمين الذكي: دائماً نضع الرمز الأعلى مضاعفاً المتبقي
    rem = [5, 7, 6, 8, 1, 2]
    st.session_state.preds.append(next(x for x in rem if x not in top[:4]))
else:
    probs = {i: 0 for i in range(1, 9)}

# --- 5. الواجهة الموحدة (Neuromorphic Box) ---
st.markdown(f"""<style>
    .neu-box {{
        border: 2px solid #00f2ff;
        background: #000000;
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.2);
    }}
    .metric-val {{ font-size: 20px; font-weight: bold; color: #00f2ff; }}
</style>""", unsafe_allow_html=True)

with st.expander("⚙️ التحكم المالي"):
    bq = st.number_input("رهان المربع", value=50)
    bi = st.number_input("رهان التأمين", value=100)

st.markdown('<div class="neu-box">', unsafe_allow_html=True)
st.markdown(f'<div style="display:flex; justify-content:space-between; margin-bottom:15px;">'
            f'<div>رصيدك<br><span class="metric-val">{4400+st.session_state.balance}</span></div>'
            f'<div>الصافي<br><span class="metric-val" style="color:{"#00f2ff" if st.session_state.balance >=0 else "#ff4b4b"};">{st.session_state.balance:+}</span></div>'
            f'</div>', unsafe_allow_html=True)

# التوقعات (المربع الذهبي)
st.markdown('<div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:10px; margin-bottom:15px;">' + 
            "".join([f'<div style="background:#111; border:1px solid #333; padding:10px; border-radius:12px; font-size:25px;">{SYMBOLS[c]}</div>' for c in st.session_state.preds[:4]]) + '</div>', unsafe_allow_html=True)

st.markdown(f'<div style="background:#00f2ff11; border:1px dashed #00f2ff; padding:8px; border-radius:10px; color:#00f2ff; font-size:14px;">{advice}</div>', unsafe_allow_html=True)
st.markdown(f'<div style="margin-top:10px; font-size:11px; color:#666;">🛡️ تأمين: {SYMBOLS[st.session_state.preds[4]]} | آخر النتائج: {" ".join([SYMBOLS[x] for x in hist[-5:]])}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# الأزرار
st.write(""); c1, c2 = st.columns(5), st.columns(4)
for i, code in enumerate([5, 7, 6, 8, 9]):
    if c1[i].button(SYMBOLS[code], key=f"n1_{code}"): register_result(code, bq, bi); st.rerun()
for i, code in enumerate([1, 2, 3, 4]):
    if c2[i].button(SYMBOLS[code], key=f"n2_{code}"): register_result(code, bq, bi); st.rerun()
