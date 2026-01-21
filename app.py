import streamlit as st

# --- 1. إعدادات الصفحة الفنية ---
st.set_page_config(page_title="Greedy AI v100.0", page_icon="💎", layout="centered")

# --- 2. تهيئة الذاكرة العميقة (Deep State Initialization) ---
# التأكد من عدم نقص أي مفتاح برمجي
if 'history' not in st.session_state:
    st.session_state.update({
        'history': [], 'hits': 0, 'misses': 0, 'cons_m': 0, 
        'p_count': 0, 'preds': [1, 2, 3, 4, 5], 'action_hit': [],
        'max_streak': 0, 'cur_streak': 0, 'balance': 0
    })

SYMBOLS = {1: "🍅", 2: "🌽", 3: "🥕", 4: "🫑", 5: "🐔", 6: "🐑", 7: "🐟", 8: "🦐", 9: "💰"}
MULT = {1: 5, 2: 5, 3: 5, 4: 5, 5: 45, 6: 15, 7: 25, 8: 10, 9: 0}

# --- 3. محرك الأنماط والعمليات الحسابية (Engine) ---
def register_result(code, bq, bi):
    h = st.session_state.history
    # منطق حساب الأنماط (تراكمي)
    if len(h) >= 2:
        current_pair = [h[-1], code]
        for i in range(len(h) - 1):
            if h[i:i+2] == current_pair:
                st.session_state.p_count += 1
                break
    
    # تحديد الفوز أو الخسارة
    is_quad = code in st.session_state.preds[:4]
    is_ins = (len(st.session_state.preds) > 4 and code == st.session_state.preds[4])
    is_hit = is_quad or is_ins
    
    # نظام الحساب المالي (شرط جولة 30)
    if len(h) >= 30:
        total_cost = (bq * 4) + bi
        win_val = (bq * MULT[code]) if is_quad else ((bi * MULT[code]) if is_ins else 0)
        st.session_state.balance += (win_val - total_cost)
        
    # تحديث العدادات الإحصائية
    if is_hit:
        st.session_state.hits += 1
        st.session_state.cur_streak += 1
        st.session_state.max_streak = max(st.session_state.max_streak, st.session_state.cur_streak)
        st.session_state.cons_m = 0
    elif code != 9:
        st.session_state.misses += 1
        st.session_state.cons_m += 1
        st.session_state.cur_streak = 0
        
    st.session_state.history.append(code)
    st.session_state.action_hit.append(is_hit)

# --- 4. رادار التوقعات (Shift & Chain Detection) ---
hist = st.session_state.history
total_h = len(hist)
# كشف "غدر السيرفر" (3 خسارات متتالية)
shift_active = (len(st.session_state.action_hit) >= 3 and all(x is False for x in st.session_state.action_hit[-3:]) and total_h > 10)

if total_h > 0:
    # حساب أوزان الرموز بناءً على التكرار والفجوات
    recent_15 = hist[-15:]
    scores = {}
    for i in range(1, 9):
        # معادلة الوزن: (عدد التكرار * 1.5) + (قرب الظهور * 0.5)
        gap = list(reversed(hist)).index(i) if i in hist else total_h
        scores[i] = (recent_15.count(i) * 1.5) + (total_h - gap) * 0.1
        
        # درع السلسلة: إذا الرمز ظهر مرتين مؤخراً، خفف احتماله (ضد السلاسل الوهمية)
        if hist[-2:].count(i) >= 1: scores[i] *= 0.6
        
        # فلتر التكيف: إذا السيرفر يغدر، ارفع رموز "اللحم الباردة"
        if shift_active and i >= 5 and i not in hist[-5:]: scores[i] *= 2.0

    top_sorted = sorted(scores, key=scores.get, reverse=True)
    st.session_state.preds = top_sorted[:4]
    # اختيار التأمين (اللحم الأكثر استحقاقاً للظهور)
    st.session_state.preds.append(next((m for m in [5,6,7,8] if m not in top_sorted[:4]), 5))
    
    mx = max(scores.values()) if scores.values() else 1
    probs = {i: int((scores[i]/mx)*100) for i in range(1, 9)}
else:
    probs = {i: 0 for i in range(1, 9)}

# --- 5. التصميم البصري (Scannable UI) ---
st.markdown("""<style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .stat-box { background: #111; border: 1px solid #333; padding: 5px; border-radius: 8px; text-align: center; }
    .gold-box { border: 2px solid #39ff14; background: #1a1a1a; padding: 10px; border-radius: 15px; text-align: center; }
</style>""", unsafe_allow_html=True)

# القسم المالي والهدف
with st.expander("⚙️ إعدادات الجلسة والرهان", expanded=(total_h < 31)):
    c1, c2, c3 = st.columns(3)
    cap = c1.number_input("المحفظة", value=4400)
    bq = c2.number_input("رهان المربع", value=50)
    bi = c3.number_input("رهان التأمين", value=100)
    if st.button("تصفير الذاكرة 🔄"):
        st.session_state.clear(); st.rerun()

