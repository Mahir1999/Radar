import streamlit as st
import pandas as pd # أضفنا مكتبات لتحليل أعمق

# --- 1. الإعدادات المتقدمة للواجهة ---
st.set_page_config(
    page_title="Greedy AI - Ultimate Edition",
    page_icon="👑",
    layout="centered"
)

# --- 2. تهيئة الذاكرة الشاملة (ذاكرة لا تنسى) ---
if 'history' not in st.session_state:
    st.session_state.update({
        'history': [],            # سجل الرموز المدخلة
        'hits': 0,               # عدد مرات النجاح
        'misses': 0,             # عدد مرات الإخفاق
        'preds_history': [],     # تاريخ التوقعات (للتراجع)
        'action_hit': [],        # سجل الفوز/الخسارة لكل جولة
        'balance': 0,            # الصافي المالي التراكمي
        'max_streak': 0,         # أعلى سلسلة فوز
        'cur_streak': 0,         # السلسلة الحالية
        'fingerprint': "جاري مسح السيرفر...",
        'preds': [5, 7, 6, 8, 1], # التوقعات الحالية
        'anti_fraud_mode': False  # وضع كشف الغدر
    })

# مصفوفة الرموز والمضاعفات الثابتة
SYMBOLS = {1: "🍅", 2: "🌽", 3: "🥕", 4: "🫑", 5: "🐔", 6: "🐑", 7: "🐟", 8: "🦐", 9: "💰"}
MULT = {1: 5, 2: 5, 3: 5, 4: 5, 5: 45, 6: 15, 7: 25, 8: 10, 9: 0}

# --- 3. محرك الحسابات المالية الدقيق ---
def register_result(code, b_q, b_i):
    """دالة احترافية لمعالجة الجولة مالياً وإحصائياً"""
    # جلب آخر توقعات تم عرضها للمستخدم
    last_preds = list(st.session_state.preds)
    st.session_state.preds_history.append(last_preds)
    
    # فحص الفوز: هل الرمز في المربع الذهبي (أول 4) أم في التأمين (الخامس)؟
    is_quad = code in last_preds[:4]
    is_ins = (len(last_preds) > 4 and code == last_preds[4])
    is_hit = is_quad or is_ins
    
    # حسابات المحفظة
    cost = (b_q * 4) + b_i
    win = 0
    if is_quad:
        win = b_q * MULT[code]
    elif is_ins:
        win = b_i * MULT[code]
    
    # تحديث الصافي
    st.session_state.balance += (win - cost)
    
    # تحديث العدادات
    if is_hit:
        st.session_state.hits += 1
        st.session_state.cur_streak += 1
        st.session_state.max_streak = max(st.session_state.max_streak, st.session_state.cur_streak)
    else:
        if code != 9: # الخنزير يسجل كخسارة
            st.session_state.misses += 1
            st.session_state.cur_streak = 0
            
    st.session_state.history.append(code)
    st.session_state.action_hit.append(is_hit)

# --- 4. خوارزمية "العقل المدبر" (Mastermind Engine) ---
hist = st.session_state.history
total_h = len(hist)
msg = "العب بتركيز.."
risk_level = "Low"

if total_h > 0:
    # أ- حساب الأوزان التاريخية (Frequency & Recency)
    scores = {}
    for c in range(1, 9):
        # وزن التكرار القريب
        f_weight = hist[-10:].count(c) * 3.0
        # وزن الغياب (كل ما طال الغياب زاد الرقم)
        gap = list(reversed(hist)).index(c) if c in hist else total_h
        scores[c] = f_weight + (gap * 1.8)

    # ب- نظام كشف الغدر (Anti-Fraud System)
    # إذا آخر 3 جولات خسارة، السيرفر "غدار" حالياً
    last_3 = st.session_state.action_hit[-3:] if total_h >= 3 else [True]
    st.session_state.anti_fraud_mode = last_3.count(False) >= 2
    
    if st.session_state.anti_fraud_mode:
        # وضع الطوارئ: اللحاق بالنمط المكرر فوراً (خضار)
        msg = "⚠️ تنبيه: السيرفر يغدر! جاري اللحاق بالخضار.."
        risk_level = "HIGH"
        st.session_state.fingerprint = "🚨 نمط: سحب سيولة"
        # رفع الرموز اللي تكررت في آخر 5 جولات (لحاق بالنمط)
        for c in range(1, 5): 
            if hist[-5:].count(c) > 0: scores[c] *= 10.0
    else:
        # وضع الهجوم الطبيعي: مطاردة اللحوم
        veg_chain = sum(1 for x in hist[-4:] if x <= 4)
        if veg_chain >= 3:
            msg = "🚀 فرصة: ارتداد لحوم وشيك.. ضاعف الرهان!"
            scores[5] *= 5.0 # الدجاجة
            scores[7] *= 4.0 # السمك
            st.session_state.fingerprint = "🔥 نمط: انفجار مالي"
        else:
            msg = "🟢 السيرفر متزن.. استمر في اللعب"
            st.session_state.fingerprint = "⚖️ نمط: مستقر"

    # تصفية التوقعات النهائية
    top_candidates = sorted(scores, key=scores.get, reverse=True)
    st.session_state.preds = top_candidates[:4]
    
    # اختيار رمز التأمين (أفضل رمز خارج المربع الذهبي)
    st.session_state.preds.append(next((m for m in [5, 7, 1, 8, 6] if m not in top_candidates[:4]), 5))
    
    # حساب النسب المئوية للعرض
    mx = max(scores.values()) if scores.values() else 1
    probs = {i: int((scores[i]/mx)*100) for i in range(1, 9)}
