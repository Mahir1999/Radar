import streamlit as st
import time

# --- إعدادات الصفحة واستقرار النظام ---
st.set_page_config(page_title="Greedy AI v89.0 - Omni Engine", page_icon="🔮", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .stButton>button { width: 100%; height: 48px; font-weight: bold; border-radius: 10px; }
    .last-result-banner { background: #1a1a1a; padding: 10px; border-radius: 10px; border-right: 5px solid #39ff14; text-align: center; margin-bottom: 10px; color: #39ff14; font-weight: bold; font-size: 18px; }
    .timeline-container { display: flex; gap: 5px; margin-bottom: 15px; padding: 8px; background: #0e1117; border-radius: 8px; overflow-x: auto; }
    .timeline-item { padding: 4px 10px; background: #262730; border-radius: 6px; font-size: 13px; white-space: nowrap; color: #eee; }
    .next-hit-card { background: linear-gradient(135deg, #1a1a1a 0%, #000 100%); border: 2px solid #39ff14; padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 15px; }
    .quad-box { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
    .quad-item { background: #002200; border: 1px solid #39ff14; padding: 8px; border-radius: 8px; color: white; font-weight: bold; font-size: 14px;}
    .stats-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 10px; }
    .stat-box { background: #111; padding: 8px; border-radius: 10px; text-align: center; border: 1px solid #333; font-size: 12px; }
    .omni-metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }
    .metric-card { background: #0a0a0a; border: 1px dashed #444; padding: 10px; border-radius: 10px; text-align: center; font-size: 11px; }
    .wave-push { color: #39ff14; font-weight: bold; animation: blinker 2s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.5; } }
    </style>
    """, unsafe_allow_html=True)

SYMBOLS = {1: {"name": "🍅 طماطم"}, 2: {"name": "🌽 ذرة"}, 3: {"name": "🥕 جزر"}, 4: {"name": "🫑 فلفل"},
           5: {"name": "🐔 دجاجة"}, 6: {"name": "🐑 خروف"}, 7: {"name": "🐟 سمك"}, 8: {"name": "🦐 روبيان"}, 9: {"name": "💰 جكبوت"}}

# --- إدارة الحالة المستمرة ---
if 'history' not in st.session_state: st.session_state.history = []
if 'hits' not in st.session_state: st.session_state.hits = 0
if 'misses' not in st.session_state: st.session_state.misses = 0
if 'consecutive_misses' not in st.session_state: st.session_state.consecutive_misses = 0
if 'patterns_found' not in st.session_state: st.session_state.patterns_found = 0
if 'current_preds' not in st.session_state: st.session_state.current_preds = []

def register_result(code):
    if st.session_state.current_preds:
        if code in st.session_state.current_preds:
            st.session_state.hits += 1
            st.session_state.consecutive_misses = 0
        elif code != 9:
            st.session_state.misses += 1
            st.session_state.consecutive_misses += 1
            if st.session_state.consecutive_misses % 2 == 0: st.session_state.patterns_found += 1
    st.session_state.history.append(code)

hist = st.session_state.history
total_h = len(hist)

# --- 1. رادار الموجة وميزان السيرفر ---
wave_status = "امتصاص ⏳"
bank_pressure = "منخفض"
if total_h > 10:
    recent_hits = sum(1 for c in hist[-10:] if any(c in p for p in [st.session_state.current_preds])) # تقديري
    if recent_hits >= 4: wave_status = "دفع (FIRE) 🔥"
    bank_pressure = "ممتلئ (انفجار قريب)" if st.session_state.misses > st.session_state.hits + 10 else "متوازن"

# --- عرض العدادات العليا ---
st.markdown(f"""
<div class="stats-grid">
    <div class="stat-box">🔄 الجولة: <b>{total_h}</b></div>
    <div class="stat-box" style="color:#39ff14">✅ فوز: <b>{st.session_state.hits}</b></div>
    <div class="stat-box" style="color:#ff4b4b">❌ خطأ: <b>{st.session_state.misses}</b></div>
</div>
<div class="omni-metrics">
    <div class="metric-card">🌊 الموجة: <span class="wave-push">{wave_status}</span></div>
    <div class="metric-card">⚖️ ضغط السيرفر: <b>{bank_pressure}</b></div>
</div>
""", unsafe_allow_html=True)

# --- محرك التحليل v89 (البصمة الزمنية) ---
if total_h > 5:
    gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 10)}
    # حساب التردد (البصمة الزمنية)
    freq = {c: total_h / hist.count(c) if hist.count(c) > 0 else 50 for c in range(1, 9)}
    
    # دمج الأوزان (القديم 10%، الجديد 70%، البصمة 20%)
    scores = {}
    for c in range(1, 9):
        recent_weight = hist[-15:].count(c) * 0.70
        historic_weight = hist.count(c) * 0.10
        time_sig = 1.0 if gaps[c] >= freq[c] else 0.5 # إذا تجاوز الفجوة المعتادة يصبح "ساخناً"
        scores[c] = (recent_weight + historic_weight) * time_sig

    top_4_codes = sorted(scores, key=scores.get, reverse=True)[:4]
    
    # فلتر النخبة (من v88)
    recent_variance = len(set(hist[-5:]))
    if recent_variance >= 5 and st.session_state.consecutive_misses >= 3:
        st.session_state.current_preds = []
        st.warning("⚠️ عشوائية فائقة - البرنامج يحلل البصمات الجديدة، انتظر جولة..")
    else:
        st.session_state.current_preds = top_4_codes
        st.markdown(f"""
        <div class="next-hit-card">
            <div style="color:#39ff14; font-size:12px; font-weight:bold;">🎯 المربع الذهبي (Omni-Prediction)</div>
            <div class="quad-box">
                {"".join([f'<div class="quad-item">{"⏳ " if gaps[c] >= freq[c] else ""}{SYMBOLS[c]["name"]}</div>' for c in top_4_codes])}
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- شريط الجكبوت والتحكم ---
gap_9 = (list(reversed(hist)).index(9) if 9 in hist else total_h)
st.markdown(f'<div style="text-align:center; font-size:12px; color:#ff0055; margin-bottom:10px;">💰 رادار الجكبوت: غائب منذ {gap_9} جولة | أنماط مكتشفة: {st.session_state.patterns_found}</div>', unsafe_allow_html=True)

if hist:
    st.markdown(f'<div class="last-result-banner">⏮️ الأخيرة: {SYMBOLS[hist[-1]]["name"]}</div>', unsafe_allow_html=True)
    timeline_html = '<div class="timeline-container">'
    for code in reversed(hist[-12:]): timeline_html += f'<div class="timeline-item">{SYMBOLS[code]["name"].split()[0]}</div>'
    timeline_html += '</div>'
    st.markdown(timeline_html, unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    if st.button("↩️ تراجع"): 
        if hist: st.session_state.history.pop(); st.rerun()
with c2:
    if st.button("🗑️ مسح الكل"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

st.write("🔘 **سجل النتيجة:**")
r1 = st.columns(5); r2 = st.columns(4)
for i, code in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[code]["name"].split()[0], key=f"b_{code}"): register_result(code); st.rerun()
for i, code in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[code]["name"].split()[0], key=f"b_{code}"): register_result(code); st.rerun()
