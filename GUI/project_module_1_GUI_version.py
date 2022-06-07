from selenium import webdriver
import time
import uuid
import os
from pydantic import validate_arguments
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import argparse
from tqdm import tqdm


class Scraper():

    """ This class contains all the navigation & data collection methods
    of a webscraper.
    
    Parameters
    ----------
    url : str 
        the url of the desired website
    cat_flag : str
        string representing the book category
    subcategory_flag : str
        string representing the book subcategory
    headless_flag : str
        string representing the driver mode (headless or not)
    metadata_dictionary : dict = None
        dictionary will contain metadata about individual book   
    """


    def __init__(self, url: str, cat_flag: str, subcategory_flag: str, headless_flag: str, metadata_dictionary = None):

        """
        See help(Scraper) for all the details
        """

        self.url = url
        self.category_flag = cat_flag
        self.subcategory_flag = subcategory_flag
        self.headless_flag = headless_flag
        #create metadata dictionary skeleton
        self.metadata_dictionary = metadata_dictionary
        if self.metadata_dictionary == None:
            self.metadata_dictionary = {
                "uniqueid" : " ",
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

        print('Chosen category:' + self.category_flag)

        if self.headless_flag == "yes":        
            options = webdriver.ChromeOptions()

            options.add_argument("--no-sandbox") 
            options.add_argument("--headless")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-setuid-sandbox") 
            options.add_argument('--disable-gpu')
        
            options.add_argument("user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005 Safari/537.36'")
            options.add_argument("window-size=1920,1080")

            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        elif self.headless_flag == "no":
            self.driver = webdriver.Chrome()
            
        self.browser = self.driver.get(self.url)

        # open webpage & bypass cookies
        self._bypass_cookies()
        # creates raw_data folder where all data will be saved
        self._create_metadata_folders('raw_data')
        # gets list of book subcategories
        self.subcategories = self._get_book_subcategory()

    
    def _bypass_cookies(self):
    
        """ This method bypasses cookies on the website page"""

        # wait so website doesn't suspect you are a bot
        time.sleep(2)
        # find cookies button xpath & clicks button
        accept_cookies_button = self.driver.find_element_by_xpath('//*[@id="onetrust-accept-btn-handler"]')
        accept_cookies_button.click()


    @staticmethod
    @validate_arguments
    def _create_metadata_folders(directory_name: str):

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


    def _get_book_category(self) -> list:
        
        """ This method gets the desired book category to scrape from and
        returns the link to this category

        Returns
        -------
        str
            a string containing the url corresponding to the book category
        """
        
        #get all a elements containing the book categories
        desktop_version_path = self.driver.find_element_by_xpath('//div[@class = "navs-container desktop-navs"]/ul[@class = "subnavs"][1]/li[2]')
        books_category_path = desktop_version_path.find_elements_by_xpath('.//span[@class = "name nav-header-link"]/a')
        # we only interested in 5 categories: fiction, crime, science finction, graphic novel and non-fiction
        books_category_path = books_category_path[0:5]
        # get link to desired categories
        books_categories = [item.get_attribute('href') for item in books_category_path]

        flag_dictionary = {0 : 'fiction', 1 : 'crime-thrillers-mystery', 2 : 'science-fiction-fantasy-horror', 
        3 : 'graphic-novels-manga', 4 : 'non-fiction-books'} 

        for key, value in flag_dictionary.items():
            #if flag is given
            if value == self.category_flag:
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
        self._create_metadata_folders(category_folder)
    
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
    def _get_books_list(self, subcategory: str, number_pages: int) -> list:

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
    def _collect_book_metadata(self, books_list: list, postcode: str):

        """ This method collects metadata from individual book pages

        Parameters
        ----------
        book_list : list
            list of strings representing url for individual book pages, as scraped before for the desired subcategories
        postcode : str
            string representing a valid UK postcode 
            
        """

        self.metadata_list = []
        print('Acquiring book metadata')
        for item in tqdm(books_list):
        
            time.sleep(0.01)
            # access individual book page
            self.driver.get(item)

            #generate unique ids from page id and uuid
            self.metadata_dictionary["uniqueid"] = item.split('/')[-1]
            self.metadata_dictionary["UUID"] = str(uuid.uuid4())
            
            # get all the structured metadata
            book_title = self.driver.find_element_by_xpath('//span[@class = "book-title"]').text
            self.metadata_dictionary["Book Title"] = book_title
            isbn = self.driver.find_element_by_xpath('//span[@itemprop = "isbn"]').get_attribute("innerHTML")
            self.metadata_dictionary["ISBN"] = isbn    
            current_price = self.driver.find_element_by_xpath('//b[@itemprop = "price"]').text
            self.metadata_dictionary["Current Price"] = current_price
            published_date = (self.driver.find_element_by_xpath('//meta[@itemprop = "datePublished"]')).get_attribute('content')
            self.metadata_dictionary["Published Date"] = published_date
            publisher = self.driver.find_element_by_xpath('//span[@itemprop = "publisher"]').get_attribute("innerHTML")
            self.metadata_dictionary["Publisher"] = publisher
           
            # 'Coming soon' books & maps are missing some of the metadata other books have
            try:
                author = self.driver.find_element_by_xpath('//span[@itemprop = "author"]').text
                initial_price = self.driver.find_element_by_xpath('//b[@class = "price-rrp"]').text
                no_pages = self.driver.find_element_by_xpath('//span[@itemprop = "numberOfPages"]').text
                stock = self.driver.find_element_by_xpath('//span[@id = "scope_offer_availability"]').text
                availability = self.driver.find_element_by_xpath('//p[@class = "stock-message"]').text
                height = self.driver.find_element_by_xpath('//span[@itemprop = "height"]').get_attribute("innerHTML")
                width = self.driver.find_element_by_xpath('//span[@itemprop = "width"]').get_attribute("innerHTML")                          
        
            except:
                author = 'No author'
                initial_price = 'Coming soon'
                no_pages = 'Coming soon'
                stock = 'Coming soon'
                availability = 'Coming soon'
                height = 'No information'
                width = 'No information'

            self.metadata_dictionary["Author"] = author
            self.metadata_dictionary["Initial Price"] = initial_price
            self.metadata_dictionary["Number of Pages"] = no_pages
            self.metadata_dictionary["Stock"] = stock
            self.metadata_dictionary["Availability"] = availability
            self.metadata_dictionary["Height"] = height
            self.metadata_dictionary["Width"] = width

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
                #if book is not published already
                if self.metadata_dictionary["Availability"] == 'Coming soon' or self.metadata_dictionary["Availability"] == 'Awaiting publication':

                    bookstore_name = 'Book not available yet'
                    bookstore_address = 'Book not available yet'
                    bookstore_schedule = 'Book not available yet'
                    collection_time = 'Book not available yet'
                #if user introduces an incorrect UK postcode
                else:
                    bookstore_name = 'Information not available'
                    bookstore_address = 'Information not available'
                    bookstore_schedule = 'Information not available'
                    collection_time = 'Information not available'

            self.metadata_dictionary["Bookstore Name"] = bookstore_name
            self.metadata_dictionary["Bookstore Address"] = bookstore_address
            self.metadata_dictionary["Collection Time"] = collection_time
            self.metadata_dictionary["Schedule"] = bookstore_schedule

            #if book is not available for collection today
            if self.metadata_dictionary["Schedule"] == '':
               self.metadata_dictionary["Schedule"] = "Book not available for collection today"
            
            # now append dictionary to a list of dictionaries - 
            dictionary_copy = self.metadata_dictionary.copy()
            self.metadata_list.append(dictionary_copy)

       
    @validate_arguments
    def _click_and_collect(self, postcode: str):

        """ Method accesses click and collect from book page and searches for closest bookstore where you can find the 
        desired book using given postcode
        
        Parameters
        ----------
        postcode : str
            string representing a valid UK postcode 
        """

        click_and_collect_button = self.driver.find_element_by_xpath('//div[@class = "book-actions"]//button[@class = "button button-gold js-open-modal"]')
        click_and_collect_button.click()

        search_bar = self.driver.find_element_by_xpath('//input[@placeholder = "Town, city, or postcode"]')
        time.sleep(2)
        search_bar.send_keys(postcode)
        go_button = self.driver.find_element_by_xpath('//button[@id = "searchterm"]')
        go_button.click()