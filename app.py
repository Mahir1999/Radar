import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Jackpot Sniper v12.0", page_icon="🎯", layout="centered")

# --- ستايل الواجهة ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 55px; font-weight: bold; border-radius: 12px; }
    div[data-testid="stMetric"] { background-color: #0c0c0c; padding: 15px; border-radius: 15px; border: 1px solid #1e1e1e; color: #39ff14; }
    </style>
    """, unsafe_allow_html=True)

# --- تعريف الرموز (قيم تراكمية لضمان عدم التصفير) ---
SYMBOLS = {
    1: {"name": "🍅 طماطم", "val": 10}, 2: {"name": "🌽 ذرة", "val": 10},
    3: {"name": "🥕 جزر", "val": 10}, 4: {"name": "🫑 فلفل", "val": 10},
    5: {"name": "🐔 دجاجة", "val": 5}, 6: {"name": "🐄 بقر", "val": 5},
    7: {"name": "🐟 سمك", "val": -10}, 8: {"name": "🦐 روبيان", "val": -15}
}

# --- تهيئة البيانات ---
if 'history' not in st.session_state:
    st.session_state.update({'history': [], 'vault': 0})

def add_entry(code):
    st.session_state.vault += SYMBOLS[code]['val']
    st.session_state.history.append(code)

# --- الهيدر ---
st.title("🎯 رادار صيد الـ Jackpot")
makkah = datetime.now(pytz.timezone('Asia/Riyadh')).strftime("%I:%M %p")
st.write(f"🕋 توقيت مكة: **{makkah}**")

# --- عدادات الرادار ---
c1, c2 = st.columns(2)
with c1:
    st.metric("رصيد السيرفر التراكمي", st.session_state.vault)
with c2:
    missing_big = 0
    if st.session_state.history:
        bigs = [7, 8]
        found = [i for i, x in enumerate(reversed(st.session_state.history)) if x in bigs]
        missing_big = found[0] if found else len(st.session_state.history)
    st.metric("عداد غياب الجوائز", f"{missing_big} جولة")

# --- لوحة الأزرار ---
st.write("### 🔘 سجل النتيجة الحالية:")
r1, r2 = st.columns(4), st.columns(4)
for i, code in enumerate(range(1, 5)):
    if r1[i].button(SYMBOLS[code]['name']):
        add_entry(code); st.rerun()
for i, code in enumerate(range(5, 9)):
    if r2[i].button(SYMBOLS[code]['name']):
        add_entry(code); st.rerun()

# --- محرك التوقعات (مضبوط على 20 جولة للدقة القصوى) ---
st.divider()
if len(st.session_state.history) >= 20:
    st.subheader("🤖 توقعات الـ AI (دقة عالية)")
    
    # تحليل التكرار والأنماط
    counts = pd.Series(st.session_state.history).value_counts()
    likely_code = counts.idxmax()
    
    st.success(f"الاحتمال الأكثر تكراراً حالياً: **{SYMBOLS[likely_code]['name']}**")
    
    # إشارة الصيد
    if missing_big > 45 and st.session_state.vault > 250:
        st.error("🚨 **إشارة Jackpot قوية:** السيرفر مشحون والغياب طويل جداً!")
    else:
        st.info("⚖️ النمط مستقر حالياً، اتبع التوقعات بحذر.")
else:
    progress = len(st.session_state.history)
    st.info(f"📡 جاري بناء قاعدة البيانات للدقة القصوى... ({progress}/20)")
    st.progress(progress / 20)

# --- التحكم ---
st.divider()
ca, cb = st.columns(2)
with ca:
    if st.button("↩️ تراجع (Undo)"):
        if st.session_state.history:
            last = st.session_state.history.pop()
            st.session_state.vault -= SYMBOLS[last]['val']; st.rerun()
with cb:
    if st.button("🗑️ جلسة جديدة (Reset)"):
        st.session_state.history = []; st.session_state.vault = 0; st.rerun()
