import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Strategic Radar v69", page_icon="🛡️", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .stButton>button { width: 100%; height: 48px; font-weight: bold; border-radius: 10px; }
    .last-result-banner {
        background: #1a1a1a; padding: 10px; border-radius: 10px; border-right: 5px solid #39ff14;
        text-align: center; margin-bottom: 10px; color: #39ff14; font-weight: bold;
    }
    .timeline-container {
        display: flex; gap: 5px; margin-bottom: 15px; padding: 8px;
        background: #0e1117; border-radius: 8px; overflow-x: auto;
    }
    .timeline-item {
        padding: 4px 10px; background: #262730; border-radius: 6px; font-size: 13px; white-space: nowrap; color: #eee;
    }
    .break-alert {
        background: #2e2100; border: 1px solid #ffaa00; border-radius: 10px;
        padding: 10px; text-align: center; color: #ffaa00; font-weight: bold; margin-bottom: 10px;
    }
    .pulse-card {
        background: #0e1117; border: 1px solid #333; border-radius: 12px;
        padding: 12px; margin-bottom: 15px; border-left: 4px solid #39ff14;
    }
    .prob-box { 
        background: #111; border: 1px solid #333; border-radius: 8px; 
        padding: 10px; text-align: center; font-size: 14px;
    }
    .main-highlight { border: 2px solid #39ff14 !important; background: #002200 !important; box-shadow: 0 0 10px #39ff14; }
    </style>
    """, unsafe_allow_html=True)

# --- تحديث قائمة العناصر (تبديل البقر بالخروف) ---
SYMBOLS = {
    1: {"name": "🍅 طماطم", "type": "veg", "mult": 5}, 
    2: {"name": "🌽 ذرة", "type": "veg", "mult": 5},
    3: {"name": "🥕 جزر", "type": "veg", "mult": 5}, 
    4: {"name": "🫑 فلفل", "type": "veg", "mult": 5},
    5: {"name": "🐔 دجاجة", "type": "ani", "mult": 45}, 
    6: {"name": "🐑 خروف", "type": "ani", "mult": 15}, # تم التغيير هنا
    7: {"name": "🐟 سمك", "type": "ani", "mult": 25}, 
    8: {"name": "🦐 روبيان", "type": "ani", "mult": 10},
    9: {"name": "💰 جكبوت", "type": "jack", "mult": 100}
}

if 'history' not in st.session_state: st.session_state.history = []

def register_result(code):
    st.session_state.history.append(code)

# --- التحكم العلوي وعداد الثقة ---
c_stat, c_reset = st.columns([3, 1])
hist = st.session_state.history
total_h = len(hist)

with c_stat:
    if total_h < 30:
        progress = total_h / 30
        st.write(f"📡 استقرار البيانات: {int(progress*100)}%")
        st.progress(progress)
    else:
        st.write("✅ **وضع الدقة العالية نشط**")
        st.progress(1.0)

with c_reset:
    if st.button("🗑️ مسح"): st.session_state.clear(); st.rerun()

# --- شريط النتائج الأخير ---
if hist:
    st.markdown(f'<div class="last-result-banner">⏮️ آخر نتيجة: {SYMBOLS[hist[-1]]["name"]}</div>', unsafe_allow_html=True)
    timeline_html = '<div class="timeline-container">'
    for code in reversed(hist[-12:]):
        timeline_html += f'<div class="timeline-item">{SYMBOLS[code]["name"].split()[0]}</div>'
    timeline_html += '</div>'
    st.markdown(timeline_html, unsafe_allow_html=True)

# --- كاشف كسر النمط ---
if len(hist) >= 4:
    last_types = [SYMBOLS[c]["type"] for c in hist[-4:]]
    if all(t == "veg" for t in last_types):
        st.markdown('<div class="break-alert">⚠️ تحذير: سلسلة خضروات طويلة! احتمال لكسر النمط بـ (حيوان).</div>', unsafe_allow_html=True)
    elif all(t == "ani" for t in last_types):
        st.markdown('<div class="break-alert">⚠️ تحذير: سلسلة حيوانات طويلة! احتمال لكسر النمط بـ (خضار).</div>', unsafe_allow_html=True)

# --- رادار نبض السيرفر ---
if total_h >= 10:
    recent_10 = hist[-10:]
    hot_symbol = max(set(recent_10), key=recent_10.count)
    gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 9)}
    cold_symbol = max(gaps, key=gaps.get)

    st.markdown(f"""
    <div class="pulse-card">
        🚀 <b>رادار الموجة الحالية:</b><br>
        • الرمز الساخن: <b>{SYMBOLS[hot_symbol]['name']}</b><br>
        • الرمز المتأخر: <b>{SYMBOLS[cold_symbol]['name']}</b> (غائب منذ {gaps[cold_symbol]} جولة)
    </div>
    """, unsafe_allow_html=True)

# --- محرك التحليل السريع (80/20) ---
st.subheader("📊 توقعات التحليل الموزون")
if total_h >= 30:
    global_counts = {c: hist.count(c) for c in range(1, 9)}
    recent_25 = hist[-25:]
    recent_counts = {c: recent_25.count(c) for c in range(1, 9)}
    
    combined_scores = {}
    for c in range(1, 9):
        score = (global_counts.get(c, 0) / total_h) * 0.2 + (recent_counts.get(c, 0) / 25) * 0.8
        combined_scores[c] = score * 100
    
    sorted_probs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
    p_cols = st.columns(5)
    for i, (code, prob) in enumerate(sorted_probs[:5]):
        with p_cols[i]:
            is_best = "main-highlight" if i == 0 else ""
            st.markdown(f'<div class="prob-box {is_best}">{SYMBOLS[code]["name"].split()[0]}<br><b>{prob:.0f}%</b></div>', unsafe_allow_html=True)
else:
    st.warning(f"⚠️ يرجى تسجيل {30 - total_h} جولة إضافية.")

# --- تسجيل النتائج ---
st.write("🔘 **سجل النتيجة الآن:**")
res_row1 = st.columns(5)
for i, code in enumerate([5, 7, 6, 8, 9]):
    if res_row1[i].button(SYMBOLS[code]["name"].split()[0], key=f"r_{code}"):
        register_result(code); st.rerun()

res_row2 = st.columns(4)
for i, code in enumerate([1, 2, 3, 4]):
    if res_row2[i].button(SYMBOLS[code]["name"].split()[0], key=f"r_{code}"):
        register_result(code); st.rerun()
