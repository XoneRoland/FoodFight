"""Network-free guest entry, cancellation, admin visibility and session cleanup."""
import os
from playwright.sync_api import sync_playwright
from guest_helpers import complete_guest_form
URL=os.environ.get('FOODFIGHT_BASE_URL','http://127.0.0.1:8000').rstrip('/')+'/Food_Fight_Development.html'
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for label,width,height in [('desktop',1280,800),('iPad portrait',820,1180),('iPad landscape',1180,820)]:
        ctx=browser.new_context(viewport={'width':width,'height':height},has_touch=True)
        page=ctx.new_page();errors=[];posts=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None)
        page.goto(URL)
        def tap(s):page.locator(s).tap()
        def admin():
            tap('#adminOpenButton');page.locator('#adminPasswordInput').fill('RGE123');tap('#adminLoginButton')
        tap('#guestPlayButton')
        assert page.locator('#guestScreen').is_visible()
        assert page.locator('#guestSubmit').is_disabled()
        assert page.locator('#guestConsent').is_checked()==False
        assert page.locator('#guestFirstName,#guestLastName').count()==0
        tap('#guestCancel');assert page.locator('#endlessButton').is_disabled()
        admin();assert page.locator('#activePlayerStatus').inner_text()=='No active player.'
        tap('#adminHomeButton');tap('#guestPlayButton')
        complete_guest_form(page)
        assert page.locator('#endlessButton').is_enabled()
        assert 'Playing anonymously' in page.locator('#guestStatus').inner_text()
        tap('#endlessButton');page.wait_for_timeout(2100);tap('#homeButton')
        tap('#puzzleButton');page.locator('#levelCards button').first.tap();tap('#homeButton')
        admin();assert page.locator('#activePlayerUsername').inner_text()=='Guest (not registered)'
        assert page.locator('#activePlayerRegistration').inner_text()=='Not requested'
        tap('#adminHomeButton');tap('#guestPlayButton')
        page.locator('#guestUsername').fill('not_sent');tap('#guestCancel')
        admin();assert page.locator('#activePlayerUsername').inner_text()=='Guest (not registered)'
        tap('#adminHomeButton');tap('#endGuestSession')
        assert page.locator('#endlessButton').is_disabled()
        admin();assert page.locator('#activePlayerStatus').inner_text()=='No active player.'
        tap('#adminHomeButton');tap('#guestPlayButton');complete_guest_form(page)
        page.reload();assert page.locator('#endlessButton').is_disabled()
        admin();assert page.locator('#activePlayerStatus').inner_text()=='No active player.'
        tap('#adminHomeButton');tap('#guestPlayButton');complete_guest_form(page)
        admin();tap('#toggleAnonymousButton');assert page.locator('#activePlayerStatus').inner_text()=='No active player.'
        tap('#toggleAnonymousButton');tap('#adminHomeButton');assert page.locator('#endlessButton').is_disabled()
        assert not posts,posts
        assert not page.evaluate("Object.values(localStorage).some(v=>v.includes('not_sent'))")
        assert not errors,errors
        print(label+': PASS — no-consent entry sends nothing; cancel/options, gameplay, admin, end/reload/disable')
        ctx.close()
    ctx=browser.new_context();page=ctx.new_page()
    page.add_init_script("Storage.prototype.setItem=function(){throw Error('blocked')};Storage.prototype.getItem=function(){throw Error('blocked')}")
    page.goto(URL);page.locator('#guestPlayButton').click();complete_guest_form(page)
    assert page.locator('#endlessButton').is_enabled()
    print('Storage blocked: PASS — anonymous play requires no registration or persistent storage')
    browser.close()
