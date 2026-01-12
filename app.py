import streamlit as st
from datetime import datetime

# --- إعدادات الصفحة الاحترافية ---
st.set_page_config(page_title="AI Pro Radar v40", page_icon="🏆", layout="centered")

# --- تنسيق الواجهة المتقدم (CSS) ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 48px; font-weight: bold; border-radius: 10px; transition: 0.3s; }
    .status-card { padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 10px; border: 2px solid; }
    .payout-mode { background: #002b00; border-color: #39ff14; color: #39ff14; animation: pulse 2s infinite; }
    .collection-mode { background: #2b0000; border-color: #ff4b4b; color: #ff4b4b; }
    .prediction-card { background: #111; padding: 20px; border-radius: 15px; text-align: center; border: 1px solid #444; margin-top: 10px; }
    @keyframes pulse { 0% { box-shadow: 0 0 5px #39ff14; } 50% { box-shadow: 0 0 20px #39ff14; } 100% { box-shadow: 0 0 5px #39ff14; } }
    .trap-alert { padding: 10px; background: #451a00; border: 1px solid #ffaa00; color: #ffaa00; border-radius: 8px; font-size: 13px; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- تعريف البيانات الأساسية ---
SYMBOLS = {
    1: {"name": "🍅 طماطم", "mult": 5}, 2: {"name": "🌽 ذرة", "mult": 5},
    3: {"name": "🥕 جزر", "mult": 5}, 4: {"name": "🫑 فلفل", "mult": 5},
    5: {"name": "🐔 دجاجة", "mult": 45}, 6: {"name": "🐄 بقر", "mult": 15},
    7: {"name": "🐟 سمك", "mult": 25}, 8: {"name": "🦐 روبيان", "mult": 10},
    9: {"name": "💰 جاكبوت", "mult": 100}
}

# --- إدارة الذاكرة المستمرة ---
if 'history' not in st.session_state: st.session_state.history = []
if 'total_net' not in st.session_state: st.session_state.total_net = 0
if 'broken_patterns' not in st.session_state: st.session_state.broken_patterns = {}
if 'last_pred' not in st.session_state: st.session_state.last_pred = None

def register_result(code, bets):
    # 1. حساب المال
    total_bet = sum(bets.values())
    win_amount = bets.get(code, 0) * SYMBOLS[code]["mult"]
    st.session_state.total_net += (win_amount - total_bet)
    
    # 2. رصد كسر الأنماط (الأفخاخ)
    hist = st.session_state.history
    if st.session_state.last_pred and len(hist) > 0:
        prev_code = hist[-1]
        if st.session_state.last_pred != code:
            pattern_key = f"{prev_code}->{st.session_state.last_pred}"
            st.session_state.broken_patterns[pattern_key] = st.session_state.broken_patterns.get(pattern_key, 0) + 1
    
    # 3. تسجيل التاريخ
    st.session_state.history.append(code)
    st.session_state.last_pred = None

# --- الواجهة الرئيسية ---
st.title("🏆 رادار الصياد الذكي v40.0")

# --- ⏰ 1. ساعة توزيع الأرباح (Payout Clock) ---
current_min = datetime.now().minute
hist = st.session_state.history
last_20 = hist[-20:]
big_wins = [x for x in last_20 if x in [5, 6, 7, 9]]

if len(last_20) >= 10:
    if len(big_wins) >= 2:
        st.markdown(f'<div class="status-card payout-mode">🌟 وضع الدفع نشط: الدقيقة ({current_min}) مناسبة للهجوم</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-card collection-mode">🛑 وضع السحب نشط: الدقيقة ({current_min}) خطيرة جداً</div>', unsafe_allow_html=True)
else:
    st.info("📡 جاري تحليل دورة السيرفر اللحظية...")

# --- 🤖 2. رادار التوقعات وكاشف الأفخاخ ---
if len(hist) >= 10:
    last = hist[-1]
    active_window = hist[-50:]
    next_opts = [active_window[i+1] for i in range(len(active_window)-1) if active_window[i] == last]
    
    if next_opts:
        pred = max(set(next_opts), key=next_opts.count)
        prob = int((next_opts.count(pred) / len(next_opts)) * 100)
        st.session_state.last_pred = pred
        
        st.markdown(f"""
            <div class="prediction-card">
                <span style="color:#888; font-size:13px;">التوقع اللحظي (ثقة {prob}%)</span><br>
                <span style="color:#39ff14; font-size:26px; font-weight:bold;">{SYMBOLS[pred]['name']}</span>
            </div>
        """, unsafe_allow_html=True)
        
        # فحص الفخ
        pattern_key = f"{last}->{pred}"
        broken_count = st.session_state.broken_patterns.get(pattern_key, 0)
        if broken_count >= 1:
            st.markdown(f'<div class="trap-alert">⚠️ فخ مرصود: السيرفر كسر هذا النمط {broken_count} مرات سابقاً!</div>', unsafe_allow_html=True)
else:
    st.warning("📡 سجل 10 جولات لتفعيل رادار التوقعات.")

# --- 💰 3. لوحة الرهان الذكية (فصل كامل) ---
with st.expander("📝 إدارة رهاناتك (فصل الخضروات والأصناف)"):
    st.write("**🥗 قسم الخضروات (x5):**")
    v1, v2, v3, v4 = st.columns(4)
    b1 = v1.number_input("🍅", 0, 1000, 0, 5)
    b2 = v2.number_input("🌽", 0, 1000, 0, 5)
    b3 = v3.number_input("🥕", 0, 1000, 0, 5)
    b4 = v4.number_input("🫑", 0, 1000, 0, 5)
    
    st.write("**🔥 الأهداف الكبرى:**")
    h1, h2, h3 = st.columns(3)
    b5 = h1.number_input("🐔 (x45)", 0, 1000, 0, 5)
    b7 = h2.number_input("🐟 (x25)", 0, 1000, 0, 5)
    b6 = h3.number_input("🐄 (x15)", 0, 1000, 0, 5)

current_bets = {1:b1, 2:b2, 3:b3, 4:b4, 5:b5, 6:b6, 7:b7, 8:0, 9:0}

# --- 🔘 4. تسجيل النتائج ---
st.subheader("🔘 سجل ما ظهر الآن:")
r1 = st.columns(5)
for i, code in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[code]["name"].split()[0]): 
        register_result(code, current_bets); st.rerun()

r2 = st.columns(4)
for i in range(1, 5):
    if r2[i-1].button(SYMBOLS[i]["name"].split()[0]): 
        register_result(i, current_bets); st.rerun()

# --- 📊 5. الإحصائيات والتحكم ---
st.divider()
c_stat1, c_stat2 = st.columns(2)
with c_stat1:
    color = "#39ff14" if st.session_state.total_net >= 0 else "#ff4b4b"
    st.metric("صافي الربح الكلي", f"{st.session_state.total_net}", delta=None)
with c_stat2:
    found_big = [i for i, x in enumerate(reversed(hist)) if x in [5, 7]]
    dist = found_big[0] if found_big else len(hist)
    st.metric("غياب الجوائز الكبرى", f"{dist} جولة")

if st.sidebar.button("🗑️ تصفير الجلسة بالكامل"):
    st.session_state.clear(); st.rerun()
if st.sidebar.button("↩️ تراجع عن خطأ"):
    if st.session_state.history: st.session_state.history.pop(); st.rerun()
