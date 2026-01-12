import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Individual Bet Radar v44", page_icon="🎯", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 45px; font-weight: bold; border-radius: 8px; }
    .prob-card { 
        background: #111; border: 1px solid #333; border-radius: 10px; 
        padding: 10px; text-align: center; margin-bottom: 5px;
    }
    .high-prob { border: 2px solid #39ff14 !important; background: #002200 !important; }
    .countdown-box { padding: 20px; background: #001a33; border: 2px dashed #0088ff; border-radius: 15px; text-align: center; }
    .bet-label { font-size: 14px; font-weight: bold; color: #ccc; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

SYMBOLS = {
    1: {"name": "🍅 طماطم", "mult": 5}, 2: {"name": "🌽 ذرة", "mult": 5},
    3: {"name": "🥕 جزر", "mult": 5}, 4: {"name": "🫑 فلفل", "mult": 5},
    5: {"name": "🐔 دجاجة", "mult": 45}, 6: {"name": "🐄 بقر", "mult": 15},
    7: {"name": "🐟 سمك", "mult": 25}, 8: {"name": "🦐 روبيان", "mult": 10},
    9: {"name": "💰 جاكبوت", "mult": 100}
}

if 'history' not in st.session_state: st.session_state.history = []
if 'total_net' not in st.session_state: st.session_state.total_net = 0

def register_result(code, bets):
    total_bet = sum(bets.values())
    win_amount = bets.get(code, 0) * SYMBOLS[code]["mult"]
    st.session_state.total_net += (win_amount - total_bet)
    st.session_state.history.append(code)

st.title("🎯 رادار الإدارة الفردية v44.0")

# --- 🛰️ مصفوفة الاحتمالات ---
hist = st.session_state.history
if len(hist) >= 20:
    last = hist[-1]
    active_window = hist[-60:]
    next_options = [active_window[i+1] for i in range(len(active_window)-1) if active_window[i] == last]
    
    if next_options:
        st.subheader("🎯 احتمالات الجولة القادمة:")
        cols = st.columns(3)
        sorted_probs = sorted(
            [(code, (next_options.count(code)/len(next_options))*100) for code in set(next_options)],
            key=lambda x: x[1], reverse=True
        )
        for i, (code, prob) in enumerate(sorted_probs):
            with cols[i % 3]:
                is_high = "high-prob" if i == 0 else ""
                st.markdown(f'<div class="prob-card {is_high}">{SYMBOLS[code]["name"]}<br><b style="color:#39ff14;">{prob:.1f}%</b></div>', unsafe_allow_html=True)
else:
    needed = 20 - len(hist)
    st.markdown(f'<div class="countdown-box">📡 بانتظار {needed} جولة لتفعيل الرادار...</div>', unsafe_allow_html=True)

# --- 📝 لوحة الرهان الفردية (التعديل المطلوب) ---
st.divider()
st.subheader("📝 إدارة مبالغ الرهان لكل عنصر:")

with st.container():
    # الأهداف الكبرى
    c_big1, c_big2, c_big3 = st.columns(3)
    bet_5 = c_big1.number_input("🐔 دجاجة (x45)", 0, 5000, 0, 5)
    bet_7 = c_big2.number_input("🐟 سمك (x25)", 0, 5000, 0, 5)
    bet_6 = c_big3.number_input("🐄 بقر (x15)", 0, 5000, 0, 5)

    # الأهداف المتوسطة والخضروات
    c_med1, c_med2 = st.columns(2)
    bet_8 = c_med1.number_input("🦐 روبيان (x10)", 0, 5000, 0, 5)
    bet_9 = c_med2.number_input("💰 جاكبوت (x100)", 0, 5000, 0, 5)

    st.write("🥗 رهان الخضروات (x5):")
    v1, v2, v3, v4 = st.columns(4)
    bet_1 = v1.number_input("🍅 طماطم", 0, 5000, 0, 5)
    bet_2 = v2.number_input("🌽 ذرة", 0, 5000, 0, 5)
    bet_3 = v3.number_input("🥕 جزر", 0, 5000, 0, 5)
    bet_4 = v4.number_input("🫑 فلفل", 0, 5000, 0, 5)

# تجميع الرهانات في قاموس واحد للحساب
current_bets = {
    1: bet_1, 2: bet_2, 3: bet_3, 4: bet_4,
    5: bet_5, 6: bet_6, 7: bet_7, 8: bet_8, 9: bet_9
}

# --- 🔘 تسجيل النتائج ---
st.divider()
st.write("### 🔘 سجل النتيجة فور ظهورها:")
row1 = st.columns(5)
for i, code in enumerate([5, 7, 6, 8, 9]):
    if row1[i].button(SYMBOLS[code]["name"].split()[0]): 
        register_result(code, current_bets); st.rerun()

row2 = st.columns(4)
for i in range(1, 5):
    if row2[i-1].button(SYMBOLS[i]["name"].split()[0]): 
        register_result(i, current_bets); st.rerun()

# الإحصائيات الجانبية
st.sidebar.metric("صافي الربح الحالي", f"{st.session_state.total_net}")
st.sidebar.write(f"📊 عدد الجولات المسجلة: {len(hist)}")
if st.sidebar.button("🗑️ تصفير الجلسة"):
    st.session_state.clear(); st.rerun()
