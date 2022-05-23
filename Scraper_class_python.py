from selenium import webdriver
import time
import uuid
import os
import json
import urllib.request
from pydantic import validate_arguments
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class Scraper():

    """ This class represents a webscraper.
    
    Parameters
    ----------
        url : str 
            the url of the desired website
        category_list : list 
            list containing book categories user wants to scrape data from
        metadata_list : list = None
            list that will be populate with metadata_dictionary elements
        metadata_dictionary : dict = None
            dictionary will contain metadata about individual book 
        
    """

    def __init__(self, url: str, metadata_dictionary = None, metadata_list = None):

        """
        See help(Scraper) for all the details
        """

        self.url = url

        #create metadata dictionary skeleton
        self.metadata_dictionary = metadata_dictionary
        if self.metadata_dictionary == None:
            self.metadata_dictionary = {"Unique id" : " ",
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

        self.metadata_list = metadata_list
        if self.metadata_list == None:
            self.metadata_list = []
    
    def open_webpage(self):

        """This method uses selenium web driver to open desired webpage in Chrome """
        capabilities = DesiredCapabilities.CHROME.copy()
        capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}

        self.driver = webdriver.Chrome(desired_capabilities=capabilities)
        self.browser = self.driver.get(self.url)
    
    def bypass_cookies(self):
    
        """ This method bypasses cookies on the website page"""

        # wait so website doesn't suspect you are a bot
        time.sleep(2)

        # find cookies button xpath & clicks button
        accept_cookies_button = self.driver.find_element_by_xpath('//*[@id="onetrust-accept-btn-handler"]')
        accept_cookies_button.click()   

    @validate_arguments
    def access_link(self, link: str):

        """ This method clicks on desired link
        
        Parameters
        ----------
        link : str
            A string containing the corresponding url for a webpage
        """

        self.driver.get(link)  

    @validate_arguments
    def get_book_category(self, index: int) -> str:
        
        """ This method gets the desired book category to scrape (from user input) and
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

        #first part of xpath always navigated to desktop version of website: desktop-navs
        books_categories_path = self.driver.find_element_by_xpath('//div[@class = "navs-container desktop-navs"]/ul[@class = "subnavs"][1]/li[2]')
        # get all a elements containing the book categories
        books_categories = books_categories_path.find_elements_by_xpath('.//span[@class = "name nav-header-link"]/a')
        # we only interested in 5 categories: fiction, crime, science finction, graphic novel and non-fiction
        books_categories = books_categories[0:5]

        # get link to desired categories
        self.books_categories = [item.get_attribute('href') for item in books_categories]

        return self.books_categories[index]       

    @validate_arguments
    def get_book_subcategory(self, index: int):

        """ This method finds subcategories of given category and navigates to their corresponding page
        
        Parameters
        ----------
        index : int
            integer representing the position in the book category list
        """

        self.books_subcategories = []
        
        self.category_header = self.get_book_category(index)
        
        #category_header = self.get_book_category()
        self.access_link(self.category_header)

        #find list of category sub-divisions
        subcategories_list = self.driver.find_elements_by_xpath('//div[@class = "span3 tablet-span6 mobile-span6"]//a')

        #get links to subcategories
        self.books_subcategories = [item.get_attribute('href') for item in subcategories_list]

    
    def access_subcategory_list_page(self):

        """ This method searches for Our Best <subcategory> header on the page
        then clicks the see all/see more button to access the whole list of books
        from this subcategory
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
    def get_books_list(self, number_pages: int) -> list:

        """ This is a navigation method that first scrolls down the page then goes to the
        next page by changing the URL (fastest navigation method tested)

        Parameters
        ----------
        number_pages : int
            An integer representing the number of pages user wants to scrape for each subcategory
        
        Returns
        -------
        list
            a list of strings representing the urls to individual book pages
        """
        
        if self.driver.current_url[-7 : -1] == "?page=":
            self.current_url = self.driver.current_url[:-7] + '/page/'
        
        elif self.driver.current_url[-7 : -1] == "/page/":
            self.current_url = self.driver.current_url[:-1]
        
        else:
            self.current_url = self.driver.current_url + '/page/'

        i = 1
        self.final_book_list = []
        while i <= number_pages:

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            books_list = self.driver.find_elements_by_xpath('//div[@class = "image-wrap"]/a')
            self.books_list = [item.get_attribute('href') for item in books_list]

            i += 1
            self.new_url = self.current_url + str(i)
            self.driver.get(self.new_url)
            
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

        """ This method access individual book links and collects necessary metadata

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

        for item in books_list:

            # access individual book page
            self.access_link(item)

            #generate unique ids from page id and uuid
            self._generate_unique_id(item)
            self.metadata_dictionary["UUID"] = str(uuid.uuid4())
            
            # get all the structured metadata

            book_title = self.driver.find_element_by_xpath('//span[@class = "book-title"]').text
            self.metadata_dictionary["Book Title"] = book_title
            author = self.driver.find_element_by_xpath('//span[@itemprop = "author"]').text
            self.metadata_dictionary["Author"] = author
            #isbn = self.driver.find_element_by_xpath('//p[@class = "spec"]/i[2]/span').get_attribute("innerHTML")
            isbn = self.driver.find_element_by_xpath('//span[@itemprop = "isbn"]').get_attribute("innerHTML")
            self.metadata_dictionary["ISBN"] = isbn    
            current_price = self.driver.find_element_by_xpath('//b[@itemprop = "price"]').text
            self.metadata_dictionary["Current Price"] = current_price
                
            published_date = (self.driver.find_element_by_xpath('//meta[@itemprop = "datePublished"]')).get_attribute('content')
            self.metadata_dictionary["Published Date"] = published_date
            publisher = self.driver.find_element_by_xpath('//span[@itemprop = "publisher"]').get_attribute("innerHTML")
            #publisher = self.driver.find_element_by_xpath('//p[@class = "spec"]/i[1]/span').get_attribute("innerHTML")
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

            self.metadata_dictionary["Initial Price"] = initial_price
            self.metadata_dictionary["Number of Pages"] = no_pages
            self.metadata_dictionary["Stock"] = stock
            self.metadata_dictionary["Availability"] = availability

            
            height = self.driver.find_element_by_xpath('//span[@itemprop = "height"]').get_attribute("innerHTML")
            self.metadata_dictionary["Height"] = height
            width = self.driver.find_element_by_xpath('//span[@itemprop = "width"]').get_attribute("innerHTML")                          
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
            
            # now append dictionary to a list of dictionaries
            dictionary_copy = self.metadata_dictionary.copy()
            self.metadata_list.append(dictionary_copy) 

        return self.metadata_list      

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
    def _get_key(val: list) -> str:

        """ Method returns the key of a value if this is part of the dictionary values
        
        Parameters
        ----------
        val : list
            list containing the values to check if they are part of the dictionary
        
        Returns
        -------
        str:
            string representing the corresponding key
        """

        for key, value in all_subcategories.items():
            if val in value:
               return key

    @staticmethod
    @validate_arguments
    def _create_metadata_folders(directory_name: str):

        """ Method creates metadata folders
        
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


    def save_book_covers(self):

        """Method saves book covers(images) inside a folder called images"""
        
        for image in range(len(self.metadata_list)):

            image_url = self.metadata_list[image]["Link to image"]
            save_path = os.path.join(os.getcwd(), (str(image) + '.jpg'))
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-Agent', 'MyApp/1.0')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(image_url, save_path)