# شريط الحالة المالية (المصلح)
st.markdown(f'<div style="display:flex; justify-content:space-between; background:#000; padding:10px; border-radius:10px; border:1px solid #444; margin-bottom:10px;">'
            f'<div><small style="color:#777;">الرصيد</small><br><b>{cap + st.session_state.balance}</b></div>'
            f'<div><small style="color:#777;">الربح (من ج 30)</small><br><b style="color:{"#39ff14" if st.session_state.balance >= 0 else "#ff4b4b"}">{st.session_state.balance:+}</b></div>'
            f'<div><small style="color:#777;">الحالة</small><br><b style="color:#ffaa00;">{"نشط ✅" if total_h >= 30 else "إحماء ⏳"}</b></div></div>', unsafe_allow_html=True)

# المربع الذهبي وشريط القوة %
st.markdown(f'<div class="gold-box"><div style="color:#39ff14; font-size:11px; font-weight:bold; margin-bottom:5px;">🎯 المربع الذهبي (Deep AI)</div>'
            f'<div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:6px;">' + 
            "".join([f'<div style="background:#002200; border:1px solid #39ff14; padding:5px; border-radius:10px;">{SYMBOLS[c]}<br><span style="font-size:9px;">{probs[c]}%</span></div>' for c in st.session_state.preds[:4]]) + 
            '</div></div>', unsafe_allow_html=True)

# التأمين وآخر 5
ins = st.session_state.preds[4]; last_5 = "".join([f'<span style="margin-left:5px;">{SYMBOLS[c]}</span>' for c in hist[-5:]])
st.markdown(f'<div style="display:flex; gap:8px; margin: 10px 0;"><div style="width:80px; background:#111; border:1px solid #00aaff; border-radius:12px; text-align:center;"><small style="color:#00aaff; font-size:9px;">🛡️ تأمين</small><br><span style="font-size:20px;">{SYMBOLS[ins]}</span></div>'
            f'<div style="flex:1; background:#111; border-radius:12px; border:1px solid #333; display:flex; align-items:center; justify-content:center; font-size:24px;">{last_5 if last_5 else "..."}</div></div>', unsafe_allow_html=True)

# أزرار الإدخال
r1, r2 = st.columns(5), st.columns(4)
for i, c in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[c], key=f"x_{c}"): register_result(c, bq, bi); st.rerun()
for i, c in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[c], key=f"x_{c}"): register_result(c, bq, bi); st.rerun()

# رادار الإشارات الذكي
r10 = sum(1 for x in st.session_state.action_hit[-10:] if x)
scam = "آمن ✅" if r10 >= 4 or total_h < 10 else "غدر 🚨"
trnd = "مستقر ✅" if not shift_active else "تكيف 🌀"
sig = "WAIT 🟡"
if scam == "غدر 🚨" or shift_active: sig = "STOP 🔴"
elif r10 >= 5: sig = "GO 🟢"

st.markdown(f'<div style="display:grid; grid-template-columns: repeat(4, 1fr); gap: 4px; margin-bottom: 8px;">'
            f'<div class="stat-box">📡 {trnd}</div><div class="stat-box">🚨 {scam}</div>'
            f'<div class="stat-box">🏆 {st.session_state.max_streak}</div><div class="stat-box">🚥 {sig}</div></div>', unsafe_allow_html=True)

# شريط التحكم السفلي (التراجع + العدادات)
c1, c2, c3, c4 = st.columns([0.8, 1, 1, 1])
if c1.button("↩️"): 
    if st.session_state.history: st.session_state.history.pop(); st.session_state.action_hit.pop(); st.rerun()
c2.markdown(f'<div class="stat-box">🔄 جولة<br>{total_h}</div>', unsafe_allow_html=True)
c3.markdown(f'<div class="stat-box" style="color:#39ff14;">✅ صح<br>{st.session_state.hits}</div>', unsafe_allow_html=True)
c4.markdown(f'<div class="stat-box" style="color:#ff4b4b;">❌ خطأ<br>{st.session_state.misses}</div>', unsafe_allow_html=True)

# تحليل الأنماط النهائي
p_msg, p_clr = ("نمط مكتشف ✅", "#39ff14") if any(hist[i:i+3] == hist[-3:] for i in range(len(hist)-4)) else ("تحليل الذاكرة..", "#777")
st.markdown(f'<div style="background:#0a0a0a; border:1px dashed {p_clr}; padding:6px; border-radius:10px; font-size:11px; color:{p_clr}; text-align:center; font-weight:bold; margin-top:5px;">🔍 {p_msg} | 📉 {st.session_state.p_count} نمط محفوظ</div>', unsafe_allow_html=True)
