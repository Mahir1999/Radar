import streamlit as st
import time

# --- إعدادات الصفحة واستقرار البيانات ---
st.set_page_config(page_title="Greedy AI v87.0 - Jackpot Edition", page_icon="💰", layout="centered")

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
    .stat-box { background: #111; padding: 10px; border-radius: 10px; text-align: center; border: 1px solid #333; font-size: 13px; }
    .risk-indicator { padding: 12px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 15px; border: 2px solid; }
    .jackpot-meter { background: #1a0000; border: 1px solid #ff0055; color: #ff0055; padding: 8px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 14px; margin-top: 10px; }
    .audit-log { background: #001a1a; border: 1px solid #00ffcc; color: #00ffcc; padding: 5px; border-radius: 8px; font-size: 11px; margin-top: 5px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

SYMBOLS = {1: {"name": "🍅 طماطم"}, 2: {"name": "🌽 ذرة"}, 3: {"name": "🥕 جزر"}, 4: {"name": "🫑 فلفل"},
           5: {"name": "🐔 دجاجة"}, 6: {"name": "🐑 خروف"}, 7: {"name": "🐟 سمك"}, 8: {"name": "🦐 روبيان"}, 9: {"name": "💰 جكبوت"}}

# --- إدارة الجلسة (الحفاظ على البيانات) ---
if 'history' not in st.session_state: st.session_state.history = []
if 'hits' not in st.session_state: st.session_state.hits = 0
if 'misses' not in st.session_state: st.session_state.misses = 0
if 'consecutive_misses' not in st.session_state: st.session_state.consecutive_misses = 0
if 'patterns_found' not in st.session_state: st.session_state.patterns_found = 0
if 'audit_msg' not in st.session_state: st.session_state.audit_msg = "استقرار الخوارزمية"
if 'current_preds' not in st.session_state: st.session_state.current_preds = []

def register_result(code):
    if st.session_state.current_preds:
        if code in st.session_state.current_preds:
            st.session_state.hits += 1
            st.session_state.consecutive_misses = 0
            st.session_state.audit_msg = "✅ تم تأكيد النمط"
        elif code != 9:
            st.session_state.misses += 1
            st.session_state.consecutive_misses += 1
            if st.session_state.consecutive_misses % 2 == 0:
                st.session_state.audit_msg = "🔍 فحص تذبذب ودمج أنماط..."
                if len(st.session_state.history) > 5: st.session_state.patterns_found += 1
    st.session_state.history.append(code)

hist = st.session_state.history
total_h = len(hist)

# --- نظام الأمان والمخاطر ---
win_rate = (st.session_state.hits / total_h * 100) if total_h > 0 else 0
risk_level = "SAFE"
if total_h > 10:
    if win_rate < 35 or st.session_state.consecutive_misses >= 4: risk_level = "DANGER"
    elif win_rate < 45: risk_level = "CAUTION"

r_color = {"SAFE": "#39ff14", "CAUTION": "#ffaa00", "DANGER": "#ff4b4b"}[risk_level]
r_text = {"SAFE": "✅ العب الآن", "CAUTION": "⚠️ حذر (تذبذب)", "DANGER": "🛑 توقف فوراً"}[risk_level]

st.markdown(f'<div class="risk-indicator" style="background: {r_color}22; border-color: {r_color}; color: {r_color};">{r_text}</div>', unsafe_allow_html=True)

# --- العدادات الشاملة ---
st.markdown(f"""
<div class="stats-grid">
    <div class="stat-box">🔄 الجولة: <b>{total_h}</b></div>
    <div class="stat-box hit">✅ صح: <b>{st.session_state.hits}</b></div>
    <div class="stat-box miss">❌ خطأ: <b>{st.session_state.misses}</b></div>
</div>
<div class="audit-log">📟 {st.session_state.audit_msg} | أنماط مدمجة: {st.session_state.patterns_found}</div>
""", unsafe_allow_html=True)

# --- رادار الجكبوت الذكي ---
gap_9 = (list(reversed(hist)).index(9) if 9 in hist else total_h)
jackpot_prob = min(gap_9 * 2, 100) # احتمال افتراضي يزيد مع الغياب
j_status = "بارد" if jackpot_prob < 40 else "دافئ" if jackpot_prob < 75 else "🔥🔥 ساخن جداً"
st.markdown(f'<div class="jackpot-meter">🎰 رادار الجكبوت: {j_status} (غائب منذ {gap_9} جولة)</div>', unsafe_allow_html=True)

# --- أزرار التحكم ---
c1, c2 = st.columns(2)
with c1:
    if st.button("↩️ تراجع"): 
        if hist: st.session_state.history.pop(); st.rerun()
with c2:
    if st.button("🗑️ مسح الكل"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

if hist:
    st.markdown(f'<div class="last-result-banner">⏮️ الأخيرة: {SYMBOLS[hist[-1]]["name"]}</div>', unsafe_allow_html=True)
    timeline_html = '<div class="timeline-container">'
    for code in reversed(hist[-12:]): timeline_html += f'<div class="timeline-item">{SYMBOLS[code]["name"].split()[0]}</div>'
    timeline_html += '</div>'
    st.markdown(timeline_html, unsafe_allow_html=True)

# --- محرك التوقع v87 ---
gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 10)}
if total_h > 0:
    w = 0.9 if st.session_state.consecutive_misses >= 2 else 0.75
    scores = {c: (hist[-30:].count(c) * w + (gaps[c] * (1-w))) for c in range(1, 9)}
    top_4_codes = sorted(scores, key=scores.get, reverse=True)[:4]
    st.session_state.current_preds = top_4_codes
    
    st.markdown(f"""
    <div class="next-hit-card">
        <div style="color:#39ff14; font-size:12px; font-weight:bold;">🎯 المربع الذهبي (توقع النمط المدمج)</div>
        <div class="quad-box">
            <div class="quad-item">{SYMBOLS[top_4_codes[0]]["name"]}</div>
            <div class="quad-item">{SYMBOLS[top_4_codes[1]]["name"]}</div>
            <div class="quad-item">{SYMBOLS[top_4_codes[2]]["name"]}</div>
            <div class="quad-item">{SYMBOLS[top_4_codes[3]]["name"]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- إدخال النتائج ---
st.write("🔘 **سجل النتيجة الجديدة:**")
r1 = st.columns(5); r2 = st.columns(4)
for i, code in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[code]["name"].split()[0], key=f"b_{code}"): register_result(code); st.rerun()
for i, code in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[code]["name"].split()[0], key=f"b_{code}"): register_result(code); st.rerun()
