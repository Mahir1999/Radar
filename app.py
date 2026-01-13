import streamlit as st
import time

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Smart AI Assistant v82", page_icon="🤖", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .stButton>button { width: 100%; height: 48px; font-weight: bold; border-radius: 10px; }
    .last-result-banner {
        background: #1a1a1a; padding: 10px; border-radius: 10px; border-right: 5px solid #39ff14;
        text-align: center; margin-bottom: 10px; color: #39ff14; font-weight: bold; font-size: 18px;
    }
    .timeline-container {
        display: flex; gap: 5px; margin-bottom: 15px; padding: 8px;
        background: #0e1117; border-radius: 8px; overflow-x: auto;
    }
    .timeline-item { padding: 4px 10px; background: #262730; border-radius: 6px; font-size: 13px; white-space: nowrap; color: #eee; }
    .next-hit-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #000 100%);
        border: 2px solid #39ff14; padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 15px;
    }
    .quad-box { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
    .quad-item { background: #002200; border: 1px solid #39ff14; padding: 8px; border-radius: 8px; color: white; font-weight: bold; font-size: 14px;}
    .stats-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-bottom: 10px; }
    .stat-box { background: #111; padding: 10px; border-radius: 10px; text-align: center; border: 1px solid #333; font-size: 14px; }
    .hit { color: #39ff14; } .miss { color: #ff4b4b; }
    .risk-indicator { padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 10px; }
    .prob-box { background: #111; border: 1px solid #333; border-radius: 8px; padding: 8px; text-align: center; position: relative; }
    .gap-counter { position: absolute; top: 2px; right: 5px; font-size: 10px; color: #ff4b4b; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

SYMBOLS = {
    1: {"name": "🍅 طماطم"}, 2: {"name": "🌽 ذرة"}, 3: {"name": "🥕 جزر"}, 4: {"name": "🫑 فلفل"},
    5: {"name": "🐔 دجاجة"}, 6: {"name": "🐑 خروف"}, 7: {"name": "🐟 سمك"}, 8: {"name": "🦐 روبيان"}, 9: {"name": "💰 جكبوت"}
}

# --- تهيئة حالة الجلسة ---
if 'history' not in st.session_state: st.session_state.history = []
if 'hits' not in st.session_state: st.session_state.hits = 0
if 'misses' not in st.session_state: st.session_state.misses = 0
if 'current_preds' not in st.session_state: st.session_state.current_preds = []
if 'consecutive_misses' not in st.session_state: st.session_state.consecutive_misses = 0
if 'consecutive_hits' not in st.session_state: st.session_state.consecutive_hits = 0
if 'learned' not in st.session_state: st.session_state.learned = False

def register_result(code):
    if st.session_state.current_preds:
        if code in st.session_state.current_preds:
            st.session_state.hits += 1
            st.session_state.consecutive_hits += 1
            st.session_state.consecutive_misses = 0
        elif code != 9:
            st.session_state.misses += 1
            st.session_state.consecutive_misses += 1
            st.session_state.consecutive_hits = 0
            
    # التحقق من شرط إعادة الضبط (5 أخطاء متتالية)
    if st.session_state.consecutive_misses >= 5:
        st.session_state.learned = False
        st.session_state.consecutive_misses = 0
        st.toast("⚠️ تم رصد عشوائية عالية! إعادة تحليل النمط...")

    # التحقق من شرط الفهم (5 صحيحة متتالية)
    if st.session_state.consecutive_hits >= 5:
        st.session_state.learned = True

    st.session_state.history.append(code)

hist = st.session_state.history
total_h = len(hist)

# --- مؤشر حالة اللعب (إدارة المخاطر) ---
risk_color = "#39ff14" if st.session_state.consecutive_misses < 3 else "#ff4b4b"
risk_text = "✅ العب الآن (السيرفر مستقر)" if st.session_state.consecutive_misses < 3 else "⚠️ توقف فوراً (السيرفر عشوائي)"
if total_h < 10: risk_text = "⏳ جاري تقييم المخاطر..."

st.markdown(f'<div class="risk-indicator" style="background: {risk_color}22; border: 1px solid {risk_color}; color: {risk_color};">{risk_text}</div>', unsafe_allow_html=True)

# --- واجهة العدادات ---
st.markdown(f"""
<div class="stats-grid">
    <div class="stat-box">🔄 الجولة: <b>{total_h}</b></div>
    <div class="stat-box hit">✅ صح: <b>{st.session_state.hits}</b></div>
    <div class="stat-box miss">❌ خطأ: <b>{st.session_state.misses}</b></div>
</div>
""", unsafe_allow_html=True)

# --- أزرار التحكم ---
c1, c2 = st.columns(2)
with c1:
    if st.button("↩️ تراجع"): 
        if hist: st.session_state.history.pop(); st.rerun()
with c2:
    if st.button("🗑️ مسح الكل"): 
        for key in st.session_state.keys(): del st.session_state[key]
        st.rerun()

# --- شريط النتائج ---
if hist:
    st.markdown(f'<div class="last-result-banner">⏮️ الأخيرة: {SYMBOLS[hist[-1]]["name"]}</div>', unsafe_allow_html=True)
    timeline_html = '<div class="timeline-container">'
    for code in reversed(hist[-12:]):
        timeline_html += f'<div class="timeline-item">{SYMBOLS[code]["name"].split()[0]}</div>'
    timeline_html += '</div>'
    st.markdown(timeline_html, unsafe_allow_html=True)

# --- محرك التوقع (4 خيارات) ---
gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 10)}

if total_h > 0:
    weight_recent = 0.85 if st.session_state.learned else 0.6
    scores = {c: (hist[-20:].count(c) * weight_recent + (gaps[c] * (1-weight_recent))) for c in range(1, 9)}
    top_4_codes = sorted(scores, key=scores.get, reverse=True)[:4]
    st.session_state.current_preds = top_4_codes
    
    status_msg = "✅ السيرفر مكشوف!" if st.session_state.learned else "📡 جاري مطابقة الأنماط..."
    
    st.markdown(f"""
    <div class="next-hit-card">
        <div style="color:#39ff14; font-size:12px; font-weight:bold;">{status_msg} (توقع الرباعي الذهبي)</div>
        <div class="quad-box">
            <div class="quad-item">{SYMBOLS[top_4_codes[0]]["name"]}</div>
            <div class="quad-item">{SYMBOLS[top_4_codes[1]]["name"]}</div>
            <div class="quad-item">{SYMBOLS[top_4_codes[2]]["name"]}</div>
            <div class="quad-item">{SYMBOLS[top_4_codes[3]]["name"]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- رادار الفجوات ---
st.subheader("📊 رادار الفجوات الرقمي")
global_counts = {c: hist.count(c) for c in range(1, 9)}
sorted_items = sorted(global_counts.items(), key=lambda x: x[1], reverse=True)
p1 = st.columns(4)
for i, (code, count) in enumerate(sorted_items[:4]):
    with p1[i]: st.markdown(f'<div class="prob-box" style="border:1px solid #39ff14;"><span class="gap-counter">{gaps[code]}</span>{SYMBOLS[code]["name"].split()[0]}<br><b>نشط</b></div>', unsafe_allow_html=True)
p2 = st.columns(4)
for i, (code, count) in enumerate(sorted_items[4:8]):
    with p2[i]: st.markdown(f'<div class="prob-box"><span class="gap-counter">{gaps[code]}</span>{SYMBOLS[code]["name"].split()[0]}<br><b>ساكن</b></div>', unsafe_allow_html=True)

# --- أزرار الإدخال ---
st.write("🔘 **سجل النتيجة:**")
r1 = st.columns(5); r2 = st.columns(4)
for i, code in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[code]["name"].split()[0], key=f"b_{code}"): register_result(code); st.rerun()
for i, code in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[code]["name"].split()[0], key=f"b_{code}"): register_result(code); st.rerun()
