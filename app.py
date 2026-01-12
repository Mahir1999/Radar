import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="AI Probability Matrix v43", page_icon="📊", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 45px; font-weight: bold; border-radius: 8px; }
    .prob-card { 
        background: #111; border: 1px solid #333; border-radius: 10px; 
        padding: 10px; text-align: center; margin-bottom: 5px;
    }
    .high-prob { border: 2px solid #39ff14 !important; background: #002200 !important; }
    .countdown-box { padding: 20px; background: #001a33; border: 2px dashed #0088ff; border-radius: 15px; text-align: center; }
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

st.title("📊 مصفوفة الاحتمالات الذكية v43.0")

hist = st.session_state.history
count = len(hist)

# --- 🛰️ تحليل مصفوفة الاحتمالات القادمة ---
if count >= 20:
    last = hist[-1]
    active_window = hist[-60:]
    # البحث عن كل ما ظهر بعد الرمز الأخير في التاريخ
    next_options = [active_window[i+1] for i in range(len(active_window)-1) if active_window[i] == last]
    
    st.subheader("🎯 توزيع احتمالات الجولة القادمة:")
    if next_options:
        cols = st.columns(3)
        # حساب التكرار لكل رمز متاح في الخيارات القادمة
        unique_next = set(next_options)
        sorted_probs = sorted(
            [(code, (next_options.count(code)/len(next_options))*100) for code in unique_next],
            key=lambda x: x[1], reverse=True
        )
        
        for i, (code, prob) in enumerate(sorted_probs):
            with cols[i % 3]:
                is_high = "high-prob" if i == 0 else ""
                st.markdown(f"""
                    <div class="prob-card {is_high}">
                        <span style="font-size:20px;">{SYMBOLS[code]['name']}</span><br>
                        <span style="color:#39ff14; font-weight:bold;">{prob:.1f}%</span>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("🔄 النمط الحالي جديد، لا توجد بيانات سابقة لهذا التسلسل.")
else:
    needed = 20 - count
    st.markdown(f'<div class="countdown-box">📡 جاري جمع البيانات الاستراتيجية... متبقي {needed} جولات</div>', unsafe_allow_html=True)
    st.progress(count / 20)

# --- لوحة التسجيل والرهان ---
st.divider()
with st.expander("📝 إدارة مبالغ الرهان"):
    c1, c2, c3 = st.columns(3)
    b5 = c1.number_input("🐔 دجاجة", 0, 1000, 0, 5)
    b7 = c2.number_input("🐟 سمك", 0, 1000, 0, 5)
    b_v = c3.number_input("خضروات", 0, 1000, 0, 5)
current_bets = {5:b5, 7:b7, 1:b_v/4, 2:b_v/4, 3:b_v/4, 4:b_v/4, 6:0, 8:0, 9:0}

st.write("### 🔘 سجل النتيجة فور ظهورها:")
r1 = st.columns(5)
for i, code in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[code]["name"].split()[0]): register_result(code, current_bets); st.rerun()

r2 = st.columns(4)
for i in range(1, 5):
    if r2[i-1].button(SYMBOLS[i]["name"].split()[0]): register_result(i, current_bets); st.rerun()

# الإحصائيات الجانبية
st.sidebar.metric("الأرباح", st.session_state.total_net)
if st.sidebar.button("🗑️ تصفير"):
    st.session_state.clear(); st.rerun()
