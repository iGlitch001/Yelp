import json
from playwright.sync_api import sync_playwright

playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=False)
my_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
page = browser.new_page(user_agent=my_user_agent)
page.goto('https://www.yelp.com/biz/kothai-republic-san-francisco?osq=Restaurants')

for script in  page.locator('yelp-react-root div script').all():
    script_text = script.inner_text()
    if 'AggregateRating' in script_text:
        biz_json = json.loads(script_text)
        print(biz_json['name'])
        print(biz_json['telephone'])
        print(biz_json['address']['streetAddress'])
        print(biz_json['address']['addressLocality'])
        print(biz_json['address']['addressRegion'])
        print(biz_json['address']['postalCode'])
        print(biz_json['address']['addressCountry'])
        print(biz_json['aggregateRating']['ratingValue'])
        print(biz_json['aggregateRating']['reviewCount'])

page.get_by_text('Business website').locator('..').locator('p a').inner_text()
