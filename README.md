# Waterstones Webscraping Project

This project is designed to collect structured and unstructured data from https://www.waterstones.com, a well-known British bookshop website. This webscraper can provide you with your own personalised reading list based on your favourite book genre. 
Technologies used for webscraping include: Selenium and a postcode API https://postcodes.io.

## Basic project structure
The project directory has two modules, each containing a class, namely: Scraper and Run_Scraper(). 

1. Scraper class includes important initialisation & navigation methods, such as:
   + navigating to main webpage & bypassing cookies 
   + a method that returns the link to the desired book category
   + a method that returns links to all subcategories
   + methods that access the Our Best <subcategory> webpage and return a list of individual book pages
   + methods that scrape unstructured and structured data from the individual book page
   
2. Run_Scraper class calls upon Scraper class and adds further functionality, such as:
   + saving the scraped data & images locally in a structured format
   + a method that uploads the raw data folder to an AWS S3 bucket
   + a method that uploads the images (book covers) directly to the AWS S3 bucket without locally saving them first
   + a method that saves each data entry to an AWS RDS database (and additional methods to prevent rescraping the same data twice)
   
## Run_Scraper class flags
This class can be called with different CLI flags, which provides a personalised user experience. There are three CLI flags the user can use when calling Scraper_Runner.py - the module that host the Run_Scrapper class:
   + **--category flag: this is a mandatory flag which allows the user to select book category to scrape from**
       + --category f : corresponds to fiction 
       + --category c : corresponds to crime-thrillers-mystery 
       + --category s : corresponds to science-fiction-fantasy-horror
       + --category g : corresponds to graphic-novels-manga 
       + --category n : corresponds to non-fiction
   
   + **--subcategory flag: this is an optional flag**
       + can be True or False
       + --subcategory (if given value is False) : will scrape individual subcategories and save data locally in a structure: category/subcategory/data (includes json file and images files)
       + no flag (value is True) : will scrape across subcategories, and remove duplicate book links
       + when called without this flag, the individual data entry will be uploaded to an AWS RDS database 
   
   + **--headless flag: this is an optional flag**
       + can be True or False
       + --headless (if given value is False): will run webscraper in headless mode
       + no flag (value is True) : opens up Google Chrome
       
#### Note.
To run Scraper_Runner.py locally you will first need to instal a chromedriver. On MacOS you can use **brew install chromedriver**, then navigate to **usr/local/bin** and run the following **xattr -d com.apple.quarantine chromedriver** to verify the developer. Make sure that your local Chrome version matches the chromedriver version.

## GUI webscraper version
The GUI directory also provides a user interface version of this webscraper. To use this GUI, you can clone this repository locally and then run webscraper_GUI.py on your machine. Alternatively, you can pull the GUI's Docker image as follow: docker pull mayaaiuga/scraper_gui.latest **(see next section on how to run docker image)**.

#### Note.
If you want to run the GUI not in headless mode, you will first need to install geckodriver (**brew install geckodriver** for MacOS).

The GUI has a welcome page:
   
<img width="459" alt="GUI_welcome_page" src="https://user-images.githubusercontent.com/104773240/176442724-3eca36cc-826d-46c6-bad7-1fbbf38356be.png">

The GUI also allows the user to interactively select the three CLI flags mentioned above. Additionally, it allows the user to input two other parameters:
   + Number of pages : this represents the number of pages (one page has 24 books) to scrape for each subcategory
   + Postcode : this should be a valid UK postcode
The postcode parameter is used to find the closest Waterstones bookshop at which user can find a desired book (including its address, timetable and a possible collection time). The GUI check if postcode is valid UK postcode using the https://postcodes.io API, otherwise it will ask for a new input.
   
   <img width="510" alt="GUI_Page_One" src="https://user-images.githubusercontent.com/104773240/176708689-f7c48edc-2f78-4698-a938-801e15838455.png">

The email filed is used to send the user a book recommendation list on their email, based on the category they picked.

Pressing **the START button** will cause the webscraper to run. Pressing **the BACK button** will return to Welcome Page.
   
If everything runs successfully you will be prompted to a final page showcasing Bernard Black (from the Black Books TV show) having a blast in his bookshop (in the form of a GIF).
   
   <img width="468" alt="GUI_Page_Two" src="https://user-images.githubusercontent.com/104773240/176443496-d288a6af-0545-42b9-bf6f-ce49597a8f4c.png">

Finally, press **EXIT** to close the GUI.
   
## GUI Docker Image.
The image can be pulled as follows: docker pull mayaaiuga/scraper_gui_firefox:latest. The container will run on Firefox rather than Chrome as the files in **project**. This is to accomodate for Mac M1 chips, where is not yet possible to run headless Chrome.
   
