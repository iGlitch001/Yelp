from playwright.sync_api import Playwright, sync_playwright, expect


def get_links(page):
    links = []
    business_links = page.locator("#main-content div ul")
    for link in business_links.locator('li a').all():
        href = link.get_attribute('href')
        if '?osq='in href:
            links.append(href)
    links = list(set(links))
    print(len(links))
    print(links)
    return links

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.yelp.com/search?find_desc=Restaurants&find_loc=San+Francisco%2C+CA", wait_until='networkidle')
    urls = get_links(page)
    
    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)