import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Pro Financial Radar x45", page_icon="📊", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 45px; font-weight: bold; border-radius: 8px; }
    .finance-box { padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 15px; border: 1px solid #333; }
    .profit { color: #00ff00; font-size: 20px; font-weight: bold; }
    .loss { color: #ff4b4b; font-size: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# تعريف الرموز والضرب
SYMBOLS = {
    1: {"name": "🍅 طماطم", "mult": 5}, 2: {"name": "🌽 ذرة", "mult": 5},
    3: {"name": "🥕 جزر", "mult": 5}, 4: {"name": "🫑 فلفل", "mult": 5},
    5: {"name": "🐔 دجاجة", "mult": 45}, 6: {"name": "🐄 بقر", "mult": 15},
    7: {"name": "🐟 سمك", "mult": 25}, 8: {"name": "🦐 روبيان", "mult": 10},
    9: {"name": "💰 جاكبوت", "mult": 100}
}

# تهيئة الجلسة
if 'history' not in st.session_state:
    st.session_state.update({'history': [], 'total_net': 0})

def process_round(winner_code, bets):
    # إجمالي ما صرفته في هذه الجولة
    total_bet_this_round = sum(bets.values())
    # الربح من العنصر الذي ظهر فعلياً
    win_amount = bets.get(winner_code, 0) * SYMBOLS[winner_code]["mult"]
    # الصافي (ربح - إجمالي الرهانات)
    net = win_amount - total_bet_this_round
    st.session_state.total_net += net
    st.session_state.history.append(winner_code)

# --- الواجهة ---
st.title("📊 رادار الحساب المالي الدقيق v25.0")

# --- لوحة المراهنة (تحديد المبالغ) ---
st.subheader("💰 1. حدد مبالغ الرهان لهذه الجولة:")
with st.expander("فتح لوحة الرهانات", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        bet_veg = st.number_input("الرهان على كل نوع خضار (x5):", min_value=0, value=0, step=5)
        bet_hen = st.number_input("الرهان على الدجاجة (x45):", min_value=0, value=0, step=5)
        bet_fish = st.number_input("الرهان على السمك (x25):", min_value=0, value=0, step=5)
    with col2:
        bet_cow = st.number_input("الرهان على البقر (x15):", min_value=0, value=0, step=5)
        bet_shrimp = st.number_input("الرهان على الروبيان (x10):", min_value=0, value=0, step=5)
        bet_jack = st.number_input("الرهان على الجاكبوت (x100):", min_value=0, value=0, step=5)

# تجميع الرهانات في قاموس
current_bets = {
    1: bet_veg, 2: bet_veg, 3: bet_veg, 4: bet_veg,
    5: bet_hen, 6: bet_cow, 7: bet_fish, 8: bet_shrimp, 9: bet_jack
}

# --- تسجيل النتيجة ---
st.divider()
st.subheader("🔘 2. اضغط العنصر الذي ظهر:")
c1, c2, c3, c4 = st.columns(4)
for i in range(1, 5):
    with [c1, c2, c3, c4][i-1]:
        if st.button(SYMBOLS[i]["name"]): process_round(i, current_bets); st.rerun()

b1, b2, b3, b4 = st.columns(4)
if b1.button("🐔 دجاجة"): process_round(5, current_bets); st.rerun()
if b2.button("🐟 سمك"): process_round(7, current_bets); st.rerun()
if b3.button("🐄 بقر"): process_round(6, current_bets); st.rerun()
if b4.button("🦐 روبيان"): process_round(8, current_bets); st.rerun()

if st.button("🌟 JACKPOT 🌟"): process_round(9, current_bets); st.rerun()

# --- عرض النتائج المالية ---
st.divider()
net_val = st.session_state.total_net
status_class = "profit" if net_val >= 0 else "loss"

st.markdown(f"""
    <div class="finance-box">
        إجمالي صافي الربح/الخسارة الحقيقي حتى الآن:<br>
        <span class="{status_class}">{net_val} نقطة</span>
    </div>
""", unsafe_allow_html=True)

# عداد الغياب
super_targets = [5, 7] 
found = [i for i, x in enumerate(reversed(st.session_state.history)) if x in super_targets]
dist = found[0] if found else len(st.session_state.history)
st.metric("غياب (x45/x25)", f"{dist} جولة")

# --- التحكم ---
if st.button("🗑️ تصغير السجل والميزانية"):
    st.session_state.update({'history': [], 'total_net': 0})
    st.rerun()
