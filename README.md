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

### Mac Setup
(Tested on MacOS Big Sur 11.4, M1 Chip, Intel Chip)

1. Install Pyenv and Python 3.8.10

```bash
brew install pyenv
pyenv install 3.8.10
pyenv global 3.8.10

# Run this and follow instructions for how to update your PATH, ~/.profile, ~/.zprofile, and ~/.zshrc. Then do a full logout and log back in.
pyenv init

# Verify pyenv is working
>> python -V 
Python 3.8.10
```

2. Install homebrew prerequisites

```bash
# Microphone support
brew install portaudio

# Sphinx NLP library (Optional, also requires python 3.6)
# https://pypi.org/project/pocketsphinx/
# https://github.com/Uberi/speech_recognition/blob/master/reference/pocketsphinx.rst
brew install swig

# For AppKit
brew install cairo gobject-introspection

# For Kivy
# https://kivy.org/doc/stable/installation/installation-osx.html#install-source-os
brew install pkg-config sdl2 sdl2_image sdl2_ttf sdl2_mixer gstreamer
```

3. Install Chrome Web driver (for browser automation)

Instructions [here](https://www.selenium.dev/documentation/en/selenium_installation). On MacOS you also have to grant permissions to web driver. Download the same version as your version of Chrome.

### Ubuntu Setup

(Tested on Ubuntu 20.04)

1. Install Python Virtual Environment

```
sudo apt install python3-venv
```

2. Install library dependencies

```
sudo apt install python3.8-dev

# Kivy depends on this
sudo apt install python3-tk
sudo apt install libcairo2-dev

# SpeechRecognition package depends on these
sudo apt install libportaudio2 portaudio19-dev

# PyGObject depends on this
sudo apt install libgirepository1.0-dev
```

### Common Python Setup

1. Create Virtualenv (Python 3.8)

```bash
pip3 install virtualenv
virtualenv .venv --python=python3
source .venv/bin/activate
```

2. Install python dependencies

```bash
# export ARCHFLAGS="-arch x86_64"  # for pyaudio on older versions of MacOS (not required on Big Sur)
pip install -r requirements.txt
```

3. Install [Kivy](https://kivy.org) (Mac Only)

```bash
# The M1 architecture requires we install Kivy from source
# https://kivy.org/doc/stable/gettingstarted/installation.html#from-source
git clone git://github.com/kivy/kivy.git kivy_repo && cd kivy_repo
python -m pip install -e ".[base]"  && cd ..
```

4. Verify things are working

```bash
# Say something
python scratch/speech_recognition_examples.py

# A window with "Hello world" should open
python scratch/kivy_example.py

# Verify Selenium is installed correctly
python scratch/selenium_example.py

# Run the main app (then click Record and "Switch to Chrome")
python main.py
```

## Distributing the app

Some options for packaging the app into a native executable:

* https://github.com/pyinstaller/pyinstaller
* https://pyoxidizer.readthedocs.io/en/stable/pyoxidizer_comparisons.html
* https://py2app.readthedocs.io/en/latest/ (Mac-only)

## Links

Documentation
* [AppKit](https://developer.apple.com/documentation/appkit)

For creating menu bars on MacOS
* https://github.com/jaredks/rumps
* https://stackoverflow.com/questions/26815360/how-to-create-menu-item-in-osx-menubar-using-pyinstaller-packaged-kivy-python-ap

Similar projects
* https://github.com/ulwlu/kivy-speech-recognition/blob/master/main.py
* https://github.com/jmercouris/speech_recognition


## Roadmap

Features / Enhancements

* Keyboard shortcut to open App and click record
* "Listening" animation after clicking record
* Dedicated console on GUI for debug logs (currently logs are truncated)
* Improve responsiveness of speech recognition

Bugs / Known Issues

* Speech recognition gets stuck during Record if background noise fluctuates after calibration
* Logs are truncated at the sides on MacOS

