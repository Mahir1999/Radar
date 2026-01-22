import streamlit as st

# --- 1. الإعدادات ---
st.set_page_config(page_title="Greedy AI v105.1", page_icon="🎯", layout="centered")

# --- 2. تهيئة الذاكرة المفصلة ---
if 'history' not in st.session_state:
    st.session_state.update({
        'history': [], 'hits': 0, 'misses': 0, 'cons_m': 0, 'p_count': 0,
        'preds': [1, 2, 3, 4, 5], 'action_hit': [], 'max_streak': 0,
        'cur_streak': 0, 'balance': 0, 'target': 1000, 'fingerprint': "تحليل البيانات..."
    })

SYMBOLS = {1: "🍅", 2: "🌽", 3: "🥕", 4: "🫑", 5: "🐔", 6: "🐑", 7: "🐟", 8: "🦐", 9: "💰"}
MULT = {1: 5, 2: 5, 3: 5, 4: 5, 5: 45, 6: 15, 7: 25, 8: 10, 9: 0}

# --- 3. المحرك المصلح (إصلاح التراجع + الحساب الدقيق) ---
def register_result(code, bq, bi):
    h = st.session_state.history
    is_quad = code in st.session_state.preds[:4]
    is_ins = (len(st.session_state.preds) > 4 and code == st.session_state.preds[4])
    is_hit = is_quad or is_ins
    
    # بصمة السيرفر الذكية
    if len(h) >= 10:
        m_count = sum(1 for x in h[-10:] if x >= 5)
        if m_count > 6: st.session_state.fingerprint = "🚨 بصمة: ضغط لحوم عالٍ"
        elif m_count < 3: st.session_state.fingerprint = "🥗 بصمة: استقرار خضار"
        else: st.session_state.fingerprint = "⚖️ بصمة: سيرفر متوازن"

    # حساب الأنماط المتكررة
    if len(h) >= 2:
        last_pair = [h[-1], code]
        for i in range(len(h) - 1):
            if h[i:i+2] == last_pair:
                st.session_state.p_count += 1
                break
    
    # الحساب المالي بعد الجولة 30
    if len(h) >= 30:
        cost = (bq * 4) + bi
        win = (bq * MULT[code]) if is_quad else ((bi * MULT[code]) if is_ins else 0)
        st.session_state.balance += (win - cost)
    
    # تحديث عدادات الفوز والخسارة
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

# --- 4. محرك التوقعات الدقيق (الوزن الزمني + الميزان) ---
hist = st.session_state.history
total_h = len(hist)
shift_active = (len(st.session_state.action_hit) >= 3 and all(x is False for x in st.session_state.action_hit[-3:]) and total_h > 10)

if total_h == 0:
    st.session_state.preds = [1, 2, 3, 4, 5]
    probs = {i: 10 for i in range(1, 9)}
else:
    recent_5 = hist[-5:]
    recent_15 = hist[-15:]
    scores = {}
    for c in range(1, 9):
        # ميزة الوزن الزمني: آخر 5 جولات تأثيرها أقوى 3 مرات
        time_weight = (recent_5.count(c) * 3.0) + (recent_15.count(c) * 1.0)
        gap = list(reversed(hist)).index(c) if c in hist else total_h
        scores[c] = (time_weight * 0.75) + (gap * 0.25)
    
    # ⚖️ الميزان الرقمي الذكي (يمنع السيطرة المطلقة للحوم)
    meat_in_quad = sum(1 for p in st.session_state.preds[:4] if p >= 5)
    if meat_in_quad >= 3 or hist[-1] >= 5:
        for i in range(5, 9): scores[i] *= 0.5  # تقليل وزن اللحوم
        for i in range(1, 5): scores[i] *= 1.8  # تعزيز فرص الخضار
    
    top = sorted(scores, key=scores.get, reverse=True)
    st.session_state.preds = top[:4]
    
    # اختيار التأمين (أقوى لحم متوفر خارج المربع)
    meat_opts = [5, 6, 7, 8]
    ins_slot = next((m for m in meat_opts if m not in top[:4]), 5)
    st.session_state.preds.append(ins_slot)
    
    mx = max(scores.values()) if scores.values() else 1
    probs = {i: int((scores[i]/mx)*100) for i in range(1, 9)}

# --- 5. الواجهة الرسومية (التصميم المفصل v104) ---
st.markdown("""<style>
    .main-box { background: #1a1a1a; border: 2px solid #39ff14; padding: 12px; border-radius: 15px; text-align: center; }
    .finance-bar { display: flex; justify-content: space-between; background: #000; padding: 8px; border-radius: 10px; border: 1px solid #444; margin: 8px 0; }
    .mini-card { background: #111; border: 1px solid #444; padding: 4px; border-radius: 6px; text-align: center; color: white; font-size: 11px; font-weight: bold; }
    .finger-tag { background: #001a33; color: #00aaff; border: 1px dashed #00aaff; border-radius: 5px; font-size: 10px; padding: 4px; margin-top: 5px; font-weight: bold; }
</style>""", unsafe_allow_html=True)

