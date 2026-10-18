"""Public UI checks; no game instrumentation or free-coin test hooks needed."""
import os
from playwright.sync_api import sync_playwright

URL=os.environ.get('FOODFIGHT_BASE_URL','http://127.0.0.1:8000').rstrip('/')+'/Food_Fight_Development.html'
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for label,width,height in [('desktop',1280,800),('iPad portrait',820,1180),('iPad landscape',1180,820)]:
        ctx=browser.new_context(viewport={'width':width,'height':height},has_touch=True)
        page=ctx.new_page()
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(URL)
        def tap(selector): page.locator(selector).tap()
        def login():
            tap('#adminOpenButton')
            page.locator('#adminPasswordInput').fill('RGE123')
            tap('#adminLoginButton')
            assert page.locator('#itemForm').is_visible()
        def item(kind,name,emoji,cost):
            page.locator('#itemType').select_option(kind)
            page.locator('#itemName').fill(name)
            page.locator('#itemEmoji').fill(emoji)
            page.locator('#itemCost').fill(str(cost))
            tap('#itemForm button')
        def code(name,reward='coins',coins=100):
            page.locator('#newCode').fill(name)
            page.locator('#codeReward').select_option(reward)
            if reward=='coins':page.locator('#codeCoins').fill(str(coins))
            tap('#codeForm button')
        def redeem(name):
            page.locator('#redeemCode').fill(name)
            tap('#redeemForm button')
        assert page.locator('#itemForm').is_hidden()
        tap('#adminOpenButton')
        page.locator('#adminPasswordInput').fill('incorrect')
        tap('#adminLoginButton')
        assert page.locator('#itemForm').is_hidden()
        page.locator('#adminPasswordInput').fill('RGE123')
        tap('#adminLoginButton')
        item('blaster','Rainbow Blaster','🌈',40)
        assert 'added' in page.locator('#itemStatus').inner_text()
        item('food','Popcorn','🍿',15)
        item('food','rainbow blaster','🍳',10)
        assert 'already exists' in page.locator('#itemStatus').inner_text()
        # Hostile-looking names/symbols must render as text, not injected HTML.
        item('food','<img src=x onerror=alert(1)>','<b>X</b>',0)
        assert page.locator('#customItemList img').count()==0
        food_id=page.locator('#codeReward option').filter(has_text='Food: Popcorn').get_attribute('value')
        code('  welcome  ','coins',100)
        assert 'WELCOME added' in page.locator('#codeStatus').inner_text()
        code('welcome','coins',999)
        assert 'already exists' in page.locator('#codeStatus').inner_text()
        code('BAD CODE','coins',10)
        assert 'Use 1–32' in page.locator('#codeStatus').inner_text()
        code('FOOD-GIFT',food_id)
        page.reload()
        login()
        assert page.locator('#customItemList li').count()==3
        assert page.locator('#codeList li').count()==2
        tap('#adminLogoutButton')
        assert page.locator('#itemForm').is_hidden()
        tap('#guestPlayButton');tap('#shopButton')
        assert page.locator('#rifleCards .itemCard').count()==7
        assert page.locator('#bulletCards .itemCard').count()==10
        assert page.locator('#bulletCards img').count()==0
        redeem('missing')
        assert 'not found' in page.locator('#redeemStatus').inner_text()
        redeem(' welcome ')
        assert page.locator('#shopCoins').inner_text()=='Coins: 100'
        redeem('WELCOME')
        assert 'already been redeemed' in page.locator('#redeemStatus').inner_text()
        assert page.locator('#shopCoins').inner_text()=='Coins: 100'
        card=page.locator('#rifleCards .itemCard').filter(has_text='Rainbow Blaster')
        card.locator('button').tap()
        assert card.locator('button').inner_text()=='EQUIPPED'
        assert page.locator('#shopCoins').inner_text()=='Coins: 60'
        redeem('food-gift')
        food=page.locator('#bulletCards .itemCard').filter(has_text='Popcorn')
        assert food.locator('button').inner_text()=='EQUIP'
        food.locator('button').tap()
        assert page.locator('#shopCoins').inner_text()=='Coins: 60'
        page.reload()
        tap('#guestPlayButton');tap('#shopButton')
        assert page.locator('#rifleCards .itemCard').filter(has_text='Rainbow Blaster').locator('button').is_disabled()
        assert page.locator('#bulletCards .itemCard').filter(has_text='Popcorn').locator('button').is_disabled()
        redeem('WELCOME')
        assert 'already been redeemed' in page.locator('#redeemStatus').inner_text()
        # Custom equipment renders in gameplay without errors.
        tap('#shopBack');tap('#puzzleButton');page.locator('#levelCards button').first.tap()
        page.wait_for_timeout(250)
        tap('#homeButton');tap('#endlessButton')
        page.wait_for_timeout(2100)
        tap('#homeButton')
        assert not errors,errors
        print(label+': PASS — login, custom items/codes, validation, safe rendering, redemption, purchase/equip, reload, gameplay')
        ctx.close()
    # Quota failures must not claim additions/rewards succeeded or consume codes.
    ctx=browser.new_context()
    page=ctx.new_page();page.goto(URL)
    page.locator('#adminOpenButton').click()
    page.locator('#adminPasswordInput').fill('RGE123');page.locator('#adminLoginButton').click()
    page.evaluate("()=>{Storage.prototype.setItem=function(){throw new Error('Quota exceeded')}}")
    page.locator('#itemName').fill('Unsaved Blaster');page.locator('#itemEmoji').fill('💥')
    page.locator('#itemForm button').click()
    assert 'Could not save' in page.locator('#itemStatus').inner_text()
    assert page.locator('#customItemList li').count()==0
    page.locator('#newCode').fill('UNSAVED');page.locator('#codeForm button').click()
    assert 'Could not save' in page.locator('#codeStatus').inner_text()
    assert page.locator('#codeList li').count()==0
    page.reload()
    page.locator('#adminOpenButton').click();page.locator('#adminPasswordInput').fill('RGE123');page.locator('#adminLoginButton').click()
    page.locator('#newCode').fill('TRYAGAIN');page.locator('#codeForm button').click()
    page.locator('#adminLogoutButton').click();page.locator('#guestPlayButton').click();page.locator('#shopButton').click()
    page.evaluate("()=>{Storage.prototype.setItem=function(){throw new Error('Quota exceeded')}}")
    page.locator('#redeemCode').fill('TRYAGAIN');page.locator('#redeemForm button').click()
    assert 'Code not used' in page.locator('#redeemStatus').inner_text()
    assert page.locator('#shopCoins').inner_text()=='Coins: 0'
    page.reload();page.locator('#guestPlayButton').click();page.locator('#shopButton').click()
    page.locator('#redeemCode').fill('TRYAGAIN');page.locator('#redeemForm button').click()
    assert page.locator('#shopCoins').inner_text()=='Coins: 100'
    print('Storage failure: PASS — no false success, reward retry remains possible')
    browser.close()
