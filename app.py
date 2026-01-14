import streamlit as st

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Greedy AI v100.0", layout="centered")

st.markdown("""
    <style>
    /* تصميم المربع الموحد الثابت */
    .master-frame {
        border: 2px solid #39ff14;
        background: #000;
        padding: 10px;
        border-radius: 15px;
        text-align: center;
    }
    
    /* تنسيق جدول الأزرار لمنع الانهيار العمودي */
    .icon-table {
        width: 100%;
        border-collapse: collapse;
    }
    .icon-table td {
        padding: 5px;
        width: 33%;
    }
    
    /* تصميم الأزرار داخل الجدول */
    .stButton > button {
        width: 100% !important;
        height: 55px !important;
        background: #001a00 !important;
        color: #39ff14 !important;
        border: 1px solid #32cd32 !important;
        font-size: 22px !important;
        border-radius: 10px !important;
    }

    .status-header {
        background: #111;
        padding: 5px;
        border-radius: 8px;
        margin-bottom: 8px;
        border-bottom: 2px solid #39ff14;
    }
    .badge { padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; }
    </style>
    """, unsafe_allow_html=True)

SYMBOLS = {1: "🍅", 2: "🌽", 3: "🥕", 4: "🫑", 5: "🐔", 6: "🐑", 7: "🐟", 8: "🦐", 9: "💰"}
VEGGIES, MEATS = [1, 2, 3, 4], [5, 6, 7, 8]

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
            if st.session_state.consecutive_misses >= 2: st.session_state.patterns_found += 1
    st.session_state.history.append(code)

hist = st.session_state.history
total_h = len(hist)

# --- حساب التوقعات ---
if total_h > 0:
    gaps = {c: (list(reversed(hist)).index(c) if c in hist else total_h) for c in range(1, 9)}
    scores = {c: (hist[-15:].count(c) * 0.7 + (gaps[c] * 0.3)) for c in range(1, 9)}
    top_4 = sorted(scores, key=scores.get, reverse=True)[:4]
    insurance_slot = sorted(MEATS, key=lambda x: gaps[x], reverse=True)[0] if all(c in VEGGIES for c in top_4) else sorted(scores, key=scores.get, reverse=True)[4]
    st.session_state.current_preds = top_4 + [insurance_slot]
    
    # --- الواجهة الموحدة داخل مربع واحد ---
    st.markdown('<div class="master-frame">', unsafe_allow_html=True)
    
    # 1. شريط الحالة العلوي (الميزات المستعادة)
    p_status = "ثابت ✅" if st.session_state.consecutive_misses < 2 else "متغير ⚠️"
    p_color = "#00ff00" if p_status == "ثابت ✅" else "#ffaa00"
    st.markdown(f"""
    <div class="status-header">
        <span style="color:#39ff14; font-size:12px;">📊 {st.session_state.hits} | {st.session_state.misses} | ج {total_h}</span><br>
        <span class="badge" style="background:{p_color}; color:black;">نمط: {p_status}</span>
        <span class="badge" style="background:#444; color:white;">أنماط: {st.session_state.patterns_found}</span>
    </div>
    """, unsafe_allow_html=True)

    # 2. منطقة التوقعات (المربع الذهبي + درع التأمين)
    st.markdown(f"""
    <div style="display:flex; justify-content:space-around; align-items:center; margin-bottom:10px;">
        <div style="border:1px solid #39ff14; padding:5px; border-radius:8px;">
            <div style="font-size:9px; color:#39ff14;">🎯 الذهبي</div>
            <div style="font-size:18px;">{' '.join([SYMBOLS[c] for c in top_4])}</div>
        </div>
        <div style="border:1px solid #00aaff; padding:5px; border-radius:8px;">
            <div style="font-size:9px; color:#00aaff;">🛡️ تأمين</div>
            <div style="font-size:18px;">{SYMBOLS[insurance_slot]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. جدول الأزرار العرضي (الحل النهائي)
    # نستخدم نظام st.columns داخل المربع لضمان التوزيع العرضي
    btns = [5, 7, 6, 8, 9, 1, 2, 3, 4]
    for i in range(0, 9, 3):
        cols = st.columns(3)
        for j in range(3):
            code = btns[i+j]
            if cols[j].button(SYMBOLS[code], key=f"fixed_{code}"):
                register_result(code)
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- أزرار الإدارة الخارجية ---
st.write("")
c1, c2 = st.columns(2)
if c1.button("↩️ تراجع"):
    if hist: st.session_state.history.pop(); st.rerun()
if c2.button("🗑️ مسح"):
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()
