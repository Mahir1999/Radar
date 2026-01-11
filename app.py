import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime
import pytz
import base64

# --- إعدادات الصفحة والستايل ---
st.set_page_config(page_title="Farm Radar Pro", page_icon="🚜", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 60px; font-weight: bold; font-size: 18px; border-radius: 10px; }
    .stMetric { background-color: #1a1a1a; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- تعريف الرموز وقيمها البرمجية ---
SYMBOLS = {
    1: {"name": "🍅 طماطم", "color": "#e74c3c", "value": 20},
    2: {"name": "🌽 ذرة", "color": "#f1c40f", "value": 20},
    3: {"name": "🥕 جزر", "color": "#e67e22", "value": 20},
    4: {"name": "🫑 فلفل", "color": "#27ae60", "value": 20},
    5: {"name": "🐔 دجاجة", "color": "#ecf0f1", "value": -110},
    6: {"name": "🐄 بقر", "color": "#95a5a6", "value": -110},
    7: {"name": "🐟 سمك", "color": "#3498db", "value": -150},
    8: {"name": "🦐 روبيان", "color": "#ff7f50", "value": -200}
}

# --- تهيئة الجلسة (Session State) ---
if 'history' not in st.session_state:
    st.session_state.update({'history': [], 'vault': 0, 'X': [], 'y': []})

def process_entry(code):
    st.session_state.vault += SYMBOLS[code]['value']
    st.session_state.history.append(code)
    # تدريب الذكاء الاصطناعي البسيط
    if len(st.session_state.history) > 4:
        feat = st.session_state.history[-5:-1]
        st.session_state.X.append(feat)
        st.session_state.y.append(code)

# --- الواجهة العلوية ---
st.title("🚜 رادار المزرعة v11.0")
makkah_now = datetime.now(pytz.timezone('Asia/Riyadh')).strftime("%I:%M:%S %p")
st.write(f"🕋 توقيت مكة: `{makkah_now}`")

# --- مؤشرات الحالة ---
col1, col2 = st.columns(2)
with col1:
    v_color = "normal" if st.session_state.vault >= 0 else "inverse"
    st.metric("رصيد السيرفر", st.session_state.vault, delta=SYMBOLS[st.session_state.history[-1]]['value'] if st.session_state.history else 0, delta_color=v_color)
with col2:
    missing_big = 0
    if st.session_state.history:
        bigs = [7, 8]
        found = [i for i, x in enumerate(reversed(st.session_state.history)) if x in bigs]
        missing_big = found[0] if found else len(st.session_state.history)
    st.metric("غياب الجوائز", f"{missing_big} جولة")

# --- لوحة التحكم (الأزرار) ---
st.write("### 🔘 أدخل النتيجة الحالية:")
rows = [list(SYMBOLS.keys())[0:4], list(SYMBOLS.keys())[4:8]]
for row in rows:
    cols = st.columns(4)
    for i, code in enumerate(row):
        if cols[i].button(SYMBOLS[code]['name']):
            process_entry(code)
            st.rerun()

# --- رادار الـ Jackpot والتنبيه الصوتي ---
# --- بداية الجزء المستبدل ---
st.divider()

# 1. رادار الـ Jackpot والتنبيه الصوتي
st.subheader("🎯 رادار الصيد والتحليل")

# حساب غياب الجوائز بشكل أدق للعرض
missing_big = 0
if st.session_state.history:
    bigs = [7, 8]
    found = [i for i, x in enumerate(reversed(st.session_state.history)) if x in bigs]
    missing_big = found[0] if found else len(st.session_state.history)

if missing_big > 40 and st.session_state.vault > 200:
    st.warning("🔥 **تنبيه صيد:** السيرفر مشحون والجوائز غائبة! استعد.")
    st.components.v1.html("""<audio autoplay><source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg"></audio>""", height=0)
else:
    st.info(f"📡 الرادار يراقب... (غياب الرموز الكبرى: {missing_big} جولة)")

# 2. تحليل النمط وتوقعات AI
col_a, col_b = st.columns(2)

with col_a:
    st.write("**📜 آخر 5 نتائج:**")
    if len(st.session_state.history) > 0:
        recent = [SYMBOLS[c]['name'] for c in st.session_state.history[-5:]]
        st.success(" ← ".join(recent))
    else:
        st.write("بانتظار الإدخال...")

with col_b:
    st.write("**📊 حالة الغرفة:**")
    if len(st.session_state.history) < 5:
        st.write("تحليل النمط (0/5)...")
    else:
        # حساب بسيط للتقلب (Vibe)
        diffs = [abs(st.session_state.history[i] - st.session_state.history[i-1]) for i in range(1, len(st.session_state.history))]
        avg_vibe = sum(diffs[-5:]) / 5
        if avg_vibe > 3:
            st.error("متقلبة جداً 🔥")
        else:
            st.success("مستقرة ⚖️")

# 3. زر التراجع والمسح
st.divider()
c1, c2 = st.columns(2)
with c1:
    if st.button("↩️ تراجع (Undo)"):
        if st.session_state.history:
            last = st.session_state.history.pop()
            st.session_state.vault -= SYMBOLS[last]['value']
            st.rerun()
with c2:
    if st.button("🗑️ مسح الكل (Reset)"):
        st.session_state.history = []
        st.session_state.vault = 0
        st.rerun()

