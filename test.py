import unittest
from selenium import webdriver
import os
import sys
import json

sys.path.append(".")

from Scraper_class_python import Scraper

class TestScraper(unittest.TestCase):

    """This class has all the unit tests for the Scraper class"""
    
    def setUp(self):

        """Set up method initialises an instance of Scraper class 
        and uses its .open_webpage() method to open desired url"""

        self.webscraper = Scraper("https://www.waterstones.com")
        self.webscraper.open_webpage()


    def test_open_webpage(self):

        """ Test is successfull if the opened webpage has correct data type"""
        self.assertEqual(type(self.webscraper.driver), type(webdriver.Chrome()))
    
    @staticmethod
    def get_status(logs):

        """Static method that returns the response message of a HTTP status code
        
        Returns
        -------
        int:
            integer representing the HTTP status code 
        """

        for log in logs:
            if log['message']:
                d = json.loads(log['message'])
                try:
                    content_type = 'text/html' in d['message']['params']['response']['headers']['content-type']
                    response_received = d['message']['method'] == 'Network.responseReceived'
                    if content_type and response_received:
                        return d['message']['params']['response']['status']
                except:
                    pass

    def test_bypass_cookies(self):

        """ Test is successful if clicking the cookies button returns a HTTP status code 200 = success """

        self.webscraper.bypass_cookies()
        logs = self.webscraper.driver.get_log('performance')
        self.assertEqual(self.get_status(logs), 200)


    def test_access_link(self):

        """Test is successful if it will raise an error when trying to access a non-existing link"""

        self.webscraper.bypass_cookies()
        
        incorrect_values = ['string', 'not a  link', 'not a link again']
        self.assertRaises(ValueError, self.webscraper.access_link, incorrect_values)    


    def test_get_book_category(self):
         
      """Test is successful if the Scraper.get_book_category() returns the correct link, which is verified
      by comparing the url ending with the category"""

      self.webscraper.bypass_cookies()

      for num in range(0,5):
          self.assertTrue(type(self.webscraper.get_book_category(num)) is str)
          with self.subTest(num):
              if num == 0:
                  self.assertEqual(self.webscraper.get_book_category(num).split('/')[-1], 'fiction')
              elif num == 1:
                  self.assertEqual(self.webscraper.get_book_category(num).split('/')[-1], 'crime-thrillers-mystery')
              elif num == 2:
                  self.assertEqual(self.webscraper.get_book_category(num).split('/')[-1], 'science-fiction-fantasy-horror')
              elif num == 3:
                  self.assertEqual(self.webscraper.get_book_category(num).split('/')[-1], 'graphic-novels-manga')
              else:
                  self.assertEqual(self.webscraper.get_book_category(num).split('/')[-1], 'non-fiction-books')

    
    def test_get_book_subcategory(self):

        """Test is successful if Scraper.get_book_subcategory() method correctly returns a string
        and this string is a correct url"""

        self.webscraper.bypass_cookies()
        # num values will run this test on each book category: category[0] = fiction, etc
        for num in range(0,5):
            with self.subTest(num):
                #get subcategory list for this category
                self.webscraper.get_book_subcategory(num)
                #for each subcategory
                for item in self.webscraper.books_subcategories:
                    # checks that item is a string
                    self.assertIsInstance(item, str)
                    # checks if link is valid -> tries to access it
                    self.webscraper.access_link(item)
                    logs = self.webscraper.driver.get_log('performance')
                    self.assertEqual(self.get_status(logs), 200)
                    

    def test_access_subcategory_list_page(self):

        """Test is successful if for each subcategory we can acccess
        Our best <subcategory> header"""

        self.webscraper.bypass_cookies()
        #looking at all subcatgories from category[0] = fiction
        self.webscraper.get_book_subcategory(0)
        for num in range(0, len(self.webscraper.books_subcategories)):
            with self.subTest(num):
                #for each subTest, access one subcategory link
                self.webscraper.access_link(self.webscraper.books_subcategories[num])
                #access Our best <subcategory> page to get full book list
                self.webscraper.access_subcategory_list_page()
                logs = self.webscraper.driver.get_log('performance')
                self.assertEqual(self.get_status(logs), 200)
    
    
    def test_get_book_list(self):

        """Test is successful if for each Our best <subcategory> page we find 24 books/page
        (the number of items/each page)"""

        self.webscraper.bypass_cookies()
        # access Our best <subcategory> for category [0] = fiction, subcategory[0] = crime-thrillers-mystery
        self.webscraper.get_book_subcategory(0)
        self.webscraper.access_link(self.webscraper.books_subcategories[0])
        self.webscraper.access_subcategory_list_page()
        #num = number of pages to get book list from
        for num in range(1,5):
            with self.subTest(num):
                self.webscraper.get_books_list(num)
                self.assertEqual(len(self.webscraper.get_books_list(num)), 24*num)


    def test_collect_book_metadata(self):

        """Test is successful if the metadata collected from individual book page
        has the correct data format/type"""

        self.webscraper.bypass_cookies()
        # goes to fiction -> crime-thrillers-mystery -> collects data from 1 page of Our best <subcategory>
        self.webscraper.get_book_subcategory(0)
        self.webscraper.access_link(self.webscraper.books_subcategories[0])
        self.webscraper.access_subcategory_list_page()
        lst = self.webscraper.get_books_list(1)
        # collects metadata from all books in the list
        metadata_list = self.webscraper.collect_book_metadata(lst, "WC1 0RW")

        for item in range(0, len(metadata_list)):
            with self.subTest(item):
                self.assertTrue(str.isdigit(metadata_list[item]["Height"]))
                self.assertTrue(str.isdigit(metadata_list[item]["Width"]))
                self.assertTrue(len(metadata_list[item]["Published Date"].split('-')) == 3)
                self.assertEqual(metadata_list[item]["Unique id"], metadata_list[item]["ISBN"])

    def test_save_book_covers(self):

        """Test is successful if number of downloaded images corresponds to number of 
        book links that have been scraped (1image/book)"""

        self.webscraper.bypass_cookies()
        # goes to fiction -> crime-thrillers-mystery -> collects data from 1 page of Our best <subcategory>
        self.webscraper.get_book_subcategory(0)
        self.webscraper.access_link(self.webscraper.books_subcategories[0])
        self.webscraper.access_subcategory_list_page()
        # number of pages to get book links from
        number_pages = 1
        lst = self.webscraper.get_books_list(number_pages)
        # collect desired metadata
        self.webscraper.collect_book_metadata(lst, "WC1 0RW")
        # cd into corresponding category/subcategory image folder
        os.chdir(os.path.join(os.getcwd(), 'raw_data/fiction/crime-thrillers-mystery/images'))
        self.webscraper.save_book_covers()
        self.assertEqual(len(os.listdir()), 24 * number_pages)
    

    def tearDown(self):

        """Tear down method closes and terminates the opened webpage"""
        
        self.webscraper.driver.close()
        self.webscraper.driver.quit()

if __name__ == "__main__":
    unittest.main(argv= [''], verbosity = 2, exit = False)