import streamlit as st
import time

# --- إعدادات الصفحة ---
st.set_page_config(page_title="SafeAI Predictor v84", page_icon="🛡️", layout="centered")

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
    .stats-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-bottom: 10px; }
    .stat-box { background: #111; padding: 10px; border-radius: 10px; text-align: center; border: 1px solid #333; font-size: 14px; }
    .hit { color: #39ff14; } .miss { color: #ff4b4b; }
    .risk-indicator { padding: 12px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 15px; font-size: 16px; border: 2px solid; }
    .gap-counter { position: absolute; top: 2px; right: 5px; font-size: 10px; color: #ff4b4b; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

SYMBOLS = {1: {"name": "🍅 طماطم"}, 2: {"name": "🌽 ذرة"}, 3: {"name": "🥕 جزر"}, 4: {"name": "🫑 فلفل"},
           5: {"name": "🐔 دجاجة"}, 6: {"name": "🐑 خروف"}, 7: {"name": "🐟 سمك"}, 8: {"name": "🦐 روبيان"}, 9: {"name": "💰 جكبوت"}}

if 'history' not in st.session_state: st.session_state.history = []
if 'hits' not in st.session_state: st.session_state.hits = 0
if 'misses' not in st.session_state: st.session_state.misses = 0
if 'consecutive_misses' not in st.session_state: st.session_state.consecutive_misses = 0
if 'current_preds' not in st.session_state: st.session_state.current_preds = []

def register_result(code):
    if st.session_state.current_preds:
        if code in st.session_state.current_preds:
            st.session_state.hits += 1
            st.session_state.consecutive_misses = 0
        elif code != 9:
            st.session_state.misses += 1
            st.session_state.consecutive_misses += 1
    st.session_state.history.append(code)

hist = st.session_state.history
total_h = len(hist)

# --- نظام تقييم المخاطر الجديد ---
win_rate = (st.session_state.hits / total_h * 100) if total_h > 0 else 0
risk_level = "SAFE"
if total_h > 10:
    if win_rate < 35 or st.session_state.consecutive_misses >= 3:
        risk_level = "DANGER"
    elif win_rate < 45:
        risk_level = "CAUTION"

if risk_level == "DANGER":
    risk_color, risk_text = "#ff4b4b", "🛑 توقف فوراً! السيرفر في حالة امتصاص"
elif risk_level == "CAUTION":
    risk_color, risk_text = "#ffaa00", "⚠️ حذر: نسبة الأخطاء مرتفعة"
else:
    risk_color, risk_text = "#39ff14", "✅ العب الآن: الخوارزمية مستقرة"

if total_h < 5: risk_text = "⏳ جاري فحص السيرفر..."

st.markdown(f'<div class="risk-indicator" style="background: {risk_color}22; border-color: {risk_color}; color: {risk_color};">{risk_text}</div>', unsafe_allow_html=True)

# --- العدادات ---
st.markdown(f"""
<div class="stats-grid">
    <div class="stat-box">🔄 الجولة: <b>{total_h}</b></div>
    <div class="stat-box hit">✅ صح: <b>{st.session_state.hits}</b></div>
    <div class="stat-box miss">❌ خطأ: <b>{st.session_state.misses}</b></div>
</div>
""", unsafe_allow_html=True)

# --- أزرار التحكم والنتائج ---
c1, c2 = st.columns(2)
with c1:
    if st.button("↩️ تراجع"): 
        if hist: st.session_state.history.pop(); st.rerun()
with c2:
    if st.button("🗑️ مسح الكل"):
        for k in st.session_state.keys(): del st.session_state[k]
        st.rerun()

if hist:
    st.markdown(f'<div class="last-result-banner">⏮️ الأخيرة: {SYMBOLS[hist[-1]]["name"]}</div>', unsafe_allow_html=True)
    timeline_html = '<div class="timeline-container">'
    for code in reversed(hist[-12:]): timeline_html += f'<div class="timeline-item">{SYMBOLS[code]["name"].split()[0]}</div>'
    timeline_html += '</div>'
    st.markdown(timeline_html, unsafe_allow_html=True)

# --- محرك التوقع v84 ---
gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 10)}
if total_h > 0:
    # تعديل الوزن لزيادة الدقة عند كثرة الأخطاء
    w = 0.95 if risk_level == "DANGER" else 0.8
    scores = {c: (hist[-30:].count(c) * w + (gaps[c] * (1-w))) for c in range(1, 9)}
    top_4_codes = sorted(scores, key=scores.get, reverse=True)[:4]
    st.session_state.current_preds = top_4_codes
    
    st.markdown(f"""
    <div class="next-hit-card">
        <div style="color:#39ff14; font-size:12px; font-weight:bold;">🎯 المربع الذهبي (التوقعات)</div>
        <div class="quad-box">
            <div class="quad-item">{SYMBOLS[top_4_codes[0]]["name"]}</div>
            <div class="quad-item">{SYMBOLS[top_4_codes[1]]["name"]}</div>
            <div class="quad-item">{SYMBOLS[top_4_codes[2]]["name"]}</div>
            <div class="quad-item">{SYMBOLS[top_4_codes[3]]["name"]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- رادار الفجوات ---
st.subheader("📊 رادار الفجوات")
global_counts = {c: hist.count(c) for c in range(1, 9)}
sorted_items = sorted(global_counts.items(), key=lambda x: x[1], reverse=True)
p1 = st.columns(4); p2 = st.columns(4)
for i, (code, count) in enumerate(sorted_items[:4]):
    with p1[i]: st.markdown(f'<div style="background:#111; padding:8px; border-radius:8px; text-align:center; position:relative; border:1px solid #333;"><span class="gap-counter">{gaps[code]}</span>{SYMBOLS[code]["name"].split()[0]}</div>', unsafe_allow_html=True)
for i, (code, count) in enumerate(sorted_items[4:8]):
    with p2[i]: st.markdown(f'<div style="background:#111; padding:8px; border-radius:8px; text-align:center; position:relative; border:1px solid #333;"><span class="gap-counter">{gaps[code]}</span>{SYMBOLS[code]["name"].split()[0]}</div>', unsafe_allow_html=True)

# --- الإدخال ---
st.write("🔘 **سجل النتيجة:**")
r1 = st.columns(5); r2 = st.columns(4)
for i, code in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[code]["name"].split()[0], key=f"b_{code}"): register_result(code); st.rerun()
for i, code in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[code]["name"].split()[0], key=f"b_{code}"): register_result(code); st.rerun()
