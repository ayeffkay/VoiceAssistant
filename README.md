# Project description

This is voice assistant prototype.

**Frontend** html + css + js

**Backend** flask + redis

**Supported features**
* Voice or text input. Speech to text conversion is done with [Google Cloud Speech API](https://cloud.google.com/speech-to-text)
* Translation from Russian to English using [Google Translate API](https://pypi.org/project/googletrans/)
* Translation history (can be removed)

Output speech synthesis is implemented with [gTTS](https://pypi.org/project/gTTS/) but doesn't work now (js doesn't recognize link to Response object from Flask).


# Usage

1. For performing queries to Google Speech API the key needed. Possible options:
    * Set up authentication by yourself (see [tutorial](https://cloud.google.com/speech-to-text/docs/libraries#setting_up_authentication) for details). It's free.
    * Contact me and I'll share my key (unfortunately I cannot share the key publicly)
    
2. To compose docker image:
```
docker build -t voice-assistant .
docker-compose up
```

3. Due to security reasons audio recording with *navigator.mediaDevices.getUserMedia* cannot be performed on non-security connections (including localhost). To resolve issue, [generate SSL for localhost](https://habr.com/ru/company/globalsign/blog/435476/). Then after docker-compose run
```
localhost:5000
```
I have not found any other way for audio to be recorded on localhost (if you run 0.0.0.0:5000 audio will not be recorded).

4. Sometimes Google Translate API doesn't recognize queries for unknown reasons. You'll get 'Not recognized' output. Important: this is not application error, this is error response from Google's API.

