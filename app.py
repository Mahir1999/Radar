import streamlit as st

# --- 1. الإعدادات ---
st.set_page_config(page_title="Greedy AI v105.0", page_icon="💎", layout="centered")

# --- 2. تهيئة الذاكرة ---
keys = ['history', 'hits', 'misses', 'cons_m', 'p_count', 'preds', 'action_hit', 'max_streak', 'cur_streak', 'balance', 'target', 'fingerprint']
for key in keys:
    if key not in st.session_state:
        if key in ['history', 'preds', 'action_hit']: st.session_state[key] = []
        elif key == 'fingerprint': st.session_state[key] = "تحليل..."
        else: st.session_state[key] = 0

SYMBOLS = {1: "🍅", 2: "🌽", 3: "🥕", 4: "🫑", 5: "🐔", 6: "🐑", 7: "🐟", 8: "🦐", 9: "💰"}
MULT = {1: 5, 2: 5, 3: 5, 4: 5, 5: 45, 6: 15, 7: 25, 8: 10, 9: 0}

# --- 3. المحرك المصلح ---
def register_result(code, bet_q, bet_i):
    h = st.session_state.history
    is_quad_hit = code in st.session_state.preds[:4]
    is_ins_hit = (len(st.session_state.preds) > 4 and code == st.session_state.preds[4])
    is_hit = is_quad_hit or is_ins_hit
    
    # حساب الأنماط
    if len(h) >= 2:
        last_pair = [h[-1], code]
        for i in range(len(h) - 1):
            if h[i:i+2] == last_pair:
                st.session_state.p_count += 1
                break
    
    # الحساب المالي (بعد الجولة 30)
    if len(h) >= 30:
        total_bet = (bet_q * 4) + bet_i
        win_amount = 0
        if is_quad_hit: win_amount = bet_q * MULT[code]
        elif is_ins_hit: win_amount = bet_i * MULT[code]
        st.session_state.balance += (win_amount - total_bet)
    
    # تحديث العدادات
    if is_hit:
        st.session_state.hits += 1
        st.session_state.cur_streak += 1
        if st.session_state.cur_streak > st.session_state.max_streak:
            st.session_state.max_streak = st.session_state.cur_streak
    else:
        if code != 9:
            st.session_state.misses += 1
            st.session_state.cur_streak = 0
    
    st.session_state.history.append(code)
    st.session_state.action_hit.append(is_hit)

# --- 4. محرك التوقعات مع "كاسر الانحياز" ---
hist = st.session_state.history
total_h = len(hist)

if total_h == 0:
    st.session_state.preds = [1, 2, 3, 4, 5]
    probs = {i: 10 for i in range(1, 9)}
else:
    recent_15 = hist[-15:]
    scores = {}
    for c in range(1, 9):
        gap = list(reversed(hist)).index(c) if c in hist else total_h
        scores[c] = (recent_15.count(c) * 0.8 + (gap * 0.2))
    
    # ⚖️ ميزان رقمي صارم (منع صمود اللحوم)
    meat_in_preds = sum(1 for p in st.session_state.preds[:4] if p >= 5)
    if meat_in_preds >= 3 or hist[-1] >= 5: # إذا المربع غرقان لحم أو آخر جولة لحم
        for i in range(5, 9): scores[i] *= 0.4 # خفض اللحوم بقوة
        for i in range(1, 5): scores[i] *= 1.8 # رفع الخضار فوراً

    top_sorted = sorted(scores, key=scores.get, reverse=True)
    st.session_state.preds = top_sorted[:4]
    
    # اختيار التأمين (خوارزمية ذكية)
    meat_opts = [5, 6, 7, 8]
    ins_slot = next((m for m in meat_opts if m not in st.session_state.preds[:4]), 5)
    st.session_state.preds.append(ins_slot)
    
    mx = max(scores.values()) if scores.values() else 1
    probs = {i: int((scores[i]/mx)*100) for i in range(1, 9)}

# --- 5. الواجهة الرسومية ---
st.markdown("""<style>
    .main-box { background: #1a1a1a; border: 2px solid #39ff14; padding: 12px; border-radius: 15px; text-align: center; }
    .finance-bar { display: flex; justify-content: space-between; background: #000; padding: 8px; border-radius: 10px; border: 1px solid #444; margin: 8px 0; }
    .mini-card { background: #111; border: 1px solid #444; padding: 4px; border-radius: 6px; text-align: center; color: white; font-size: 11px; font-weight: bold; }
</style>""", unsafe_allow_html=True)

