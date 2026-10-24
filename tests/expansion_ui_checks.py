"""Exercise the shipped HTML with browser input, without game test hooks."""
import os, subprocess, re
from pathlib import Path
from playwright.sync_api import sync_playwright
from guest_helpers import complete_guest_form
ROOT=Path(__file__).resolve().parents[1]
URL=os.environ.get('FOODFIGHT_BASE_URL','http://127.0.0.1:8000').rstrip('/')+'/Food_Fight_Development.html'
source=(ROOT/'Food_Fight_Development.html').read_text()
baseline=subprocess.check_output(['git','show','530fb1e:Food_Fight_Development.html'],cwd=ROOT,text=True)
for pattern in [r'const levelTemplates=\[.*?\n\];',r'function collision\(a,b\)\{.*?\}']:
 assert re.search(pattern,source,re.S).group()==re.search(pattern,baseline,re.S).group()
for name in ['Food_Fight_Classic_Anonymous_Admin.html','Food_Fight_Classic_Colour.html']:
 assert (ROOT/'source'/name).read_bytes()==subprocess.check_output(['git','show','530fb1e:source/'+name],cwd=ROOT)
loop_pattern=r'function puzzleLoop\(t\).*?(?=\nfunction drawProjectileAt)'
loop=re.search(loop_pattern,source,re.S).group().replace('retireComboShot(b);','').replace("recordEvent('hits');registerComboHit(b);persist();",'')
assert loop==re.search(loop_pattern,baseline,re.S).group(), 'Physics loop changed beyond additive event hooks'
assert not re.search(r'<script[^>]+src=',source)
print('Preservation PASS: all 12 templates, collision function, recovered originals, no external scripts')
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for name,w,h,theme,cost in [('desktop',1280,800,'Classic',0),('iPad portrait',820,1180,'Kitchen Chaos',250),('iPad landscape',1180,820,'Midnight Snack',500),('mobile',390,844,'Classic',0)]*int(os.environ.get('FOODFIGHT_UI_REPEATS','1')):
  if os.environ.get('FOODFIGHT_UI_VIEWPORT') and name!=os.environ['FOODFIGHT_UI_VIEWPORT']:continue
  ctx=b.new_context(viewport={'width':w,'height':h},has_touch=True,is_mobile=name!='desktop')
  page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script("window.inputLog=[];for(const type of ['pointerdown','pointerup','pointercancel','touchstart','touchend','click','gotpointercapture','lostpointercapture'])document.addEventListener(type,e=>inputLog.push([e.type,e.target.id,e.pointerId,e.clientX,e.clientY,e.isPrimary,e.defaultPrevented,e.touches?.length]),true)")
  assert page.goto(URL).status==200
  page.evaluate("localStorage.setItem('bulletDashSave',JSON.stringify({coins:800,highScore:777,unlockedLevel:12,clearedLevels:[1,2,3,4,5,6,7,8,9,10,11,12]}))")
  page.reload()
  page.locator('#guestPlayButton').tap();complete_guest_form(page)
  page.locator('#dailyButton').tap();page.locator('#claimDaily').tap()
  assert page.locator('#claimDaily').is_disabled()
  page.locator('#featureBack').tap();page.locator('#shopButton').tap()
  card=page.locator('#backgroundCards .itemCard').filter(has_text=theme)
  if cost:card.locator('button').tap()
  page.locator('#shopBack').tap();page.locator('#levelsButton').tap()
  assert page.locator('#levelCards button:enabled').count()==12
  page.locator('#levelCards button').first.tap()
  target={'x':w*.78,'y':74+.4*(h-142)}
  if name=='desktop':
   page.mouse.move(110,h*.52);page.mouse.down();page.mouse.move(target['x'],target['y'],steps=6);page.mouse.up()
  else:
   cdp=ctx.new_cdp_session(page)
   # Human-paced movement: a single 200px jump and release in one millisecond
   # can make Chromium's gesture recognizer suppress the following native click.
   start={'x':110,'y':h*.52}
   cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[start]})
   for step in range(1,7):
    page.wait_for_timeout(20)
    point={k:start[k]+(target[k]-start[k])*step/6 for k in ('x','y')}
    cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[point]})
   page.wait_for_timeout(20)
   cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
   cdp.detach()
  page.wait_for_function("document.getElementById('resultScreen').classList.contains('active')")
  assert page.locator('#resultTitle').inner_text()=='LEVEL CLEARED'
  assert '★★★' in page.locator('#resultStars').inner_text()
  page.locator('#resultHome').tap()
  try:page.locator('#homeScreen').wait_for(state='visible',timeout=3000)
  except Exception:
   Path('/tmp/foodfight-review').mkdir(exist_ok=True)
   page.screenshot(path='/tmp/foodfight-review/navigation-failure.png')
   print('Input log:',page.evaluate('window.inputLog.slice(-24)'))
   print('Navigation failure:',page.evaluate("[...document.querySelectorAll('.screen.active')].map(s=>s.id)"),errors)
   raise
  page.locator('#achievementsButton').tap()
  page.locator('.featureCard').filter(has=page.locator('h3',has_text='First Bite')).locator('button').tap()
  page.locator('#featureBack').tap()
  # Native keyboard activation of the new menu control.
  page.locator('#statisticsButton').focus();page.keyboard.press('Enter')
  assert page.locator('#featureTitle').inner_text()=='STATISTICS'
  assert '777' in page.locator('#featureContent').inner_text()
  page.locator('#featureBack').tap();page.locator('#missionsButton').tap()
  assert page.locator('#featureContent button').count()==3
  page.locator('#featureBack').tap()
  saved=page.evaluate("JSON.parse(localStorage.getItem('bulletDashSave'))")
  assert saved['coins']==850-cost and saved['highScore']==777
  assert saved['featuresV1']['stats']['fired']==1 and saved['featuresV1']['stats']['hits']==1
  assert saved['featuresV1']['stars']['1']==3
  Path('/tmp/foodfight-review').mkdir(exist_ok=True)
  page.screenshot(path='/tmp/foodfight-review/'+name.replace(' ','-')+'-home.png')
  page.locator('#puzzleButton').tap();page.locator('#levelCards button').first.tap()
  page.screenshot(path='/tmp/foodfight-review/'+name.replace(' ','-')+'-game.png')
  page.locator('#homeButton').tap();page.reload()
  assert page.evaluate("JSON.parse(localStorage.getItem('bulletDashSave')).coins")==850-cost
  assert not errors,errors
  print(name+': PASS — real input, new panels/claims, keyboard activation, themes, real puzzle clear/stars, reload, no JS errors')
  ctx.close()
 b.close()