### for MacOS
In order to be able to run the image locally you will first need to set up the display for the GUI as well as the sound system for the music accompanying the GUI.
 
**1.Installing Xquartz for visual display**
   + brew install xquartz
   + open Xquartz locally 
   + go to Preferences --> Security --> tick allow connections from network clients & restart Xquartz
   + get the host IP: **IP=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')**
   + set the DISPLAY environment variable: **export DISPLAY=$IP:0**
   + add PATH to xhost: **export PATH=/usr/X11/bin/xhost:$PATH**
   + add IP to xhost: **xhost + $IP**

**2.Installing Pulseaudio**
   + brew install pulseaudio
   + set up pulseaudio network: go to **/usr/local/Cellar/pulseaudio/<pulse_audio_version>/etc/pulse/default.pa** or **/usr/local/homebrew/Cellar/pulseaudio/<pulse_audio_version>/etc/pulse/default.pa**
   + uncommented these two lines: **load-module module-esound-protocol-tcp** & **load-module module-native-protocol-tcp**
   
Finally, to run the docker image:
   + **docker run -it --rm -v ~/.config/pulse:/root/.config/pulse -e DISPLAY=IP:0 -e PULSE_SERVER=IP:4713 scraper_gui_firefox:latest**
   + -v ~/.config/pulse:/root/.config/pulse - makes sure both client and server have same cookie file for pulse audio
   + -e PULSE_SERVER=IP:4713 -default pulseaudio port is 4713 but you can double check by running **lsof -PiTCP -sTCP:LISTEN**
## Testing.
All the public methods have been tested using the unittest module in Python. The tests can be evaluated by running the test_module.py inside the test directory.
The tests check the following functionalities:
   + whether the correct number of book links has been scrapped (based on the --subcategory flag value)
   + whether the correct metadata was collected (based on whether provided postcode is a valid or invalid UK postcode)
   
## Cloud storage
For this project, we are using two AWS services to store data in the cloud, namely S3 and RDS.

 We provide two different ways of storing data on S3, based on CLI flags the user choses, namely whether the --subcategory flag is given or not:
   + if --subcategory : data is first locally saved (the metadata in json file and images as jpg) with data belogining to the same subcategory being saved in one directory. After that, data is uploaded to S3, retaining the category/subcategory format.
   + if no subcategory flag provided: images are directly saved to S3 using their url and the urllib library
   
**For AWS RDS storage** the process is the following:
   + instead of saving the metadata from individual book pages into a list of dictionary, after scraping each book page the information (the metadata dictionary) is converted to a pandas data frame and sent out to the RDS database
   + the database is checked before a new entry is added in order to avoid duplicate entries

## Cloud computing
To make the webscraper scalably distributable in the cloud, first a Docker image was built. This image is publicly accessible on DockerHub and can be pulled as follows: docker pull mayaaiuga/scraper:latest.
This Dockerimage has been successively pulled & run on an AWS EC2 instance.
   
## Monitoring: Prometheus and Grafana
Prometheus was used to monitor OS and Docker metrics from a local machine, while the webscraper ran in a docker container on the EC2 instance. For this, the following steps were followed:
   + the prometheus dockerimage was pulled on the EC2 instance
   + Prometheus was configured to scrape node exporter metrics (this allows to track OS metrics)
   + Prometheus was configured to track Docker

Grafana was used to create a dashboard and track custom metrics.

Example of tracked OS metrics:
   1. Total free RAM provides us with the amount of free memory left on the system
   2. Total usable RAM provides us with the amount of memory on the server as a whole
   3. CPU usage %
   4. The average network traffic received, per second, over the last minute (in bytes)
   <img width="562" alt="Grafana_OSmetrics" src="https://user-images.githubusercontent.com/104773240/172405935-f87603d1-e0ea-40ba-ae1b-28dba017582d.png">
  
Example of tracked Docker metrics:
   1. Number of container actions/second
   2. Container states: how many containers are in each state
   3. Total number of events
   4. Time to process each container action
   <img width="531" alt="Grafana_DockerMetrics" src="https://user-images.githubusercontent.com/104773240/172408585-fc662720-3481-469d-9ed1-991eb0c90ae9.png">

## CI/CD pipeline for DockerImage
 
A basic CI/CD pipeline was introduced using GitHub Actions. This workflow, means that every time there is a push to the main branch, a new DockerImage will be created automatically. This image will then be pushed to DockerHub. The workflow can be found at /.github/workflows
   
Lastly, a daily CronJob was set up on the EC2 instance. The CronJob does the following:
   + restarts the webscraper everyday on the EC2 instance
   + stops and kills the docker container from the previous job
   + pulls the latest scraper image from DockerHub & runs the scraper.
