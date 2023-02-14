import json
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

def parse_biz_page(page, url):
    scripts = page.locator('yelp-react-root div script').all()
    for script in  scripts:
        script_text = script.inner_text()
        if 'AggregateRating' in script_text:
            biz_json = json.loads(script_text)
            biz_details_dict = {
                "Name": biz_json['name'],
                "Phone": biz_json['telephone'],
                "Address": biz_json['address']['streetAddress'],
                "City": biz_json['address']['addressLocality'],
                "State": biz_json['address']['addressRegion'],
                "PostalCode": biz_json['address']['postalCode'],
                "Country": biz_json['address']['addressCountry'],
                "Rating":biz_json['aggregateRating']['ratingValue'],
                "Reviews": biz_json['aggregateRating']['reviewCount'],
                "Website": page.get_by_text('Business website').locator('..').locator('p a').inner_text(),
                "Yelp URL": url
            }
            print(f"Name: {biz_json['name']}",
                f"/nPhone: {biz_json['telephone']}",
                f"/nAddress: {biz_json['address']['streetAddress']}",
                f"/nCity: {biz_json['address']['addressLocality']}",
                f"/nState: {biz_json['address']['addressRegion']}",
                f"/nPostalCode: {biz_json['address']['postalCode']}",
                f"/nCountry: {biz_json['address']['addressCountry']}",
                f"/nRating: {biz_json['aggregateRating']['ratingValue']}",
                f"/nReviews: {biz_json['aggregateRating']['reviewCount']}",
                f"/nWebsite: {page.get_by_text('Business website').locator('..').locator('p a').inner_text()}",
                f"/nYelp URL: {url}")

    return biz_details_dict

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    my_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    context = browser.new_context(base_url="https://www.yelp.com", user_agent=my_user_agent)
    page = context.new_page()
    page.goto("https://www.yelp.com/search?find_desc=Restaurants&find_loc=San+Francisco%2C+CA", wait_until='networkidle')
    urls = get_links(page)
    for murl in urls:
        page.goto(murl, wait_until='networkidle')
        biz_details = parse_biz_page(page, murl)
        
    
    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)