"""우리집 건강수첩 · streamlit run family_health.py
설치: requirements.txt. Streamlit Cloud에서 실행 파일 family_health.py 선택.
로그인 없음: 같은 서버를 사용하는 모든 방문자는 동일 기록을 볼 수 있음. 공개 배포에 민감정보 입력 금지.
SQLite 로컬 저장: Cloud 재배포/초기화 시 유실 가능. CSV 백업 권장.
알림은 앱이 열린 동안만 제공. 화면 꺼짐/브라우저 종료 시 보장 불가. 휴대폰 기본 알람 병행.
성인 혈압 색상: AHA 기준. 정상 <120/<80, 주의 120~139 또는 80~89,
높음 >=140 또는 >=90. <90 또는 <60은 낮음 주의. >=180 또는 >=120은 재확인/긴급 안내.
색상은 기록 참고용이며 진단/개인 치료 목표가 아님. 약 용량 변경 금지.
"""
import streamlit as st
import sqlite3,json,uuid,html
from datetime import datetime,timedelta,time
from zoneinfo import ZoneInfo
import streamlit.components.v1 as components
st.set_page_config(page_title='우리집 건강수첩',page_icon='🌿',initial_sidebar_state='collapsed')
def now():return datetime.now(ZoneInfo('Asia/Seoul'))
def conn():
 c=sqlite3.connect('family_health.sqlite3',timeout=15)
 c.execute('create table if not exists records(id text primary key, kind text, payload text)');return c
def items(kind):
 with conn() as c:return [dict(json.loads(x[1]),id=x[0]) for x in c.execute('select id,payload from records where kind=?',(kind,))]
def put(kind,d):
 d=dict(d);i=d.pop('id',str(uuid.uuid4()))
 with conn() as c:c.execute('insert or replace into records values(?,?,?)',(i,kind,json.dumps(d,ensure_ascii=False)))
def delete(i):
 with conn() as c:c.execute('delete from records where id=?',(i,))
def classify(s,d):
 if s>=180 or d>=120:return '매우 높음','#C73440',96
 if s<90 or d<60:return '낮음 · 재확인','#C73440',12
 if s>=140 or d>=90:return '높음 · 상담 필요','#C73440',80
 if s>=120 or d>=80:return '주의 · 관찰','#D69E16',57
 return '정상 범위','#29875D',35
st.markdown('''<style>
:root{color-scheme:light}html,body,.stApp{background:#F3F8F1!important;color:#203D30!important;font-family:Arial,sans-serif!important}.block-container{max-width:650px;padding:3.5rem 1.2rem 2rem}h1,h2,h3,p,label{color:#203D30!important}input{font-size:26px!important;background:white!important;color:#203D30!important;-webkit-text-fill-color:#203D30!important;height:65px!important}button{min-height:64px!important;border-radius:18px!important}button p{font-size:22px!important;font-weight:650!important}.stButton>button,.stFormSubmitButton>button{background:#DDEFD6!important;border:1px solid #B3CEA8!important;width:100%!important}[data-testid="stSidebar"]{display:none}header{background:#F3F8F1!important}.result{padding:24px;border-radius:22px;background:white;margin:14px 0;font-size:26px;font-weight:bold}.label{font-size:21px;margin-bottom:4px}
</style>''',unsafe_allow_html=True)
if 'page' not in st.session_state:st.session_state.page='홈'
page=st.session_state.page
def go(p):st.session_state.page=p;st.rerun()
def family():
 names=sorted(set(['아빠','엄마','나']+[x['person'] for k in ['bp','med'] for x in items(k)]))
 return st.selectbox('가족',names,key='family',index=names.index('아빠') if '아빠' in names else 0)
if page=='홈':
 st.title('우리집 건강수첩 🌿')
 st.markdown('<style>.stButton>button{min-height:23vh!important}.stButton>button p{font-size:32px!important}</style>',unsafe_allow_html=True)
 if st.button('🩺 혈압 기록'):go('혈압')
 if st.button('💊 약 먹기'):go('약')
