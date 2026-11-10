def complete_guest_form(page):
    """Use the network-free guest path in general gameplay regression tests."""
    page.locator('#guestSkip').click()
