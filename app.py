import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="High Accuracy Radar v63", page_icon="📈", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .stNumberInput div div input { padding: 5px !important; }
    .stButton>button { width: 100%; height: 45px; font-weight: bold; border-radius: 8px; font-size: 16px; }
    .last-result-banner {
        background: #1a1a1a; padding: 10px; border-radius: 10px; border-right: 5px solid #39ff14;
        text-align: center; margin-bottom: 10px; color: #39ff14; font-weight: bold;
    }
    .timeline-container {
        display: flex; gap: 5px; margin-bottom: 15px; padding: 8px;
        background: #0e1117; border-radius: 8px; overflow-x: auto;
    }
    .timeline-item {
        padding: 4px 8px; background: #262730; border-radius: 4px; font-size: 12px; white-space: nowrap;
    }
    .prob-box { 
        background: #111; border: 1px solid #333; border-radius: 8px; 
        padding: 8px; text-align: center; font-size: 13px;
    }
    .main-highlight { border: 2px solid #39ff14 !important; background: #002200 !important; box-shadow: 0 0 10px #39ff14; }
    .stat-card {
        background: #1a1a1a; padding: 8px; border-radius: 8px; border: 1px solid #444;
        text-align: center; font-size: 14px;
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

# --- الهيدر العلوي ---
c_stat, c_reset, c_clear = st.columns([2, 1, 1])
with c_stat:
    color = "#39ff14" if st.session_state.total_net >= 0 else "#ff4b4b"
    st.markdown(f'<div class="stat-card">الربح: <b style="color:{color};">{st.session_state.total_net}</b> | جولة: <b>{len(st.session_state.history)}</b></div>', unsafe_allow_html=True)
with c_reset:
    if st.button("🗑️ الكل"): st.session_state.clear(); st.rerun()
with c_clear:
    if st.button("🧹 رهان"): st.session_state.last_bets = {i: 0 for i in range(1, 9)}; st.rerun()

# --- شريط الأحداث ---
hist = st.session_state.history
if hist:
    st.markdown(f'<div class="last-result-banner">⏮️ الأخير: {SYMBOLS[hist[-1]]["name"]}</div>', unsafe_allow_html=True)
    timeline_html = '<div class="timeline-container">'
    for code in reversed(hist[-15:]):
        timeline_html += f'<div class="timeline-item">{SYMBOLS[code]["name"].split()[0]}</div>'
    timeline_html += '</div>'
    st.markdown(timeline_html, unsafe_allow_html=True)

# --- المحلل الشامل المتفتح (v57 Logic مع تحسين العرض) ---
st.subheader("📊 توقعات النمط الحالي")
top_bet_candidates = []

if len(hist) >= 25:
    total_len = len(hist)
    global_counts = {c: hist.count(c) for c in set(hist)}
    recent_hist = hist[-25:]
    recent_counts = {c: recent_hist.count(c) for c in set(recent_hist)}
    
    combined_scores = {}
    for c in range(1, 9):
        # ميزان دقيق: 40% للتاريخ الكامل و 60% لآخر 25 جولة (الزخم الحالي)
        score = (global_counts.get(c, 0) / total_len) * 0.4 + (recent_counts.get(c, 0) / 25) * 0.6
        combined_scores[c] = score * 100
    
    sorted_probs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
    
    # سنعرض أي عنصر يتجاوز نسبة 10% لضمان عدم ضياع أي فرصة
    visible_probs = [item for item in sorted_probs if item[1] > 10]
    top_bet_candidates = [item[0] for item in visible_probs[:4]] # لأغراض التمييز في الخانات
    
    p_cols = st.columns(min(len(visible_probs), 5))
    for i, (code, prob) in enumerate(visible_probs[:5]):
        with p_cols[i]:
            # تمييز الخيار الأول فقط كقائد للنمط
            is_best = "main-highlight" if i == 0 else ""
            st.markdown(f'<div class="prob-box {is_best}">{SYMBOLS[code]["name"].split()[0]}<br><b>{prob:.0f}%</b></div>', unsafe_allow_html=True)
else:
    st.warning(f"📡 جمع البيانات مستمر... متبقي {25-len(hist)} جولة.")

# --- إدارة الرهانات (أفقية) ---
st.write("📝 **مبالغ الرهان:**")
def label_style(code):
    if len(top_bet_candidates) > 0 and code == top_bet_candidates[0]: return f"🔥 {SYMBOLS[code]['name'].split()[0]}"
    if code in top_bet_candidates: return f"⭐ {SYMBOLS[code]['name'].split()[0]}"
    return SYMBOLS[code]['name'].split()[0]

b_row1 = st.columns(4)
for i, code in enumerate([5, 7, 6, 8]):
    st.session_state.last_bets[code] = b_row1[i].number_input(label_style(code), 0, 5000, st.session_state.last_bets[code], 5, key=f"b_{code}")

b_row2 = st.columns(4)
for i, code in enumerate([1, 2, 3, 4]):
    st.session_state.last_bets[code] = b_row2[i].number_input(label_style(code), 0, 5000, st.session_state.last_bets[code], 5, key=f"b_{code}")

# --- تسجيل النتائج (أفقية) ---
st.write("🔘 **تسجيل النتيجة:**")
res_row1 = st.columns(5)
for i, code in enumerate([5, 7, 6, 8, 9]):
    if res_row1[i].button(SYMBOLS[code]["name"].split()[0], key=f"r_{code}"):
        register_result(code); st.rerun()

res_row2 = st.columns(4)
for i, code in enumerate([1, 2, 3, 4]):
    if res_row2[i].button(SYMBOLS[code]["name"].split()[0], key=f"r_{code}"):
        register_result(code); st.rerun()
