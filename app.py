import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Auto-Counter Radar v60", page_icon="⏲️", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .stButton>button { width: 100%; height: 45px; font-weight: bold; border-radius: 8px; }
    .last-result-banner {
        background: #1a1a1a; padding: 10px; border-radius: 10px; border-right: 5px solid #39ff14;
        text-align: center; margin-bottom: 10px; color: #39ff14; font-weight: bold;
    }
    .gap-card {
        background: #0e1117; border: 1px solid #333; border-radius: 6px;
        padding: 5px; text-align: center; margin-bottom: 5px;
    }
    .prob-box { 
        background: #111; border: 1px solid #333; border-radius: 8px; 
        padding: 5px; text-align: center; font-size: 13px;
    }
    .main-highlight { border: 2px solid #39ff14 !important; background: #002200 !important; box-shadow: 0 0 10px #39ff14; }
    .stat-card {
        background: #1a1a1a; padding: 10px; border-radius: 8px; border: 1px solid #444;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

SYMBOLS = {
    1: {"name": "🍅 طماطم", "mult": 5}, 2: {"name": "🌽 ذرة", "mult": 5},
    3: {"name": "🥕 جزر", "mult": 5}, 4: {"name": "🫑 فلفل", "mult": 5},
    5: {"name": "🐔 دجاجة", "mult": 45}, 6: {"name": "🐄 بقر", "mult": 15},
    7: {"name": "🐟 سمك", "mult": 25}, 8: {"name": "🦐 روبيان", "mult": 10},
    9: {"name": "💰 جكبوت", "mult": 100}
}

# --- إدارة الذاكرة المستمرة ---
if 'history' not in st.session_state: st.session_state.history = []
if 'total_net' not in st.session_state: st.session_state.total_net = 0
if 'last_bets' not in st.session_state: st.session_state.last_bets = {i: 0 for i in range(1, 9)}
# عداد الغياب الذي يتفاعل تلقائياً
if 'current_gaps' not in st.session_state: st.session_state.current_gaps = {i: 0 for i in range(1, 9)}

def register_result(code):
    # 1. حساب الربح والخسارة
    current_bets = st.session_state.last_bets
    total_bet = sum(current_bets.values())
    win_amount = current_bets.get(code, 0) * (SYMBOLS[code]["mult"] if code in SYMBOLS else 0)
    st.session_state.total_net += (win_amount - total_bet)
    
    # 2. تحديث عدادات الغياب تلقائياً
    for i in st.session_state.current_gaps:
        if i == code:
            st.session_state.current_gaps[i] = 0  # تصفير غياب العنصر الذي ظهر
        else:
            st.session_state.current_gaps[i] += 1 # زيادة غياب بقية العناصر
            
    st.session_state.history.append(code)

# --- واجهة التحكم العلوي ---
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    color = "#39ff14" if st.session_state.total_net >= 0 else "#ff4b4b"
    st.markdown(f'<div class="stat-card">الربح الصافي: <b style="color:{color};">{st.session_state.total_net}</b></div>', unsafe_allow_html=True)
with c2:
    if st.button("🗑️ تصفير"): st.session_state.clear(); st.rerun()
with c3:
    if st.button("💾 حفظ"): st.toast("✅ تم الحفظ!"); 

# --- قسم إدخال وتعديل الغيابات (تلقائي/يدوي) ---
with st.expander("🕒 عدادات غياب العناصر (تتغير تلقائياً)"):
    st.write("يمكنك تعديل الأرقام يدوياً هنا قبل البدء، وستستمر بالعد تلقائياً مع كل جولة:")
    gc = st.columns(4)
    codes_order = [5, 7, 6, 8, 1, 2, 3, 4]
    for i, c in enumerate(codes_order):
        with gc[i % 4]:
            st.session_state.current_gaps[c] = st.number_input(f"{SYMBOLS[c]['name'].split()[0]} غائب", 0, 1000, st.session_state.current_gaps[c], key=f"gap_input_{c}")

# --- التحليل الذكي بناءً على العدادات الحالية ---
hist = st.session_state.history
st.write("📊 **التوقعات (بناءً على ضغط الغياب):**")

combined_scores = {}
for c in range(1, 9):
    gap = st.session_state.current_gaps[c]
    # معادلة الضغط: الغياب الطويل يرفع نسبة الثقة
    gap_score = min((gap / 35) * 70, 75) 
    # وزن التكرار التاريخي (25%)
    freq_score = (hist.count(c) / len(hist) * 25) if len(hist) > 0 else 10
    combined_scores[c] = gap_score + freq_score

sorted_res = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
top_c = sorted_res[0][0]

p_cols = st.columns(4)
for i, (code, score) in enumerate(sorted_res[:4]):
    with p_cols[i]:
        is_best = "main-highlight" if i == 0 else ""
        st.markdown(f'<div class="prob-box {is_best}">{SYMBOLS[code]["name"].split()[0]}<br>ثقة: <b>{score:.0f}%</b></div>', unsafe_allow_html=True)

# --- واجهة الرهان والنتائج ---
st.write("📝 **مبالغ الرهان:**")
def lbl(c): return f"🌟{SYMBOLS[c]['name'].split()[0]}" if c == top_c else SYMBOLS[c]['name'].split()[0]

br1 = st.columns(4)
for i, c in enumerate([5, 7, 6, 8]):
    st.session_state.last_bets[c] = br1[i].number_input(lbl(c), 0, 5000, st.session_state.last_bets[c], 5, key=f"bet_{c}")
br2 = st.columns(4)
for i, c in enumerate([1, 2, 3, 4]):
    st.session_state.last_bets[c] = br2[i].number_input(lbl(c), 0, 5000, st.session_state.last_bets[c], 5, key=f"bet_{c}")

st.write("🔘 **سجل النتيجة الآن:**")
rr1 = st.columns(5)
for i, c in enumerate([5, 7, 6, 8, 9]):
    if rr1[i].button(SYMBOLS[c]["name"].split()[0], key=f"res_{c}"): register_result(c); st.rerun()

rr2 = st.columns(4)
for i, c in enumerate([1, 2, 3, 4]):
    if rr2[i].button(SYMBOLS[c]["name"].split()[0], key=f"res_{c}"): register_result(c); st.rerun()

if hist:
    st.markdown(f'<div class="last-result-banner">⏮️ آخر عنصر ظهر: {SYMBOLS[hist[-1]]["name"]}</div>', unsafe_allow_html=True)
