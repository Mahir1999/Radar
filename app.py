import streamlit as st

# --- 1. الإعدادات الأساسية للواجهة ---
st.set_page_config(
    page_title="Greedy AI Mastermind",
    page_icon="💎",
    layout="centered"
)

# --- 2. تهيئة الذاكرة التاريخية (ضمان عدم ضياع البيانات) ---
if 'history' not in st.session_state:
    st.session_state.update({
        'history': [],           # سجل الرموز
        'hits': 0,              # عدد المرات الناجحة
        'misses': 0,            # عدد مرات الإخفاق
        'preds_history': [],    # سجل التوقعات للتراجع
        'action_hit': [],       # هل كانت الجولة فوز؟
        'max_streak': 0,        # أعلى سلسلة فوز
        'cur_streak': 0,        # السلسلة الحالية
        'balance': 0,           # الصافي المالي
        'fingerprint': "بدء تحليل النمط...",
        'preds': [5, 7, 6, 8, 1] # التوقعات الافتراضية
    })

# مصفوفة الرموز والمضاعفات (القيم الثابتة)
SYMBOLS = {1: "🍅", 2: "🌽", 3: "🥕", 4: "🫑", 5: "🐔", 6: "🐑", 7: "🐟", 8: "🦐", 9: "💰"}
MULT = {1: 5, 2: 5, 3: 5, 4: 5, 5: 45, 6: 15, 7: 25, 8: 10, 9: 0}

# --- 3. المحرك المالي التفصيلي ---
def register_result(code, b_q, b_i):
    """دالة تسجيل النتائج وحساب الأرباح والخسائر بدقة"""
    current_preds = list(st.session_state.preds)
    st.session_state.preds_history.append(current_preds)
    
    # تحديد نوع الفوز (مربع ذهبي أم تأمين)
    is_quad = code in current_preds[:4]
    is_ins = (len(current_preds) > 4 and code == current_preds[4])
    is_hit = is_quad or is_ins
    
    # حساب التكلفة والربح
    cost = (b_q * 4) + b_i
    win = 0
    if is_quad:
        win = b_q * MULT[code]
    elif is_ins:
        win = b_i * MULT[code]
    
    # تحديث الصافي المالي
    st.session_state.balance += (win - cost)
    
    # تحديث الإحصائيات العامة
    if is_hit:
        st.session_state.hits += 1
        st.session_state.cur_streak += 1
        st.session_state.max_streak = max(st.session_state.max_streak, st.session_state.cur_streak)
    else:
        if code != 9: # لا نحسب الخنزير كخسارة في بعض الأنماط ولكن هنا نسجله
            st.session_state.misses += 1
            st.session_state.cur_streak = 0
            
    st.session_state.history.append(code)
    st.session_state.action_hit.append(is_hit)

# --- 4. خوارزمية التوقع العميقة (Deep Analytics) ---
hist = st.session_state.history
total_h = len(hist)
advice = "بانتظار البيانات..."

if total_h > 0:
    # حساب قوة الرموز بناءً على الوزن الزمني والفجوات
    scores = {}
    for c in range(1, 9):
        # 1. تكرار الرمز في آخر 15 جولة
        freq_weight = hist[-15:].count(c) * 2.5
        # 2. طول الغياب (Gap)
        gap = list(reversed(hist)).index(c) if c in hist else total_h
        # 3. دمج المعايير
        scores[c] = freq_weight + (gap * 1.5)
    
    # منطق "الميزان الرقمي": كشف حالات التجفيف (الخضار المتكرر)
    last_4 = hist[-4:] if total_h >= 4 else []
    is_drying = all(x <= 4 for x in last_4) if last_4 else False
    
    if is_drying:
        # إذا كان هناك تجفيف، نرفع احتمالية اللحوم للدرجة القصوى
        scores[5] *= 4.0 # الدجاجة
        scores[7] *= 3.0 # السمك
        scores[6] *= 2.5 # الخروف
        advice = "🚨 هجوم: السيرفر في منطقة ارتداد لحوم!"
        st.session_state.fingerprint = "🔥 نمط: ارتداد عنيف"
    else:
        advice = "🟢 توازن: العب بنمط المربع المعتاد"
        st.session_state.fingerprint = "⚖️ نمط: سيرفر مستقر"

    # ترتيب التوقعات
    top_candidates = sorted(scores, key=scores.get, reverse=True)
    st.session_state.preds = top_candidates[:4]
    
    # تحديد عنصر التأمين (أقوى عنصر خارج المربع)
    st.session_state.preds.append(next((m for m in [5, 7, 8, 6] if m not in top_candidates[:4]), 5))
    
    # حساب النسب المئوية للعرض الرسومي
    mx_score = max(scores.values()) if scores.values() else 1
    probs = {i: int((scores[i]/mx_score)*100) for i in range(1, 9)}
else:
    probs = {i: 0 for i in range(1, 9)}

