# jarvis


Potential use cases
- quick switch to application or a tab
- layout application windows in a grid
- automate interactions with applications (share)
- start/stop recording
- take screenshot
- quick note taking
- copy to different clipboard buffers "copy this as blah", "paste from blah"
- set reminders
- notify

## Setup

(Tested on MacOS Big Sur 11.4)

1. Install Pyenv and Python 3.6 on MacOSX (newer python versions not supported by some deps)

```bash
brew install pyenv
pyenv install 3.6.14
pyenv global 3.6.14

# Run this and follow instructions for how to update your PATH, ~/.profile, ~/.zprofile, and ~/.zshrc. Then do a full logout and log back in.
pyenv init

# Verify pyenv is working
>> python -V 
Python 3.6.14
```

2. Create Virtualenv (Python 3.6)

```bash
pip install virtualenv
virtualenv .venv
source .venv/bin/activate
```

3. Install prerequisites for SpeechRecognition https://pypi.org/project/SpeechRecognition/

```bash
# Microphone support
brew install portaudio

# Offline NLP library
# https://pypi.org/project/pocketsphinx/
# https://github.com/Uberi/speech_recognition/blob/master/reference/pocketsphinx.rst
brew install swig
```

4. Install python dependencies

```bash
# export ARCHFLAGS="-arch x86_64"  # for pyaudio on older versions of MacOS (not required on Big Sur)
pip install -r requirements.txt
```

5. Verify things are working

```bash
# Say something
python speech_recognition_examples.py

# A window with "Hello world" should open
python kivy_example.py

# Run the Kivy GUI
python speech_app.py
```

## Distributing the app

Some options for packaging the app into a native executable:

* https://github.com/pyinstaller/pyinstaller
* https://pyoxidizer.readthedocs.io/en/stable/pyoxidizer_comparisons.html
* https://py2app.readthedocs.io/en/latest/ (Mac-only)

## Links

For creating menu bars on MacOS
* https://github.com/jaredks/rumps
* https://stackoverflow.com/questions/26815360/how-to-create-menu-item-in-osx-menubar-using-pyinstaller-packaged-kivy-python-ap

Similar projects
* https://github.com/ulwlu/kivy-speech-recognition/blob/master/main.py
* https://github.com/jmercouris/speech_recognition
