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
:root{color-scheme:light}.stApp{background:#F3F8F1!important;color:#203D30!important}.block-container{max-width:580px;padding:3.8rem 1rem 2rem}h1,h2,h3,p,label{color:#203D30!important}input,[data-baseweb="input"],[data-baseweb="base-input"],[data-baseweb="select"]>div{background:#fff!important;color:#203D30!important;-webkit-text-fill-color:#203D30!important}button{border-radius:16px!important;min-height:54px!important}button p{font-size:18px!important;color:#203D30!important}.stButton>button{background:#E0EFDB!important;border:1px solid #B8D3AF!important}header{background:#F3F8F1!important}[data-testid="stSidebar"]{display:none}.card{background:white;padding:18px;border-radius:20px;border:1px solid #D7E7D1;margin:10px 0}.thermo{width:26px;height:115px;border:3px solid #D1DCD1;border-radius:30px;position:relative;display:inline-block;vertical-align:middle;margin-right:20px;overflow:hidden}
</style>''',unsafe_allow_html=True)
if 'page' not in st.session_state:st.session_state.page='홈'
if st.session_state.page!='홈':
 if st.button('‹ 처음으로'):st.session_state.page='홈';st.rerun()
people=sorted(set(['아빠','엄마','나']+[x['person'] for k in ['bp','med'] for x in items(k)]))
if st.session_state.page=='홈':
 st.title('🌿 우리집 건강수첩')
 st.write('')
 if st.button('🩺 혈압 재기',use_container_width=True):st.session_state.page='혈압';st.rerun()
 if st.button('💊 약 먹기',use_container_width=True):st.session_state.page='약';st.rerun()
 st.caption('혈압계로 잰 값을 기록해요.')
 with st.expander('저장·개인정보'):
  st.warning('로그인이 없어 이 앱 방문자는 가족 기록을 모두 볼 수 있어요. 공개 공유하지 마세요. 서버 초기화 시 기록이 사라질 수 있어요.')
elif st.session_state.page=='혈압':
 st.title('🩺 혈압 기록')
 person=st.selectbox('누구의 혈압인가요?',people+['새 가족'])
 if person=='새 가족':person=st.text_input('이름 또는 별명',max_chars=20).strip()
 with st.form('bp',clear_on_submit=False):
  a,b=st.columns(2);s=a.number_input('최고혈압',60,260,120);d=b.number_input('최저혈압',30,160,80)
  pulse=st.number_input('맥박',30,220,70)
  if st.form_submit_button('기록 저장',use_container_width=True):
   if not person:st.error('가족을 선택해 주세요.')
   elif s<=d:st.error('최고혈압과 최저혈압을 확인해 주세요.')
   else:put('bp',{'person':person,'s':s,'d':d,'pulse':pulse,'at':now().isoformat()});st.rerun()
 logs=sorted([r for r in items('bp') if r['person']==person],key=lambda x:x['at'],reverse=True)
 if logs:
  r=logs[0];label,color,level=classify(r['s'],r['d'])
  st.markdown(f'<div class="card"><span class="thermo"><span style="position:absolute;bottom:0;width:100%;height:{level}%;background:{color}"></span></span><span style="display:inline-block;vertical-align:middle;color:{color};font-size:23px;font-weight:700">{r["s"]} / {r["d"]} mmHg<br>{label}</span></div>',unsafe_allow_html=True)
  if r['s']>=180 or r['d']>=120:st.error('가슴 통증·호흡곤란·마비·말하기 어려움이 있으면 즉시 119. 증상이 없어도 1분 이상 후 다시 측정하고 계속 높으면 즉시 의료진에게 연락하세요.')
  elif r['s']<90 or r['d']<60:st.warning('어지럼·실신 등 증상이 있으면 의료진에게 연락하세요. 의식 저하 등 위급하면 119.')
  recent=[r for r in logs if datetime.fromisoformat(r['at'])>=now()-timedelta(days=7)]
  if recent:st.metric(f'최근 7일 측정 평균 · {len(recent)}회',f'{sum(r["s"] for r in recent)/len(recent):.0f} / {sum(r["d"] for r in recent)/len(recent):.0f} mmHg')
  with st.expander('기록 보기 · 삭제 · 다운로드'):
   import pandas as pd
   df=pd.DataFrame([{'시간':datetime.fromisoformat(r['at']).strftime('%m/%d %H:%M'),'최고':r['s'],'최저':r['d'],'맥박':r['pulse']} for r in logs]);st.dataframe(df,hide_index=True)
   st.download_button('기록 다운로드',df.to_csv(index=False).encode('utf-8-sig'),'blood_pressure.csv','text/csv')
   chosen=st.selectbox('삭제할 기록',logs,format_func=lambda r:f'{r["at"][:16]} · {r["s"]}/{r["d"]}')
   if st.button('선택 기록 삭제'):delete(chosen['id']);st.rerun()
 with st.expander('측정·색상 기준'):
  st.write('성인 참고 기준: 초록 <120 및 <80 / 노랑 120~139 또는 80~89 / 빨강 ≥140 또는 ≥90, 또는 <90 또는 <60. 높은 단계 우선. 개인 진단·응급도 판정은 아닙니다.')
  st.write('5분 안정 후 1분 간격으로 두 번 측정해 각각 기록하세요. 평균은 저장한 측정값의 단순평균입니다. 혈압약은 임의로 줄이거나 늘리지 마세요.')
  st.link_button('미국심장협회 기준','https://www.heart.org/en/health-topics/high-blood-pressure/understanding-blood-pressure-readings/monitoring-your-blood-pressure-at-home')
else:
 st.title('💊 오늘 먹을 약')
 person=st.selectbox('가족 선택',people+['새 가족'])
 if person=='새 가족':person=st.text_input('이름 또는 별명',max_chars=20).strip()
 st.caption('처방받은 복용법대로 등록하세요. 앱이 열려 있을 때만 알림이 동작해요. 휴대폰 알람도 설정해 주세요.')
 sound=st.toggle('화면 내 알림 켜기',value=False)
 with st.expander('＋ 약 추가'):
  with st.form('med',clear_on_submit=True):
   name=st.text_input('약 이름',max_chars=70);dose=st.text_input('복용량 · 예: 1정, 식후',max_chars=100)
   times=st.text_input('매일 먹는 시간',placeholder='08:00, 13:00, 20:00')
   if st.form_submit_button('약 등록',use_container_width=True):
    try:
     ts=sorted(set(datetime.strptime(t.strip(),'%H:%M').strftime('%H:%M') for t in times.split(',')))
     if not person or not name.strip() or not ts:raise ValueError()
     put('med',{'person':person,'name':name.strip(),'dose':dose,'times':ts});st.rerun()
    except ValueError:st.error('이름과 시간을 확인해 주세요. 예: 08:00, 20:00')
 @st.fragment(run_every='20s')
 def medication_list():
  meds=[m for m in items('med') if m['person']==person];taken={x['slot'] for x in items('taken') if x['date']==str(now().date())};due=[]
  if not meds:st.info('＋ 약 추가에서 등록하세요.')
  for m in meds:
   for t in m['times']:
    slot=m['id']+'_'+t;done=slot in taken
    a,b=st.columns([3,2]);a.markdown(f'**{html.escape(t)} · {html.escape(m["name"])}**');a.caption(m['dose'])
    if done:b.write('✅ 복용 완료')
    elif b.button('먹었어요',key=slot,use_container_width=True):
     put('taken',{'slot':slot,'date':str(now().date()),'at':now().isoformat()});st.rerun()
    if not done and t<=now().strftime('%H:%M'):due.append(m['name']+' '+t)
  if due:
   st.warning('복용 여부 확인: '+', '.join(due))
   if sound:
    import json as j
    components.html('''<button onclick="var a=new AudioContext();var o=a.createOscillator();o.connect(a.destination);o.frequency.value=660;o.start();o.stop(a.currentTime+.3);this.innerText='소리 확인 완료'">🔔 알림 소리 재생</button>''',height=45)
   st.caption('복용을 놓쳤다면 처방 안내나 약사에게 확인하세요. 임의로 두 배 복용하지 마세요.')
 medication_list()
 with st.expander('약 관리 · 복용 기록'):
  for m in [m for m in items('med') if m['person']==person]:
   if st.button('삭제 · '+m['name'],key='del'+m['id']):delete(m['id']);st.rerun()
  records=items('taken');med_ids={m['id'] for m in items('med') if m['person']==person}
  records=[x for x in records if x['slot'].rsplit('_',1)[0] in med_ids]
  for r in sorted(records,key=lambda x:x['at'],reverse=True)[:30]:
   st.write(r['at'][:16].replace('T',' ')+' · 복용 완료')
   if st.button('완료 취소',key='undo'+r['id']):delete(r['id']);st.rerun()
