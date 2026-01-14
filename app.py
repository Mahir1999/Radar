import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Greedy AI v95.0", page_icon="📡", layout="centered")

# --- منطق المخاطر ---
if 'misses' not in st.session_state: st.session_state.misses = 0
if 'hits' not in st.session_state: st.session_state.hits = 0
if 'consecutive_misses' not in st.session_state: st.session_state.consecutive_misses = 0

risk_level = "LOW"
if st.session_state.misses > st.session_state.hits: risk_level = "HIGH"
if st.session_state.consecutive_misses >= 3: risk_level = "CRITICAL"

# --- التنسيق (CSS) ---
warning_color = "#ff4b4b" if risk_level != "LOW" else "#39ff14"
st.markdown(f"""
    <style>
    .block-container {{ padding-top: 1rem; border-top: 5px solid {warning_color}; }}
    .stButton>button {{ width: 100%; height: 45px; font-weight: bold; border-radius: 8px; font-size: 13px; }}
    .next-hit-card {{ background: #1a1a1a; border: 2px solid #39ff14; padding: 10px; border-radius: 15px; text-align: center; margin-bottom: 10px; }}
    .quad-box {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 5px; }}
    .quad-item {{ background: #002200; border: 1px solid #39ff14; padding: 6px; border-radius: 8px; color: white; font-weight: bold; font-size: 12px; }}
    .stats-grid-4 {{ display: grid; grid-template-columns: 1fr 1fr 1fr 1.2fr; gap: 5px; margin-bottom: 10px; }}
    .stat-box-v2 {{ background: #111; padding: 6px 2px; border-radius: 8px; text-align: center; border: 1px solid #333; font-size: 10px; }}
    .history-row {{ display: flex; gap: 8px; margin-bottom: 15px; align-items: center; }}
    .insurance-box-v3 {{ width: 90px; background: #001a33; border: 2px solid #00aaff; padding: 5px; border-radius: 12px; text-align: center; }}
    .history-scroll {{ flex: 1; background: #111; border: 1px solid #444; padding: 8px; border-radius: 12px; display: flex; justify-content: flex-end; gap: 6px; overflow: hidden; }}
    .history-tag {{ background: #222; border: 1px solid #39ff14; padding: 4px 8px; border-radius: 6px; font-size: 16px; }}
    .density-radar {{ background: #0a0a0a; border: 1px dashed #39ff14; padding: 5px; border-radius: 8px; font-size: 10px; color: #39ff14; text-align: center; flex: 2; }}
    </style>
    """, unsafe_allow_html=True)

SYMBOLS = {1: "🍅", 2: "🌽", 3: "🥕", 4: "🫑", 5: "🐔", 6: "🐑", 7: "🐟", 8: "🦐", 9: "💰"}
SYMBOLS_FULL = {1: "طماطم", 2: "ذرة", 3: "جزر", 4: "فلفل", 5: "دجاجة", 6: "خروف", 7: "سمك", 8: "روبيان", 9: "جكبوت"}

if 'history' not in st.session_state: st.session_state.history = []
if 'patterns_count' not in st.session_state: st.session_state.patterns_count = 0
if 'current_preds' not in st.session_state: st.session_state.current_preds = []

def register_result(code):
    hist = st.session_state.history
    if len(hist) > 4:
        last_pair = hist[-2:] + [code]
        if str(last_pair) in str(hist): st.session_state.patterns_count += 1
    if st.session_state.current_preds:
        if code in st.session_state.current_preds:
            st.session_state.hits += 1
            if st.session_state.consecutive_misses >= 2: st.session_state.patterns_count += 1
            st.session_state.consecutive_misses = 0
        elif code != 9:
            st.session_state.misses += 1
            st.session_state.consecutive_misses += 1
    st.session_state.history.append(code)

hist = st.session_state.history
total_h = len(hist)

