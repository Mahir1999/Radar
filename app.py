import streamlit as st

# --- 1. الإعدادات ---
st.set_page_config(page_title="The Predator v115.0", page_icon="⚡", layout="centered")

# --- 2. الذاكرة الفولاذية ---
if 'history' not in st.session_state:
    st.session_state.update({
        'history': [], 'balance': 0, 'hits': 0, 'misses': 0,
        'action_hit': [], 'preds': [1, 2, 3, 5, 8], 'preds_history': [],
        'power_level': "Low"
    })

SYMBOLS = {1: "🍅", 2: "🌽", 3: "🥕", 4: "🫑", 5: "🐔", 6: "🐑", 7: "🐟", 8: "🦐", 9: "💰"}
MULT = {1: 5, 2: 5, 3: 5, 4: 5, 5: 45, 6: 15, 7: 25, 8: 10, 9: 0}

# --- 3. المحرك المالي ---
def register_result(code, b_q, b_i):
    lp = list(st.session_state.preds)
    st.session_state.preds_history.append(lp)
    is_q, is_i = code in lp[:4], (len(lp) > 4 and code == lp[4])
    win = (b_q * MULT[code]) if is_q else ((b_i * MULT[code]) if is_i else 0)
    st.session_state.balance += (win - (b_q * 4 + b_i))
    st.session_state.history.append(code)
    st.session_state.action_hit.append(is_q or is_i)

# --- 4. خوارزمية "المفترس" (Logic v115) ---
hist = st.session_state.history; total_h = len(hist)
status_msg = "جاري تعقب السيرفر..."
color_theme = "#39ff14"

if total_h >= 3:
    last_5 = hist[-5:]
    # كشف "موجة التكرار" (الخضار المتواصل)
    veg_count = sum(1 for x in last_5 if x <= 4)
    
    if veg_count >= 4:
        # السيرفر في حالة "تنشيف"، لا تعانده!
        status_msg = "⚠️ موجة خضار عنيفة: اتبع السيرفر للحماية"
        color_theme = "#00aaff" # لون الحماية
        scores = {c: (last_5.count(c) * 50) for c in range(1, 9)}
        st.session_state.preds = [1, 2, 3, 4] # المربع الذهبي خضار بالكامل
        st.session_state.preds.append(5) # التأمين دجاجة للطوارئ
    else:
        # السيرفر بدأ يفتح، وقت الهجوم
        status_msg = "🔥 السيرفر يفتح: هجوم على اللحوم والمضاعفات"
        color_theme = "#ff00ff" # لون الهجوم
        scores = {c: (list(reversed(hist)).index(c) if c in hist else total_h) * 2 for c in range(1, 9)}
        top = sorted(scores, key=scores.get, reverse=True)
        st.session_state.preds = top[:4]
        st.session_state.preds.append(next((m for m in [1, 8, 5] if m not in top[:4]), 1))
else:
    probs = {i: 0 for i in range(1, 9)}

# --- 5. الواجهة (المربع الموحد - Predator UI) ---
st.markdown(f"""<style>
    .predator-box {{
        border: 3px solid {color_theme};
        background: #000;
        padding: 20px;
        border-radius: 30px;
        text-align: center;
        box-shadow: 0 0 25px {color_theme}44;
    }}
    .stat-text {{ font-size: 14px; color: #888; }}
    .highlight {{ font-size: 22px; font-weight: bold; color: white; }}
</style>""", unsafe_allow_html=True)

with st.expander("💰 تحكم السيولة"):
    bq = st.number_input("رهان المربع", value=50)
    bi = st.number_input("رهان التأمين", value=100)

st.markdown(f'<div class="predator-box">', unsafe_allow_html=True)
st.markdown(f'<div style="display:flex; justify-content:space-between;">'
            f'<div class="stat-text">الرصيد الكلي<br><span class="highlight">{4400+st.session_state.balance}</span></div>'
            f'<div class="stat-text">صافي الربح<br><span class="highlight" style="color:{color_theme};">{st.session_state.balance:+}</span></div>'
            f'</div>', unsafe_allow_html=True)

# المربع الذهبي (التوقعات)
st.markdown('<div style="margin: 20px 0; display:grid; grid-template-columns: repeat(4, 1fr); gap:10px;">' + 
            "".join([f'<div style="background:#111; border:1px solid {color_theme}; padding:15px; border-radius:15px; font-size:25px;">{SYMBOLS[c]}</div>' for c in st.session_state.preds[:4]]) + '</div>', unsafe_allow_html=True)

st.markdown(f'<div style="background:{color_theme}22; border:1px dashed {color_theme}; padding:10px; border-radius:12px; font-weight:bold; color:{color_theme};">{status_msg}</div>', unsafe_allow_html=True)

# الرادار السفلي
st.markdown(f'<div style="margin-top:15px; display:flex; justify-content:space-around; font-size:12px; color:#555;">'
            f'<div>🛡️ التأمين: {SYMBOLS[st.session_state.preds[4]]}</div>'
            f'<div>📊 النمط: {len(st.session_state.history)} جولات</div>'
            f'<div>⚡ القوة: {st.session_state.cur_streak}</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# أزرار الإدخال
st.write(""); c1, c2 = st.columns(5), st.columns(4)
for i, code in enumerate([5, 7, 6, 8, 9]):
    if c1[i].button(SYMBOLS[code], key=f"p1_{code}"): register_result(code, bq, bi); st.rerun()
for i, code in enumerate([1, 2, 3, 4]):
    if c2[i].button(SYMBOLS[code], key=f"p2_{code}"): register_result(code, bq, bi); st.rerun()

if st.button("↩️ تصحيح آخر خطأ"):
    if st.session_state.history:
        st.session_state.history.pop(); st.rerun()
