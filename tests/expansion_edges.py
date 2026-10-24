"""Reward boundaries, storage failures, day rollover and malformed extensions."""
import os, datetime
from playwright.sync_api import sync_playwright
from guest_helpers import complete_guest_form
URL=os.environ.get('FOODFIGHT_BASE_URL','http://127.0.0.1:8000').rstrip('/')+'/Food_Fight_Development.html'
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 ctx=b.new_context(timezone_id='America/Los_Angeles');page=ctx.new_page();errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.clock.install(time=datetime.datetime(2026,10,24,6,59,tzinfo=datetime.timezone.utc))
 page.goto(URL)
 def tap(s):page.locator(s).click()
 def join():tap('#guestPlayButton');complete_guest_form(page)
 def stored():return page.evaluate("JSON.parse(localStorage.getItem('bulletDashSave'))")
 def block():page.evaluate("()=>{Storage.prototype.setItem=function(){throw Error('quota')}}")
 base={'coins':900,'highScore':500,'unlockedLevel':12,'clearedLevels':[1,2,3],'unlockedR':['burger-cannon'],'unlockedB':['burger'],'equippedR':'burger-cannon','equippedB':'burger','puzzleBest':{'3':100},'keepExtra':123}
 def reset(data=base):
  page.reload();page.evaluate('(s)=>localStorage.setItem("bulletDashSave",JSON.stringify(s))',data);page.reload();join()
 reset();tap('#dailyButton');block();tap('#claimDaily')
 assert stored()==base and 'Claimed today' not in page.locator('#featureContent').inner_text()
 page.reload();join();tap('#dailyButton')
 page.evaluate("()=>{const button=document.getElementById('claimDaily');button.click();button.click()}")
 assert stored()['coins']==925 and stored()['featuresV1']['daily']['lastDate']=='2026-10-23'
 # One minute past local midnight, even though UTC remains the same date.
 page.clock.set_system_time(datetime.datetime(2026,10,24,7,1,tzinfo=datetime.timezone.utc))
 tap('#featureBack');tap('#dailyButton');tap('#claimDaily')
 assert stored()['coins']==975 and stored()['featuresV1']['daily']['lastDate']=='2026-10-24'
 # Moving the clock backwards cannot repeat an already-claimed date.
 page.clock.set_system_time(datetime.datetime(2026,10,23,7,1,tzinfo=datetime.timezone.utc))
 tap('#featureBack');tap('#dailyButton');assert page.locator('#claimDaily').is_disabled()
 print('Calendar/double-tap PASS — Los Angeles local midnight, rollback, detached repeated button events, failed daily save')
 reset();tap('#missionsButton')
 mission_save=stored();m=mission_save['featuresV1']['missions'];m['progress']={k:100 for k in m['progress']}
 reset(mission_save);tap('#missionsButton');before=stored();block()
 page.locator('#featureContent button:enabled').first.click();assert stored()==before
 page.reload();join();tap('#missionsButton')
 page.evaluate("()=>{const button=document.querySelector('#featureContent button:enabled');button.click();button.click()}")
 after=stored();assert len(after['featuresV1']['missions']['claimed'])==1
 assert after['coins']-before['coins'] in (25,50,75,100)
 # A button rendered yesterday must not grant an old mission's reward today.
 page.clock.set_system_time(datetime.datetime(2026,10,25,7,1,tzinfo=datetime.timezone.utc))
 before_coins=stored()['coins'];page.locator('#featureContent button:enabled').first.click()
 assert stored()['coins']==before_coins and stored()['featuresV1']['missions']['date']=='2026-10-25'
 print('Missions PASS — failed save, detached double claim, stale-date reward rejected')
 reset();tap('#shopButton');before=stored();block()
 page.locator('#backgroundCards .itemCard').filter(has_text='Kitchen Chaos').locator('button').click()
 assert stored()==before
 page.reload();join();tap('#shopButton')
 page.evaluate("()=>{const button=[...document.querySelectorAll('#backgroundCards .itemCard')].find(c=>c.textContent.includes('Kitchen Chaos')).querySelector('button');button.click();button.click()}")
 assert stored()['coins']==650
 print('Background atomicity PASS — storage failure grants nothing, detached repeat pays once')
 reset();tap('#dailyButton')
 # A sequential claim in another tab changes the save; the stale tab must not overwrite it.
 other=ctx.new_page();other.goto(URL);other.locator('#guestPlayButton').click();complete_guest_form(other)
 other.locator('#dailyButton').click();other.locator('#claimDaily').click()
 other_save=other.evaluate("JSON.parse(localStorage.getItem('bulletDashSave'))")
 tap('#claimDaily');assert stored()==other_save
 assert 'another tab' in page.locator('#toast').inner_text()
 other.close()
 print('Stale-tab protection PASS — reward transaction refuses to overwrite newer progress')
 malformed={**base,'featuresV1':{'version':-1,'stats':{'fired':-3,'earned':'oops'},'daily':{'index':99,'lastDate':'2026-99-99'},'missions':{'date':'bad','ids':['fire','fire'],'progress':None,'claimed':'all'},'claimedAchievements':'all','stars':{'1':9,'3':'3'},'backgrounds':{'owned':'midnight','equipped':'midnight'}}}
 reset(malformed);assert stored()==malformed
 tap('#dailyButton');tap('#claimDaily');good=stored()
 assert good['coins']==925 and good['highScore']==500 and good['keepExtra']==123
 assert good['featuresV1']['stats']['fired']==0 and good['featuresV1']['stars']=={'1':1,'2':1,'3':1}
 assert good['featuresV1']['backgrounds']=={'owned':['classic'],'equipped':'classic'}
 assert good['clearedLevels']==[1,2,3] and good['puzzleBest']=={'3':100}
 print('Malformed migration PASS — repair new fields only, preserve legacy coins/scores/unlocks/unknown fields')
 assert not errors,errors
 b.close()
