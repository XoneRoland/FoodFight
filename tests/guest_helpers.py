def complete_guest_form(page, first='Alex', last='Player', username='alex_player'):
    page.locator('#guestFirstName').fill(first)
    page.locator('#guestLastName').fill(last)
    page.locator('#guestUsername').fill(username)
    page.locator('#guestForm button[type=submit]').click()
