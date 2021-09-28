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

We *try* to follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).

## Roadmap

See the [Brainstorm](https://docs.google.com/document/d/1xiLHVMMXLBE7JgWXhZ18eERzvKIUjfbp4kCxcofDmzk/edit?usp=sharing) doc for the "crazy ideas."

Features / Enhancements

* Keyboard shortcut to open App and click record
* "Listening" animation after clicking record
* Dedicated console on GUI for debug logs (currently logs are truncated)
* [Record from history](https://caster.readthedocs.io/en/latest/readthedocs/Caster_Commands/Record_Macros/) (save a sequence of voice commands as a macro)

Bugs / Known Issues

* If you forget to call "exit" in stream mode and let the microphone run for awhile before your next command, google will continue to record audio and try to process an extremely large transcript which causes the program to timeout / drag. We need a way to detect silence in stream mode, and clear the audio buffer. We can use a timeout parameter in the Microphone or GoogleTranscriber to clear the buffer if no commands are heard for N seconds
* [Mac] The TaskBar loads slowly and gets stuck sometimes
* [Mac] "Switch to X" gets stuck if program is minimized ()
* [Mac] GUI layout isn't formatted properly. Appears to be differences between Monitors or Operating Systems we need to work out. Ideally the GUI can appear the same across all monitors/OS.

UI Features/Bugs

* Use real-time sound detection from mic to play animation (don't wait for google)?
* Show/Hide GUI using the Python API (make keyboard shortcut)
* Send Show/Hide event to Python when the user opens the window
* UI should always be on top of all windows (pin the window)?

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

# If running without a GUI and pyautogui gives you KEYERROR :DISPLAY. Add this to ~/.bashrc, etc.
export DISPLAY=:0
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
git clone https://github.com/pyatom/pyatom.git pyatom_repo && cd pyatom_repo
python -m pip install future
python -m pip install . && cd ..
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
python -m scratch.selenium_example

# Run the Kivy app (then click Record and "Switch to Chrome")
python main.py

# OR, run the electron app
python electron.py

# And in prophet...
npm install
npm run start
```

6. App steps

```bash
# Load contacts from google
python -m higgins.automation.contacts.google

# Install pytorch
pip3 install torch==1.9.0+cu111 torchvision==0.10.0+cu111 torchaudio==0.9.0 -f https://download.pytorch.org/whl/torch_stable.html
```

## Testing

Run unit tests

```bash
# Optionally prepend SPEED_LIMIT=N_SEC to slow down the automation when debugging
pytest tests/
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

Audio Libraries
* https://github.com/amsehili/auditok
* https://github.com/jleb/pyaudio
* https://github.com/tyiannak/pyAudioAnalysis
* https://github.com/rhasspy/rhasspy-silence (silence detection)

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
* https://arxiv.org/abs/1809.08887 (Spider, text2sql database)

Python (background tasks and queues)
* https://testdriven.io/blog/developing-an-asynchronous-task-queue-in-python/
* https://docs.celeryproject.org/en/stable/
* https://python-rq.org/
* https://huey.readthedocs.io/en/latest/

NLP
* https://beta.openai.com/examples (GPT3 API)

Code Generation
* [auto-generate regex from NL examples](https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00339/96479/Sketch-Driven-Regular-Expression-Generation-from)
* [generate regex from examples](https://dl.acm.org/doi/abs/10.1145/3385412.3385988)
* [Code generation with external retrieval](https://arxiv.org/abs/2004.09015)
* [Excel Formula Prediction](http://proceedings.mlr.press/v139/chen21m.html)

NLP-to-Bash
* https://devhints.io/
* https://github.com/idank/explainshell
* https://github.com/tldr-pages/tldr (better man pages with examples!)
* [NL2Bash Competition](https://eval.ai/web/challenges/challenge-page/674/leaderboard/1831#leaderboardrank-1)
* [Tellina - NL2Bash](https://github.com/TellinaTool/tellina)
* [IBM CLI code](https://clai-home.mybluemix.net/)
* ["Skill Plugin" API for Jarvis](https://github.com/IBM/clai/tree/master/clai/server/plugins)

Desktop Launcher Tools (Mac Spotlight++)
* [Alfred](https://www.alfredapp.com/) and [plugins](http://www.packal.org/)
* [Raycast](https://raycast.com/)

Headless Browsers
* https://github.com/dhamaniasad/HeadlessBrowsers

Personal Assistant
* https://github.com/neuml/txtai (local (no API) semantic search engine, could replace Open.AI for queries)
* https://github.com/daveshap/NLCA_Question_Generator (question generator, to ask clarifying questions given something the user says)
    * How to determine user intent? Generate some questions based on the chat thread, then use semantic search to answer the questions.

Semantic Search
* https://beta.openai.com/docs/guides/search (semantic search)
* https://beta.openai.com/docs/guides/answers (semantic search --> QA pipeline)
* https://github.com/neuml/txtai
* https://github.com/neuml/txtai/blob/master/examples/04_Add_semantic_search_to_Elasticsearch.ipynb
* https://cloud.google.com/natural-language/docs/samples/language-classify-text-tutorial-query
* https://aws.amazon.com/kendra/ (semantic search)
* https://aws.amazon.com/comprehend/ (text analysis, search)


## GPT3 Notes

* [How to avoid making up facts (and large document parsing)](https://community.openai.com/t/how-do-i-upload-a-book-to-gpt3/1499/9)
* [Fine-tune a model to improve truthfulness](https://docs.google.com/document/d/1Cx25TplZ3tL_cTFlFEChLJ2z1l1sa2WKivAVCpqYPnE/edit#heading=h.qnufq9wqvxvd)
    * Sample 10+ generations and pass them through a discriminator / classifier to determine truthfulness
* [Preventing Hallucination Facebook](https://www.unite.ai/preventing-hallucination-in-gpt-3-and-other-complex-language-models/)
* [Longformer - Larger texts](https://arxiv.org/abs/2004.05150)
* [Improving reasoning skills](https://blog.andrewcantino.com/blog/2021/05/28/how-to-dramatically-improve-the-reasoning-ability-of-GPT-3/)

### Ideas to improve truthfulness

* Generator samples 10 answers, discriminator evaluates the answers and selects the best
* Fine-tune the model on your facts
* Lower the temperature
* Include "I don't know" as a valid response, with examples (false positives)
* Incorporate the model's confidence (log probs?) to evaluate the reply (and determine how many times to sample?)

### Ideas to process large documents

Website for GPT-based projects http://gptcrush.com/
Email-related product from GPT https://www.hypertype.co/

* NOTE: You pay money for every document searched
* Pre-search the data with a cheap model (Ada) or non-model-based search engine (Gmail API, ElasticSearch, txt AI)
* Break large documents into snippets
* Pre-process the document into summarizations or salient facts
* Run semantic search, then completion (like answers/ endpoint)
* [I have 6M documents and fast search with SOLR (ElasticSearch)](https://community.openai.com/t/summarizing-or-question-answering-from-long-wikipedia-articles/4137/6)
* Steps
  * Search relevant documents with cheap local engine (elasticsearch, SOLR)
  * Upload chunks of these articles dynamically based on the most relevant chunk from that article
  * Pass results to semantic search or answers endpoint

### Semantic Search / Email Processing

* [Info Retreival with ReRank](https://github.com/UKPLab/sentence-transformers/blob/master/examples/applications/semantic-search/semantic_search_wikipedia_qa.py)
* [Info Retreival with ReRank](https://github.com/UKPLab/sentence-transformers/tree/master/examples/applications/retrieve_rerank) (Could be used for email search. Can operate on paragraphs.)
* [Topic Modeling](https://maartengr.github.io/BERTopic/tutorial/algorithm/algorithm.html) - topic modeling / clustering. Guided (manually seed topics), semi, or unsupervised. Could be used to categorize emails by their semantic meaning (recruiter emails, family/personal, flights, verification codes, orders/receipts, promotions, etc.)
* [TextRank] https://towardsdatascience.com/textrank-for-keyword-extraction-by-python-c0bae21bcec0 - extract most important keywords from emails and discard the rest
* [Extractive Summarization Overview](https://www.machinelearningplus.com/nlp/text-summarization-approaches-nlp-example) - Gensim
* Extracting data from HTML tables and websites [1](https://arxiv.org/abs/1903.08305) [2](https://arxiv.org/abs/1403.1939)
* [TextPipe](https://github.com/textpipe/textpipe) Extracting text from HTML pages


### Data Labeling

* https://prodi.gy/features (Scriptable annotation tool for NLP tasks -- and some CV)
* 

