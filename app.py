import streamlit as st

# --- 1. الإعدادات العامة ---
st.set_page_config(page_title="Greedy AI v106.2", page_icon="💎", layout="centered")

# --- 2. تهيئة الذاكرة (لضمان حفظ البيانات عند تحديث الصفحة) ---
if 'history' not in st.session_state:
    st.session_state.history = []
    st.session_state.hits = 0
    st.session_state.misses = 0
    st.session_state.preds_history = []
    st.session_state.action_hit = []
    st.session_state.max_streak = 0
    st.session_state.cur_streak = 0
    st.session_state.balance = 0
    st.session_state.fingerprint = "بدء التحليل..."

# مصفوفة الرموز والمضاعفات
SYMBOLS = {1: "🍅", 2: "🌽", 3: "🥕", 4: "🫑", 5: "🐔", 6: "🐑", 7: "🐟", 8: "🦐", 9: "💰"}
MULT = {1: 5, 2: 5, 3: 5, 4: 5, 5: 45, 6: 15, 7: 25, 8: 10, 9: 0}

# --- 3. المحرك المالي والحسابات ---
def register_result(code, b_q, b_i):
    # حفظ التوقعات الحالية قبل تسجيل النتيجة (من أجل زر التراجع)
    current_preds = list(st.session_state.preds)
    st.session_state.preds_history.append(current_preds)
    
    is_quad = code in current_preds[:4]
    is_ins = (len(current_preds) > 4 and code == current_preds[4])
    is_hit = is_quad or is_ins
    
    # تفعيل الحساب المالي بعد الجولة 30
    if len(st.session_state.history) >= 30:
        cost = (b_q * 4) + b_i
        win = 0
        if is_quad:
            win = b_q * MULT[code]
        elif is_ins:
            win = b_i * MULT[code]
        
        # إضافة الصافي (الربح - التكلفة) للرصيد
        st.session_state.balance += (win - cost)
    
    # تحديث إحصائيات الفوز والخسارة
    if is_hit:
        st.session_state.hits += 1
        st.session_state.cur_streak += 1
        st.session_state.max_streak = max(st.session_state.max_streak, st.session_state.cur_streak)
    else:
        if code != 9:
            st.session_state.misses += 1
            st.session_state.cur_streak = 0
            
    st.session_state.history.append(code)
    st.session_state.action_hit.append(is_hit)

# --- 4. محرك التوقعات (ميزان + وزن زمني) ---
hist = st.session_state.history
total_h = len(hist)

if total_h > 0:
    # حساب الوزن الزمني (تركيز 75% على آخر 15 جولة)
    scores = {}
    for c in range(1, 9):
        freq = (hist[-5:].count(c) * 3.0 + hist[-15:].count(c))
        gap = list(reversed(hist)).index(c) if c in hist else total_h
        scores[c] = (freq * 0.75) + (gap * 0.25)
    
    # ميزة الميزان الرقمي: منع سيطرة اللحوم وتعزيز الخضار
    meat_in_quad = sum(1 for p in (st.session_state.preds if 'preds' in st.session_state else [1,2,3,4])[:4] if p >= 5)
    if meat_in_quad >= 3 or hist[-1] >= 5:
        for i in range(5, 9): scores[i] *= 0.5
        for i in range(1, 5): scores[i] *= 1.8
    
    top = sorted(scores, key=scores.get, reverse=True)
    st.session_state.preds = top[:4]
    
    # تحديد عنصر التأمين (أقوى لحم خارج المربع)
    ins_item = next((m for m in [5, 6, 7, 8] if m not in top[:4]), 5)
    st.session_state.preds.append(ins_item)
    
    # نسب الاحتمالية للعرض
    mx = max(scores.values()) if scores.values() else 1
    probs = {i: int((scores[i]/mx)*100) for i in range(1, 9)}
    
    # ميزة بصمة السيرفر
    m_count = sum(1 for x in hist[-10:] if x >= 5)
    if m_count > 6: st.session_state.fingerprint = "🚨 بصمة: ضغط لحوم عالٍ"
    elif m_count < 3: st.session_state.fingerprint = "🥗 بصمة: استقرار خضار"
    else: st.session_state.fingerprint = "⚖️ بصمة: سيرفر متوازن"
else:
    st.session_state.preds = [1, 2, 3, 4, 5]
    probs = {i: 0 for i in range(1, 9)}

# --- 5. الواجهة الرسومية (CSS + التصميم الموحد) ---
st.markdown("""<style>
    .main-box { background: #1a1a1a; border: 2px solid #39ff14; padding: 12px; border-radius: 15px; text-align: center; }
    .finance-bar { display: flex; justify-content: space-between; background: #000; padding: 8px; border-radius: 10px; border: 1px solid #444; margin: 8px 0; }
    .mini-card { background: #111; border: 1px solid #444; padding: 4px; border-radius: 6px; text-align: center; color: white; font-size: 11px; font-weight: bold; }
    .finger-tag { background: #001a33; color: #00aaff; border: 1px dashed #00aaff; border-radius: 5px; font-size: 10px; padding: 4px; margin-top: 5px; font-weight: bold; }
</style>""", unsafe_allow_html=True)

