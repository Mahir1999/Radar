import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Stable Radar v14.0", page_icon="🎯", layout="centered")

# --- ستايل الواجهة ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 50px; font-weight: bold; border-radius: 10px; }
    div[data-testid="stMetric"] { background-color: #0c0c0c; padding: 10px; border-radius: 12px; border: 1px solid #1e1e1e; color: #39ff14; }
    </style>
    """, unsafe_allow_html=True)

# --- تعريف الرموز (لاحظ: كل القيم أصبحت موجبة لضمان عدم التصفير) ---
SYMBOLS = {
    1: {"name": "🍅 طماطم", "val": 1}, 2: {"name": "🌽 ذرة", "val": 1},
    3: {"name": "🥕 جزر", "val": 1}, 4: {"name": "🫑 فلفل", "val": 1},
    5: {"name": "🐔 دجاجة", "val": 1}, 6: {"name": "🐄 بقر", "val": 1},
    7: {"name": "🐟 سمك", "val": 1}, 8: {"name": "🦐 روبيان", "val": 1}
}

# --- تهيئة البيانات (Session State) ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'vault' not in st.session_state:
    st.session_state.vault = 0

def add_entry(code):
    # إضافة القيمة للميزانية (دائماً جمع +)
    st.session_state.vault += SYMBOLS[code]['val']
    # إضافة الكود للسجل
    st.session_state.history.append(code)

# --- الواجهة ---
st.title("🎯 رادار الصيد المستقر")
makkah = datetime.now(pytz.timezone('Asia/Riyadh')).strftime("%I:%M %p")
st.write(f"🕋 مكة: **{makkah}**")

# عرض العدادات
c1, c2 = st.columns(2)
with c1:
    st.metric("رصيد العمليات", st.session_state.vault)
with c2:
    st.metric("إجمالي الجولات المسجلة", len(st.session_state.history))

# --- الأزرار ---
st.write("### 🔘 سجل النتيجة:")
r1, r2 = st.columns(4), st.columns(4)
for i, code in enumerate(range(1, 5)):
    if r1[i].button(SYMBOLS[code]['name']):
        add_entry(code)
        st.rerun()
for i, code in enumerate(range(5, 9)):
    if r2[i].button(SYMBOLS[code]['name']):
        add_entry(code)
        st.rerun()

# --- قسم التوقعات (يظهر دائماً الآن) ---
st.divider()
st.subheader("🤖 تحليل الرادار")

total_rounds = len(st.session_state.history)

if total_rounds >= 20:
    # حساب التوقع بناءً على أكثر عنصر تكراراً في السجل
    counts = pd.Series(st.session_state.history).value_counts()
    likely_code = counts.idxmax()
    st.success(f"✅ **التوقع القادم:** {SYMBOLS[likely_code]['name']}")
    st.info("الذكاء الاصطناعي يحلل الآن بناءً على دقة 20 جولة.")
else:
    # شريط التقدم للوصول لـ 20 جولة
    st.warning(f"⏳ جاري جمع البيانات.. سجلت {total_rounds} من أصل 20 جولة")
    st.progress(total_rounds / 20)

# --- سجل آخر 5 جولات ---
if total_rounds > 0:
    st.write("**📜 آخر 5 جولات:**")
    st.write(" ← ".join([SYMBOLS[c]['name'] for c in st.session_state.history[-5:]]))

# --- أزرار التحكم ---
st.divider()
ca, cb = st.columns(2)
with ca: 
    if st.button("↩️ تراجع (Undo)"):
        if st.session_state.history:
            last = st.session_state.history.pop()
            st.session_state.vault -= SYMBOLS[last]['val']
            st.rerun()
with cb:
    if st.button("🗑️ مسح الكل (Reset)"):
        st.session_state.history = []
        st.session_state.vault = 0
        st.rerun()
