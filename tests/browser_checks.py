"""Run with Python Playwright and system Chromium; serve the repo on port 8000 first.
Test-only instrumentation exposes the existing closure in the browser response;
no hooks or seeded currency are added to the deployable HTML.
"""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
TARGET = os.environ.get('FOODFIGHT_TARGET', 'Food_Fight_Development.html')
URL = os.environ.get('FOODFIGHT_BASE_URL','http://127.0.0.1:8000').rstrip('/') + '/' + TARGET
HOOK = """window.testGame={puzzleStart,endlessOver,goHome,
 snapshot:()=>({state,score,coins:save.coins,shots:shotCount,aiming,bullet:{...bullet},targets:targets.map(t=>({...t})),projectiles:shots.map(s=>({...s})),barriers:barriers.map(b=>({...b}))}),
 lifetimeAt:dt=>{puzzleStart(0);cancelAnimationFrame(raf);firePuzzle(bullet.x,bullet.y+100);last=0;
 for(let i=1;i<=20/dt;i++){puzzleLoop(i*dt*16.67);cancelAnimationFrame(raf)}
 return shots[0].life},
 crashAt:n=>{score=n;runCoins=0;endlessOver()}};"""

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for name, size in [('desktop', (1280,800)), ('iPad portrait', (820,1180)), ('iPad landscape', (1180,820))]:
        ctx=browser.new_context(viewport={'width':size[0],'height':size[1]},has_touch=True)
        page=ctx.new_page()
        errors=[]
        page.on('pageerror', lambda e: errors.append(str(e)))
        source=(ROOT / TARGET).read_text()
        instrumented=source.replace('})();', HOOK+'\n})();')
        page.route('**/'+TARGET, lambda route: route.fulfill(status=200,content_type='text/html',body=instrumented))
        page.goto(URL)
        def snap(): return page.evaluate('testGame.snapshot()')
        def click(selector): page.locator(selector).click()
        def pointer(kind, ident, x=300,y=400):
            page.locator('canvas').dispatch_event(kind,{'pointerId':ident,'pointerType':'touch','button':0,'buttons':0 if kind in ('pointerup','pointercancel') else 1,'clientX':x,'clientY':y})
        assert page.locator('#homeScreen').is_visible()
        assert page.locator('#endlessButton').is_disabled()
        click('#guestPlayButton')
        click('#shopButton')
        assert page.locator('#rifleCards .itemCard').count()==6
        assert page.locator('#bulletCards .itemCard').count()==8
        click('#bulletCards .itemCard:nth-child(2) button')
        assert 'more coins' in page.locator('#toast').inner_text()
        click('#shopBack')
        click('#puzzleButton')
        assert page.locator('#levelCards .levelCard').count()==12
        assert page.locator('#levelCards button:disabled').count()==11
        page.locator('#levelCards button').first.click()
        # A second finger cannot release or replace the active aim.
        initial=snap()['shots']
        pointer('pointerdown',1)
        pointer('pointerdown',2)
        pointer('pointerup',2)
        assert snap()['shots']==initial and snap()['aiming']
        pointer('pointercancel',1)
        assert snap()['shots']==initial and not snap()['aiming']
        # Fire at the actual first target and wait for the physics loop to clear it.
        target=snap()['targets'][0]
        pointer('pointerdown',1)
        pointer('pointerup',1,target['x'],target['y'])
        page.wait_for_function("document.getElementById('resultTitle').textContent==='LEVEL CLEARED' && document.getElementById('resultScreen').classList.contains('active')")
        assert snap()['coins']==10
        click('#retryButton')
        target=snap()['targets'][0]
        pointer('pointerdown',1)
        pointer('pointerup',1,target['x'],target['y'])
        page.wait_for_function("testGame.snapshot().state==='puzzleresult'")
        assert snap()['coins']==10
        assert 'Coins earned: 0'==page.locator('#resultCoins').inner_text()
        # Initialize every unchanged puzzle, then exercise out-of-shots and reset.
        for level in range(12):
            page.evaluate('(n)=>testGame.puzzleStart(n)',level)
            assert snap()['targets'] and snap()['shots']>0
        for dt in (0.5,1,2):
            assert abs(page.evaluate('(dt)=>testGame.lifetimeAt(dt)',dt)-240)<0.001
        page.evaluate('testGame.puzzleStart(0)')
        for _ in range(3):
            pointer('pointerdown',1)
            pointer('pointerup',1,100,50)
        page.wait_for_function("testGame.snapshot().state==='puzzleresult'",timeout=15000)
        assert page.locator('#resultTitle').inner_text()=='OUT OF SHOTS'
        click('#retryButton')
        click('#resetLevelButton')
        assert snap()['shots']==3
        # Resize an active puzzle and verify target geometry follows the viewport.
        old=snap()['targets'][0]
        page.set_viewport_size({'width':size[1],'height':size[0]})
        page.wait_for_timeout(100)
        new=snap()['targets'][0]
        assert abs(new['x']-old['x']*size[1]/size[0])<1
        page.set_viewport_size({'width':size[0],'height':size[1]})
        page.wait_for_timeout(100)
        click('#homeButton')
        click('#endlessButton')
        page.wait_for_function("testGame.snapshot().state==='playing'")
        # Real browser touch dispatch exercises pointer capture, unlike synthetic events.
        cdp=ctx.new_cdp_session(page)
        for typ,points in [('touchStart',[{'x':250,'y':300}]),('touchMove',[{'x':300,'y':350}]),('touchEnd',[])]:
            cdp.send('Input.dispatchTouchEvent',{'type':typ,'touchPoints':points})
        assert snap()['bullet']['targetX']==300
        # Deterministic score at collision boundary: no reliance on random obstacles.
        page.evaluate('testGame.crashAt(200)')
        assert snap()['coins']==30
        page.evaluate('testGame.endlessOver()')
        assert snap()['coins']==30, 'duplicate crash must not award twice'
        click('#resultHome')
        # Seed a legacy save to check compatibility, purchase deductions and equip persistence.
        page.evaluate("localStorage.setItem('bulletDashSave',JSON.stringify({...JSON.parse(localStorage.getItem('bulletDashSave')),coins:300}))")
        page.reload()
        click('#guestPlayButton')
        click('#shopButton')
        click('#bulletCards .itemCard:nth-child(2) button')
        assert snap()['coins']==240
        click('#rifleCards .itemCard:nth-child(2) button')
        assert snap()['coins']==60
        click('#bulletCards .itemCard:first-child button')
        click('#bulletCards .itemCard:nth-child(2) button')
        assert snap()['coins']==60
        page.reload()
        saved=page.evaluate("JSON.parse(localStorage.getItem('bulletDashSave'))")
        assert saved['coins']==60 and saved['equippedB']=='pizza' and saved['equippedR']=='frying-pan'
        assert saved['clearedLevels']==[1] and saved['unlockedLevel']==2
        click('#adminOpenButton')
        page.locator('#adminPasswordInput').fill('wrong')
        click('#adminLoginButton')
        assert not page.locator('#adminControls').is_visible()
        page.locator('#adminPasswordInput').fill('RGE123')
        page.locator('#adminPasswordInput').press('Enter')
        assert page.locator('#adminControls').is_visible()
        click('#toggleAnonymousButton')
        click('#adminHomeButton')
        assert page.locator('#guestPlayButton').is_disabled()
        assert page.locator('#endlessButton').is_disabled()
        page.reload()
        assert page.locator('#guestPlayButton').is_disabled()
        click('#adminOpenButton')
        page.locator('#adminPasswordInput').fill('RGE123')
        click('#adminLoginButton')
        click('#toggleAnonymousButton')
        click('#adminLogoutButton')
        click('#guestPlayButton')
        assert page.locator('#endlessButton').is_enabled()
        other=ctx.new_page()
        other.goto(URL)
        other.evaluate("localStorage.setItem('foodFightAnonymousPlayEnabled','false')")
        page.wait_for_function("document.getElementById('guestPlayButton').disabled")
        assert page.locator('#endlessButton').is_disabled()
        other.close()
        assert not errors,errors
        print(name+': PASS — gameplay, rewards, purchase/equip/save, admin, multitouch, rotation, real touch')
        ctx.close()
    # Storage-denied mode must retain the local admin toggle for the current session.
    ctx=browser.new_context()
    page=ctx.new_page()
    page.add_init_script("Storage.prototype.setItem=function(){throw new Error('Storage unavailable')}; Storage.prototype.getItem=function(){throw new Error('Storage unavailable')}")
    page.goto(URL)
    page.locator('#adminOpenButton').click()
    page.locator('#adminPasswordInput').fill('RGE123')
    page.locator('#adminLoginButton').click()
    page.locator('#toggleAnonymousButton').click()
    page.locator('#adminHomeButton').click()
    assert page.locator('#guestPlayButton').is_disabled()
    print('Storage unavailable: PASS — admin toggle still works in memory')
    browser.close()