# --- 1. التحذيرات والعدادات ---
if risk_level == "CRITICAL": st.markdown('<div style="color:#ff4b4b; text-align:center; font-weight:bold; font-size:14px; margin-bottom:5px;">🚨 خطر استرداد: انسحب!</div>', unsafe_allow_html=True)
p_status = "ثابت ✅" if st.session_state.consecutive_misses < 2 else "متغير ⚠️"
p_color = "#39ff14" if p_status == "ثابت ✅" else "#ff4b4b"
st.markdown(f'<div class="stats-grid-4"><div class="stat-box-v2">🔄 جولة<br><b>{total_h}</b></div><div class="stat-box-v2" style="color:#39ff14">✅ فوز<br><b>{st.session_state.hits}</b></div><div class="stat-box-v2" style="color:#ff4b4b">❌ خطأ<br><b>{st.session_state.misses}</b></div><div class="stat-box-v2" style="border-color:{p_color}">📉 النمط<br><b style="color:{p_color}">{p_status}</b></div></div>', unsafe_allow_html=True)

# --- 2. المربع الذهبي والتأمين ---
if total_h >= 0:
    gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 9)}
    recent_15 = hist[-15:]
    scores = {c: (recent_15.count(c) * 0.7 + (gaps[c] * 0.3)) for c in range(1, 9)}
    top_4 = sorted(scores, key=scores.get, reverse=True)[:4]
    insurance_slot = sorted([5,6,7,8], key=lambda x: gaps[x], reverse=True)[0] if all(c in [1,2,3,4] for c in top_4) else sorted(scores, key=scores.get, reverse=True)[4]
    st.session_state.current_preds = top_4 + [insurance_slot]
    
    st.markdown(f'<div class="next-hit-card"><div style="color:#39ff14; font-size:11px; font-weight:bold;">🎯 المربع الذهبي</div><div class="quad-box">{"".join([f'<div class="quad-item">{SYMBOLS[c]} {SYMBOLS_FULL[c]}</div>' for c in top_4])}</div></div>', unsafe_allow_html=True)

    # --- 3. الصف المدمج (تأمين + آخر 5) ---
    last_5 = hist[-5:]
    history_html = "".join([f'<div class="history-tag">{SYMBOLS[c]}</div>' for c in last_5])
    confidence = min(95, 40 + (gaps[insurance_slot] * 2))
    st.markdown(f'<div class="history-row"><div class="insurance-box-v3"><div style="color:#00aaff; font-size:8px; font-weight:bold;">🛡️ تأمين</div><div style="font-size:15px;">{SYMBOLS[insurance_slot]}</div><div style="font-size:8px; color:#00aaff;">{confidence}%</div></div><div class="history-scroll"><div style="color:#666; font-size:9px; align-self:center; margin-right:auto; margin-left:5px;">⏮️ آخر 5:</div>{history_html if history_html else "..."}</div></div>', unsafe_allow_html=True)

# --- 4. أزرار التسجيل ---
r1, r2 = st.columns(5), st.columns(4)
for i, c in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[c], key=f"btn_{c}"): register_result(c); st.rerun()
for i, c in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[c], key=f"btn_{c}"): register_result(c); st.rerun()

# --- 5. رادار الكثافة وزر تراجع (في صف واحد) ---
if total_h > 0:
    counts = {SYMBOLS[c]: recent_15.count(c) for c in range(1, 9)}
    top_3_density = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:3]
    radar_text = " ".join([f"{k}:{v}" for k, v in top_3_density])
    
    c1, c2 = st.columns([1, 2])
    if c1.button("↩️ تراجع"):
        if hist: st.session_state.history.pop(); st.rerun()
    c2.markdown(f'<div class="density-radar">📡 ملوك الموجة (آخر 15):<br><b>{radar_text}</b></div>', unsafe_allow_html=True)

# العداد السفلي
gap_9 = (list(reversed(hist)).index(9) if 9 in hist else total_h)
st.markdown(f'<div style="text-align:center; font-size:10px; color:#555; margin-top:5px;">🧠 أنماط: {st.session_state.patterns_count} | 💰 جكبوت: {gap_9}</div>', unsafe_allow_html=True)
