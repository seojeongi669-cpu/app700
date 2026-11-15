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
import pandas as pd
st.markdown('''<style>
:root{color-scheme:light}.stApp{background:#F2F6FC!important;color:#18334F!important}.block-container{max-width:820px;padding:3.8rem 1rem 2rem}header{background:#F2F6FC!important}h1,h2,h3,p,label{color:#18334F!important}button{min-height:52px!important;border-radius:14px!important}.stButton,.stButton>button{width:100%!important}.stButton>button{background:#E1EDFF!important;border:1px solid #BCD1F0!important}.stButton>button p{font-size:19px!important;font-weight:650!important;color:#163E72!important}[data-baseweb="select"]>div{min-height:52px!important;height:auto!important;background:white!important;color:#18334F!important}input{background:white!important;color:#18334F!important;-webkit-text-fill-color:#18334F!important}[data-testid="stMetric"]{background:#fff;padding:14px;border-radius:16px;border:1px solid #DCE7F6}[data-testid="stSidebar"]{display:none}.hero{background:linear-gradient(125deg,#175FC7,#438BE8);padding:24px;border-radius:22px;color:white;margin-bottom:20px}.hero h2,.hero p{color:white!important;margin:0}.home-title{font-size:19px;color:#45637F}
</style>''',unsafe_allow_html=True)
st.markdown('''<style>
#MainMenu,footer,[data-testid="stToolbar"]{display:none!important}
.block-container{max-width:520px!important;padding:3.5rem 1.1rem 3rem!important}
.stApp{background:#EDF3FB!important}
h1{font-size:28px!important;letter-spacing:-1px!important;margin-bottom:14px!important}
[data-testid="stForm"]{background:#fff!important;border:1px solid #DFE8F5!important;border-radius:22px!important;padding:20px!important;box-shadow:0 5px 18px #18334F08}
[data-testid="stTextInput"] input{font-size:27px!important;font-weight:700!important;min-height:64px!important;text-align:center!important;border-radius:12px!important}
.stButton>button,.stFormSubmitButton>button{transition:none!important;box-shadow:none!important;min-height:54px!important;background:#E1EDFF!important;color:#163E72!important;border:1px solid #BCD1F0!important}
.stButton>button:hover,.stButton>button:focus,.stButton>button:active,.stFormSubmitButton>button:hover,.stFormSubmitButton>button:focus{background:#E1EDFF!important;color:#163E72!important;border-color:#BCD1F0!important}
.stFormSubmitButton>button{width:100%!important;background:#2368D2!important;border:none!important}
.stFormSubmitButton>button p{color:white!important;font-weight:700!important}
[data-testid="stTabs"] [role="tablist"]{background:#DFE8F5;border-radius:14px;padding:5px;gap:3px}
[data-testid="stTabs"] [role="tab"]{flex:1;justify-content:center;border-radius:10px;font-size:16px!important}
[data-testid="stTabs"] [aria-selected="true"]{background:white!important}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:20px!important}
</style>''',unsafe_allow_html=True)
if 'page' not in st.session_state:st.session_state.page='홈'
def go(p):st.session_state.page=p;st.rerun()
page=st.session_state.page
if page=='홈':
 st.markdown('<div class="hero"><h2>우리집 건강수첩</h2><p>가족의 일주일을 한눈에</p></div>',unsafe_allow_html=True)
 st.markdown('<style>.stButton>button{min-height:145px!important;background:white!important;border:1px solid #D6E3F6!important;box-shadow:0 5px 18px #18334F08!important;text-align:left!important;justify-content:flex-start!important;padding:24px!important}.stButton>button p{font-size:26px!important;color:#17437C!important}</style>',unsafe_allow_html=True)
 if st.button('🩺 혈압 · 주간 기록',use_container_width=True):go('혈압')
 if st.button('💊 복약 · 주간 기록',use_container_width=True):go('약')
