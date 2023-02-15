Simple Yelp Scraper
===

## DESCRIPTION

The script is using playwright to visit the "STARTING_URL" (search results) page and scrape the URLs
of all the results excluding the sponsored  results, after which the script will
visit each URL and scrape data from the page. The data will then be saved in a CSV
file.

## INSTALLATION

pip install playwright

playwright install



## USAGE

edit "STARTING_URL" in pw_scraper.py

run python pw_scraper.py



