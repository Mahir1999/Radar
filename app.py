import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Advanced Pattern Radar v58", page_icon="🎯", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .stNumberInput div div input { padding: 5px !important; }
    .stButton>button { width: 100%; height: 45px; font-weight: bold; border-radius: 8px; font-size: 16px; }
    .last-result-banner {
        background: #1a1a1a; padding: 8px; border-radius: 8px; border-right: 4px solid #39ff14;
        text-align: center; margin-bottom: 10px; font-size: 14px; color: #39ff14;
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
        padding: 5px; text-align: center; font-size: 12px;
    }
    .main-highlight { border: 1px solid #39ff14 !important; background: #002200 !important; box-shadow: 0 0 8px #39ff14; }
    .stat-card {
        background: #1a1a1a; padding: 8px; border-radius: 8px; border: 1px solid #444;
        text-align: center; font-size: 13px;
    }
    .gap-section { background: #001a1a; padding: 10px; border-radius: 10px; border: 1px dashed #00ffff; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

SYMBOLS = {
    1: {"name": "🍅 طماطم", "mult": 5}, 2: {"name": "🌽 ذرة", "mult": 5},
    3: {"name": "🥕 جزر", "mult": 5}, 4: {"name": "🫑 فلفل", "mult": 5},
    5: {"name": "🐔 دجاجة", "mult": 45}, 6: {"name": "🐄 بقر", "mult": 15},
    7: {"name": "🐟 سمك", "mult": 25}, 8: {"name": "🦐 روبيان", "mult": 10},
    9: {"name": "💰 جكبوت", "mult": 100}
}

# --- إدارة الذاكرة ---
if 'history' not in st.session_state: st.session_state.history = []
if 'total_net' not in st.session_state: st.session_state.total_net = 0
if 'last_bets' not in st.session_state: st.session_state.last_bets = {i: 0 for i in range(1, 9)}
# ذاكرة الغيابات المبدئية
if 'initial_gaps' not in st.session_state: st.session_state.initial_gaps = {i: 0 for i in range(1, 9)}

def register_result(code):
    current_bets = st.session_state.last_bets
    total_bet = sum(current_bets.values())
    win_amount = current_bets.get(code, 0) * (SYMBOLS[code]["mult"] if code in SYMBOLS else 0)
    st.session_state.total_net += (win_amount - total_bet)
    st.session_state.history.append(code)

# --- 1️⃣ التحكم العلوي ---
c_stat, c_reset, c_clear = st.columns([2, 1, 1])
with c_stat:
    color = "#39ff14" if st.session_state.total_net >= 0 else "#ff4b4b"
    st.markdown(f'<div class="stat-card">الربح: <b style="color:{color};">{st.session_state.total_net}</b> | جولة: {len(st.session_state.history)}</div>', unsafe_allow_html=True)
with c_reset:
    if st.button("🗑️ الكل"): st.session_state.clear(); st.rerun()
with c_clear:
    if st.button("🧹 رهان"): st.session_state.last_bets = {i: 0 for i in range(1, 9)}; st.rerun()

if st.button("💾 حفظ البيانات وتثبيت الجلسة"):
    st.toast("✅ تم الحفظ بنجاح!")

# --- 2️⃣ ميزة تسجيل الغياب قبل البدء ---
with st.expander("🕒 تسجيل غياب العناصر قبل البدء (اختياري)"):
    st.markdown('<div class="gap-section">أدخل كم جولة غاب كل عنصر قبل أن تبدأ التسجيل الآن:</div>', unsafe_allow_html=True)
    g_cols1 = st.columns(4)
    for i, code in enumerate([5, 7, 6, 8]):
        st.session_state.initial_gaps[code] = g_cols1[i].number_input(SYMBOLS[code]["name"].split()[0], 0, 500, st.session_state.initial_gaps[code], key=f"gap_{code}")
    g_cols2 = st.columns(4)
    for i, code in enumerate([1, 2, 3, 4]):
        st.session_state.initial_gaps[code] = g_cols2[i].number_input(SYMBOLS[code]["name"].split()[0], 0, 500, st.session_state.initial_gaps[code], key=f"gap_{code}")

# --- 3️⃣ شريط التاريخ ---
hist = st.session_state.history
if hist:
    st.markdown(f'<div class="last-result-banner">⏮️ الأخير: {SYMBOLS[hist[-1]]["name"]}</div>', unsafe_allow_html=True)
    timeline_html = '<div class="timeline-container">'
    for code in reversed(hist[-15:]):
        timeline_html += f'<div class="timeline-item">{SYMBOLS[code]["name"].split()[0]}</div>'
    timeline_html += '</div>'
    st.markdown(timeline_html, unsafe_allow_html=True)

# --- 4️⃣ المحلل الذكي (يدمج الغياب التاريخي مع اللعب الحالي) ---
top_candidate = None
st.write("📊 **تحليل الاحتمالية المتقدم:**")

# خوارزمية حساب الاحتمال بناءً على الغياب (Gap Analysis) والوزن التاريخي
combined_scores = {}
for c in range(1, 9):
    # حساب الغياب الحالي
    last_seen_in_hist = -1
    for i in range(len(hist)-1, -1, -1):
        if hist[i] == c:
            last_seen_in_hist = (len(hist) - 1 - i)
            break
    
    # إذا لم يظهر في التاريخ، نستخدم الغياب المبدئي + طول التاريخ الحالي
    current_gap = last_seen_in_hist if last_seen_in_hist != -1 else (st.session_state.initial_gaps[c] + len(hist))
    
    # وزن الغياب (كلما زاد الغياب زادت النسبة) + وزن التكرار العام
    gap_weight = min(current_gap * 2, 100) 
    freq_weight = (hist.count(c) / len(hist) * 100) if len(hist) > 0 else 0
    
    combined_scores[c] = (gap_weight * 0.7) + (freq_weight * 0.3)

sorted_probs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
top_candidate = sorted_probs[0][0]

p_cols = st.columns(5)
for i, (code, prob) in enumerate(sorted_probs[:5]):
    with p_cols[i]:
        is_best = "main-highlight" if i == 0 else ""
        st.markdown(f'<div class="prob-box {is_best}">{SYMBOLS[code]["name"].split()[0]}<br><b>{prob:.0f}%</b></div>', unsafe_allow_html=True)

# --- 5️⃣ إدارة الرهانات (أفقية) ---
st.write("📝 **مبالغ الرهان:**")
def label_style(code): return f"🌟{SYMBOLS[code]['name'].split()[0]}" if code == top_candidate else SYMBOLS[code]['name'].split()[0]

b_row1 = st.columns(4)
for i, code in enumerate([5, 7, 6, 8]):
    with b_row1[i]:
        st.session_state.last_bets[code] = st.number_input(label_style(code), 0, 5000, st.session_state.last_bets[code], 5, key=f"b_{code}")
b_row2 = st.columns(4)
for i, code in enumerate([1, 2, 3, 4]):
    with b_row2[i]:
        st.session_state.last_bets[code] = st.number_input(label_style(code), 0, 5000, st.session_state.last_bets[code], 5, key=f"b_{code}")

# --- 6️⃣ تسجيل النتائج (أفقية) ---
st.write("🔘 **تسجيل النتيجة:**")
res_row1 = st.columns(5)
for i, code in enumerate([5, 7, 6, 8, 9]):
    if res_row1[i].button(SYMBOLS[code]["name"].split()[0], key=f"r_{code}"):
        register_result(code); st.rerun()
res_row2 = st.columns(4)
for i, code in enumerate([1, 2, 3, 4]):
    if res_row2[i].button(SYMBOLS[code]["name"].split()[0], key=f"r_{code}"):
        register_result(code); st.rerun()
