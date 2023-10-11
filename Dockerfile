FROM python:3.9

# Update the package repository and install the necessary tools and install firefox
RUN apt-get update && apt-get install -y \
    jq \
    wget \
    tar
RUN apt-get install -y firefox-esr


# get the latest release version of firefox 
RUN latest_release=$(curl -sS https://api.github.com/repos/mozilla/geckodriver/releases/latest | jq -r .tag_name) && \
    # Download the latest release of geckodriver
    wget https://github.com/mozilla/geckodriver/releases/download/$latest_release/geckodriver-$latest_release-linux32.tar.gz \
    # extract the geckodriver
    && tar -xvzf geckodriver* \
    # add executable permissions to the driver
    && chmod +x geckodriver \
    # Move gecko driver in the system path
    && mv geckodriver /usr/local/bin

#set display port to avoid crash
ENV DISPLAY=:99

#copy local files
COPY . .
#install dependencies
RUN pip install -r ./requirements.txt
#
ENTRYPOINT ["python", "project/Scraper_Runner.py"]
CMD ["--category", "--headless"]
