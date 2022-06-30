FROM python:3.9

# Update the system and install firefox
RUN apt-get update 
RUN apt -y upgrade 
RUN apt-get install -y firefox-esr

# get the latest release version of firefox 
RUN latest_release=$(curl -sS https://api.github.com/repos/mozilla/geckodriver/releases/latest \
    | grep tag_name | sed -E 's/.*"([^"]+)".*/\1/') && \
    # Download the latest release of geckodriver
    wget https://github.com/mozilla/geckodriver/releases/download/$latest_release/geckodriver-$latest_release-linux32.tar.gz \
    # extract the geckodriver
    && tar -xvzf geckodriver* \
    # add executable permissions to the driver
    && chmod +x geckodriver \
    # Move gecko driver in the system path
    && mv geckodriver /usr/local/bin

# Install Tkinter
RUN apt-get install tk -y 
# Install PulseAudio
RUN apt-get -qq update && apt-get install -y pulseaudio
# Install Kivy dependencies
RUN apt-get install -y ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev

#copy local files
COPY . .
#install dependencies
RUN pip install -r ./requirements.txt
RUN pip uninstall kivy
RUN pip install --no-binary kivy kivy

ENTRYPOINT ["python", "GUI/webscraper_GUI.py"]
