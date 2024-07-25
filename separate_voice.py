import speech_recognition as sr
import pyaudio as pa
import sounddevice as sd
import soundfile as sf
import argparse

recognizer = sr.Recognizer()
parser = argparse.ArgumentParser(add_help=False)

def listen_Recognize(source, time = None):
    audio = recognizer.listen(source, phrase_time_limit= time)
    text = recognizer.recognize_google(audio, language = "tr-TR")
    text = text.capitalize()
    return text

def process(text):
    #Müzik çalınmaya başladıktan sonra terminal donuyor
    match text:
        case "Müzik":
            try:
                data, fs = sf.read("muzik.wav", dtype="float32")
                print("Müzik oynatılıyor")
                sd.play(data, fs)
            except KeyboardInterrupt:
                parser.exit('Müzik durduruldu.')
            except Exception as e:
                parser.exit(type(e).__name__ + ': ' + str(e))
        
        case 2:
            pass

        case "Çıkış":
            print("İyi günler dilerim.")
            exit()
            
while True:
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise = 0.5
            recognizer.energy_threshold = 2000
            print("Müzik dinlemek isterseniz 'Müzik' diyebilir veya 'Çıkış' diyerek konuşmayı bitirebilirsiniz.")
            print("Dinleniliyor..")
            text = listen_Recognize(source, 5)
            process(text)
    except sr.UnknownValueError:
        print("Dediğiniz anlaşılmadı, tekrar eder misiniz?")