else:
 if st.button('← 처음 화면'):go('홈')
 person=family()
 if page=='혈압':
  st.title('혈압 기록')
  if st.button('📋 지난 기록 보기'):go('기록')
  with st.form('bp'):
   st.markdown('### ① 혈압계 위쪽 숫자')
   upper=st.text_input('위쪽 숫자',placeholder='예: 120',max_chars=3,label_visibility='collapsed')
   st.markdown('### ② 혈압계 아래쪽 숫자')
   lower=st.text_input('아래쪽 숫자',placeholder='예: 80',max_chars=3,label_visibility='collapsed')
   if st.form_submit_button('저장하기',use_container_width=True):
    try:
     sv=int(upper.strip());dv=int(lower.strip())
     if not(50<=sv<=300 and 30<=dv<=180 and sv>dv):raise ValueError()
     put('bp',{'person':person,'s':sv,'d':dv,'pulse':None,'at':now().isoformat()});st.session_state.just_saved=True;st.rerun()
    except ValueError:st.error('혈압계의 숫자를 다시 확인해 주세요.')
  logs=sorted([x for x in items('bp') if x['person']==person],key=lambda x:x['at'],reverse=True)
  if logs:
   r=logs[0];label,color,level=classify(r['s'],r['d'])
   st.markdown(f'<div class="result" style="color:{color}"><span style="display:inline-block;width:18px;height:65px;border:2px solid {color};border-radius:20px;vertical-align:middle;margin-right:15px;background:linear-gradient(to top,{color} {level}%,#fff {level}%);"></span>{r["s"]} / {r["d"]}<br>{label}</div>',unsafe_allow_html=True)
   st.caption('최근 기록 · '+datetime.fromisoformat(r['at']).strftime('%m월 %d일 %H:%M'))
   if r['s']>=180 or r['d']>=120:st.error('가슴 통증·숨참·마비·말하기 어려움: 즉시 119. 증상이 없어도 1분 후 재측정하고 계속 높으면 즉시 의료진에게 연락하세요.')
   elif r['s']<90 or r['d']<60:st.warning('어지럼·실신이 있으면 의료진에게 연락하세요. 의식 저하 등 위급하면 119.')
  st.caption('혈압계로 잰 값을 기록합니다. 색상은 참고용이며 약은 임의로 바꾸지 마세요.')
 elif page=='기록':
  st.title('지난 혈압')
  if st.button('＋ 혈압 입력'):go('혈압')
  logs=sorted([x for x in items('bp') if x['person']==person],key=lambda x:x['at'],reverse=True)
  recent=[x for x in logs if datetime.fromisoformat(x['at'])>=now()-timedelta(days=7)]
  if recent:st.metric('최근 7일 측정 평균',f'{sum(x["s"] for x in recent)/len(recent):.0f} / {sum(x["d"] for x in recent)/len(recent):.0f}')
  if not logs:st.info('아직 기록이 없어요.')
  for r in logs[:60]:
   label,color,_=classify(r['s'],r['d'])
   with st.container(border=True):
    st.write(datetime.fromisoformat(r['at']).strftime('%m월 %d일 · %H:%M'))
    st.markdown(f'<div style="color:{color};font-size:28px;font-weight:bold">{r["s"]} / {r["d"]} · {label}</div>',unsafe_allow_html=True)
    if st.button('잘못된 기록 지우기',key=r['id']):delete(r['id']);st.rerun()
 elif page=='약':
  st.title('오늘 먹을 약')
  if st.button('＋ 약 추가하기'):go('약추가')
  meds=[m for m in items('med') if m['person']==person]
  taken={x['slot']:x for x in items('taken') if x['date']==str(now().date())}
  if not meds:st.info('약 추가하기를 눌러 주세요.')
  for m in meds:
   with st.container(border=True):
    st.subheader(m['name'])
    for t in m.get('times') or ['시간 미지정']:
     slot=m['id']+'_'+t
     st.write('🕒 '+t)
     if slot in taken:
      st.success('오늘 먹었어요 ✓')
      if st.button('잘못 눌렀어요',key='undo'+slot):delete(taken[slot]['id']);st.rerun()
     elif st.button('먹었어요',key='done'+slot):put('taken',{'slot':slot,'date':str(now().date()),'at':now().isoformat()});st.rerun()
    if st.button('약 수정',key='edit'+m['id']):st.session_state.edit_med=m['id'];go('약수정')
  st.caption('복용은 처방대로. 시간 알림은 휴대폰 기본 알람을 이용하세요.')
 elif page in ['약추가','약수정']:
  old=next((m for m in items('med') if m['id']==st.session_state.get('edit_med')),None) if page=='약수정' else None
  st.title('약 수정' if old else '약 추가')
  if st.button('← 약 목록'):go('약')
  with st.form('medicine'):
   name=st.text_input('① 약 이름',value=old['name'] if old else '',placeholder='예: 혈압약',max_chars=70)
   selected=st.multiselect('② 먹는 때를 눌러 주세요',['아침','점심','저녁','자기 전'],default=[t for t in (old.get('times',[]) if old else []) if t in ['아침','점심','저녁','자기 전']])
   if st.form_submit_button('저장하기',use_container_width=True):
    if not name.strip():st.error('약 이름을 적어 주세요.')
    else:
     record={'person':person,'name':name.strip(),'times':selected or (old.get('times',[]) if old else []),'dose':''}
     if old:record['id']=old['id']
     put('med',record);go('약')
  st.caption('먹는 때는 처방받은 대로 선택하세요. 선택하지 않아도 저장됩니다.')
  if old and st.button('이 약 삭제하기'):delete(old['id']);go('약')