# --- 5. التصميم الرسومي (CSS) ---
st.markdown("""
<style>
    .master-box {
        border: 2px solid #39ff14;
        background: linear-gradient(180deg, #121212 0%, #000000 100%);
        padding: 20px;
        border-radius: 25px;
        text-align: center;
        box-shadow: 0px 0px 30px rgba(57, 255, 20, 0.15);
    }
    .finance-grid {
        display: flex;
        justify-content: space-between;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid #333;
    }
    .quad-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-top: 15px;
    }
    .symbol-card {
        background: #0a0a0a;
        border: 1px solid #333;
        padding: 10px;
        border-radius: 12px;
        transition: 0.3s;
    }
    .symbol-card-active {
        border: 1px solid #39ff14;
        background: #001a00;
    }
    .advice-tag {
        background: #002200;
        color: #39ff14;
        padding: 8px;
        border-radius: 10px;
        font-size: 14px;
        margin-top: 15px;
        font-weight: bold;
        border: 1px dashed #39ff14;
    }
</style>
""", unsafe_allow_html=True)

# --- 6. عرض الواجهة ---
with st.expander("🛠️ إعدادات المحرك والسيولة"):
    col1, col2, col3 = st.columns(3)
    wallet = col1.number_input("المحفظة", value=4400)
    bet_q = col2.number_input("مبلغ المربع", value=50)
    bet_i = col3.number_input("مبلغ التأمين", value=100)

# الصندوق الموحد (The Master Box)
st.markdown('<div class="master-box">', unsafe_allow_html=True)

# صف الحالة المالية
st.markdown(f'''
<div class="finance-grid">
    <div style="color:#aaa;">الرصيد الكلي:<br><b style="color:white; font-size:18px;">{wallet + st.session_state.balance}</b></div>
    <div style="color:#aaa;">صافي الربح:<br><b style="color:{"#39ff14" if st.session_state.balance >= 0 else "#ff4b4b"}; font-size:18px;">{st.session_state.balance:+}</b></div>
</div>
''', unsafe_allow_html=True)

# المربع الذهبي
st.markdown('<div style="color:#39ff14; font-size:14px; font-weight:bold;">🎯 التوقعات الذكية (المربع الذهبي)</div>', unsafe_allow_html=True)
st.markdown('<div class="quad-grid">', unsafe_allow_html=True)
for p in st.session_state.preds[:4]:
    st.markdown(f'''
    <div class="symbol-card symbol-card-active">
        <span style="font-size:24px;">{SYMBOLS[p]}</span><br>
        <small style="color:#39ff14;">{probs[p]}%</small>
    </div>
    ''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# نصيحة النظام والبصمة
st.markdown(f'<div class="advice-tag">💡 {advice}</div>', unsafe_allow_html=True)

# شريط التأمين وآخر الجولات
st.markdown(f'''
<div style="display:flex; justify-content:space-between; margin-top:15px; align-items:center; background:#0a0a0a; padding:10px; border-radius:12px; border:1px solid #222;">
    <div style="text-align:left;"><small style="color:#00aaff;">🛡️ تأمين</small><br><span style="font-size:20px;">{SYMBOLS[st.session_state.preds[4]]}</span></div>
    <div style="font-size:18px;">{" ".join([SYMBOLS[x] for x in hist[-5:]]) if hist else "..."}</div>
    <div style="text-align:right;"><small style="color:#00aaff;">📡 البصمة</small><br><small style="color:white;">{st.session_state.fingerprint}</small></div>
</div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- 7. أزرار الإدخال والتحكم ---
st.write("")
row1 = st.columns(5)
row2 = st.columns(4)

for idx, c in enumerate([5, 7, 6, 8, 9]):
    if row1[idx].button(SYMBOLS[c], key=f"btn_h_{c}", use_container_width=True):
        register_result(c, bet_q, bet_i)
        st.rerun()

for idx, c in enumerate([1, 2, 3, 4]):
    if row2[idx].button(SYMBOLS[c], key=f"btn_l_{c}", use_container_width=True):
        register_result(c, bet_q, bet_i)
        st.rerun()

# أزرار التراجع والإحصائيات السفلية
st.markdown("---")
c_undo, c_stat1, c_stat2, c_stat3 = st.columns([1, 1, 1, 1])

if c_undo.button("↩️ تراجع"):
    if st.session_state.history:
        last_code = st.session_state.history.pop()
        last_action = st.session_state.action_hit.pop()
        last_preds = st.session_state.preds_history.pop()
        
        # عكس العملية المالية
        cost = (bet_q * 4) + bet_i
        is_q = last_code in last_preds[:4]
        is_i = (len(last_preds) > 4 and last_code == last_preds[4])
        win = (bet_q * MULT[last_code]) if is_q else ((bet_i * MULT[last_code]) if is_i else 0)
        st.session_state.balance -= (win - cost)
        
        if last_action: st.session_state.hits -= 1
        else: st.session_state.misses -= 1
        st.rerun()

c_stat1.metric("الجولات", total_h)
c_stat2.metric("صح", st.session_state.hits, delta_color="normal")
c_stat3.metric("خطأ", st.session_state.misses, delta_color="inverse")
