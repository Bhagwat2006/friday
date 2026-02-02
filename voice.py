import pyttsx3
import speech_recognition as sr
import threading
from config import settings

class VoiceEngine:
    def __init__(self):
        self.engine = pyttsx3.init('sapi5')
        self.setup_voice()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise once at startup
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    def setup_voice(self):
        voices = self.engine.getProperty('voices')
        # Try to find a female voice or specifically "Zira" (common on Windows)
        voice_id = None
        for voice in voices:
            if "Zira" in voice.name or "female" in voice.name.lower():
                voice_id = voice.id
                break
        
        if not voice_id and len(voices) > 0:
            voice_id = voices[0].id
            
        if voice_id:
            self.engine.setProperty('voice', voice_id)
            
        self.engine.setProperty('rate', settings.VOICE_RATE)
        self.engine.setProperty('volume', settings.VOICE_VOLUME)

    def speak(self, text):
        if not text:
            return
        print(f"{settings.AI_NAME}: {text}")
        
        # Run speech in a separate thread to ensure smooth flow
        # We process the ENTIRE text at once for natural intonation
        def _speak_thread():
            try:
                # Initialize engine for this utterance
                engine = pyttsx3.init()
                
                # Setup voice
                voices = engine.getProperty('voices')
                voice_id = None
                for voice in voices:
                    if "Zira" in voice.name or "female" in voice.name.lower():
                        voice_id = voice.id
                        break
                if voice_id: engine.setProperty('voice', voice_id)
                
                engine.setProperty('rate', settings.VOICE_RATE)
                engine.setProperty('volume', settings.VOICE_VOLUME)
                
                # Say the full text - no chunking, no pauses
                engine.say(text)
                engine.runAndWait()
                
            except Exception as e:
                print(f"Voice Error: {e}")

        t = threading.Thread(target=_speak_thread)
        t.start()
        t.join() # Wait for speech to complete naturally

    def listen(self):
        with self.microphone as source:
            print(f"\n[{settings.AI_NAME} is listening...]")
            try:
                # Short timeout for quick interactions
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                query = self.recognizer.recognize_google(audio, language='en-in')
                print(f"{settings.USER_NAME}: {query}")
                return query.lower()
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                return None
            except Exception as e:
                print(f"Microphone Error: {e}")
                return None
