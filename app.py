import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Ultra Horizontal Radar v53", page_icon="🎯", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 40px; font-weight: bold; border-radius: 6px; }
    .last-result-banner {
        background: #1a1a1a; padding: 10px; border-radius: 10px; border-right: 5px solid #39ff14;
        text-align: center; margin-bottom: 10px; font-size: 18px; color: #39ff14;
    }
    .timeline-container {
        display: flex; justify-content: flex-start; gap: 8px; margin-bottom: 15px; padding: 10px;
        background: #0e1117; border-radius: 8px; border: 1px solid #333; overflow-x: auto;
    }
    .timeline-item {
        padding: 4px 12px; background: #262730; border-radius: 4px; border: 1px solid #444;
        font-size: 14px; white-space: nowrap;
    }
    .prob-box { 
        background: #111; border: 1px solid #333; border-radius: 8px; 
        padding: 8px; text-align: center;
    }
    .main-highlight { border: 2px solid #39ff14 !important; background: #002200 !important; }
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
    9: {"name": "💰 جاكبوت", "mult": 100}
}

# --- نظام حفظ البيانات ---
if 'history' not in st.session_state: st.session_state.history = []
if 'total_net' not in st.session_state: st.session_state.total_net = 0
if 'last_bets' not in st.session_state: st.session_state.last_bets = {i: 0 for i in range(1, 9)} # تم حذف 9 (الجاكبوت)

def register_result(code):
    current_bets = st.session_state.last_bets
    total_bet = sum(current_bets.values())
    win_amount = current_bets.get(code, 0) * SYMBOLS[code]["mult"]
    st.session_state.total_net += (win_amount - total_bet)
    st.session_state.history.append(code)

# --- الهيدر العلوي ---
c_head1, c_head2, c_head3, c_head4 = st.columns([2, 1, 1, 1])
with c_head1:
    color = "#39ff14" if st.session_state.total_net >= 0 else "#ff4b4b"
    st.markdown(f'<div class="stat-card">صافي الأرباح: <b style="color:{color};">{st.session_state.total_net}</b></div>', unsafe_allow_html=True)
with c_head2:
    st.markdown(f'<div class="stat-card">الجولة: <b>{len(st.session_state.history)}</b></div>', unsafe_allow_html=True)
with c_head3:
    if st.button("🗑️ تصفير الكل"): st.session_state.clear(); st.rerun()
with c_head4:
    if st.button("🧹 مسح الرهان"): 
        st.session_state.last_bets = {i: 0 for i in range(1, 9)}; st.rerun()

# --- تتبع التاريخ ---
hist = st.session_state.history
if hist:
    st.markdown(f'<div class="last-result-banner">⏮️ العنصر الأخير: {SYMBOLS[hist[-1]]["name"]}</div>', unsafe_allow_html=True)
    timeline_html = '<div class="timeline-container">'
    for code in reversed(hist[-15:]):
        timeline_html += f'<div class="timeline-item">{SYMBOLS[code]["name"].split()[0]}</div>'
    timeline_html += '</div>'
    st.markdown(timeline_html, unsafe_allow_html=True)

# --- مصفوفة الاحتمالات (تنسيق أفقي) ---
top_candidate = None
st.write("📊 **مصفوفة التوقعات القادمة:**")
if len(hist) >= 20:
    last_val = hist[-1]
    lookback = hist[-80:]
    next_options = [lookback[i+1] for i in range(len(lookback)-1) if lookback[i] == last_val]
    if next_options:
        sorted_probs = sorted([(c, (next_options.count(c)/len(next_options))*100) for c in set(next_options)], key=lambda x: x[1], reverse=True)
        top_candidate = sorted_probs[0][0]
        p_cols = st.columns(min(len(sorted_probs), 9))
        for i, (code, prob) in enumerate(sorted_probs[:9]):
            with p_cols[i]:
                is_best = "main-highlight" if i == 0 else ""
                st.markdown(f'<div class="prob-box {is_best}">{SYMBOLS[code]["name"].split()[0]}<br><b>{prob:.0f}%</b></div>', unsafe_allow_html=True)
else:
    st.info(f"📡 جاري تحليل البيانات... متبقي {20-len(hist)} جولة.")

# --- إدارة مبالغ الرهان (أفقي بالكامل بدون جاكبوت) ---
st.write("📝 **إدارة مبالغ الرهان (أفقي):**")
def label_style(code): return f"🌟 {SYMBOLS[code]['name'].split()[0]}" if code == top_candidate else SYMBOLS[code]['name'].split()[0]

bet_cols = st.columns(8)
bet_order = [5, 7, 6, 8, 1, 2, 3, 4] # استثناء 9 (الجاكبوت)
for i, code in enumerate(bet_order):
    with bet_cols[i]:
        st.session_state.last_bets[code] = st.number_input(label_style(code), 0, 5000, st.session_state.last_bets[code], 5, key=f"bet_{code}")

# --- تسجيل النتائج (أفقي بالكامل) ---
st.write("🔘 **سجل النتيجة فور ظهورها:**")
res_cols = st.columns(9)
res_order = [5, 7, 6, 8, 9, 1, 2, 3, 4]
for i, code in enumerate(res_order):
    if res_cols[i].button(SYMBOLS[code]["name"].split()[0], key=f"res_{code}"):
        register_result(code); st.rerun()
