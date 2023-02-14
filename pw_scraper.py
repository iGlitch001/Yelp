import json
import csv
import os.path
from urllib.parse import unquote
from playwright.sync_api import Playwright, sync_playwright, TimeoutError


def get_links(page):
    links = []
    business_links = page.locator("#main-content div ul")
    for link in business_links.locator('li a').all():
        href = link.get_attribute('href')
        if '?osq='in href:
            links.append(href)
    links = list(set(links))
    print(f"Retrived {len(links)} Business URLs")
    print(link for link in links)
    return links

def parse_biz_page(page, url):
    try:
        website = page.get_by_text('Business website').locator('..').locator('p a').get_attribute('href', timeout=20000)
        website = website.split('url=')[1]
        website = website.split('&cache')[0]
        website = unquote(website)
    except TimeoutError:
        website = None

    try:
        scripts = page.locator('yelp-react-root div script').all()
    except TimeoutError:
        return None

    for script in  scripts:
        script_text = script.inner_text()
        if 'AggregateRating' in script_text:
            biz_json = json.loads(script_text)
            biz_details_dict = {
                "Name": biz_json['name'],
                "Phone": biz_json['telephone'],
                "Address": biz_json['address']['streetAddress'].replace('\n', ' '),
                "City": biz_json['address']['addressLocality'],
                "State": biz_json['address']['addressRegion'],
                "PostalCode": biz_json['address']['postalCode'],
                "Country": biz_json['address']['addressCountry'],
                "Rating":biz_json['aggregateRating']['ratingValue'],
                "Reviews": biz_json['aggregateRating']['reviewCount'],
                "Website": website,
                "Yelp URL": f"https://www.yelp.com{url}"
            }
            # print(f"Name: {biz_json['name']}",
            #     f"\nPhone: {biz_json['telephone']}",
            #     f"\nAddress: {biz_json['address']['streetAddress']}",
            #     f"\nCity: {biz_json['address']['addressLocality']}",
            #     f"\nState: {biz_json['address']['addressRegion']}",
            #     f"\nPostalCode: {biz_json['address']['postalCode']}",
            #     f"\nCountry: {biz_json['address']['addressCountry']}",
            #     f"\nRating: {biz_json['aggregateRating']['ratingValue']}",
            #     f"\nReviews: {biz_json['aggregateRating']['reviewCount']}",
            #     f"\nWebsite: {website}",
            #     f"\nYelp URL: https://www.yelp.com{url}")
            print(json.dumps(biz_details_dict, indent=4))

    return biz_details_dict

def write_to_csv(biz_list):
    print('Writing to CSV file...')
    filename = "yelp.csv"
    fnames = biz_list[0].keys()
    print(fnames)
    mode = "a" if os.path.exists(filename) else "w"
    with open(filename, mode, encoding="utf-8") as yelp:
        writer = csv.DictWriter(yelp, fieldnames=fnames)
        if mode == "w":
            writer.writeheader()
        for data in biz_list:
            print(data)
            writer.writerow(data)


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    # my_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    my_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    context = browser.new_context(base_url="https://www.yelp.com", user_agent=my_user_agent)
    page = context.new_page()
    page.goto("https://www.yelp.com/search?find_desc=Restaurants&find_loc=San+Francisco%2C+CA&start=20")
    urls = get_links(page)
    biz_details_list = []
    for url in urls:
        print(f"Visiting https://www.yelp.com{url}")
        page.goto(url)
        biz_details = parse_biz_page(page, url)
        if biz_details:
            biz_details_list.append(biz_details)
    write_to_csv(biz_details_list)
    
    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)