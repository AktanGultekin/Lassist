import speech_recognition as sr
import pyttsx3
import GPT_RegEx
#https://www.geeksforgeeks.org/python-convert-speech-to-text-and-text-to-speech/
#Sesten gelen text üzerinden regex uygulayarak bilgi edinmek

r = sr.Recognizer()
audio = "audio.wav"

def speakTest(command):
    engine = pyttsx3.init("sapi5", True)
    engine.say(command)
    engine.runAndWait()

while(True):
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration = 0.2)
            audio2 = r.listen(source)
            print("Dinleniliyor...")
            metin = r.recognize_google(audio2, language = "tr-TR")
            metin = metin.capitalize()
            GPT_RegEx.text_from_audio.append(metin) # Söylenilen metni GPT_RegEx dosyasındaki text_from_audio listesine kaydedeceğiz.

            print(f"Bunu mu söylemek istediniz: {metin}")
            speakTest(metin)
            
        with open("microphone-results.wav", "wb") as f:
            f.write(audio2.get_wav_data())
            
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))

    except sr.UnknownValueError:
        print("Unknown error occurred!")

    except KeyboardInterrupt:
        print("Mikrofon kapatıldı.")
        exit()

    
        


