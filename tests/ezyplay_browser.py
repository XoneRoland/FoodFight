"""Built-site browser integration. Native input plus recorded controls using the
same advance() loop as the game. Instrumentation is response-only, never shipped.
"""
import os,json,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
BASE=os.environ.get('EZYPLAY_BASE_URL','http://127.0.0.1:8051').rstrip('/')
HOOK='''
window.__racerTest={
 snapshot:()=>({mode:session.mode,time:session.time,remaining:session.remaining,car:{...session.car},checkpoint:session.nextCheckpoint,controls:controls.value(),progress:structuredClone(progress),render:renderer?{...renderer.info,width:renderer.canvas.width,height:renderer.canvas.height}:null}),
 replay:record=>{
  if(session.track.id!==record.id)throw Error('Wrong track replay');
  startTrack(current);const original=controls.value;
  try{for(const [count,throttle,brake,steer] of record.controls){controls.value=()=>({throttle,brake,steer});for(let i=0;i<count;i++)advance()}}
  finally{controls.value=original;controls.clear()}
  renderer.render(session.car,0,true);return {mode:session.mode,time:session.time,checkpoints:session.nextCheckpoint,result:session.result};
 }
};
'''
records=json.loads((ROOT/'tests/racer_paths.json').read_text())['records']
assert (ROOT/'Food_Fight_Development.html').read_bytes()==subprocess.check_output(['git','show','a299daa:Food_Fight_Development.html'],cwd=ROOT)
source=(ROOT/'racer/racer.mjs').read_text()
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 for label,w,h in [('desktop',1280,800),('iPad landscape',1180,820),('iPad portrait',820,1180),('mobile',390,844)]:
  if os.environ.get('EZYPLAY_BROWSER_VIEWPORT') and label!=os.environ['EZYPLAY_BROWSER_VIEWPORT']:continue
  ctx=browser.new_context(viewport={'width':w,'height':h},has_touch=True,is_mobile=label!='desktop')
  page=ctx.new_page();errors=[];failed=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('response',lambda r:failed.append(str(r.status)+' '+r.url) if r.status>=400 else None)
  page.route('**/racer/racer.mjs',lambda route:route.fulfill(content_type='text/javascript',body=source+HOOK))
  assert page.goto(BASE+'/').status==200
  assert page.get_by_role('link',name='PLAY FOOD FIGHT').is_visible()
  food='{"coins":987,"highScore":321,"unlockedLevel":6,"clearedLevels":[1,2,3]}'
  catalogue='{"items":[],"codes":[]}'
  page.evaluate('(v)=>{localStorage.setItem("bulletDashSave",v[0]);localStorage.setItem("foodFightLocalCatalogueV1",v[1])}',[food,catalogue])
  page.get_by_role('link',name='PLAY RACER').tap();page.wait_for_url('**/racer/')
  page.wait_for_function('!!window.__racerTest')
  def snap():return page.evaluate('__racerTest.snapshot()')
  def tap(s):page.locator(s).tap()
  def await_racing():
   try:page.wait_for_function("__racerTest.snapshot().mode==='racing'",timeout=15000)
   except Exception:
    print('Race start diagnostic',label,snap(),page.evaluate('[document.visibilityState,document.hasFocus()]'),errors,flush=True)
    raise
  assert page.locator('#graphicsError').is_hidden(),page.locator('#graphicsMessage').inner_text()
  assert page.evaluate("localStorage.getItem('ezyplay_racer_v1')")==None
  tap('#trackSelectButton');assert page.locator('.track-card').count()==12
  assert page.locator('.track-card button:disabled').count()==11
  tap('#trackBack');tap('#controlsButton');assert page.locator('#help').is_visible();tap('#helpBack')
  page.bring_to_front()
  tap('#playButton');assert snap()['mode']=='countdown'
  page.keyboard.down('w');page.wait_for_timeout(400)
  assert snap()['time']==0 and snap()['car']['s']==6
  await_racing()
  page.wait_for_function('__racerTest.snapshot().car.s>8',timeout=10000);page.keyboard.up('w')
  assert snap()['car']['s']>7,('actual keyboard acceleration must move the car',snap())
  old_yaw=snap()['car']['yaw'];page.keyboard.down('d');page.wait_for_timeout(300);page.keyboard.up('d')
  assert snap()['car']['yaw']>old_yaw
  page.keyboard.down('a');page.wait_for_timeout(250);page.keyboard.up('a')
  page.keyboard.press('Escape');assert snap()['mode']=='paused';before=snap()['time'];page.wait_for_timeout(350);assert snap()['time']==before
  page.keyboard.press('Escape');assert snap()['mode']=='racing'
  page.keyboard.down('s');page.wait_for_timeout(1500);page.keyboard.up('s')
  assert snap()['car']['vx']*__import__('math').sin(snap()['car']['yaw'])+snap()['car']['vz']*__import__('math').cos(snap()['car']['yaw'])<0
  page.keyboard.press('r');assert snap()['mode']=='countdown' and snap()['time']==0 and snap()['checkpoint']==0
  await_racing()
  page.evaluate("()=>{window.touchLog=[];for(const type of ['pointerdown','pointerup','pointercancel'])document.addEventListener(type,e=>touchLog.push([e.type,e.target.dataset.drive,e.pointerId]),true)}")
  cdp=ctx.new_cdp_session(page)
  def center(selector):
   box=page.locator(selector).bounding_box();return {'x':box['x']+box['width']/2,'y':box['y']+box['height']/2}
  gas={**center('[data-drive=throttle]'),'id':1};left={**center('[data-drive=left]'),'id':2}
  cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[gas,left]})
  page.wait_for_timeout(300);assert snap()['controls']=={'throttle':1,'brake':0,'steer':-1}
  # Ending one touch leaves the accelerator held by the other finger.
  cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[left]})
  assert snap()['controls']['throttle']==1 and snap()['controls']['steer']==0,(snap()['controls'],page.evaluate('touchLog'))
  # Capture must release even when a finger moves outside its original button.
  cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{**gas,'x':w/2,'y':h/2}]})
  cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
  assert snap()['controls']=={'throttle':0,'brake':0,'steer':0}
  cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[gas,left]})
  cdp.send('Input.dispatchTouchEvent',{'type':'touchCancel','touchPoints':[]})
  assert snap()['controls']=={'throttle':0,'brake':0,'steer':0}
  page.keyboard.down('w')
  cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[gas]})
  cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
  assert snap()['controls']['throttle']==1,'ending a touch must not cancel a held keyboard input'
  page.evaluate("window.dispatchEvent(new Event('blur'))")
  assert snap()['mode']=='paused' and snap()['controls']['throttle']==0
  page.keyboard.up('w');tap('#resumeButton')
  # Timing/render budget observation, not a claim of real iPad performance.
  frames=snap()['render']['frames'];page.wait_for_timeout(1000);fps=snap()['render']['frames']-frames
  render=snap()['render'];assert render['drawCalls']==2 and render['width']*render['height']<=1400000 and render['vertices']<120000
  print(label+': native keyboard, simultaneous touch, partial release, outside release, cancel, blur/pause PASS; software-rendered frames/s ≈',fps,'resolution scale',render.get('scale'),flush=True)
  Path('/tmp/ezyplay-review').mkdir(exist_ok=True)
  page.screenshot(path='/tmp/ezyplay-review/'+label.replace(' ','-')+'-driving.png')
  for record in records:
   if record['id']>1:tap('#nextButton')
   result=page.evaluate('(record)=>__racerTest.replay(record)',record)
   assert result['mode']=='finished' and abs(result['time']-record['time'])<.001
   assert result['checkpoints']==record['checkpoints']
   assert page.locator('#result').is_visible()
   assert snap()['render']['drawCalls']==2 and snap()['render']['vertices']<120000
   saved=snap()['progress'];assert saved['unlocked']==min(12,record['id']+1)
   assert saved['stats']['finishes']==record['id']
   assert abs(saved['bestTimes'][str(record['id'])]-record['time'])<.001
  assert snap()['progress']['completed']==list(range(1,13))
  tap('#resultTracks');assert page.locator('.track-card button:enabled').count()==12
  tap('#trackBack');page.get_by_role('button',name='Car color: Coral red',exact=True).tap()
  expected=snap()['progress'];assert expected['color']=='#ff6479'
  assert page.evaluate("localStorage.getItem('bulletDashSave')")==food
  assert page.evaluate("localStorage.getItem('foodFightLocalCatalogueV1')")==catalogue
  page.reload();page.wait_for_function('!!window.__racerTest');assert snap()['progress']==expected
  page.locator('#platformHome').tap();page.wait_for_url(BASE+'/')
  page.get_by_role('link',name='PLAY FOOD FIGHT').tap();page.wait_for_url('**/food-fight/')
  frame=page.frame_locator('iframe');assert '987' in frame.locator('#coinsText').inner_text()
  assert '321' in frame.locator('#highScoreText').inner_text()
  page.get_by_role('link',name='BACK TO EZYPLAY').tap();page.wait_for_url(BASE+'/')
  assert page.evaluate("localStorage.getItem('bulletDashSave')")==food
  # Direct Food Fight route, original in-game Home behavior and a real touch puzzle clear.
  page.goto(BASE+'/food-fight/')
  frame=page.frame_locator('iframe')
  frame.locator('#guestPlayButton').tap()
  frame.locator('#guestFirstName').fill('Test');frame.locator('#guestLastName').fill('Player');frame.locator('#guestUsername').fill('tester')
  frame.locator('#guestForm button[type=submit]').tap();frame.locator('#puzzleButton').tap();frame.locator('#levelCards button').first.tap()
  box=frame.locator('#game').bounding_box();fw,fh=box['width'],box['height']
  begin={'x':box['x']+min(110,fw*.15),'y':box['y']+fh*.52}
  target={'x':box['x']+fw*.78,'y':box['y']+74+.4*(fh-142)}
  cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[begin]})
  for step in range(1,7):
   page.wait_for_timeout(20);point={k:begin[k]+(target[k]-begin[k])*step/6 for k in ('x','y')}
   cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[point]})
  cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
  frame.locator('#resultScreen.active').wait_for(timeout=10000)
  assert frame.locator('#resultTitle').inner_text()=='LEVEL CLEARED'
  frame.locator('#resultHome').tap();assert frame.locator('#homeScreen').is_visible()
  saved_food=page.evaluate("JSON.parse(localStorage.getItem('bulletDashSave'))")
  assert saved_food['coins']==987 and saved_food['highScore']==321 and saved_food['unlockedLevel']==6
  page.get_by_role('link',name='BACK TO EZYPLAY').tap();page.wait_for_url(BASE+'/')
  assert not errors,errors;assert not failed,failed
  page.screenshot(path='/tmp/ezyplay-review/'+label.replace(' ','-')+'-home.png')
  print(label+': all 12 tracks rendered, legitimately completed via input replays, unlocked, saved; Food Fight isolation/navigation PASS',flush=True)
  ctx.close()
 # Unsupported WebGL must show useful UI rather than a broken black canvas.
 ctx=browser.new_context();page=ctx.new_page();fallback_errors=[];page.on('pageerror',lambda e:fallback_errors.append(str(e)))
 page.add_init_script("const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(type,...args){return type==='webgl'?null:original.call(this,type,...args)}")
 page.goto(BASE+'/racer/');page.locator('#graphicsError').wait_for(state='visible');assert page.locator('#playButton').is_disabled()
 page.locator('#platformHome').click();page.wait_for_url(BASE+'/');assert not fallback_errors,fallback_errors
 ctx.close()
 # Denied storage must not stop menus/colors; context loss must be recoverable.
 ctx=browser.new_context();page=ctx.new_page();blocked_errors=[];page.on('pageerror',lambda e:blocked_errors.append(str(e)))
 page.add_init_script("Storage.prototype.getItem=function(){throw Error('blocked')};Storage.prototype.setItem=function(){throw Error('blocked')}")
 page.goto(BASE+'/racer/');page.get_by_role('button',name='Car color: Coral red',exact=True).click()
 assert 'browser storage is unavailable' in page.locator('#notice').inner_text()
 page.evaluate("document.getElementById('scene').getContext('webgl').getExtension('WEBGL_lose_context').loseContext()")
 page.locator('#graphicsError').wait_for(state='visible');assert 'interrupted' in page.locator('#graphicsMessage').inner_text()
 assert not blocked_errors,blocked_errors;ctx.close()
 ctx=browser.new_context();page=ctx.new_page();page.goto(BASE+'/racer/')
 page.keyboard.down('ArrowUp');assert page.locator('[data-drive=throttle]').get_attribute('aria-pressed')=='true'
 page.keyboard.down('w');page.keyboard.up('ArrowUp');assert page.locator('[data-drive=throttle]').get_attribute('aria-pressed')=='true'
 page.keyboard.up('w');assert page.locator('[data-drive=throttle]').get_attribute('aria-pressed')=='false'
 for key,action in [('ArrowLeft','left'),('ArrowRight','right'),('ArrowDown','brake')]:
  page.keyboard.down(key);assert page.locator('[data-drive='+action+']').get_attribute('aria-pressed')=='true';page.keyboard.up(key);assert page.locator('[data-drive='+action+']').get_attribute('aria-pressed')=='false'
 ctx.close();print('Arrow key aliases and independent keyboard holds PASS',flush=True)
 print('Fallbacks PASS: unavailable/lost WebGL, accessible EzyPlay return, blocked-storage session behavior',flush=True)
 browser.close()