else:
 top1,top2=st.columns([1,2])
 if top1.button('‹ 홈',use_container_width=True):go('홈')
 people=sorted(set(['아빠','엄마','나']+[x['person'] for k in ['bp','med'] for x in items(k)]))
 person=top2.selectbox('가족 선택',people,index=people.index('아빠'),label_visibility='collapsed')
 monday=now().date()-timedelta(days=now().weekday())
 chosen=now().date()
 start=chosen-timedelta(days=chosen.weekday());days=[start+timedelta(days=i) for i in range(7)]
 weekdays=['월','화','수','목','금','토','일']

 if page=='혈압':
  st.title('혈압 기록')
  logs=[x for x in items('bp') if x['person']==person]
  rows=[]
  for i,day in enumerate(days):
   found=[x for x in logs if datetime.fromisoformat(x['at']).date()==day]
   rows.append({'날짜':f'{day:%m/%d} {weekdays[i]}','최고':round(sum(x['s'] for x in found)/len(found)) if found else None,'최저':round(sum(x['d'] for x in found)/len(found)) if found else None})
  weeklogs=[x for x in logs if start<=datetime.fromisoformat(x['at']).date()<=days[-1]]
  st.caption('혈압계에 나온 숫자를 적어 주세요.')
  with st.form('daily_pressure',border=False):
   measured=now().date()
   c1,c2=st.columns(2)
   high=c1.text_input('최고혈압',placeholder='120',max_chars=3)
   low=c2.text_input('최저혈압',placeholder='80',max_chars=3)
   if st.form_submit_button('이 혈압 저장하기',use_container_width=True):
    try:
     sv,dv=int(high.strip()),int(low.strip())
     if not (50<=sv<=300 and 30<=dv<=180 and sv>dv):raise ValueError()
     put('bp',{'person':person,'s':sv,'d':dv,'pulse':None,'at':datetime.combine(measured,now().time(),tzinfo=ZoneInfo('Asia/Seoul')).isoformat()})
     st.rerun()
    except ValueError:st.error('혈압계에서 확인한 숫자를 적어 주세요. 최고혈압이 최저혈압보다 커야 해요.')
  if logs:
   latest=max(logs,key=lambda x:x['at']);label,color,_=classify(latest['s'],latest['d'])
   st.markdown(f'<div style="background:white;border-left:6px solid {color};border-radius:16px;padding:16px;margin:15px 0;color:{color}"><small>마지막 기록</small><div style="font-size:32px;font-weight:700">{latest["s"]} / {latest["d"]}</div><strong>{label}</strong></div>',unsafe_allow_html=True)
   if latest['s']>=180 or latest['d']>=120:st.error('가슴 통증·숨참·마비·말하기 어려움은 즉시 119. 증상이 없어도 1분 후 다시 재고 계속 높으면 즉시 의료진에게 연락하세요.')
   elif latest['s']<90 or latest['d']<60:st.warning('어지럼·실신 등 증상이 있으면 의료진에게 연락하세요. 위급하면 119.')
  if weeklogs:
   mean_s=sum(x['s'] for x in weeklogs)/len(weeklogs);mean_d=sum(x['d'] for x in weeklogs)/len(weeklogs)
   st.markdown(f'**이번 주 평균　{mean_s:.0f} / {mean_d:.0f} mmHg**')
  if st.button('지난 기록 보기',use_container_width=True):
   st.session_state.show_history=not st.session_state.get('show_history',False)
  if st.session_state.get('show_history',False):
   for r in sorted(logs,key=lambda x:x['at'],reverse=True)[:30]:
    label,color,_=classify(r['s'],r['d'])
    when=datetime.fromisoformat(r['at']).strftime('%m/%d %H:%M')
    st.markdown(f'<div style="padding:10px;border-bottom:1px solid #DCE7F6;color:{color}">{when}　 <b>{r["s"]} / {r["d"]}</b>　{label}</div>',unsafe_allow_html=True)
   st.caption('단위 mmHg · 평균은 이번 주 측정값의 단순평균. 색상은 성인 참고 기준이며 진단이 아닙니다. 약은 처방대로 복용하세요.')
 else:
  st.title('복약 · 일주일')
  meds=[x for x in items('med') if x['person']==person]
  taken=items('taken');today=str(now().date())
  tab1,tab2,tab3=st.tabs(['오늘 먹기','주간 기록','약 추가·관리'])
  with tab1:
   if not meds:st.info('약 추가·관리에서 약 이름을 등록하세요.')
   for m in meds:
    with st.container(border=True):
     st.subheader(m['name'])
     for t in m.get('times') or ['하루 1회 기록']:
      slot=m['id']+'_'+t;r=next((x for x in taken if x['date']==today and x['slot']==slot),None)
      if st.button(('✅ '+t+' · 완료 취소') if r else (t+' · 먹었어요'),key=slot,use_container_width=True):
       if r:delete(r['id'])
       else:put('taken',{'slot':slot,'date':today,'at':now().isoformat()})
       st.rerun()
  with tab2:
   rows=[];expected=sum(len(m.get('times') or ['1']) for m in meds)
   slots={m['id']+'_'+t for m in meds for t in (m.get('times') or ['하루 1회 기록'])}
   # 이전 버전의 시간 미지정 기록도 포함
   slots|={m['id']+'_'+t for m in meds for t in ['시간 미지정','하루 기록']}
   for i,day in enumerate(days):
    done=len({x['slot'] for x in taken if x['date']==str(day) and x['slot'] in slots})
    rows.append({'날짜':f'{day:%m/%d} {weekdays[i]}','복용 확인 횟수':done if day<=now().date() else None})
   for row in rows:
    value='—' if pd.isna(row['복용 확인 횟수']) else str(int(row['복용 확인 횟수']))+'회'
    st.markdown(f'<div style="display:flex;justify-content:space-between;padding:16px 18px;background:white;border-radius:14px;margin:7px 0;color:#18334F"><span>{row["날짜"]}</span><strong>{value}</strong></div>',unsafe_allow_html=True)
   st.caption('기록한 복용 확인 횟수입니다. 처방 변경·약 삭제 전후에는 직접 비교하지 마세요.')
  with tab3:
   with st.form('newmed',clear_on_submit=True):
    name=st.text_input('약 이름',placeholder='예: 혈압약')
    times=st.multiselect('먹는 때',['아침','점심','저녁','자기 전'])
    if st.form_submit_button('약 추가',use_container_width=True):
     if name.strip():put('med',{'person':person,'name':name.strip(),'times':times,'dose':''});st.rerun()
     else:st.error('약 이름을 적어 주세요.')
   for m in meds:
    if st.button(m['name']+' 삭제',key='del'+m['id']):delete(m['id']);st.rerun()
  st.caption('복용은 처방대로 · 놓쳤어도 임의로 두 배 복용하지 마세요. 알림은 휴대폰 알람을 사용하세요.')
