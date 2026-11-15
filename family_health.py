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
if 'page' not in st.session_state:st.session_state.page='홈'
def go(p):st.session_state.page=p;st.rerun()
page=st.session_state.page
if page=='홈':
 st.markdown('<div class="hero"><h2>우리집 건강수첩</h2><p>가족의 일주일을 한눈에</p></div>',unsafe_allow_html=True)
 st.markdown('<style>.stButton>button{min-height:160px!important}.stButton>button p{font-size:27px!important}</style>',unsafe_allow_html=True)
 if st.button('🩺 혈압 · 주간 기록',use_container_width=True):go('혈압')
 if st.button('💊 복약 · 주간 기록',use_container_width=True):go('약')
else:
 top1,top2=st.columns([1,2])
 if top1.button('‹ 홈',use_container_width=True):go('홈')
 people=sorted(set(['아빠','엄마','나']+[x['person'] for k in ['bp','med'] for x in items(k)]))
 person=top2.selectbox('가족 선택',people,index=people.index('아빠'),label_visibility='collapsed')
 monday=now().date()-timedelta(days=now().weekday())
 chosen=st.date_input('주간 선택 · 해당 날짜가 속한 주',value=now().date(),max_value=now().date())
 start=chosen-timedelta(days=chosen.weekday());days=[start+timedelta(days=i) for i in range(7)]
 weekdays=['월','화','수','목','금','토','일']
 st.caption(f'{start:%m.%d} — {days[-1]:%m.%d}')
 if page=='혈압':
  st.title('혈압 · 일주일')
  logs=[x for x in items('bp') if x['person']==person]
  rows=[]
  for i,day in enumerate(days):
   found=[x for x in logs if datetime.fromisoformat(x['at']).date()==day]
   rows.append({'날짜':f'{day:%m/%d} {weekdays[i]}','최고':round(sum(x['s'] for x in found)/len(found)) if found else None,'최저':round(sum(x['d'] for x in found)/len(found)) if found else None})
  weeklogs=[x for x in logs if start<=datetime.fromisoformat(x['at']).date()<=days[-1]]
  a,b=st.columns(2)
  a.metric('이번 주 평균 최고',f'{sum(x["s"] for x in weeklogs)/len(weeklogs):.0f} mmHg' if weeklogs else '기록 없음')
  b.metric('이번 주 평균 최저',f'{sum(x["d"] for x in weeklogs)/len(weeklogs):.0f} mmHg' if weeklogs else '기록 없음')
  st.caption('칸을 두 번 눌러 숫자 입력 → 아래 저장')
  edited=st.data_editor(pd.DataFrame(rows),hide_index=True,use_container_width=True,height=285,disabled=['날짜'],column_config={'최고':st.column_config.NumberColumn('최고혈압',min_value=50,max_value=300,step=1),'최저':st.column_config.NumberColumn('최저혈압',min_value=30,max_value=180,step=1)},key=f'bp_{person}_{start}')
  if st.button('일주일 기록 저장',use_container_width=True):
   valid=True
   for i,row in edited.iterrows():
    sv,dv=row['최고'],row['최저']
    if pd.isna(sv) and pd.isna(dv):continue
    if pd.isna(sv) or pd.isna(dv) or sv<=dv or days[i]>now().date():valid=False
   if not valid:st.error('최고·최저를 함께 입력하고, 최고가 더 큰지 확인하세요. 미래 날짜에는 기록할 수 없어요.')
   else:
    # 편집한 날짜만 대표 측정값으로 대체. 변경하지 않은 날의 복수 측정은 보존.
    for i,row in edited.iterrows():
     old=rows[i]
     def same(v,w):return (pd.isna(v) and pd.isna(w)) or (not pd.isna(v) and not pd.isna(w) and v==w)
     if same(row['최고'],old['최고']) and same(row['최저'],old['최저']):continue
     for x in logs:
      if datetime.fromisoformat(x['at']).date()==days[i]:delete(x['id'])
     if not pd.isna(row['최고']):put('bp',{'person':person,'s':int(row['최고']),'d':int(row['최저']),'pulse':None,'at':datetime.combine(days[i],time(12),tzinfo=ZoneInfo('Asia/Seoul')).isoformat()})
    st.rerun()
  if weeklogs:
   latest=max(weeklogs,key=lambda x:x['at']);label,color,_=classify(latest['s'],latest['d'])
   st.markdown(f'<div style="padding:14px;background:white;border-left:7px solid {color};border-radius:12px;color:{color};font-size:21px;font-weight:bold">최근 {latest["s"]}/{latest["d"]} · {label}</div>',unsafe_allow_html=True)
   if latest['s']>=180 or latest['d']>=120:st.error('가슴 통증·숨참·마비·언어 이상은 119. 증상이 없어도 1분 후 재측정, 계속 높으면 즉시 의료진에게 연락하세요.')
   elif latest['s']<90 or latest['d']<60:st.warning('어지럼·실신 등 증상이 있으면 의료진에게 연락하세요. 위급하면 119.')
  st.bar_chart(pd.DataFrame(rows).set_index('날짜'),color=['#2674D9','#8AB5EC'],height=180)
  st.caption('단위 mmHg · 빈칸은 미측정 · 평균은 저장된 측정값의 단순평균. 수정한 날짜의 기존 측정은 입력값 하나로 대체됩니다. 색은 성인 참고 기준이며 약을 임의로 조절하지 마세요.')
 else:
  st.title('복약 · 일주일')
  meds=[x for x in items('med') if x['person']==person]
  taken=items('taken');today=str(now().date())
  tab1,tab2,tab3=st.tabs(['오늘 먹기','주간 그래프','약 추가·관리'])
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
   st.bar_chart(pd.DataFrame(rows).set_index('날짜'),color='#2674D9',height=240)
   st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
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
