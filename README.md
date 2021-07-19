# jarvis

* [Architecture Overview](https://docs.google.com/document/d/13zdsfZo1CowELebOghJDcNnIFnKkGBB2g_AN2ByaiQU)
* [Google Drive](https://drive.google.com/drive/folders/1rnHkYZJzJOSadJtp-F4n4ItPE8-IsAUX)

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

## Roadmap

Features / Enhancements

* Keyboard shortcut to open App and click record
* "Listening" animation after clicking record
* Dedicated console on GUI for debug logs (currently logs are truncated)
* [Record from history](https://caster.readthedocs.io/en/latest/readthedocs/Caster_Commands/Record_Macros/) (save a sequence of voice commands as a macro) - 

Bugs / Known Issues

* If you forget to call "exit" in stream mode and let the microphone run for awhile before your next command, google will continue to record audio and try to process an extremely large transcript which causes the program to timeout / drag. We need a way to detect silence in stream mode, and clear the audio buffer. We can use a timeout parameter in the Microphone or GoogleTranscriber to clear the buffer if no commands are heard for N seconds
* [Mac] The TaskBar loads slowly and gets stuck sometimes
* [Mac] "Switch to X" gets stuck if program is minimized ()
* [Mac] GUI layout isn't formatted properly. Appears to be differences between Monitors or Operating Systems we need to work out. Ideally the GUI can appear the same across all monitors/OS. 

## Developer Setup

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

brew install openssl
```

3. Update environment variables to properly configure clang

Either add these to ~/.profile or manually run them in the shell before running `pip install -r requirements`

```
export GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=1
export GRPC_PYTHON_BUILD_SYSTEM_ZLIB=1
export CPLUS_INCLUDE_PATH="${CPLUS_INCLUDE_PATH:+${CPLUS_INCLUDE_PATH}:}/opt/homebrew/opt/openssl/include"
```

4. Install Chrome Web driver (for browser automation)

Instructions [here](https://www.selenium.dev/documentation/en/selenium_installation). On MacOS you also have to grant permissions to web driver. Download the same version as your version of Chrome.

5. Set up Google Cloud Project

First, create a GCP project or use the Jarvis one (jarvis-1626279785926). If you create one, you'll need to set up
a billing account and enable the Cloud Speech APIs.

Next, install the SDK https://cloud.google.com/sdk/docs/install and configure it.

```bash
gcloud init
gcloud config list

# Should see something like
[core]
account = bfortuner@gmail.com
disable_usage_reporting = True
project = jarvis-1626279785926

# Login to get credentials
gcloud auth application-default login  
```

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

# Taskbar icon support requires this
sudo apt install gir1.2-appindicator3-0.1
```

### Python Setup

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

4. Install [atomac](https://github.com/pyatom/pyatom) (Mac Only)

Atomac seems to have a dependency because of which we can't install directly 
using `pip install` so we need to get the source code.

```bash
git clone https://github.com/pyatom/pyatom.git && cd pyatom
python -m pip install future
python -m pip install && cd ..
```

5. Verify things are working

```bash
# Say something
python scratch/speech_recognition_examples.py

# Verify GCP auth is working
python scratch/google_speech_recognition_example.py

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

Voice Programming
* https://github.com/jim-schwoebel/voicebook (Textbook with Python example code! Useful utilities.)
* https://github.com/dictation-toolbox/dragonfly
    * https://github.com/daanzu/dragonfly/blob/kaldi/dragonfly/engines/backend_kaldi/engine.py (example with Kaldi)
* https://github.com/dictation-toolbox/Caster
* https://github.com/jim-schwoebel/voicebook/blob/master/chapter_1_fundamentals/readme.md (a lot of useful utilities for working with audio and speech stuff)
* https://github.com/lyncisdev/voco
* https://github.com/VoiceCode/voicecode ([website](https://www.voicecode.io))
* https://www.nuance.com/dragon/business-solutions/dragon-professional-individual.html
* https://github.com/dictation-toolbox/Vocola2/tree/master/src/vocola2/samples (Application-specific commands)
* https://dragonfluid.readthedocs.io/en/latest/README.html (chaining multiple commands)
* 

Speech Recognition
* https://github.com/alphacep/vosk-api (offline library for fast speech recognition)
* https://github.com/kaldi-asr/kaldi (Dragonfly defaults to this over Sphinx..)
* https://github.com/daanzu/kaldi-active-grammar/blob/master/docs/models.md (Kaldi model comparison)
* https://github.com/CHERTS/mspeech (and synthesis)
* https://github.com/dictation-toolbox/dragonfly
* https://github.com/ulwlu/kivy-speech-recognition/blob/master/main.py
* https://github.com/jmercouris/speech_recognition

Microphone/audio recording example
* https://github.com/daanzu/kaldi-active-grammar/blob/master/examples/audio.py
* https://github.com/daanzu/kaldi-active-grammar/blob/master/examples/full_example.py

Audio ML
* https://github.com/jim-schwoebel/allie/tree/master/augmentation/audio_augmentation 

Datasets
* https://www.neurolex.ai/ (Audio, voice, speaking)