# الضبط المالي
with st.expander("📊 الضبط المالي", expanded=(total_h < 31)):
    c1, c2, c3 = st.columns(3)
    cap = c1.number_input("المحفظة", value=4400)
    bq = c2.number_input("المربع", value=50)
    bi = c3.number_input("التأمين", value=100)

# بار الرصيد
st.markdown(f'<div class="finance-bar">'
            f'<div><small style="color:#777;">الرصيد</small><br><b>{cap + st.session_state.balance}</b></div>'
            f'<div><small style="color:#777;">الربح الصافي</small><br><b style="color:{"#39ff14" if st.session_state.balance >= 0 else "#ff4b4b"}">{st.session_state.balance:+}</b></div>'
            f'<div><small style="color:#777;">الحالة</small><br><b style="color:#ffaa00;">{"نشط ✅" if total_h >= 30 else "إحماء ⏳"}</b></div></div>', unsafe_allow_html=True)

# صندوق التوقعات والبصمة
st.markdown(f'<div class="main-box"><div style="color:#39ff14; font-size:11px; font-weight:bold; margin-bottom:5px;">🎯 المربع الذهبي</div>'
            f'<div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:6px;">' + 
            "".join([f'<div style="background:#002200; border:1px solid #39ff14; padding:5px; border-radius:8px;">{SYMBOLS[c]}<div style="font-size:8px;">{probs[c]}%</div></div>' for c in st.session_state.preds[:4]]) + 
            f'</div><div class="finger-tag">{st.session_state.fingerprint}</div></div>', unsafe_allow_html=True)

# التأمين وآخر جولات
ins_code = st.session_state.preds[4]
last_5_html = "".join([f'<span style="margin-left:4px;">{SYMBOLS[c]}</span>' for c in hist[-5:]])
st.markdown(f'<div style="display:flex; gap:8px; margin: 10px 0;"><div style="width:75px; background:#111; border:1px solid #00aaff; border-radius:10px; text-align:center;"><small style="color:#00aaff; font-size:9px;">🛡️ تأمين</small><br><span style="font-size:18px;">{SYMBOLS[ins_code]}</span></div>'
            f'<div style="flex:1; background:#111; border-radius:10px; border:1px solid #333; display:flex; align-items:center; justify-content:center; font-size:22px;">{last_5_html if last_5_html else "..."}</div></div>', unsafe_allow_html=True)

# أزرار الإدخال
r1, r2 = st.columns(5), st.columns(4)
for i, c in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[c], key=f"btn1_{c}"): register_result(c, bq, bi); st.rerun()
for i, c in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[c], key=f"btn2_{c}"): register_result(c, bq, bi); st.rerun()

# --- 6. الرادار السفلي ---
h10_stat = sum(1 for x in st.session_state.action_hit[-10:] if x)
is_shifted = (len(st.session_state.action_hit) >= 3 and all(x is False for x in st.session_state.action_hit[-3:]) and total_h > 10)
signal = "STOP 🔴" if (total_h > 10 and h10_stat < 3) or is_shifted else ("GO 🟢" if h10_stat >= 5 else "WAIT 🟡")

st.markdown(f'<div style="display:grid; grid-template-columns: repeat(4, 1fr); gap: 4px; margin-bottom: 8px;">'
            f'<div class="mini-card">📡 {"تكيف" if is_shifted else "مستقر"}</div>'
            f'<div class="mini-card">🚨 {"غدر" if h10_stat < 4 else "آمن"}</div>'
            f'<div class="mini-card">🏆 {st.session_state.max_streak}</div>'
            f'<div class="mini-card">🚥 {signal}</div></div>', unsafe_allow_html=True)

# أزرار التحكم
c_undo, c_round, c_hit, c_miss = st.columns([0.8, 1, 1, 1])
if c_undo.button("↩️"):
    if st.session_state.history:
        l_code = st.session_state.history.pop()
        l_stat = st.session_state.action_hit.pop()
        l_preds = st.session_state.preds_history.pop()
        if len(st.session_state.history) >= 29:
            c_cost = (bq * 4) + bi
            is_q = l_code in l_preds[:4]
            is_i = (len(l_preds) > 4 and l_code == l_preds[4])
            c_win = (bq * MULT[l_code]) if is_q else ((bi * MULT[l_code]) if is_i else 0)
            st.session_state.balance -= (c_win - c_cost)
        if l_stat: st.session_state.hits -= 1
        else: st.session_state.misses -= 1
        st.rerun()

c_round.markdown(f'<div class="mini-card">🔄 جولة<br>{total_h}</div>', unsafe_allow_html=True)
c_hit.markdown(f'<div class="mini-card" style="color:#39ff14;">✅ صح<br>{st.session_state.hits}</div>', unsafe_allow_html=True)
c_miss.markdown(f'<div class="mini-card" style="color:#ff4b4b;">❌ خطأ<br>{st.session_state.misses}</div>', unsafe_allow_html=True)
