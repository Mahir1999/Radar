import streamlit as st
import pandas as pd

# --- إعدادات الصفحة الاحترافية ---
st.set_page_config(page_title="Ultra AI Radar v34", page_icon="🏆", layout="centered")

# --- تنسيق الواجهة (CSS) ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 48px; font-weight: bold; border-radius: 10px; transition: 0.3s; }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 4px 15px rgba(57, 255, 20, 0.3); }
    .prediction-header { 
        padding: 20px; background: linear-gradient(135deg, #000 0%, #111 100%); 
        border: 2px solid #39ff14; border-radius: 15px; text-align: center; margin-bottom: 15px;
    }
    .prediction-text { color: #39ff14; font-size: 28px; font-weight: bold; text-shadow: 0 0 10px #39ff14; }
    .advisor-box { padding: 15px; border-radius: 12px; text-align: center; font-weight: bold; margin-bottom: 20px; border: 2px solid; }
    .safe { background: #001a00; border-color: #00ff00; color: #00ff00; }
    .warning { background: #1a1a00; border-color: #ffff00; color: #ffff00; }
    .danger { background: #2b0000; border-color: #ff4b4b; color: #ff4b4b; animation: pulse 1s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.7; } 100% { opacity: 1; } }
    .finance-card { background: #111; padding: 10px; border-radius: 10px; border: 1px solid #333; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- تعريف الرموز وقيم الضرب ---
SYMBOLS = {
    1: {"name": "🍅 طماطم", "mult": 5}, 2: {"name": "🌽 ذرة", "mult": 5},
    3: {"name": "🥕 جزر", "mult": 5}, 4: {"name": "🫑 فلفل", "mult": 5},
    5: {"name": "🐔 دجاجة", "mult": 45}, 6: {"name": "🐄 بقر", "mult": 15},
    7: {"name": "🐟 سمك", "mult": 25}, 8: {"name": "🦐 روبيان", "mult": 10},
    9: {"name": "💰 جاكبوت", "mult": 100}
}

# --- إدارة الجلسة (الذاكرة المستمرة) ---
if 'history' not in st.session_state: st.session_state.history = []
if 'total_net' not in st.session_state: st.session_state.total_net = 0

def process_round(winner_code, bets):
    total_bet = sum(bets.values())
    win_amount = bets.get(winner_code, 0) * SYMBOLS[winner_code]["mult"]
    st.session_state.total_net += (win_amount - total_bet)
    st.session_state.history.append(winner_code)

# --- نافذة التحليل اللحظي (آخر 50 جولة) ---
full_h = st.session_state.history
active_window = full_h[-50:] if len(full_h) > 50 else full_h

# --- العناوين الرئيسية ---
st.title("🏆 رادار الصياد الذكي v34.0")

# --- 1. قسم التوقع والمستشار (الأهم) ---
if len(active_window) >= 10:
    last_code = active_window[-1]
    next_opts = [active_window[i+1] for i in range(len(active_window)-1) if active_window[i] == last_code]
    
    # حساب الاحتمالية
    if next_opts:
        pred_code = max(set(next_opts), key=next_opts.count)
        prob = int((next_opts.count(pred_code) / len(next_opts)) * 100)
        
        # عرض التوقع
        st.markdown(f"""
            <div class="prediction-header">
                <span style="color:#888; font-size:14px;">التوقع اللحظي القادم (ثقة {prob}%)</span><br>
                <span class="prediction-text">{SYMBOLS[pred_code]['name']}</span>
            </div>
        """, unsafe_allow_html=True)

        # المستشار الذكي
        found_big = [i for i, x in enumerate(reversed(full_h)) if x in [5, 7, 9]]
        dist = found_big[0] if found_big else len(full_h)
        
        if dist > 45 and prob > 55:
            st.markdown('<div class="advisor-box danger">🔥 هجوم (MAX BET): السيرفر في ذروة الانفجار والنمط متطابق!</div>', unsafe_allow_html=True)
        elif prob > 40 or dist > 30:
            st.markdown('<div class="advisor-box warning">⚠️ رهان متوسط: المؤشرات إيجابية، راهن بحذر.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="advisor-box safe">🛡️ رهان آمن: السيرفر هادئ، لا تندفع.</div>', unsafe_allow_html=True)
    else:
        st.info("🔄 السيرفر في نمط جديد تماماً، سجل الجولة القادمة للتحليل.")
else:
    st.warning(f"📡 اجمع {10 - len(active_window)} جولات إضافية لتفعيل التوقع الذكي.")

# --- 2. عداد الطاقة والمالية ---
col_m1, col_m2 = st.columns(2)
with col_m1:
    found_big = [i for i, x in enumerate(reversed(full_h)) if x in [5, 7, 9]]
    dist = found_big[0] if found_big else len(full_h)
    burst = min(100, int((dist / 60) * 100))
    st.write(f"🔋 شحن الجائزة: {burst}%")
    st.progress(burst / 100)
with col_m2:
    net = st.session_state.total_net
    c = "#39ff14" if net >= 0 else "#ff4b4b"
    st.markdown(f'<div class="finance-card">صافي الربح الكلي<br><b style="color:{c}; font-size:20px;">{net}</b></div>', unsafe_allow_html=True)

# --- 3. لوحة الرهان المفصلة ---
with st.expander("📝 إدارة مبالغ الرهان لهذه الجولة", expanded=False):
    st.write("**🥗 الخضروات (x5):**")
    v1, v2, v3, v4 = st.columns(4)
    bt = v1.number_input("🍅", 0, 1000, 0, 5)
    bc = v2.number_input("🌽", 0, 1000, 0, 5)
    ba = v3.number_input("🥕", 0, 1000, 0, 5)
    bp = v4.number_input("🫑", 0, 1000, 0, 5)
    st.divider()
    st.write("**🏆 الأهداف الكبرى:**")
    h1, h2, h3 = st.columns(3)
    b_hen = h1.number_input("🐔 (x45)", 0, 1000, 0, 5)
    b_fis = h2.number_input("🐟 (x25)", 0, 1000, 0, 5)
    b_cow = h3.number_input("🐄 (x15)", 0, 1000, 0, 5)
    
current_bets = {1:bt, 2:bc, 3:ba, 4:bp, 5:b_hen, 7:b_fis, 6:b_cow, 8:0, 9:0}

# --- 4. أزرار تسجيل النتائج ---
st.subheader("🔘 سجل النتيجة التي ظهرت:")
row1 = st.columns(4)
for i in range(1, 5):
    if row1[i-1].button(SYMBOLS[i]["name"]): process_round(i, current_bets); st.rerun()

row2 = st.columns(5)
for i, code in enumerate([5, 7, 6, 8, 9]):
    if row2[i].button(SYMBOLS[code]["name"].split()[0]): process_round(code, current_bets); st.rerun()

# --- 5. شريط التحكم ---
st.sidebar.title("⚙️ التحكم")
if st.sidebar.button("🗑️ مسح الجلسة وتصفير"):
    st.session_state.history = []; st.session_state.total_net = 0; st.rerun()
if st.sidebar.button("↩️ تراجع عن آخر جولة"):
    if st.session_state.history: st.session_state.history.pop(); st.rerun()

st.sidebar.divider()
st.sidebar.write(f"📜 سجل الجولات: {len(full_h)}")
if len(full_h) > 0:
    st.sidebar.write("آخر 10 نتائج:")
    st.sidebar.code(" | ".join([SYMBOLS[x]["name"].split()[0] for x in full_h[-10:]]))
