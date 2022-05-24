from random import choices
from selenium import webdriver
import time
import uuid
import os
import json
import urllib.request
from pydantic import validate_arguments
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import argparse


class Scraper():

    """ This class represents a webscraper.
    
    Parameters
    ----------
        url : str 
            the url of the desired website
        metadata_dictionary : dict = None
            dictionary will contain metadata about individual book 
        
    """

    def __init__(self, url: str, metadata_dictionary = None):

        """
        See help(Scraper) for all the details
        """

        self.url = url

        #create metadata dictionary skeleton
        self.metadata_dictionary = metadata_dictionary
        if self.metadata_dictionary == None:
            self.metadata_dictionary = {
                "Unique id" : " ",
                "UUID" : " ",
                "Book Title" : " ",
                "Author" : " ",
                "Initial Price" : " ",
                "Current Price" : " ",
                "ISBN" : " ",
                "Number of Pages" : " ",
                "Published Date" : " ",
                "Publisher" : " ",
                "Stock" : " ",
                "Availability" : " ",
                "Height" : " ",
                "Width" : " ",
                "Link to image": " ",
                "Bookstore Name" : " ",
                "Bookstore Address" : " ",
                "Schedule" : " ",
                "Collection Time" : " "}

        # open webpage & bypass cookies
        self._open_webpage()
        self._bypass_cookies()
        # creates raw_data folder where all data will be saved
        self.create_metadata_folders('raw_data')
        # gets list of book subcategories
        self.subcategories = self._get_book_subcategory()
       
    def _open_webpage(self):

        """This method uses selenium web driver to open desired webpage in Chrome """

        capabilities = DesiredCapabilities.CHROME.copy()
        capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
        self.driver = webdriver.Chrome(desired_capabilities=capabilities)
        self.browser = self.driver.get(self.url)
    
    def _bypass_cookies(self):
    
        """ This method bypasses cookies on the website page"""

        # wait so website doesn't suspect you are a bot
        time.sleep(2)
        # find cookies button xpath & clicks button
        accept_cookies_button = self.driver.find_element_by_xpath('//*[@id="onetrust-accept-btn-handler"]')
        accept_cookies_button.click()   

    def scraper_flags(self):

        """This method allows for user to raise a flag corresponding
        to the book category they want data scraped from"""

        # first flag is for choosing desired book category
        self.parser = argparse.ArgumentParser(description = "Which main book category you want to select?")

        # f for fiction default = argparse.SUPPRESS
        self.default_choice = 'f'
        self.parser.add_argument(
            '--category', 
            default = self.default_choice, 
            choices = ['f', 'c', 'sf', 'g', 'nf']
            )
        #self.parser.add_argument('--c',  action = "store_true", default = False)
        # sf for science-fiction
        #self.parser.add_argument('--sf', action = "store_true", default = False)
        # g for graphic novels and manga
        #self.parser.add_argument('--g', action = "store_true", default = False)
        # nf for non-fiction
        #self.parser.add_argument('--nf', action = "store_true", default = False)
        self.args = self.parser.parse_args(args=[])

    def _get_book_category(self) -> list:
        
        """ This method gets the desired book category to scrape from and
        returns the link to this category

        Parameters
        ----------
        index : int
            integer representing the position in the book category list

        Returns
        -------
        str
            a string containing the url corresponding to the book category
        """
        #get user flag
        self.scraper_flags()

        #first part of xpath always navigated to desktop version of website: desktop-navs
        desktop_version_path = self.driver.find_element_by_xpath('//div[@class = "navs-container desktop-navs"]/ul[@class = "subnavs"][1]/li[2]')
        # get all a elements containing the book categories
        books_category_path = desktop_version_path.find_elements_by_xpath('.//span[@class = "name nav-header-link"]/a')
        # we only interested in 5 categories: fiction, crime, science finction, graphic novel and non-fiction
        books_category_path = books_category_path[0:5]
        # get link to desired categories
        books_categories = [item.get_attribute('href') for item in books_category_path]

        flag_dictionary = {0 : 'f', 1 : 'c', 2 : 'sf', 3 : 'g', 4 : 'nf'}
        for key, flag in flag_dictionary.items():
            if (flag is self.args.category) == True:
                self.book_category = books_categories[key]
                #return only book category we are interested in
                return self.book_category
    
    def _get_book_subcategory(self) -> list:

        """ This method finds the subcategories of a given category 
        
        Returns
        ----------
        list
            list containing hyperlinks to all book subcategories
        """
        
        self.subcategory_list = []
       
        self._get_book_category()
        #access category webpage
        self.driver.get(self.book_category)
        #create category folder inside raw_data folder
        category_folder = self.book_category.split('/')[-1]
        self.create_metadata_folders(category_folder)
    
        subcategories_path = self.driver.find_elements_by_xpath('//div[@class = "span3 tablet-span6 mobile-span6"]//a')
        #get links to subcategories
        self.books_subcategories = [item.get_attribute('href') for item in subcategories_path]
        self.subcategory_list.append(self.books_subcategories)
        return sum(self.subcategory_list, [])

    
    def _access_subcategory_list_page(self):

        """ This method searches for Our Best <subcategory> header on the page then
        clicks the see all/see more button to access the book list from this subcategory
        """
                
        header_path = self.driver.find_element_by_xpath('//header[@class = "span12 pages-header-row"]')
        #find see all button - sometimes called see more but same xpath
        self.see_all_button = header_path.find_element_by_xpath('./a[@class = "button button-teal"]')
        self.see_all_button.click()
        time.sleep(3)
        
        #sometimes the pages containing full books list are nested, e.g our best thriller crime - our best thriller 
        try:
            header_path = self.driver.find_element_by_xpath('//header[@class = "span12 pages-header-row"]')
            self.see_all_button = header_path.find_element_by_xpath('./a[@class = "button button-teal"]')
            self.see_all_button.click()
            time.sleep(3)
        except:
            pass
                        
    @validate_arguments    
    def get_books_list(self, subcategory: str, number_pages: int) -> list:

        """ This is a navigation method that accesses subcategory book list,
        then scrolls through the page. It changes between consecutive pages
        by changing the url

        Parameters
        ----------
        subcategory : str 
            A string representing the url to a book subcategory
        number_pages : int
            An integer representing the number of pages user wants to scrape for each subcategory
        
        Returns
        -------
        list
            a list of strings representing the urls to individual book pages
        """
        try:
            self.driver.get(subcategory)
        except:
            pass
        self._access_subcategory_list_page()

        if self.driver.current_url[-7 : -1] == "?page=":
            current_url = self.driver.current_url[:-7] + '/page/'
        
        elif self.driver.current_url[-7 : -1] == "/page/":
            current_url = self.driver.current_url[:-1]
            
        else:
            current_url = self.driver.current_url + '/page/'

        i = 1
        self.final_book_list = []
        while i <= number_pages:

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            books_list = self.driver.find_elements_by_xpath('//div[@class = "image-wrap"]/a')
            self.books_list = [item.get_attribute('href') for item in books_list]
            #goes to next page
            i += 1
            new_url = current_url + str(i)
            self.driver.get(new_url)
            
            self.final_book_list.append(self.books_list)

        return sum(self.final_book_list, []) 

    @validate_arguments
    def _generate_unique_id(self, link: str):

        """ Method generates unique id for each book using its webpage url

        Parameters
        ----------
        link : str
            a string corresponding to a webpage url
        """

        self.metadata_dictionary["Unique id"] = link.split('/')[-1]
        
    @validate_arguments
    def collect_book_metadata(self, books_list: list, postcode: str) -> list:

        """ This method collects metadata from individual book pages

        Parameters
        ----------
        book_list : list
            list of strings representing url for individual book pages, as scraped before for the desired subcategories
        postcode : str
            string representing a valid postcode for London
        
        Returns
        -------
        list
            a list of dictionaries, where each dictionary is populated with metadata(both structured and unstructured data) 
            from an individual book
        """
        self.metadata_list = []

        for item in books_list:

            # access individual book page
            self.driver.get(item)

            #generate unique ids from page id and uuid
            self._generate_unique_id(item)
            self.metadata_dictionary["UUID"] = str(uuid.uuid4())
            
            # get all the structured metadata
            book_title = self.driver.find_element_by_xpath('//span[@class = "book-title"]').text
            self.metadata_dictionary["Book Title"] = book_title
            author = self.driver.find_element_by_xpath('//span[@itemprop = "author"]').text
            self.metadata_dictionary["Author"] = author
            isbn = self.driver.find_element_by_xpath('//span[@itemprop = "isbn"]').get_attribute("innerHTML")
            self.metadata_dictionary["ISBN"] = isbn    
            current_price = self.driver.find_element_by_xpath('//b[@itemprop = "price"]').text
            self.metadata_dictionary["Current Price"] = current_price
            published_date = (self.driver.find_element_by_xpath('//meta[@itemprop = "datePublished"]')).get_attribute('content')
            self.metadata_dictionary["Published Date"] = published_date
            publisher = self.driver.find_element_by_xpath('//span[@itemprop = "publisher"]').get_attribute("innerHTML")
            self.metadata_dictionary["Publisher"] = publisher
            
            # 'Coming soon' books are missing some of the metadata other books have
            try:
                initial_price = self.driver.find_element_by_xpath('//b[@class = "price-rrp"]').text
                no_pages = self.driver.find_element_by_xpath('//span[@itemprop = "numberOfPages"]').text
                stock = self.driver.find_element_by_xpath('//span[@id = "scope_offer_availability"]').text
                availability = self.driver.find_element_by_xpath('//p[@class = "stock-message"]').text

            except:
                initial_price = 'Coming soon'
                no_pages = 'Coming soon'
                stock = 'Coming soon'
                availability = 'Coming soon'

            self.metadata_dictionary["Initial Price"] = initial_price
            self.metadata_dictionary["Number of Pages"] = no_pages
            self.metadata_dictionary["Stock"] = stock
            self.metadata_dictionary["Availability"] = availability

            try:
                height = self.driver.find_element_by_xpath('//span[@itemprop = "height"]').get_attribute("innerHTML")
                self.metadata_dictionary["Height"] = height
                width = self.driver.find_element_by_xpath('//span[@itemprop = "width"]').get_attribute("innerHTML")                          
                self.metadata_dictionary["Width"] = width

            except:
                self.metadata_dictionary["Height"] = 'No information'
                self.metadata_dictionary["Width"] = 'No information'

            # get the image links/unstructured data
            image_links = self.driver.find_element_by_xpath('//div[@class = "book-image-main"]//img').get_attribute("src")
            self.metadata_dictionary["Link to image"] = image_links

            #find the click & collect metadata - cooming soon books do not have this metadata
            try:
                self._click_and_collect(postcode)
            except:
                pass

            # wait for results to load 
            time.sleep(4)
            try:
                bookstore_name = self.driver.find_element_by_xpath('//div[@class = "store"][1]//div[@class = "title"]').get_attribute("innerHTML")
                bookstore_address = self.driver.find_element_by_xpath('//div[@class = "store"][1]//div[@class = "address"]').get_attribute("innerHTML")
                bookstore_schedule = self.driver.find_element_by_xpath('//div[@class = "store"][1]//div[@class = "hours"]').get_attribute("innerHTML")
                collection_time = self.driver.find_element_by_xpath('//div[@class = "store"][1]//div[4]').get_attribute("innerHTML")
            
            except:
                bookstore_name = 'Book is not out yet'
                bookstore_address = 'Book is not out yet'
                bookstore_schedule = 'Book is not out yet'
                collection_time = 'Book is not out yet'

            self.metadata_dictionary["Bookstore Name"] = bookstore_name
            self.metadata_dictionary["Bookstore Address"] = bookstore_address
            self.metadata_dictionary["Collection Time"] = collection_time
            self.metadata_dictionary["Schedule"] = bookstore_schedule

            #if book is not available for collection today
            if self.metadata_dictionary["Schedule"] == '':
               self.metadata_dictionary["Schedule"] = "Book not available for collection today"
            
            # now append dictionary to a list of dictionaries - 
            # TODO: not sure needed anymore
            dictionary_copy = self.metadata_dictionary.copy()
            self.metadata_list.append(dictionary_copy) 
        #save data
        self._save_json_file()
        self.create_metadata_folders('images')
        self._save_book_covers()
       
    @validate_arguments
    def _click_and_collect(self, postcode: str):

        """ Method accesses click and collect from book page and searches for closest bookstore where you can find the 
        desired book using given postcode
        
        Parameters
        ----------
        postcode : str
            string representing a valid postcode for London
        """

        click_and_collect_button = self.driver.find_element_by_xpath('//div[@class = "book-actions"]//button[@class = "button button-gold js-open-modal"]')
        click_and_collect_button.click()

        search_bar = self.driver.find_element_by_xpath('//input[@placeholder = "Town, city, or postcode"]')
        time.sleep(2)
        search_bar.send_keys(postcode)
        go_button = self.driver.find_element_by_xpath('//button[@id = "searchterm"]')
        go_button.click()

    @staticmethod
    @validate_arguments
    def create_metadata_folders(directory_name: str):

        """This method creates different folders for data storage
        
        Parameters
        ----------
        directory_name : str
            a string representing the name of a new folder to be created and cd into
        """
        current_dir = os.getcwd()
        future_dir = os.path.join(current_dir, directory_name)
        if os.path.exists(future_dir):
            os.chdir(future_dir)
        else:
            os.mkdir(directory_name)
            os.chdir(future_dir)

    def _save_json_file(self):

        """This method saves the structured data in a json file"""

        with open(os.path.join(os.getcwd(), 'data.json'), 'w') as folder:
            json.dump(self.metadata_list, folder)


    def _save_book_covers(self):

        """Method saves book covers(images) inside a folder called images"""
        
        for image in range(len(self.metadata_list)):

            image_url = self.metadata_list[image]["Link to image"]
            save_path = os.path.join(os.getcwd(), (str(image) + '.jpg'))
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-Agent', 'MyApp/1.0')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(image_url, save_path)

if __name__ == "__main__":
     
    waterstones = Scraper("https://www.waterstones.com")

    if bool(waterstones.subcategories) == True:
        for subcategory in waterstones.subcategories:
            #create subcategory folder
            subcategory_folder = subcategory.split('/')[-1]
            waterstones.create_metadata_folders(subcategory_folder)
            #collect & save metadata for all the books
            book_list = waterstones.get_books_list(subcategory, 1)
            waterstones.collect_book_metadata(book_list, "WC1 0RW")
            #go back to category folder
            os.chdir('../..')
    #not all categories have subcategories        
    else:
        book_list = waterstones.get_books_list('', 1)
        waterstones.collect_book_metadata(book_list, "WC1 0RW")