if __name__ == "__main__":

    categories = ["fiction"]
    waterstones = Scraper("https://www.waterstones.com")
    waterstones.open_webpage()
    waterstones.bypass_cookies()

    #first call folder function creates raw-data subfolder
    waterstones._create_metadata_folders('raw_data')

    #initiate empty dictionary key: category, value: list of corresponding subcategories
    all_subcategories = {}
    # index to count number of category in list
    index = 0

    for category in categories:
        
        #create folders for each category
        waterstones._create_metadata_folders(category)

        #returns list of sub-categories & concatanates them
        waterstones.get_book_subcategory(index)
        all_subcategories[category] = waterstones.books_subcategories
        #increase index ->go to next category in list
        index += 1
        
        #go back to raw-data folder to create new category folder on next iteration
        os.chdir('..')

    # index to count number of subcategories
    index = 0
    # keys = categories, val_list : list of all subcategories
    key_list = list(all_subcategories.keys())
    val_list = sum(list(all_subcategories.values()), []) 

    for subcategory in val_list:
        
        #move back to previously create category folders
        category = waterstones._get_key(subcategory)
        category_path = os.path.join(os.getcwd(), category)
        os.chdir(category_path)

        #creates folder for current subcategory
        subcategory_folder = subcategory.split('/')[-1]
        waterstones._create_metadata_folders(subcategory_folder)

        # access individual page, scrolls through and retrieves links for books
        waterstones.access_link(subcategory)
        waterstones.access_subcategory_list_page()
        final_book_list = waterstones.get_books_list(1)

        metadata_list = waterstones.collect_book_metadata(final_book_list, "WC1 0RW")

        # saves list of dictionary metadata as json file
        with open(os.path.join(os.getcwd(), 'data.json'), 'w') as folder:
            json.dump(metadata_list, folder)

        # create image folder to save all book covers for this sub-category
        waterstones._create_metadata_folders('images')
        #save images
        waterstones.save_book_covers()
        # goes back to subcategory folder
        os.chdir('..')
        
        # index increase -> goes to next subcategory in list
        index =+ 1
        
        #goes back to raw-data folder
        os.chdir('../..')
