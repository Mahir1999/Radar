import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Ultimate Radar v51", page_icon="🚀", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 45px; font-weight: bold; border-radius: 8px; }
    .last-result-banner {
        background: #1a1a1a; padding: 10px; border-radius: 10px; border-left: 5px solid #ffaa00;
        text-align: center; margin-bottom: 5px; font-size: 16px; color: #ffaa00;
    }
    .timeline-container {
        display: flex; justify-content: center; gap: 5px; margin-bottom: 20px; padding: 10px;
        background: #0e1117; border-radius: 10px; border: 1px solid #333; overflow-x: auto;
    }
    .timeline-item {
        padding: 5px 10px; background: #262730; border-radius: 5px; border: 1px solid #444;
        font-size: 14px; min-width: 60px; text-align: center;
    }
    .prob-box { 
        background: #111; border: 1px solid #333; border-radius: 10px; 
        padding: 10px; text-align: center; margin-bottom: 10px;
    }
    .main-highlight { border: 2px solid #39ff14 !important; background: #002200 !important; box-shadow: 0 0 10px #39ff14; }
    .section-title { color: #39ff14; font-size: 18px; font-weight: bold; margin-top: 15px; border-bottom: 1px solid #333; padding-bottom: 5px; }
    .stat-card {
        background: #1a1a1a; padding: 15px; border-radius: 10px; border: 1px solid #444;
        text-align: center; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

SYMBOLS = {
    1: {"name": "🍅 طماطم", "mult": 5}, 2: {"name": "🌽 ذرة", "mult": 5},
    3: {"name": "🥕 جزر", "mult": 5}, 4: {"name": "🫑 فلفل", "mult": 5},
    5: {"name": "🐔 دجاجة", "mult": 45}, 6: {"name": "🐄 بقر", "mult": 15},
    7: {"name": "🐟 سمك", "mult": 25}, 8: {"name": "🦐 روبيان", "mult": 10},
    9: {"name": "💰 جاكبوت", "mult": 100}
}

# --- إدارة الذاكرة المستمرة ---
if 'history' not in st.session_state: st.session_state.history = []
if 'total_net' not in st.session_state: st.session_state.total_net = 0
# الذاكرة المسؤولة عن "ميزة الرهان الأخير"
if 'last_bets' not in st.session_state:
    st.session_state.last_bets = {i: 0 for i in range(1, 10)}

def register_result(code):
    current_bets = st.session_state.last_bets
    total_bet = sum(current_bets.values())
    win_amount = current_bets.get(code, 0) * SYMBOLS[code]["mult"]
    st.session_state.total_net += (win_amount - total_bet)
    st.session_state.history.append(code)

st.title("🚀 رادار الصياد المحترف v51.0")

# --- 1️⃣ لوحة التحكم ---
col_net, col_count, col_reset_all, col_reset_bets = st.columns([2, 1, 1, 1])
with col_net:
    color = "#39ff14" if st.session_state.total_net >= 0 else "#ff4b4b"
    st.markdown(f'<div class="stat-card">الربح الصافي<br><b style="color:{color}; font-size:22px;">{st.session_state.total_net}</b></div>', unsafe_allow_html=True)
with col_count:
    st.markdown(f'<div class="stat-card">الجولات<br><b style="font-size:22px;">{len(st.session_state.history)}</b></div>', unsafe_allow_html=True)
with col_reset_all:
    if st.button("🗑️ تصفير"): st.session_state.clear(); st.rerun()
with col_reset_bets:
    if st.button("🧹 مسح الرهان"): st.session_state.last_bets = {i: 0 for i in range(1, 10)}; st.rerun()

# --- 2️⃣ تتبع العناصر (العنصر الأخير + شريط زمني) ---
hist = st.session_state.history
if hist:
    st.markdown(f'<div class="last-result-banner">⏮️ العنصر الأخير: <b>{SYMBOLS[hist[-1]]["name"]}</b></div>', unsafe_allow_html=True)
    
    timeline_html = '<div class="timeline-container">'
    for code in reversed(hist[-10:]):
        timeline_html += f'<div class="timeline-item">{SYMBOLS[code]["name"].split()[0]}</div>'
    timeline_html += '</div>'
    st.markdown(timeline_html, unsafe_allow_html=True)

# --- 3️⃣ مصفوفة الاحتمالات ---
top_candidate = None
st.markdown('<div class="section-title">📊 مصفوفة الاحتمالات</div>', unsafe_allow_html=True)
if len(hist) >= 20:
    last = hist[-1]
    active_window = hist[-60:]
    next_options = [active_window[i+1] for i in range(len(active_window)-1) if active_window[i] == last]
    if next_options:
        cols = st.columns(3)
        sorted_probs = sorted([(code, (next_options.count(code)/len(next_options))*100) for code in set(next_options)], key=lambda x: x[1], reverse=True)
        top_candidate = sorted_probs[0][0]
        for i, (code, prob) in enumerate(sorted_probs):
            with cols[i % 3]:
                is_main = "main-highlight" if i == 0 else ""
                st.markdown(f'<div class="prob-box {is_main}">{SYMBOLS[code]["name"]}<br><b style="color:#39ff14;">{prob:.1f}%</b></div>', unsafe_allow_html=True)
else:
    st.warning(f"📡 بانتظار {20 - len(hist)} جولة للتحليل...")

# --- 4️⃣ إدارة الرهانات (هنا ميزة الرهان الأخير المستمر) ---
st.markdown('<div class="section-title">📝 مبالغ الرهان</div>', unsafe_allow_html=True)
def label_style(code): return f"🌟 {SYMBOLS[code]['name']}" if code == top_candidate else SYMBOLS[code]['name']

c1, c2, c3 = st.columns(3)
st.session_state.last_bets[5] = c1.number_input(label_style(5), 0, 5000, st.session_state.last_bets[5], 5)
st.session_state.last_bets[7] = c2.number_input(label_style(7), 0, 5000, st.session_state.last_bets[7], 5)
st.session_state.last_bets[6] = c3.number_input(label_style(6), 0, 5000, st.session_state.last_bets[6], 5)

c4, c5, c6 = st.columns(3)
st.session_state.last_bets[1] = c4.number_input(label_style(1), 0, 5000, st.session_state.last_bets[1], 5)
st.session_state.last_bets[2] = c5.number_input(label_style(2), 0, 5000, st.session_state.last_bets[2], 5)
st.session_state.last_bets[3] = c6.number_input(label_style(3), 0, 5000, st.session_state.last_bets[3], 5)

c7, c8, c9 = st.columns(3)
st.session_state.last_bets[4] = c7.number_input(label_style(4), 0, 5000, st.session_state.last_bets[4], 5)
st.session_state.last_bets[8] = c8.number_input(label_style(8), 0, 5000, st.session_state.last_bets[8], 5)
st.session_state.last_bets[9] = c9.number_input(label_style(9), 0, 5000, st.session_state.last_bets[9], 5)

# --- 5️⃣ أزرار النتائج ---
st.markdown('<div class="section-title">🔘 سجل النتيجة</div>', unsafe_allow_html=True)
r_big = st.columns(5)
for i, code in enumerate([5, 7, 6, 8, 9]):
    if r_big[i].button(SYMBOLS[code]["name"].split()[0]): register_result(code); st.rerun()

r_small = st.columns(4)
for i in range(1, 5):
    if r_small[i-1].button(SYMBOLS[i]["name"].split()[0]): register_result(i); st.rerun()
