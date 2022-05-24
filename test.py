import unittest
from selenium import webdriver
import os
import sys
import json
import random

sys.path.append(".")

from Scraper_class_python import Scraper

class TestScraper(unittest.TestCase):

    """This class has all the unit tests for the Scraper class"""
    
    def setUp(self):

        """Set up method initialises an instance of Scraper class 
        and navigates to desired category page"""

        self.webscraper = Scraper("https://www.waterstones.com")
    
    def test_scraper_flags(self):

        """Test is successful if correct category argument is passed to the class"""

        os.chdir('../..')
        self.assertEqual(self.webscraper.default_choice, self.webscraper.args.category)
    
    #webpage request.get access denied - this method overcomes that
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


    def test_create_metadata_folders(self):

        """Test is successful if correct folder name is created
        and working directory is correctly changed"""

        os.chdir('../..')
        expected_output = os.path.join(os.getcwd(), 'test_folder')
        self.webscraper.create_metadata_folders('test_folder')
        self.assertEqual(expected_output, os.getcwd())

    def test_get_book_list(self):

        """Test is successful if for each book list page we scrape 24 books
        (the number of items/each page) and we can access each book link 
        """

        #randomly select a subcategory
        index = random.randint(0,4)
        test_subcategory = self.webscraper.subcategories[index]
        #randomly select number of pages to scrape/subcategory
        number_pages = random.randint(1,2)
        book_list = self.webscraper.get_books_list(test_subcategory, number_pages)
        self.assertEqual(len(book_list), 24 * number_pages)

        for num in range(len(book_list)):
            with self.subTest(num):
                self.webscraper.driver.get(book_list[num])
                logs = self.webscraper.driver.get_log('performance')
                self.assertEqual(self.get_status(logs), 200)

    def test_collect_book_metadata(self):

        """Test is successful if the metadata collected from individual book page
        has the correct data format/type"""
        #randomly select a subcategory
        index = random.randint(0,4)
        test_subcategory = self.webscraper.subcategories[index]
        #randomly select number of pages to scrape/subcategory
        number_pages = random.randint(1,2)
        book_list = self.webscraper.get_books_list(test_subcategory, number_pages)
        
        self.webscraper.collect_book_metadata(book_list, "WC1 0RW")
        metadata_list = self.webscraper.metadata_list

        for item in range(0, len(metadata_list)):
            with self.subTest(item):
                self.assertTrue(str.isdigit(metadata_list[item]["Height"]) or metadata_list == 'No information')
                self.assertTrue(str.isdigit(metadata_list[item]["Width"]) or metadata_list == 'No information')
                self.assertTrue(len(metadata_list[item]["Published Date"].split('-')) == 3)
                self.assertEqual(metadata_list[item]["Unique id"], metadata_list[item]["ISBN"])

    
    def tearDown(self):

        """Tear down method closes and terminates the opened webpage"""
        
        self.webscraper.driver.close()
        self.webscraper.driver.quit()

if __name__ == "__main__":
    unittest.main(argv= [''], verbosity = 2, exit = False)