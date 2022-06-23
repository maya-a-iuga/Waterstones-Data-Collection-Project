import unittest
import random
import sys
import requests
import string
sys.path.append("/Users/maya/Desktop/AiCore_git/Data_Collection_Project/Waterstones-Data-Collection-Project/project")
import Scraper_Runner


class TestScraper(unittest.TestCase):

    """This class has all the unit tests for our webscraper"""
    
    def setUp(self):

        """Set up method initialises an instance of Run_Scraper class 
        and navigates to desired category page"""
        
        self.test = Scraper_Runner.Run_Scraper(cat_flag = 'g', subcategory_flag= 'store_false', headless_flag = 'store_false')
        

    def test_scrape_individual_subcategories(self):
        
        """Test is successful is correct number of books and correct
        metadata & metadata format are scraped"""

        # initialise necessary arguments
        number_pages = 1
        books_per_page = 24
        #uses postcodes API to generate a correct UK postcode
        postcode_generator = requests.get('https://api.postcodes.io/random/postcodes')
        correct_postcode = postcode_generator.json()["result"]["postcode"]

        self.test.scrape_individual_subcategories(number_pages, correct_postcode)
       
        if bool(self.test.scraper.subcategories) == True:
            number_subcategories = len(self.test.scraper.subcategories)
        else:
            number_subcategories = 1

        #checks correct numbers of books were scraped
        self.assertEqual(len(self.test.metadata_all_categories), number_pages * number_subcategories * books_per_page)

        # checks correct metadata was collected for correct postcode
        for item in range(0, 5):
            with self.subTest(item):
                self.assertNotEqual(self.test.metadata_all_categories[item]["Bookstore Name"], 'Information not available')
                self.assertNotEqual(self.test.metadata_all_categories[item]["Bookstore Address"], 'Information not available')
                self.assertNotEqual(self.test.metadata_all_categories[item]["Schedule"], 'Information not available')
                self.assertNotEqual(self.test.metadata_all_categories[item]["Collection Time"], 'Information not available')

    def test_scrape_across_subcategories(self):

        """Test is successful is correct number of books and correct
        metadata & metadata format are scraped"""

        # initialise necessary arguments
        number_pages = 1
        books_per_page = 24
        # generate a random postcode-like string
        string1 = "".join(random.choices(string.ascii_uppercase + string.digits, k = 3))
        string2 = "".join(random.choices(string.ascii_uppercase + string.digits, k = 3))
        random_postcode = string1 + " " + string2
        
        self.test.scrape_across_subcategories(number_pages, random_postcode)
        
        #checks correct numbers of books were scraped
        if bool(self.test.scraper.subcategories) == True:
            number_subcategories = len(self.test.scraper.subcategories)
            self.assertNotEqual(len(self.test.final_book_list), number_pages * number_subcategories * books_per_page)
        else:
            number_subcategories = 1
            self.assertEqual(len(self.test.final_book_list), number_pages * number_subcategories * books_per_page)
        
        #checks correct metadata was collected for incorrect postcode
        #now Run_Scraper class changes an incorrect postcode to a valid one before collecting metadata
        for item in range(0, 5):
            with self.subTest(item): 
                self.assertNotEqual(self.test.metadata_all_categories[item]["Bookstore Name"], 'Information not available')
                self.assertNotEqual(self.test.metadata_all_categories[item]["Bookstore Address"], 'Information not available')
                self.assertNotEqual(self.test.metadata_all_categories[item]["Schedule"], 'Information not available')
                self.assertNotEqual(self.test.metadata_all_categories[item]["Collection Time"], 'Information not available')
      
    
    def tearDown(self):

        """Tear down method closes and terminates the opened webpage"""
        
        self.test.scraper.driver.close()
        self.test.scraper.driver.quit()

if __name__ == "__main__":

   unittest.main(argv = [''],verbosity = 2, exit=False)
    