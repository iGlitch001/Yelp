"""
    Script for scraping yelp.com
    Change STARTING_URL for url to scrape
"""
import json
import csv
import os.path
import platform
import logging
from urllib.parse import unquote
from playwright.sync_api import Playwright, sync_playwright, TimeoutError, Page

BASE_URL = "https://www.yelp.com"
STARTING_URL = "https://www.yelp.com/search?find_desc=Restaurants&find_loc=San+Francisco%2C+CA"
CSV_FILENAME = "yelp.csv"

def get_user_agent() -> str:
    """
        check the current OS and return the corresponding user agent

    Returns:
        str: user agent string
    """
    current_os = platform.system()
    match current_os:
        case "Windows":
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        case "Darwin":
            user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        case "Linux":
            user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    return user_agent


def get_links(page: Page) -> list:
    """ 
        get all the business links from the STARTING_URL page

    Args:
        page (Page): browser tab

    Returns:
        list: list of urls
    """
    links = []
    business_links = page.locator("#main-content div ul")
    for link in business_links.locator("li a").all():
        href = link.get_attribute("href")
        if "?osq="in href:
            links.append(href)
    links = list(set(links))
    print(f"Retrived {len(links)} Business URLs")
    print(link for link in links)
    return links


def parse_biz_page(page: Page, url: str) -> dict:
    """
        get all the information from the business page

    Args:
        page (Page): browser page
        url (str): url of the business page

    Returns:
        dict: dictionary of information about the business page
    """
    try:
        website = page.get_by_text("Business website").locator("..").locator("p a").get_attribute("href", timeout=20000)
        website = website.split("url=")[1]
        website = website.split("&cache")[0]
        website = unquote(website)
    except TimeoutError:
        website = None

    try:
        scripts = page.locator("yelp-react-root div script").all()
    except TimeoutError:
        return None

    for script in  scripts:
        script_text = script.inner_text()
        if "AggregateRating" in script_text:
            biz_json = json.loads(script_text)
            biz_details_dict = {
                "Name": biz_json["name"],
                "Phone": biz_json["telephone"],
                "Address": biz_json["address"]["streetAddress"].replace("\n", " "),
                "City": biz_json["address"]["addressLocality"],
                "State": biz_json["address"]["addressRegion"],
                "PostalCode": biz_json["address"]["postalCode"],
                "Country": biz_json["address"]["addressCountry"],
                "Rating":biz_json["aggregateRating"]["ratingValue"],
                "Reviews": biz_json["aggregateRating"]["reviewCount"],
                "Website": website,
                "Yelp URL": f"{BASE_URL}{url}"
            }
            print(json.dumps(biz_details_dict, indent=4))

    return biz_details_dict


def write_to_csv(biz_list: list) -> None:
    """
        output all info to csv file

    Args:
        biz_list (list): list of dictionaries from business info
    """
    print("Writing to CSV file...")
    filename = CSV_FILENAME
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


def run(pwright: Playwright) -> None:
    """
        Playwright scraper

    Args:
        pwright (Playwright): playwright instance
    """
    browser = pwright.chromium.launch(headless=False)
    my_user_agent = get_user_agent()
    context = browser.new_context(base_url=BASE_URL, user_agent=my_user_agent)
    page = context.new_page()
    page.goto(STARTING_URL)
    urls = get_links(page)
    biz_details_list = []
    for url in urls:
        print(f"Visiting {BASE_URL}{url}")
        page.goto(url)
        biz_details = parse_biz_page(page, url)
        if biz_details:
            biz_details_list.append(biz_details)
    write_to_csv(biz_details_list)

    # ---------------------
    context.close()
    browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
