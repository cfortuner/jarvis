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
export ARCHFLAGS="-arch x86_64"

# Offline NLP library
# https://pypi.org/project/pocketsphinx/
# https://github.com/Uberi/speech_recognition/blob/master/reference/pocketsphinx.rst
brew install swig
```

4. Install python dependencies

```bash
pip install -r requirements.txt
```

5. Verify things are working

```bash
# Say something
python speech_recognition_examples.py
```
