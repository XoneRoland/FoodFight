"""Static Netlify detection + real browser opt-in flow with intercepted local POSTs.
This verifies the client contract, not receipt in Netlify's production dashboard.
"""
import os,json,subprocess
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse,parse_qs
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
BASE=os.environ.get('FOODFIGHT_BASE_URL','http://127.0.0.1:8070').rstrip('/')
URL=BASE+'/Food_Fight_Development.html'
class Forms(HTMLParser):
 def __init__(self):super().__init__();self.forms=[];self.current=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='form':self.current={'attrs':a,'fields':[]};self.forms.append(self.current)
  if self.current and tag=='input':self.current['fields'].append(a)
 def handle_endtag(self,tag):
  if tag=='form':self.current=None
parser=Forms();parser.feed((ROOT/'dist/Food_Fight_Development.html').read_text())
detected=[f for f in parser.forms if f['attrs'].get('data-netlify')=='true']
assert len(detected)==1
form=detected[0];assert form['attrs']['name']=='ezyplay-guest-registration' and form['attrs']['method'].upper()=='POST'
assert form['attrs']['netlify-honeypot']=='bot-field'
assert {f['name'] for f in form['fields']}=={'form-name','nickname','consent','bot-field'}
consent=next(f for f in form['fields'] if f['name']=='consent');assert 'required' in consent and 'checked' not in consent
assert (ROOT/'dist/privacy.html').read_bytes()==(ROOT/'privacy.html').read_bytes()
for path in (ROOT/'racer').glob('*'):
 if path.is_file():assert path.read_bytes()==subprocess.check_output(['git','show','b20444e:racer/'+path.name],cwd=ROOT)
