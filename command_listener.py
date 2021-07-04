import speech_recognition as sr


class CommandListener(object):
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def listen(self) -> str:
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source)
                text = self.recognizer.recognize_google(audio)
                return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
    