import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Pro Strategy Radar v62", page_icon="🛡️", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .stNumberInput div div input { padding: 5px !important; }
    .stButton>button { width: 100%; height: 45px; font-weight: bold; border-radius: 8px; font-size: 16px; }
    .last-result-banner {
        background: #1a1a1a; padding: 10px; border-radius: 10px; border-right: 5px solid #39ff14;
        text-align: center; margin-bottom: 10px; font-size: 14px; color: #39ff14; font-weight: bold;
    }
    .timeline-container {
        display: flex; gap: 5px; margin-bottom: 15px; padding: 8px;
        background: #0e1117; border-radius: 8px; overflow-x: auto;
    }
    .timeline-item {
        padding: 4px 8px; background: #262730; border-radius: 4px; font-size: 12px; white-space: nowrap;
    }
    .bet-box {
        background: #002200; border: 1px solid #39ff14; border-radius: 10px;
        padding: 10px; text-align: center; color: white;
    }
    .insurance-box {
        background: #221100; border: 1px solid #ffaa00; border-radius: 10px;
        padding: 10px; text-align: center; color: white;
    }
    .stat-card {
        background: #1a1a1a; padding: 8px; border-radius: 8px; border: 1px solid #444;
        text-align: center; font-size: 13px;
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

if 'history' not in st.session_state: st.session_state.history = []
if 'total_net' not in st.session_state: st.session_state.total_net = 0
if 'last_bets' not in st.session_state: st.session_state.last_bets = {i: 0 for i in range(1, 9)}

def register_result(code):
    current_bets = st.session_state.last_bets
    total_bet = sum(current_bets.values())
    win_amount = current_bets.get(code, 0) * SYMBOLS[code]["mult"]
    st.session_state.total_net += (win_amount - total_bet)
    st.session_state.history.append(code)

# --- التحكم العلوي ---
c_stat, c_reset, c_clear = st.columns([2, 1, 1])
with c_stat:
    color = "#39ff14" if st.session_state.total_net >= 0 else "#ff4b4b"
    st.markdown(f'<div class="stat-card">صافي الربح: <b style="color:{color};">{st.session_state.total_net}</b> | الجولة: <b>{len(st.session_state.history)}</b></div>', unsafe_allow_html=True)
with c_reset:
    if st.button("🗑️ الكل"): st.session_state.clear(); st.rerun()
with c_clear:
    if st.button("🧹 رهان"): st.session_state.last_bets = {i: 0 for i in range(1, 9)}; st.rerun()

# --- شريط التاريخ ---
hist = st.session_state.history
if hist:
    st.markdown(f'<div class="last-result-banner">⏮️ العنصر الأخير: {SYMBOLS[hist[-1]]["name"]}</div>', unsafe_allow_html=True)
    timeline_html = '<div class="timeline-container">'
    for code in reversed(hist[-15:]):
        timeline_html += f'<div class="timeline-item">{SYMBOLS[code]["name"].split()[0]}</div>'
    timeline_html += '</div>'
    st.markdown(timeline_html, unsafe_allow_html=True)

# --- محرك التوقعات (4 عناصر + 1 تأمين) ---
st.subheader("💡 خيارات الرهان المقترحة")
primary_bets = []
insurance_bet = None

if len(hist) >= 25:
    total_len = len(hist)
    global_counts = {c: hist.count(c) for c in set(hist)}
    recent_hist = hist[-25:]
    recent_counts = {c: recent_hist.count(c) for c in set(recent_hist)}
    
    scores = {}
    for c in range(1, 9):
        score = (global_counts.get(c, 0) / total_len) * 0.4 + (recent_counts.get(c, 0) / 25) * 0.6
        scores[c] = score * 100
    
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # تحديد الـ 4 الأساسية
    primary_bets = [item[0] for item in sorted_scores[:4]]
    # تحديد عنصر التأمين (الخامس) إذا كانت نسبته معقولة
    if len(sorted_scores) >= 5:
        insurance_bet = sorted_scores[4][0]

    # عرض الخيارات الأساسية (أفقي)
    cols = st.columns(4)
    for i, code in enumerate(primary_bets):
        with cols[i]:
            st.markdown(f'<div class="bet-box"><small>أساسي {i+1}</small><br><b>{SYMBOLS[code]["name"].split()[0]}</b></div>', unsafe_allow_html=True)
    
    # عرض عنصر التأمين
    if insurance_bet:
        st.markdown(f'<div class="insurance-box">⚠️ عنصر للتأمين (نسبة منخفضة): <b>{SYMBOLS[insurance_bet]["name"]}</b></div>', unsafe_allow_html=True)
else:
    st.warning(f"📡 جاري التحليل... متبقي {25-len(hist)} جولة.")

# --- إدارة الرهانات ---
st.write("📝 **توزيع مبالغ الرهان:**")
def get_label(code):
    if code in primary_bets: return f"✅ {SYMBOLS[code]['name'].split()[0]}"
    if code == insurance_bet: return f"🛡️ {SYMBOLS[code]['name'].split()[0]}"
    return SYMBOLS[code]['name'].split()[0]

b_row1 = st.columns(4)
for i, code in enumerate([5, 7, 6, 8]):
    st.session_state.last_bets[code] = b_row1[i].number_input(get_label(code), 0, 5000, st.session_state.last_bets[code], 5, key=f"bet_{code}")

b_row2 = st.columns(4)
for i, code in enumerate([1, 2, 3, 4]):
    st.session_state.last_bets[code] = b_row2[i].number_input(get_label(code), 0, 5000, st.session_state.last_bets[code], 5, key=f"bet_{code}")

# --- تسجيل النتائج ---
st.write("🔘 **سجل النتيجة:**")
res_row1 = st.columns(5)
for i, code in enumerate([5, 7, 6, 8, 9]):
    if res_row1[i].button(SYMBOLS[code]["name"].split()[0], key=f"r_{code}"):
        register_result(code); st.rerun()

res_row2 = st.columns(4)
for i, code in enumerate([1, 2, 3, 4]):
    if res_row2[i].button(SYMBOLS[code]["name"].split()[0], key=f"r_{code}"):
        register_result(code); st.rerun()
