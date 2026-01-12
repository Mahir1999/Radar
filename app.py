import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Smart Visual Radar v46", page_icon="⚡", layout="centered")

# --- تنسيق احترافي مع ميزة التمييز اللوني ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 45px; font-weight: bold; border-radius: 8px; }
    .prob-box { 
        background: #111; border: 1px solid #333; border-radius: 10px; 
        padding: 10px; text-align: center; margin-bottom: 10px;
    }
    .main-highlight { border: 2px solid #39ff14 !important; background: #002200 !important; box-shadow: 0 0 10px #39ff14; }
    .section-title { color: #39ff14; font-size: 18px; font-weight: bold; margin-top: 20px; border-bottom: 1px solid #333; padding-bottom: 5px; }
    /* تمييز خانة الإدخال المرشحة */
    div[data-testid="stNumberInput"] { border-radius: 8px; transition: 0.5s; }
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

st.title("⚡ الرادار البصري الذكي v46.0")

# --- 1️⃣ تحليل الاحتمالات وتحديد العنصر الذهبي ---
hist = st.session_state.history
top_candidate = None

st.markdown('<div class="section-title">📊 توزيع احتمالات الجولة القادمة</div>', unsafe_allow_html=True)
if len(hist) >= 20:
    last = hist[-1]
    active_window = hist[-60:]
    next_options = [active_window[i+1] for i in range(len(active_window)-1) if active_window[i] == last]
    
    if next_options:
        cols = st.columns(3)
        sorted_probs = sorted(
            [(code, (next_options.count(code)/len(next_options))*100) for code in set(next_options)],
            key=lambda x: x[1], reverse=True
        )
        top_candidate = sorted_probs[0][0] # الرمز الأعلى احتمالاً
        
        for i, (code, prob) in enumerate(sorted_probs):
            with cols[i % 3]:
                is_main = "main-highlight" if i == 0 else ""
                st.markdown(f'<div class="prob-box {is_main}">{SYMBOLS[code]["name"]}<br><b style="color:#39ff14;">{prob:.1f}%</b></div>', unsafe_allow_html=True)
    else:
        st.info("🔄 بانتظار تكرار النمط الأخير...")
else:
    st.warning(f"📡 بانتظار جمع {20 - len(hist)} جولة إضافية...")

# --- 2️⃣ لوحة الرهان الذكية (تتفاعل مع الاحتمالات) ---
st.markdown('<div class="section-title">📝 إدارة الرهانات (الخانة الخضراء = رهان مرشح)</div>', unsafe_allow_html=True)

def label_style(code):
    return f"🌟 {SYMBOLS[code]['name']}" if code == top_candidate else SYMBOLS[code]['name']

with st.container():
    c1, c2, c3 = st.columns(3)
    b5 = c1.number_input(label_style(5), 0, 5000, 0, 5, key="b5", help="دجاجة x45")
    b7 = c2.number_input(label_style(7), 0, 5000, 0, 5, key="b7", help="سمك x25")
    b6 = c3.number_input(label_style(6), 0, 5000, 0, 5, key="b6", help="بقر x15")

    c4, c5, c6 = st.columns(3)
    b1 = c4.number_input(label_style(1), 0, 5000, 0, 5, key="b1")
    b2 = c5.number_input(label_style(2), 0, 5000, 0, 5, key="b2")
    b3 = c6.number_input(label_style(3), 0, 5000, 0, 5, key="b3")

    c7, c8, c9 = st.columns(3)
    b4 = c7.number_input(label_style(4), 0, 5000, 0, 5, key="b4")
    b8 = c8.number_input(label_style(8), 0, 5000, 0, 5, key="b8")
    b9 = c9.number_input(label_style(9), 0, 5000, 0, 5, key="b9")

current_bets = {1:b1, 2:b2, 3:b3, 4:b4, 5:b5, 6:b6, 7:b7, 8:b8, 9:b9}

# --- 3️⃣ أزرار النتائج ---
st.markdown('<div class="section-title">🔘 سجل النتيجة فوراً</div>', unsafe_allow_html=True)
r_big = st.columns(5)
for i, code in enumerate([5, 7, 6, 8, 9]):
    if r_big[i].button(SYMBOLS[code]["name"].split()[0]): 
        register_result(code, current_bets); st.rerun()

r_small = st.columns(4)
for i in range(1, 5):
    if r_small[i-1].button(SYMBOLS[i]["name"].split()[0]): 
        register_result(i, current_bets); st.rerun()

# --- الشريط الجانبي ---
st.sidebar.metric("صافي الربح", f"{st.session_state.total_net}")
if st.sidebar.button("🗑️ تصفير"):
    st.session_state.clear(); st.rerun()