with st.expander("📊 الضبط المالي", expanded=(total_h < 31)):
    c1, c2, c3 = st.columns(3)
    cap = c1.number_input("المحفظة", value=4400)
    bq = c2.number_input("المربع", value=50)
    bi = c3.number_input("التأمين", value=100)

st.markdown(f'<div class="finance-bar">'
            f'<div><small style="color:#777;">الرصيد</small><br><b>{cap + st.session_state.balance}</b></div>'
            f'<div><small style="color:#777;">الربح الصافي</small><br><b style="color:{"#39ff14" if st.session_state.balance >= 0 else "#ff4b4b"}">{st.session_state.balance:+}</b></div>'
            f'<div><small style="color:#777;">الحالة</small><br><b style="color:#ffaa00;">{"نشط ✅" if total_h >= 30 else "إحماء ⏳"}</b></div></div>', unsafe_allow_html=True)

# تم هنا تعديل السطر بإضافة حرف f قبل علامة الاقتباس لإظهار كلمة البصمة
st.markdown(f'<div class="main-box"><div style="color:#39ff14; font-size:11px; font-weight:bold; margin-bottom:5px;">🎯 المربع الذهبي (v105.1 مصلح)</div>'
            f'<div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:6px;">' + 
            "".join([f'<div style="background:#002200; border:1px solid #39ff14; padding:5px; border-radius:8px;">{SYMBOLS[c]}<div style="font-size:8px;">{probs[c]}%</div></div>' for c in st.session_state.preds[:4]]) + 
            f'</div><div class="finger-tag">{st.session_state.fingerprint}</div></div>', unsafe_allow_html=True)

ins = st.session_state.preds[4]; last_5_icons = "".join([f'<span style="margin-left:4px;">{SYMBOLS[c]}</span>' for c in hist[-5:]])
st.markdown(f'<div style="display:flex; gap:8px; margin: 10px 0;"><div style="width:75px; background:#111; border:1px solid #00aaff; border-radius:10px; text-align:center;"><small style="color:#00aaff; font-size:9px;">🛡️ تأمين</small><br><span style="font-size:18px;">{SYMBOLS[ins]}</span></div>'
            f'<div style="flex:1; background:#111; border-radius:10px; border:1px solid #333; display:flex; align-items:center; justify-content:center; font-size:22px;">{last_5_icons if last_5_icons else "..."}</div></div>', unsafe_allow_html=True)

r1, r2 = st.columns(5), st.columns(4)
for i, c in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[c], key=f"btn1_{c}"): register_result(c, bq, bi); st.rerun()
for i, c in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[c], key=f"btn2_{c}"): register_result(c, bq, bi); st.rerun()

# الرادار السفلي
h10 = sum(1 for x in st.session_state.action_hit[-10:] if x)
sig = "توقف 🔴" if (total_h > 10 and h10 < 3) or shift_active else ("انطلق 🟢" if h10 >= 5 else "انتظر 🟡")
st.markdown(f'<div style="display:grid; grid-template-columns: repeat(4, 1fr); gap: 4px; margin-bottom: 8px;">'
            f'<div class="mini-card">📡 {"تكيف" if shift_active else "مستقر"}</div><div class="mini-card">🚨 {"غدر" if h10 < 4 else "آمن"}</div>'
            f'<div class="mini-card">🏆 {st.session_state.max_streak}</div><div class="mini-card">🚥 {sig}</div></div>', unsafe_allow_html=True)

# أزرار التحكم وإصلاح التراجع
c1, c2, c3, c4 = st.columns([0.8, 1, 1, 1])
if c1.button("↩️"):
    if st.session_state.history:
        # إصلاح التراجع الحقيقي
        status = st.session_state.action_hit.pop()
        if status: st.session_state.hits -= 1
        else: st.session_state.misses -= 1
        st.session_state.history.pop(); st.rerun()

c2.markdown(f'<div class="mini-card">🔄 جولة<br>{total_h}</div>', unsafe_allow_html=True)
c3.markdown(f'<div class="mini-card" style="color:#39ff14;">✅ صح<br>{st.session_state.hits}</div>', unsafe_allow_html=True)
c4.markdown(f'<div class="mini-card" style="color:#ff4b4b;">❌ خطأ<br>{st.session_state.misses}</div>', unsafe_allow_html=True)