with st.expander("📊 الإعدادات", expanded=(total_h < 31)):
    c1, c2, c3 = st.columns(3)
    capital = c1.number_input("المحفظة", value=4400)
    bet_q = c2.number_input("المربع", value=50)
    bet_i = c3.number_input("التأمين", value=100)

st.markdown(f'<div class="finance-bar">'
            f'<div><small style="color:#777;">الرصيد</small><br><b>{capital + st.session_state.balance}</b></div>'
            f'<div><small style="color:#777;">الربح الصافي</small><br><b style="color:{"#39ff14" if st.session_state.balance >= 0 else "#ff4b4b"}">{st.session_state.balance:+}</b></div>'
            f'<div><small style="color:#777;">الجولة</small><br><b>{total_h}</b></div></div>', unsafe_allow_html=True)

st.markdown(f'<div class="main-box"><div style="color:#39ff14; font-size:11px; font-weight:bold; margin-bottom:5px;">🎯 المربع الذهبي (تم إصلاح الميزان)</div>'
            f'<div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:6px;">' + 
            "".join([f'<div style="background:#002200; border:1px solid #39ff14; padding:5px; border-radius:8px;">{SYMBOLS[c]}<div style="font-size:8px;">{probs[c]}%</div></div>' for c in st.session_state.preds[:4]]) + 
            '</div></div>', unsafe_allow_html=True)

# التأمين وآخر 5
ins = st.session_state.preds[4]; last_5 = "".join([f'<span style="margin-left:4px;">{SYMBOLS[c]}</span>' for c in hist[-5:]])
st.markdown(f'<div style="display:flex; gap:8px; margin: 10px 0;">'
            f'<div style="width:75px; background:#111; border:1px solid #00aaff; border-radius:10px; text-align:center;"><small style="color:#00aaff; font-size:9px;">🛡️ تأمين</small><br><span style="font-size:18px;">{SYMBOLS[ins]}</span></div>'
            f'<div style="flex:1; background:#111; border-radius:10px; border:1px solid #333; display:flex; align-items:center; justify-content:center; font-size:22px;">{last_5 if last_5 else "..."}</div></div>', unsafe_allow_html=True)

# الأزرار
r1, r2 = st.columns(5), st.columns(4)
for i, c in enumerate([5, 7, 6, 8, 9]):
    if r1[i].button(SYMBOLS[c], key=f"btn_{c}"): register_result(c, bet_q, bet_i); st.rerun()
for i, c in enumerate([1, 2, 3, 4]):
    if r2[i].button(SYMBOLS[c], key=f"btn_{c}"): register_result(c, bet_q, bet_i); st.rerun()

# الرادار السفلي
hits_10 = sum(1 for x in st.session_state.action_hit[-10:] if x)
sig = "GO 🟢" if hits_10 >= 5 else ("STOP 🔴" if (total_h > 10 and hits_10 < 3) else "WAIT 🟡")
st.markdown(f'<div style="display:grid; grid-template-columns: repeat(3, 1fr); gap: 4px; margin-bottom: 8px;">'
            f'<div class="mini-card">🏆 أعلى سلسلة: {st.session_state.max_streak}</div>'
            f'<div class="mini-card">🚥 الإشارة: {sig}</div>'
            f'<div class="mini-card">📉 أنماط: {st.session_state.p_count}</div></div>', unsafe_allow_html=True)

# أزرار التحكم السفلي وإصلاح التراجع
c1, c2, c3 = st.columns([1, 1, 1])
if c1.button("↩️ تراجع"):
    if st.session_state.history:
        last_res = st.session_state.action_hit.pop()
        if last_res: st.session_state.hits -= 1
        else: st.session_state.misses -= 1
        st.session_state.history.pop()
        st.rerun()
c2.markdown(f'<div class="mini-card" style="color:#39ff14;">✅ صح: {st.session_state.hits}</div>', unsafe_allow_html=True)
c3.markdown(f'<div class="mini-card" style="color:#ff4b4b;">❌ خطأ: {st.session_state.misses}</div>', unsafe_allow_html=True)
