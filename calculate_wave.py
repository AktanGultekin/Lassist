import speech_recognition as sr
import pyttsx3
import matplotlib.pyplot as plt
import wave
import sys
import numpy as np
import time

index = 0

while index<5:
    spf = wave.open(f"microphone-results({index}).wav", "r")
    signal = spf.readframes(-1)
    signal = np.frombuffer(signal, np.int16)

    if(spf.getnchannels() == 2):
        print("Just mono files")
        sys.exit(0)

    plt.figure(index)
    plt.title("Signal Wave")
    plt.plot(signal)
    plt.show(block = True)
    index = index + 1
    


"""
spf = wave.open("microphone-results.wav", "r")
signal = spf.readframes(-1)
signal = np.frombuffer(signal, np.int16)

if(spf.getnchannels() == 2):
    print("Just mono files")
    sys.exit(0)

plt.figure(1)
plt.title("Signal Wave...")
plt.plot(signal)
plt.show()
"""

"""
r = sr.Recognizer()
file = open("metin.txt", "w")

def speakTest(command):
    engine = pyttsx3.init()
    engine.say(command)
    engine.runAndWait()

while(True):
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration = 0.2)
            audio = r.listen(source)
            print("Dinleniliyor...")
            metin = r.recognize_google(audio, language = "tr-TR")
            metin = metin.capitalize()

            print(f"Bunu mu söylemek istediniz: {metin}")
            if len(metin)>0:
                file.write(metin)
            speakTest(metin)

        with open("microphone-results.wav", "wb") as f: #Ses dosyası oluşturma
            f.write(audio.get_wav_data())      
            
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))

    except sr.UnknownValueError:
        print("Unknown error occurred!")

    except KeyboardInterrupt:
        print("Mikrofon kapatıldı.")
        file.close()
        exit()

    except UnicodeEncodeError:
        continue
        
"""