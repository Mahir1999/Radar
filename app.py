import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Heat Radar v65", page_icon="🔥", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .stButton>button { width: 100%; height: 48px; font-weight: bold; border-radius: 10px; }
    .last-result-banner {
        background: #1a1a1a; padding: 10px; border-radius: 10px; border-right: 5px solid #39ff14;
        text-align: center; margin-bottom: 10px; color: #39ff14; font-weight: bold;
    }
    .pulse-card {
        background: #0e1117; border: 1px solid #333; border-radius: 12px;
        padding: 12px; margin-bottom: 15px; border-left: 4px solid #00ffff;
    }
    .prob-box { 
        background: #111; border: 1px solid #333; border-radius: 8px; 
        padding: 10px; text-align: center; font-size: 14px;
    }
    .main-highlight { border: 2px solid #39ff14 !important; background: #002200 !important; box-shadow: 0 0 10px #39ff14; }
    .hot-text { color: #ff4b4b; font-weight: bold; }
    .cold-text { color: #00ffff; font-weight: bold; }
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

def register_result(code):
    st.session_state.history.append(code)

# --- التحكم العلوي ---
c_stat, c_reset = st.columns([3, 1])
with c_stat:
    st.info(f"📊 الجولات المسجلة: {len(st.session_state.history)}")
with c_reset:
    if st.button("🗑️ مسح"): st.session_state.clear(); st.rerun()

hist = st.session_state.history

# --- شريط النتائج الأخير ---
if hist:
    st.markdown(f'<div class="last-result-banner">⏮️ الأخير: {SYMBOLS[hist[-1]]["name"]}</div>', unsafe_allow_html=True)

# --- رادار نبض السيرفر (Server Pulse) ---
if len(hist) >= 10:
    recent_10 = hist[-10:]
    # حساب العنصر الساخن (الأكثر تكراراً مؤخراً)
    hot_symbol = max(set(recent_10), key=recent_10.count)
    
    # حساب العنصر المتأخر (أطول فترة غياب)
    gaps = {}
    for c in range(1, 9):
        try:
            gap = list(reversed(hist)).index(c)
            gaps[c] = gap
        except ValueError:
            gaps[c] = len(hist)
    cold_symbol = max(gaps, key=gaps.get)

    st.markdown(f"""
    <div class="pulse-card">
        🚀 <b>نبض السيرفر:</b><br>
        • عنصر ساخن حالياً: <span class="hot-text">{SYMBOLS[hot_symbol]['name']}</span> (تكرار عالي)<br>
        • عنصر متأخر جداً: <span class="cold-text">{SYMBOLS[cold_symbol]['name']}</span> (غائب منذ {gaps[cold_symbol]} جولة)
    </div>
    """, unsafe_allow_html=True)

# --- محرك التحليل الذكي ---
st.subheader("📊 التوقعات القادمة")
if len(hist) >= 25:
    total_len = len(hist)
    global_counts = {c: hist.count(c) for c in set(hist)}
    recent_25 = hist[-25:]
    recent_counts = {c: recent_25.count(c) for c in set(recent_25)}
    
    combined_scores = {}
    for c in range(1, 9):
        score = (global_counts.get(c, 0) / total_len) * 0.4 + (recent_counts.get(c, 0) / 25) * 0.6
        combined_scores[c] = score * 100
    
    sorted_probs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
    
    p_cols = st.columns(5)
    for i, (code, prob) in enumerate(sorted_probs[:5]):
        with p_cols[i]:
            is_best = "main-highlight" if i == 0 else ""
            st.markdown(f'<div class="prob-box {is_best}">{SYMBOLS[code]["name"].split()[0]}<br><b>{prob:.0f}%</b></div>', unsafe_allow_html=True)
else:
    st.warning(f"📡 متبقي {25-len(hist)} جولة لتفعيل التحليل الكامل.")

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

if st.button("💾 حفظ البيانات"):
    st.toast("✅ تم التثبيت!")
