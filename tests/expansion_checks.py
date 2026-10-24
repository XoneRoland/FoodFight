"""Incremental integration checks, using test-only closure access to drive real handlers.
No hooks ship in the game. Run with --stage stats|achievements|daily|stars|backgrounds|combos.
"""
import argparse, os, json
from pathlib import Path
from playwright.sync_api import sync_playwright
from guest_helpers import complete_guest_form

STAGES=['stats','achievements','daily','stars','backgrounds','combos']
parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=STAGES,default='combos');args=parser.parse_args()
stage=STAGES.index(args.stage)
ROOT=Path(__file__).resolve().parents[1]
URL=os.environ.get('FOODFIGHT_BASE_URL','http://127.0.0.1:8000').rstrip('/')+'/Food_Fight_Development.html'
legacy={'highScore':4321,'coins':875,'unlockedR':['burger-cannon','frying-pan'],'unlockedB':['burger','pizza'],'equippedR':'frying-pan','equippedB':'pizza','unlockedLevel':12,'clearedLevels':[1,2,3],'puzzleBest':{'1':200},'redeemedCodes':['OLD-CODE'],'extraLegacyField':{'keep':True}}
HOOK='''window.expansion={get:()=>JSON.parse(JSON.stringify(save)),state:()=>({state,shotCount,levelIndex}),puzzleStart,firePuzzle,goHome,
 stop:()=>cancelAnimationFrame(raf),targets:()=>targets.map(t=>({...t})),
 simulate:(frames=300)=>{cancelAnimationFrame(raf);last=0;for(let i=1;i<=frames&&state==='puzzle';i++){puzzleLoop(i*16.67);cancelAnimationFrame(raf)}},
 stageShot:(x,y,hp=1,id=0)=>{const b=shots[shots.length-1];targets=[{id,x,y,r:15,type:'agent',hp,alive:true}];b.x=x-8;b.y=y;b.vx=8.5;b.vy=0;},
 miss:()=>{for(const b of shots){b.life=0;b.alive=false}},
 preparedWin:()=>{targets.forEach(t=>t.alive=false);},
 startEndless:()=>{state='intro';startEndlessLoop();cancelAnimationFrame(raf)},
 crash:()=>{score=250;endlessOver()},
 seedStats:values=>{Object.assign(save.featuresV1.stats,values);persist()},
 load:()=>{save=loadSave()},
};'''
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 ctx=b.new_context(timezone_id='Australia/Perth',viewport={'width':1180,'height':820},has_touch=True)
 page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 source=(ROOT/'Food_Fight_Development.html').read_text()
 page.route('**/Food_Fight_Development.html',lambda route:route.fulfill(content_type='text/html',body=source.replace('})();',HOOK+'\n})();')))
 page.goto(URL)
 page.evaluate('(s)=>localStorage.setItem("bulletDashSave",JSON.stringify(s))',legacy);page.reload()
 def get():return page.evaluate('expansion.get()')
 def run(js):return page.evaluate(js)
 def tap(sel):page.locator(sel).click()
 def home():run('expansion.goHome()')
 def join():tap('#guestPlayButton');complete_guest_form(page)
 def puzzle():run('expansion.puzzleStart(0);expansion.stop()')
 def shot():run('expansion.firePuzzle(500,400);expansion.stop()')
 def hit(hp=100,target_id=0):run(f'expansion.stageShot(500,400,{hp},{target_id});expansion.simulate(1)')
 def reset():
  page.evaluate('(s)=>localStorage.setItem("bulletDashSave",JSON.stringify(s))',legacy);page.reload();join()
 def stored():return page.evaluate('JSON.parse(localStorage.getItem("bulletDashSave"))')
 assert stored()==legacy,'initialization must not write or replace legacy data'
 join();assert get()['featuresV1']['stats']==dict.fromkeys(['fired','hits','earned','rounds','puzzleWins','gameplayCoins'],0)
 for i in range(12):run(f'expansion.puzzleStart({i});expansion.stop()')
 assert get()['featuresV1']['stats']['rounds']==0,'level/menu initialization is not a round'
 puzzle();shot();hit()
 stats=get()['featuresV1']['stats'];assert stats['fired']==1 and stats['hits']==1 and stats['rounds']==1
 # The same projectile cannot hit the same target twice.
 run('expansion.simulate(1)');assert get()['featuresV1']['stats']['hits']==1
 run('expansion.startEndless();expansion.crash();expansion.crash()')
 assert get()['featuresV1']['stats']['rounds']==2 and get()['featuresV1']['stats']['fired']==2
 assert get()['featuresV1']['stats']['earned']==20 and get()['coins']==895
 page.reload();saved=get()
 for key in legacy:
  if key!='coins':assert saved[key]==legacy[key],key
 home();join();tap('#statisticsButton');assert '4,321' in page.locator('#featureContent').inner_text()
 print('Stats PASS: real shots/hits, no menu rounds, no duplicate hit/crash, legacy fields, refresh, stats UI')
 # Malformed extensions must never erase unrelated legacy fields.
 bad={**legacy,'featuresV1':{'version':-1,'stats':{'fired':'invalid','hits':-7,'earned':None}}}
 page.evaluate('(s)=>localStorage.setItem("bulletDashSave",JSON.stringify(s))',bad);page.reload()
 assert get()['coins']==875 and get()['highScore']==4321 and get()['extraLegacyField']==legacy['extraLegacyField']
 assert get()['featuresV1']['stats']['fired']==0
 if stage>=1:
  reset();tap('#achievementsButton')
  beginner=page.locator('.featureCard').filter(has=page.locator('h3',has_text='Puzzle Beginner'))
  beginner.locator('button').click();assert get()['coins']==950
  assert beginner.locator('button').is_disabled()
  home();puzzle();shot();home();tap('#achievementsButton')
  first=page.locator('.featureCard').filter(has=page.locator('h3',has_text='First Bite'));first.locator('button').click()
  assert get()['coins']==975
  page.reload();join();tap('#achievementsButton')
  assert page.locator('.featureCard').filter(has=page.locator('h3',has_text='First Bite')).locator('button').is_disabled()
  run("expansion.seedStats({fired:100,hits:50,earned:1000})");home();tap('#achievementsButton')
  for name in ['Food Fighter','Sharpshooter','Coin Collector']:
   page.locator('.featureCard').filter(has=page.locator('h3',has_text=name)).locator('button').click()
  assert len(get()['featuresV1']['claimedAchievements'])==5
  print('Achievements PASS: legacy puzzle credit, thresholds, one-time claims, reload')
 if stage>=2:
  reset();page.clock.install(time=__import__('datetime').datetime(2026,10,24,15,59,tzinfo=__import__('datetime').timezone.utc))
  tap('#dailyButton');assert 'Day 1' in page.locator('#featureContent').inner_text()
  tap('#claimDaily');assert get()['coins']==900
  assert page.locator('#claimDaily').is_disabled()
  page.reload();join();tap('#dailyButton');assert page.locator('#claimDaily').is_disabled()
  page.clock.set_system_time(__import__('datetime').datetime(2026,10,24,16,1,tzinfo=__import__('datetime').timezone.utc))
  home();tap('#dailyButton');assert 'Day 2' in page.locator('#featureContent').inner_text()
  tap('#claimDaily');assert get()['coins']==950
  page.clock.set_system_time(__import__('datetime').datetime(2026,10,29,16,1,tzinfo=__import__('datetime').timezone.utc))
  home();tap('#dailyButton');assert 'Day 3' in page.locator('#featureContent').inner_text()
  # Cycle through the rest, then day seven wraps to day one.
  for day in range(3,8):
   home();tap('#dailyButton');tap('#claimDaily')
   page.clock.set_system_time(__import__('datetime').datetime(2026,11,day,16,1,tzinfo=__import__('datetime').timezone.utc))
  home();tap('#dailyButton');assert 'Day 1' in page.locator('#featureContent').inner_text()
  tap('#missionsButton') if False else None
  home();tap('#missionsButton')
  ids=get()['featuresV1']['missions']['ids'];assert len(ids)==len(set(ids))==3
  page.reload();join();tap('#missionsButton');assert get()['featuresV1']['missions']['ids']==ids
  # Real launch events advance only selected mission counters.
  for _ in range(20):puzzle();shot()
  home();tap('#missionsButton')
  missions=get()['featuresV1']['missions'];assert missions['progress']['fired']==20 and missions['progress']['rounds']==20
  assert missions['progress']['hits']==0
  for _ in range(10):puzzle();shot();hit(1)
  for _ in range(5):run('expansion.startEndless();expansion.crash()')
  home();tap('#missionsButton')
  while page.locator('#featureContent button:enabled').count():page.locator('#featureContent button:enabled').first.click()
  claimed=get()['featuresV1']['missions']['claimed'];assert len(claimed)>0
  coins=get()['coins'];home();tap('#missionsButton');assert page.locator('#featureContent button:enabled').count()==0
  assert get()['coins']==coins
  page.clock.set_system_time(__import__('datetime').datetime(2026,11,12,16,1,tzinfo=__import__('datetime').timezone.utc))
  home();tap('#missionsButton');assert get()['featuresV1']['missions']['progress']['fired']==0
  assert get()['featuresV1']['stats']['fired']>=20
  print('Daily PASS: Perth midnight, one claim/day, refresh, missed days, seven-day cycle, deterministic missions, gameplay progress/reset/claims')
 if stage>=3:
  reset();assert get()['featuresV1']['stars']['1']==1
  puzzle();shot();run('expansion.preparedWin();expansion.simulate(1)')
  assert get()['featuresV1']['stars']['1']==3
  assert '★★★' in page.locator('#resultStars').inner_text()
  puzzle()
  for _ in range(3):shot()
  run('expansion.preparedWin();expansion.simulate(1)')
  assert get()['featuresV1']['stars']['1']==3
  page.reload();assert get()['unlockedLevel']==12 and get()['featuresV1']['stars']['1']==3
  assert get()['clearedLevels']==[1,2,3]
  print('Stars PASS: conservative migration, efficient clear, lower replay never reduces best, original unlocks intact')
 if stage>=4:
  reset();tap('#shopButton')
  kitchen=page.locator('#backgroundCards .itemCard').filter(has_text='Kitchen Chaos');kitchen.locator('button').click()
  assert get()['coins']==625
  midnight=page.locator('#backgroundCards .itemCard').filter(has_text='Midnight Snack');midnight.locator('button').click()
  assert get()['coins']==125
  page.locator('#backgroundCards .itemCard').filter(has_text='Classic').locator('button').click()
  kitchen.locator('button').click();assert get()['coins']==125
  page.reload();assert get()['featuresV1']['backgrounds']['equipped']=='kitchen'
  assert set(get()['featuresV1']['backgrounds']['owned'])=={'classic','kitchen','midnight'}
  assert get()['featuresV1']['stats']['earned']==0
  print('Backgrounds PASS: exact prices, ownership/equipping, refresh, spending does not alter earned total')
 if stage>=5:
  reset();run('expansion.puzzleStart(11);expansion.stop()')
  for _ in range(3):shot();hit()
  assert get()['coins']==885
  assert get()['featuresV1']['stats']['hits']==3
  # Same shot hitting a different target is a real hit, but not another combo increment.
  hit(target_id=1);assert get()['coins']==885
  assert get()['featuresV1']['stats']['hits']>=4
  shot();run('expansion.miss();expansion.simulate(1)')
  for _ in range(2):shot();hit()
  assert get()['coins']==885
  shot();hit();assert get()['coins']==895
  home();assert page.locator('#comboIndicator').is_hidden()
  print('Combos PASS: one credit per projectile, milestone once, target multihits retained, missed shot reset, active gameplay only')
 # Storage failures must leave claims, coins and purchases unchanged.
 if stage>=1:
  reset();tap('#achievementsButton');before=get()
  page.evaluate("()=>{Storage.prototype.setItem=function(){throw Error('storage full')}}")
  page.locator('.featureCard').filter(has=page.locator('h3',has_text='Puzzle Beginner')).locator('button').click()
  assert get()==before
  print('Atomic claims PASS: failed storage writes leave rewards and flags unchanged')
 assert not errors,errors
 b.close()
