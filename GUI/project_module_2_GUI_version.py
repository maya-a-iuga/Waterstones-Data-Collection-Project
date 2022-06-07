import time
import os
import json
from unicodedata import category
import urllib.request
from pydantic import validate_arguments
import boto3
import pandas as pd
import sqlalchemy
from sqlalchemy.sql import text 
from sqlalchemy import create_engine
import requests
import sqlalchemy
from tqdm import tqdm
import psycopg2
from project_module_1_GUI_version import Scraper 


class Run_Scraper():

    """ This class initialises the webscraper, saves the collected data
    locally and updates it to both S3 and RDS.
    
    Parameters
    ----------
    cat_flag : str
        string representing the book category
    subcategory_flag : str
        string representing the book subcategory
    headless_flag : str
        string representing the driver mode (headless or not)    
    """


    def __init__(self, cat_flag: str, subcategory_flag: str, headless_flag: str):

        """
        See help(Scraper) for all the details
        """

        self.scraper = Scraper("https://www.waterstones.com", cat_flag, subcategory_flag, headless_flag)
        self.headless_flag = headless_flag
        self.category_flag = cat_flag
        self.subcategory_flag = subcategory_flag
        self.subcategories = self.scraper.subcategories
        self.driver = self.scraper.driver


    def _save_json_file(self):

        """This method saves the structured data in a json file"""

        with open(os.path.join(os.getcwd(), 'data.json'), 'w') as folder:
            json.dump(self.scraper.metadata_list, folder)


    def _save_book_covers(self):

        """Method saves book covers(images) inside a folder called images"""
        
        for image in range(len(self.scraper.metadata_list)):

            image_url = self.scraper.metadata_list[image]["Link to image"]
            save_path = os.path.join(os.getcwd(), (str(image) + '.jpg'))
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-Agent', 'MyApp/1.0')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(image_url, save_path)


    @staticmethod
    def _upload_folder_to_s3():

        """This method uploads both json files and image data to S3 bucket"""

        s3_resource = boto3.resource('s3')
        try:
            bucket_name = "aicorebucketmaya"
            my_bucket = s3_resource.Bucket(bucket_name)
            root_path = '/Users/maya/Desktop/AiCore_git/Data_Collection_Project/Waterstones-Data-Collection-Project/raw_data'

            for path, subdirs, files in os.walk(root_path):
                path = path.replace("\\","/")
                directory_name = path.replace(root_path[:-8],"")
                #TODO: only nested for loop - cant avoid it really
                for file in files:
                    my_bucket.upload_file(os.path.join(path, file), directory_name+'/'+file)

        except Exception as err:
            print(err)
    

    def _create_rds_database(self):
        
        """This method converts json file to pandas dataframe
        and uploads it to AWS RDS as a database"""

        #connect to the database
        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        ENDPOINT = 'aicoredb.cwmfykce5lky.us-east-1.rds.amazonaws.com'
        USER = 'postgres'
        PASSWORD = 'mayaisthebest'
        PORT = 5432
        DATABASE = 'postgres'
        engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        
        #drop table
        #table_to_drop = engine.table_names()
        #sql_statement = sqlalchemy.text("DROP TABLE IF EXISTS {}".format(table_to_drop[0]))
        #engine.execute(sql_statement, autocommit = True)
         # upload entries to rds_database

        if sqlalchemy.inspect(engine).has_table("book_dataset"):
        
            sql = sqlalchemy.text("SELECT book_dataset.uniqueid FROM book_dataset")
            result = pd.read_sql_query(sql, engine)
            unique_id_list = result['uniqueid'].tolist()
 
        for entry in self.scraper.metadata_list:
            rds_entry = pd.DataFrame([entry])
            
            if entry["uniqueid"] not in unique_id_list:
                rds_entry.to_sql('book_dataset', engine, if_exists = 'append')
            #else:
             #   rds_entry.to_sql('book_dataset', engine, if_exists = 'append')
                  

    def _upload_images_to_s3(self):
        
        """This method uploads images to S3 bucket using their corresponding url"""

        s3_resource = boto3.resource('s3')
        try:
            bucket_name = "aicorebucketmaya"
            my_bucket = s3_resource.Bucket(bucket_name)
         
            for i in range(len(self.scraper.metadata_list)):
                image_url = self.scraper.metadata_list[i]["Link to image"]
                image_filename = image_url.split('/')[-1].split('.')[0]
                s3_filename = 'images/' + image_filename + '.jpg'

                req_for_image = requests.get(image_url, stream=True)
                file_object_from_req = req_for_image.raw
                req_data = file_object_from_req.read()

                my_bucket.put_object(Key=s3_filename, Body=req_data)

        except Exception as e:
            return e


    @validate_arguments
    def scrape_individual_subcategories(self, number_pages : int, postcode : str):

        """This method scrapes data from all subcategories and
        locally saves it into organised subfolders
        
        Parameters
        ----------
        number_pages : int
            int representing number of pages to scrape/subcategory
        postcode : str
            a string representing a valid London postcode
        """

        self.metadata_all_categories = []

        if bool(self.scraper.subcategories) == True:
            print('Acquiring book list')
            for subcategory in tqdm(self.scraper.subcategories):
                time.sleep(0.01)
                #create subcategory folder
                subcategory_folder = subcategory.split('/')[-1]
                self.scraper._create_metadata_folders(subcategory_folder)
                #collect & save metadata for all the books
                book_list = self.scraper._get_books_list(subcategory, number_pages)
                self.scraper._collect_book_metadata(book_list, postcode) 
                self.metadata_all_categories += self.scraper.metadata_list

                #save data
                self._save_json_file()
                self.scraper._create_metadata_folders('images')
                self._save_book_covers()
                #go back to category folder
                os.chdir('../..')
            
        #not all categories have subcategories        
        else:
            book_list = self.scraper._get_books_list('', number_pages)
            self.scraper._collect_book_metadata(book_list, postcode)
            self.metadata_all_categories = self.scraper.metadata_list

            #save data
            self._save_json_file()
            self.scraper._create_metadata_folders('images')
            self._save_book_covers()

        #upload raw data folder to s3
        #self._upload_folder_to_s3()


    @validate_arguments
    def scrape_across_subcategories(self, number_pages : int, postcode : str):
        
        """This method scrapes data from all subcategories pooled together (no book duplicates)
        and locally saves it one file

        Parameters
        ----------
        number_pages : int
            int representing number of pages to scrape/subcategory
        postcode : str
            a string representing a valid London postcode
        """

        final_book_list = []
        #create folder
        os.chdir('../..')
        self.scraper._create_metadata_folders('all_books_data')

        if bool(self.scraper.subcategories) == True:
            print('Acquiring book list')
            for subcategory in tqdm(self.scraper.subcategories):
                time.sleep(0.01)
                #collect & save metadata for all the books
                final_book_list += self.scraper._get_books_list(subcategory, number_pages)
        
        else:
            book_list = self.scraper._get_books_list('', number_pages)
            final_book_list = book_list

        #remove duplicates from book list
        self.final_book_list = list(dict.fromkeys(final_book_list))
       
        self.scraper._collect_book_metadata(self.final_book_list, postcode)
        self.metadata_all_categories = self.scraper.metadata_list
        #save data
        self._save_json_file()
        self.scraper._create_metadata_folders('images')
        self._save_book_covers()

        #save locally saved data in aws rds database
        #self._create_rds_database()
        #upload images directly to cloud
        #self._upload_images_to_s3() 
        
        
if __name__ == "__main__":
    
    waterstones = Run_Scraper(cat_flag = 'fiction', subcategory_flag = 'yes', headless_flag = 'no')
    # for when you want to save raw data locally
    if waterstones.subcategory_flag == "no":
        waterstones.scrape_individual_subcategories(1, "WC1 0RW")
    # if you want to remove duplicates book list
    elif waterstones.subcategory_flag == "yes":
        waterstones.scrape_across_subcategories(1, "WC1 0RW")