else:
    probs = {i: 0 for i in range(1, 9)}

# --- 5. التصميم الجمالي المتقدم (CSS) ---
st.markdown(f"""
<style>
    .main-container {{
        border: 2px solid {'#ff4b4b' if st.session_state.anti_fraud_mode else '#39ff14'};
        background: linear-gradient(180deg, #111111 0%, #000000 100%);
        padding: 20px;
        border-radius: 25px;
        text-align: center;
        box-shadow: 0px 0px 35px {'rgba(255, 75, 75, 0.2)' if st.session_state.anti_fraud_mode else 'rgba(57, 255, 20, 0.2)'};
    }}
    .stat-row {{
        display: flex;
        justify-content: space-between;
        margin-bottom: 15px;
        border-bottom: 1px solid #333;
        padding-bottom: 10px;
    }}
    .quad-box {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        margin: 15px 0;
    }}
    .card {{
        background: #050505;
        border: 1px solid #222;
        padding: 12px;
        border-radius: 15px;
    }}
    .card-active {{
        border: 1px solid {'#ff4b4b' if st.session_state.anti_fraud_mode else '#39ff14'};
    }}
    .advice-bar {{
        background: {'#220000' if st.session_state.anti_fraud_mode else '#001a00'};
        color: {'#ff4b4b' if st.session_state.anti_fraud_mode else '#39ff14'};
        padding: 10px;
        border-radius: 12px;
        font-weight: bold;
        border: 1px dashed;
        margin-top: 15px;
    }}
</style>
""", unsafe_allow_html=True)

# --- 6. بناء الواجهة الرسومية ---
with st.expander("🛠️ إعدادات المحفظة والسيولة"):
    c1, c2, c3 = st.columns(3)
    init_cap = c1.number_input("رأس المال الصافي", value=4400)
    b_q = c2.number_input("مبلغ المربع", value=50)
    b_i = c3.number_input("مبلغ التأمين", value=100)

# الصندوق الموحد (Scorecard Box)
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# الجزء المالي
st.markdown(f'''
<div class="stat-row">
    <div style="color:#777;">الرصيد الكلي:<br><b style="color:white; font-size:20px;">{init_cap + st.session_state.balance}</b></div>
    <div style="color:#777;">الصافي اللحظي:<br><b style="color:{"#39ff14" if st.session_state.balance >= 0 else "#ff4b4b"}; font-size:20px;">{st.session_state.balance:+}</b></div>
</div>
''', unsafe_allow_html=True)

# عرض المربع الذهبي
st.markdown(f'<div style="color:#aaa; font-size:12px;">🎯 التوقعات (المربع الذهبي)</div>', unsafe_allow_html=True)
st.markdown('<div class="quad-box">', unsafe_allow_html=True)
for sym_code in st.session_state.preds[:4]:
    st.markdown(f'''
    <div class="card card-active">
        <span style="font-size:26px;">{SYMBOLS[sym_code]}</span><br>
        <small style="color:#aaa;">{probs[sym_code]}%</small>
    </div>
    ''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# بار النصيحة الذكية
st.markdown(f'<div class="advice-bar">{msg}</div>', unsafe_allow_html=True)

# المعلومات الإضافية (تأمين + بصمة + رادار)
st.markdown(f'''
<div style="display:flex; justify-content:space-between; margin-top:15px; background:#0a0a0a; padding:10px; border-radius:15px; border:1px solid #222;">
    <div style="text-align:left;"><small style="color:#00aaff;">🛡️ تأمين</small><br><span style="font-size:20px;">{SYMBOLS[st.session_state.preds[4]]}</span></div>
    <div style="text-align:center;"><small style="color:#00aaff;">📡 البصمة</small><br><small style="color:white;">{st.session_state.fingerprint}</small></div>
    <div style="text-align:right;"><small style="color:#00aaff;">🏆 الرادار</small><br><small style="color:white;">{st.session_state.max_streak}</small></div>
</div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # نهاية الصندوق الموحد

# --- 7. أزرار التحكم والإدخال ---
st.write("")
row_up = st.columns(5)
row_down = st.columns(4)

# صف الرموز العالية
for i, code in enumerate([5, 7, 6, 8, 9]):
    if row_up[i].button(SYMBOLS[code], key=f"btn_{code}", use_container_width=True):
        register_result(code, b_q, b_i)
        st.rerun()

# صف الرموز العادية
for i, code in enumerate([1, 2, 3, 4]):
    if row_down[i].button(SYMBOLS[code], key=f"btn_{code}", use_container_width=True):
        register_result(code, b_q, b_i)
        st.rerun()

# أدوات الإحصاء والتراجع
st.markdown("---")
c_rev, c_s1, c_s2, c_s3 = st.columns([1, 1, 1, 1])

if c_rev.button("↩️ تراجع"):
    if st.session_state.history:
        l_code = st.session_state.history.pop()
        l_act = st.session_state.action_hit.pop()
        l_preds = st.session_state.preds_history.pop()
        # عكس الحساب المالي
        c_cost = (b_q * 4) + b_i
        is_q = l_code in l_preds[:4]
        is_i = (len(l_preds) > 4 and l_code == l_preds[4])
        l_win = (b_q * MULT[l_code]) if is_q else ((b_i * MULT[l_code]) if is_i else 0)
        st.session_state.balance -= (l_win - c_cost)
        if l_act: st.session_state.hits -= 1
        else: st.session_state.misses -= 1
        st.rerun()

c_s1.metric("الجولات", total_h)
c_s2.metric("✅ فوز", st.session_state.hits)
c_s3.metric("❌ خسارة", st.session_state.misses)
