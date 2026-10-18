"""Guest identity UI, privacy, cancellation, and local admin visibility."""
import os
from playwright.sync_api import sync_playwright
from guest_helpers import complete_guest_form
URL=os.environ.get('FOODFIGHT_BASE_URL','http://127.0.0.1:8000').rstrip('/')+'/Food_Fight_Development.html'
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for label,width,height in [('desktop',1280,800),('iPad portrait',820,1180),('iPad landscape',1180,820)]:
        ctx=browser.new_context(viewport={'width':width,'height':height},has_touch=True)
        page=ctx.new_page();errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(URL)
        def tap(s):page.locator(s).tap()
        def admin():
            tap('#adminOpenButton');page.locator('#adminPasswordInput').fill('RGE123');tap('#adminLoginButton')
        tap('#guestPlayButton')
        assert page.locator('#guestScreen').is_visible()
        tap('#guestForm button[type=submit]')
        assert page.locator('#guestScreen').is_visible()
        tap('#guestCancel')
        assert page.locator('#endlessButton').is_disabled()
        admin()
        assert page.locator('#activePlayerStatus').inner_text()=='No active player.'
        tap('#adminHomeButton');tap('#guestPlayButton')
        complete_guest_form(page,first='   ',last='Player',username='tester')
        assert 'first and last name' in page.locator('#guestFormStatus').inner_text()
        complete_guest_form(page,username='bad name')
        assert page.locator('#guestScreen').is_visible()
        complete_guest_form(page,first='  Alex  ',last='  O’Neil  ',username='Alex_42')
        assert page.locator('#endlessButton').is_enabled()
        assert '@Alex_42' in page.locator('#guestStatus').inner_text()
        # Exercise gameplay, then check the profile persists for this play session.
        tap('#endlessButton');page.wait_for_timeout(2100);tap('#homeButton')
        tap('#puzzleButton');page.locator('#levelCards button').first.tap();tap('#homeButton')
        admin()
        assert page.locator('#activePlayerUsername').inner_text()=='@Alex_42'
        assert page.locator('#activePlayerName').inner_text()=='Alex O’Neil'
        tap('#adminHomeButton');tap('#guestPlayButton')
        assert page.locator('#guestUsername').input_value()=='Alex_42'
        page.locator('#guestUsername').fill('not_saved');tap('#guestCancel')
        admin();assert page.locator('#activePlayerUsername').inner_text()=='@Alex_42'
        tap('#adminHomeButton');tap('#guestPlayButton')
        complete_guest_form(page,first='<b>Alex</b>',last='<img src=x>',username='safe_name')
        admin()
        assert page.locator('#activePlayerName').inner_text()=='<b>Alex</b> <img src=x>'
        assert page.locator('#activePlayerDetails img, #activePlayerDetails b').count()==0
        # Names aren't written into localStorage; they clear when the session ends.
        assert not page.evaluate("Object.values(localStorage).some(v=>v.includes('safe_name')||v.includes('<b>Alex</b>'))")
        tap('#adminHomeButton');tap('#endGuestSession')
        assert page.locator('#endlessButton').is_disabled()
        admin();assert page.locator('#activePlayerStatus').inner_text()=='No active player.'
        tap('#adminHomeButton');tap('#guestPlayButton');complete_guest_form(page)
        page.reload()
        assert page.locator('#endlessButton').is_disabled()
        admin();assert page.locator('#activePlayerStatus').inner_text()=='No active player.'
        tap('#adminHomeButton');tap('#guestPlayButton');complete_guest_form(page)
        admin();tap('#toggleAnonymousButton')
        assert page.locator('#activePlayerStatus').inner_text()=='No active player.'
        tap('#toggleAnonymousButton');tap('#adminHomeButton')
        assert page.locator('#endlessButton').is_disabled()
        assert not errors,errors
        print(label+': PASS — form, validation, cancel/edit, gameplay, admin identity, text safety, privacy, end/reload/disable')
        ctx.close()
    # Guest details still work if persistence is unavailable.
    ctx=browser.new_context();page=ctx.new_page()
    page.add_init_script("Storage.prototype.setItem=function(){throw Error('blocked')};Storage.prototype.getItem=function(){throw Error('blocked')}")
    page.goto(URL);page.locator('#guestPlayButton').click();complete_guest_form(page)
    assert page.locator('#endlessButton').is_enabled()
    print('Storage blocked: PASS — guest entry does not require persistent storage')
    browser.close()