print('Static PASS — one detectable form, exact minimal fields, unchecked consent, deployed privacy, unchanged Racer',flush=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for label,w,h in [('desktop',1280,800),('iPad portrait',820,1180),('iPad landscape',1180,820),('mobile',390,844)]:
  ctx=browser.new_context(viewport={'width':w,'height':h},has_touch=True,is_mobile=label!='desktop')
  page=ctx.new_page();errors=[];posts=[];pending=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script("const originalFetch=window.fetch;window.fetch=(url,options)=>{window.lastRegistrationOptions={credentials:options.credentials,referrerPolicy:options.referrerPolicy};return originalFetch(url,options)}")
  def route_handler(route):
   if route.request.method=='POST':posts.append(route.request);pending.append(route)
   else:route.continue_()
  page.route('**/*',route_handler)
  page.goto(URL)
  food='{"coins":987,"highScore":321,"unlockedLevel":6,"clearedLevels":[1,2,3]}'
  racer='{"version":1,"unlocked":4,"color":"#ff6479"}'
  page.evaluate('(v)=>{localStorage.setItem("bulletDashSave",v[0]);localStorage.setItem("ezyplay_racer_v1",v[1])}',[food,racer]);page.reload()
  def tap(s):page.locator(s).tap()
  def dispatch_submit():page.locator('#guestForm').dispatch_event('submit')
  tap('#guestPlayButton');assert page.locator('#guestSubmit').is_disabled()
  page.locator('#guestUsername').fill('Declined_42');dispatch_submit()
  assert 'Consent is needed' in page.locator('#guestFormStatus').inner_text() and len(posts)==0
  tap('#guestSkip');assert page.locator('#endlessButton').is_enabled() and len(posts)==0
  tap('#endGuestSession');tap('#guestPlayButton')
  page.locator('#guestUsername').fill('bad name');page.locator('#guestConsent').check();dispatch_submit()
  assert len(posts)==0
  page.locator('#guestUsername').fill('Guest_42');assert page.locator('#guestSubmit').is_enabled()
  tap('#guestSubmit');page.wait_for_timeout(50)
  assert len(posts)==1 and page.locator('#guestSubmit').is_disabled()
  assert page.locator('#guestSkip').is_disabled() and page.locator('#guestCancel').is_disabled()
  dispatch_submit();dispatch_submit();assert len(posts)==1
  request=posts[0];assert request.url==BASE+'/' and request.method=='POST'
  assert request.headers['content-type'].startswith('application/x-www-form-urlencoded')
  assert parse_qs(request.post_data,keep_blank_values=True)=={'form-name':['ezyplay-guest-registration'],'nickname':['Guest_42'],'consent':['yes'],'bot-field':['']}
  assert page.evaluate('lastRegistrationOptions')=={'credentials':'omit','referrerPolicy':'no-referrer'}
  pending[0].fulfill(status=200,content_type='text/html',body='Accepted')
  page.locator('#homeScreen').wait_for(state='visible')
  assert '@Guest_42' in page.locator('#guestStatus').inner_text()
  assert page.evaluate("localStorage.getItem('bulletDashSave')")==food
  assert page.evaluate("localStorage.getItem('ezyplay_racer_v1')")==racer
  assert not page.evaluate("Object.values(localStorage).some(v=>v.includes('Guest_42'))")
  tap('#guestPlayButton');assert page.locator('#guestSubmit').is_disabled();dispatch_submit();assert len(posts)==1
  tap('#guestCancel')
  assert page.locator('#netlifyFormsDashboard').is_hidden()
  tap('#adminOpenButton');page.locator('#adminPasswordInput').fill('wrong');tap('#adminLoginButton');assert page.locator('#netlifyFormsDashboard').is_hidden()
  page.locator('#adminPasswordInput').fill('RGE123');tap('#adminLoginButton')
  assert page.locator('#netlifyFormsDashboard').is_visible()
  assert page.locator('#netlifyFormsDashboard').get_attribute('href')=='https://app.netlify.com/projects/ezygame/forms'
  assert 'authenticated server-side API' in page.locator('#netlifyRegistrationAdmin').inner_text()
  assert page.locator('#activePlayerUsername').inner_text()=='@Guest_42'
  assert page.locator('#activePlayerName').count()==0
  tap('#adminHomeButton');tap('#endlessButton');page.wait_for_timeout(2100);assert page.locator('#hud').is_visible();tap('#homeButton')
  tap('#shopButton');assert '987' in page.locator('#shopCoins').inner_text();tap('#shopBack')
  tap('#puzzleButton');assert page.locator('#levelCards .levelCard').count()==12;page.locator('#levelCards button').first.tap();assert page.locator('#puzzleFooter').is_visible();tap('#homeButton')
  assert len(posts)==1
  tap('#endGuestSession');tap('#guestPlayButton');assert not page.locator('#guestConsent').is_checked();assert page.locator('#guestUsername').input_value()==''
  page.goto(BASE+'/privacy.html');assert page.get_by_role('heading',name='Privacy & guest play').is_visible()
  assert '30 days' in page.locator('main').inner_text()
  assert not errors,errors
  print(label+': PASS — consent/decline, minimal URL-encoded POST, in-flight/completed duplicates blocked, admin link, privacy, gameplay, saves',flush=True)
  ctx.close()
 for failure in ['http','offline','timeout']:
  ctx=browser.new_context();page=ctx.new_page();errors=[];posts=[];pending=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  def fail_route(route):
   if route.request.method!='POST':route.continue_();return
   posts.append(route.request)
   if failure=='http':route.fulfill(status=503,body='Unavailable')
   elif failure=='offline':route.abort('failed')
   else:pending.append(route)
  page.route('**/*',fail_route)
  page.goto(URL)
  if failure=='timeout':page.clock.install()
  page.locator('#guestPlayButton').click();page.locator('#guestUsername').fill('Try_Once');page.locator('#guestConsent').check();page.locator('#guestSubmit').click()
  if failure=='timeout':page.wait_for_timeout(30);page.clock.fast_forward(8100)
  page.wait_for_function("document.getElementById('guestFormStatus').textContent.includes('could not confirm')")
  assert page.locator('#guestSubmit').is_disabled() and page.locator('#guestSkip').is_enabled()
  page.locator('#guestForm').dispatch_event('submit');assert len(posts)==1
  page.locator('#guestSkip').click();assert page.locator('#endlessButton').is_enabled()
  page.locator('#shopButton').click();assert page.locator('#shopScreen').is_visible()
  assert not errors,errors
  print(failure+': PASS — no automatic/repeated retry, clear failure, anonymous gameplay available',flush=True)
  if failure=='timeout':
   for route in pending:route.abort()
  ctx.close()
 # The public Food Fight route embeds the form; test its real POST target too.
 ctx=browser.new_context(has_touch=True);page=ctx.new_page();posts=[]
 def wrapper_route(route):
  if route.request.method=='POST':
   posts.append(route.request);route.fulfill(status=200,body='Accepted')
  else:route.continue_()
 page.route('**/*',wrapper_route);page.goto(BASE+'/food-fight/')
 frame=page.frame_locator('iframe')
 frame.locator('#guestPlayButton').tap();frame.locator('#guestUsername').fill('Wrapper_42')
 frame.locator('#guestConsent').check();frame.locator('#guestSubmit').tap()
 frame.locator('#homeScreen').wait_for(state='visible')
 assert len(posts)==1 and posts[0].url==BASE+'/'
 assert '@Wrapper_42' in frame.locator('#guestStatus').inner_text()
 print('Public wrapper: PASS — consenting registration submits from embedded game to site root',flush=True)
 ctx.close()
 # A disable in another tab must cancel the pending request and invalidate it.
 ctx=browser.new_context();page=ctx.new_page();pending=[]
 def delayed_route(route):
  if route.request.method=='POST':pending.append(route)
  else:route.continue_()
 page.route('**/*',delayed_route);page.goto(URL)
 page.locator('#guestPlayButton').click();page.locator('#guestUsername').fill('Cancelled_42')
 page.locator('#guestConsent').check();page.locator('#guestSubmit').click();page.wait_for_timeout(50)
 assert len(pending)==1
 other=ctx.new_page();other.goto(BASE+'/privacy.html')
 other.evaluate("localStorage.setItem('foodFightAnonymousPlayEnabled','false')")
 page.wait_for_function("document.getElementById('guestPlayButton').disabled")
 pending[0].fulfill(status=200,body='Late acceptance');page.wait_for_timeout(50)
 assert page.locator('#endlessButton').is_disabled()
 assert page.locator('#homeScreen').is_visible()
 assert 'Cancelled_42' not in page.locator('#guestStatus').inner_text()
 print('Cross-tab disable: PASS — pending request cancelled; stale response cannot start gameplay',flush=True)
 ctx.close()
 browser.close()
