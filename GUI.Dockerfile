FROM python:3.9

#download & install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - &&\
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' &&\
    apt-get -y update &&\
    apt-get install -y google-chrome-stable &&\
    #install chromedriver
    wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip &&\
    apt-get install -yqq unzip &&\
    unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

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

#
ENTRYPOINT ["python", "GUI/webscraper_GUI.py"]
