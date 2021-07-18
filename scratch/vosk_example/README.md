# Vosk API (Fast, cross-device speech recognition)

Really really fast, not super accurate, but small models (50MB).

Setup Instructions:
https://alphacephei.com/vosk/install

```bash
# Check the latest instructions, but this worked for me (July 2021)
pip3 install vosk

# Download examples
git clone https://github.com/alphacep/vosk-api
cd vosk-api/python/example
wget https://alphacephei.com/kaldi/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 model

# Run example
python3 test_microphone.py
```
