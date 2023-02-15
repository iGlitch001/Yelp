"# Simple Yelp Scraper" 



Installation


pip install playwright

playwright install



Usage


edit "STARTING_URL" in pw_scraper.py

run python pw_scraper.py



Description

The script is using playwright to vist the "STARTING_URL" page and scrape the urls
of all the results excluding the sponspored results, after which the script will
visit each url and scrape data from the page. The data will then be saved in a csv
file.
