# Waterstones-Data-Collection-Project

This data collection project will use web scraping to collect structured and unstructured data from https://www.waterstones.com, a website of a well known british book shop chain. I have firstly chose this website as I a bit of a reading geek. How could it will be to use a web scraper to get a personalised reading list based on your favourite book genre? Secondly, from a data perspective, the website is rich in both structured and unstructured data. Plus, it has an intricate navigation system.

## Part 1.
To scrape data from this website, I have used Selenium. Initially I created a Scraper object class, that has important methods for navigation, such as:
   + a method to initialise the webpage
   + a method to bypass cookies
   + distinct methods used for navigating the webpages associated with this website
   + methods that scrape data across distinct webpages and return a list of links containing the specific books we want to scrape data from
