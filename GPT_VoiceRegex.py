#<----------------------------------------------------------------------------REGEX LIBS------------------------------------------------------------------------------>
import re
import string
from itertools import chain
import sys
#<------------------------------------------------------------------------VOICE RECOGNITION LIBS---------------------------------------------------------------------------->
import speech_recognition as sr
#import pyttsx3
import numpy as np
import os
import scipy.io.wavfile as wavfile
from scipy.io.wavfile import write
import matplotlib.pyplot as plt
from math import log10
import pyaudio
#import time
from pydub import AudioSegment
from pydub.playback import play
import sounddevice as sd
import soundfile as sf
import argparse
#<-------------------------------------------------------------------------------------------------------------------------------------------------------------->

#Fikirler
"""
*Bir otel json dosyası ve komut json dosyası düşün. Kullanıcı bir komut söylediğinde komut
dosyasındaki bir komuta erişilip aktive edilecek.

*Kullanıcı, robot ile sohbet sırasında konuştuğu şeylerden elimizde bulunan anahtar kelimeler eğer konuşma
içindeki bir cümlede geçiyorsa o cümleyi tamamiyle alıp tutabiliriz. Bu sayede ilerideki sohbetlerde bu
verileri kullanarak müşteri memnuniyetini arttırabiliriz.

*Bu tuttuğumuz cümlelerden yüzde 50'si dahi işe yarar veriler içerse yine de bize avantaj sağlar.
"""

#Bazı örnek textler
text = """Merhaba. ben Ahmet Bitik. 25 yaşındayım. İnşaat ustasıyım. Ankara'da oturuyorum. Doğum tarihim 05.04.2002"""
text2= """Selam, bana Akif Taşlı derler. Yaşım 22. İşçiyim. Tokat'da yaşıyorum. Doğum tarihim 09.11.2001"""
text3= """Selam, ben Doktor Veysel. Yaşım 35. İşçiyim. Malatya'da yaşıyorum. Doğum tarihim 04.1989"""
text4 = """Selam, ben Akman. Yaşım 58'dir. İşçiyim. Erzurum'da yaşıyorum. Doğum tarihim 06.08.1966"""
text5 = """Selam, ben Hasan. 63 yaşındayım. İşçiyim. Çanakkale'da yaşıyorum. Doğum tarihim 2.10.1961. Yani 2 Ekim 1961 doğumluyum."""
speech_text = """
10 Haziran 2024'de düğünümüz var. Bunun ardından 4 Temmuz'da Kurtuluş Günü'nü kutlayacağız. 31 Ekim'de Cadılar Bayramı'nı unutma ve Aralık'da konferansımız var.
"""

#Text listesi
texts = [text,text2, text3, text4, text5] # Ne zaman mikrofondan ses alınırsa bir metin değişkenine kaydedilip onu texts listesine eklenilecek.

text_from_audio = []

#Tekli text için tekli patternler
"""
#isim = r"Ben\s\w+\s\w+"   #isim adlı pattern ile isim soyisim alındı. --Outdated by multi/single name patterns 
yas = r"\d+\syaş\w+"  #yas adlı pattern ile konuşmadaki yaş bilgisi elde edildi.
yasadigiYer = r"(/w+'de|/w+'da (otur\w+|yaşıyor\w+|ikamet))" #yasadigiYer adlı pattern ile konuşmada kişinin yaşadığı yer bilgisi elde edildi.
tarih = r"([0-3]?[0-9].[0-1][0-9].[0-9]{4}|[1-9]{0,2}\s\w+\s[1-9][0-9]{3})" #tarih adlı pattern ile konuşmada kişinin doğum tarihi elde edildi.
"""

#Çoklu metinler için çoklu isim patternleri ve isim listeleri
multiAdPatterns = [r"[A|a]dım\s\w+\s\w+", r"[B|b]enim ismim\s\w+\s\w+", r"[B|b]ana\s\w+\s\w+", r"[B|b]en\s[a-zA-Z]+\s[a-zA-Z]+"]
singleAdPatterns = [r"ben\s[a-zA-Z]+\."]
isimTemp = []
duzensiz_isimler = [] # isimTemp ve duzensiz_isimler düzeltilmemiş isim listeleri
isimler = [] # isimler düzeltilmiş isim listesi

#Çoklu metinler için çoklu yaş patternleri ve yaş listeleri
yasPatterns = [r"\d+ yaşındayım", r"Yaşım \d+"]
yasTemp = []
duzensiz_yaslar = []
yaslar = []

#Çoklu metinler için çoklu ikametgah patternleri ve listeleri
sehirPatterns = [r"([A-Z]+'de|[A-İ]+'da (otur\w+|yaşıyor\w+))", r"Ben\s\S+\'[de|da]{2}"]
sehirTemp = []
duzensiz_sehirler = []
sehirler = []

#Çoklu metinler için çoklu ikametgah patternleri ve listeleri
tarihPatterns = [r"[0-3]?[0-9]\.[0-1]?[0-9]\.[0-9]?[0-9]{3}", r"[0-31]\s\w+\s[0-9]?[0-9]{3}"]
#r"([0-3][0-9].[0-1][0-9].[0-9]{4}|[1-9]{0,2}\s\w+\s[1-9][0-9]{3})" yedek kalıplar
#r"[0-3]?[0-9]\.[0-1]?[0-9]\.[0-9]?[0-9]{3}", r"[0-31]\s\w+\s[0-9]?[0-9]{3}"
#r"[[0-3]?[0-9]]?\.?[[0-1]?[0-9]]?\.?[1-9]?[1-9]{3}"
tarihTemp = []
duzensiz_tarihler = []
tarihler = []

#Key Memories Alanı - Bazı kalıplarla konuşmada geçen önemli anıları, önemli olayları yakalayacağız. 
""" * https://regex101.com/r/vWbq5c/1 - Özel Günler
    * https://regex101.com/r/MWQtAy/5 - Özel Gün/Ay/Yıl Formatı ve Özel Gün
    * https://regex101.com/r/GIVneT/1 - Bayram Seyran Regex
    * https://regex101.com/r/5kXvvf/3 - Combined
"""
# --- Çoklu ve birbirinden farklı metinlerde bulunan isimleri ayıklama fonksiyonu --- #

def isimAyiklama():
        
    for txt in texts:
        for pattern in multiAdPatterns:
            res = re.findall(pattern,txt)
            if len(res) == 0:
                continue
            else:
                #print(res)#Düzenlenmemiş isim listesi
                isimTemp.append(res)
                       
    for pattern in singleAdPatterns:
        for txt in texts:
            res = re.findall(pattern, txt)
            if len(res) == 0:
                continue
            else:
                #print(res)#Düzenlenmemiş isim listesi
                isimTemp.append(res)

    for i in isimTemp:
        for j in i:
            duzensiz_isimler.append(j)
    #print(duzensiz_isimler)
    isimler = [y[4:] for y in duzensiz_isimler]

    for num in range(0,len(isimler)):
        isimler[num] = isimler[num].lstrip()
        if "." in isimler[num]:
            isimler[num] = isimler[num][:-1]
        #print(x)

    for i in isimler:
        splitted_i = i.split(" ")
        with open('meslekler.csv', 'rt') as file:
            str_arr_csv = file.readlines()
            if str(splitted_i[0]) in str(str_arr_csv):
                index = isimler.index(i)
                word = splitted_i[1]
                isimler.pop(index)
                isimler.insert(index, word)
                
    print(isimler)

#isimAyiklama() #Çalışıyor
#print("\n")
#<----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------->
#<--- Çoklu ve birbirinden farklı metinlerde bulunan yaş bilgilerini ayıklama fonksiyonu --->#

def yasAyiklama():
    for txt in texts:
        for pattern in yasPatterns:
            res = re.findall(pattern, txt)
            if len(res) == 0:
                continue
            else:
                #print(res)
                yasTemp.append(res)

    """for i in yasTemp: #Kontrol
        print(i)"""

    for i in yasTemp:
        for y in i:
            duzensiz_yaslar.append(y)

    for i in duzensiz_yaslar:
        if i[0] not in string.ascii_letters:
            i = i[:2]
            yaslar.append(i)
            #print(i)
        else:
            i = i[6:]
            yaslar.append(i)
            #print(i)

    print(yaslar)

#yasAyiklama() #Çalışıyor
#print("\n")

#<----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------->
#<--- Çoklu ve birbirinden farklı metinlerde bulunan şehir bilgilerini ayıklama fonksiyonu --->#

def sehirAyiklama():
    for txt in texts:
        for pattern in sehirPatterns:
            res = re.findall(pattern,txt)
            if len(res) == 0:
                continue
            else:
                sehirTemp.append(res)

    #print(sehirTemp)
    for i in sehirTemp:
        for k in i:
            k = list(k)
            duzensiz_sehirler.append(k)

    for i in duzensiz_sehirler:
        i.pop()
        a, b, c = i[0].partition("'")
        sehirler.append(a)

    print(sehirler)

#sehirAyiklama() # Çalışıyor
#print("\n")
#<----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------->
#<--- Çoklu ve birbirinden farklı metinlerde bulunan doğum tarihi bilgilerini ayıklama fonksiyonu --->#

#Bu kısmın altı tekli metin ve patternler içindir. Üst kısım ise çoklu metin ve pattern için kullanılmıştır.
def tarihAyiklama():
    for txt in texts:
        for pattern in tarihPatterns:
            res = re.findall(pattern, txt)
            if len(res) == 0:
                    continue
            else:
                #print(res)#Düzenlenmemiş isim listesi
                duzensiz_tarihler.append(res)
    duzenli_tarihler = list(chain.from_iterable(duzensiz_tarihler))
    #print(duzenli_tarihler)

    for duzenli_tarih in duzenli_tarihler:
        if '.' in duzenli_tarih:
            duzenli_tarih = duzenli_tarih.replace('.', '/')
            tarihler.append(duzenli_tarih)
        elif ' ' in duzenli_tarih:
            duzenli_tarih = duzenli_tarih.replace(' ', '/')
            tarihler.append(duzenli_tarih)

    print(tarihler)
"""if '.' in duzensiz_tarih[0]:
        duzensiz_tarih[0] = duzensiz_tarih[0].replace('.', '/')
        tarihler.append(duzensiz_tarih[0])
    elif ' ' in duzensiz_tarih[0]:
        duzensiz_tarih[0] = duzensiz_tarih[0].replace(' ', '/')
        tarihler.append(duzensiz_tarih[0])"""
#tarihAyiklama()
#print("\n")
#<----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------->
# Ses tanıma ve dosya işlemleri

#-Değişken ve Nesne Tanımlama
recognizer = sr.Recognizer()
p = pyaudio.PyAudio()
filename = "muzik.wav"
file = open("metin.txt", "w+")
parser = argparse.ArgumentParser(add_help=False)

#-Fonksiyonlar
def select_microphone(index):
   # Get the device info
   device_info = p.get_device_info_by_index(index)
   # Check if this device is a microphone (an input device)
   if device_info.get('maxInputChannels') > 0:
      print(f"Selected Microphone: {device_info.get('name')}")
   else:
      print(f"No microphone at index {index}")

"""def speakTest(command):
    engine = pyttsx3.init()
    engine.say(command)
    print(command)
    engine.runAndWait()#ai modelinin cevabı dinlenecek kulaklık geldiğinde"""

def deleteTestFiles(choose, filename = "recording", index= 0):
    if choose == 1:
        os.remove(f"{filename}{index}.wav")

def listen_Recognize(source, time = None):
    audio = recognizer.listen(source, phrase_time_limit= time)
    text = recognizer.recognize_google(audio, language = "tr-TR")
    text = text.capitalize()
    return text

def createFile(filename = "metin", isPromptOpen = False):
    file = open(f"{filename}.txt", "r")
    if isPromptOpen == True:
        print("File created successfully.")

def writeFile(text, filename = "metin", isPromptOpen = False):
    file = open(f"{filename}.txt", "w")
    file.write(text)
    file.close()
    if isPromptOpen == True:
        print("Text wrote in file successfully.")

def appendFile(text, filename = "metin", isPromptOpen = False):
    file = open(f"{filename}.txt", "a")
    file.write(f" {text}")
    file.close()
    if isPromptOpen == True:
        print("Text appended in file successfully.")

def readFile(filename = "metin", isPromptOpen = False):
    file = open(f"{filename}.txt", "r")
    file.read()
    file.close()
    if isPromptOpen == True:
        print("Text readed from file successfully.")

def createWavFile(filename, duration = 5, freq = 44100, channels = 2, index = 0):
    freq = 44100
    recording = sd.rec(int(duration* freq), samplerate= freq, channels= channels)
    sd.wait()
    write(f"{filename}{index}.wav", freq, recording)

def process(text):
    #Müzik çalınmaya başladıktan sonra terminal donuyor. Muhtemelen ilgili kütüphanelerden kaynaklı bir durum.
    match text:
        case "Müzik":
            try:
                data, fs = sf.read("muzik.wav", dtype="float32")
                print("Müzik oynatılıyor")
                sd.play(data, fs, loop = True)
            except KeyboardInterrupt:
                parser.exit('Müzik durduruldu.')
            except Exception as e:
                parser.exit(type(e).__name__ + ': ' + str(e))
        
        case 2:
            pass

        case "Çıkış":
            print("İyi günler dilerim.")
            appendFile(text, "metin")
            createWavFile("recording", 5, 44100, 2, 0)
            exit()

#Ters ses hipotezi : Eğer bir devre vasıtasıyla dışarı ortamdan gelen sesi alarak iç ortamda aynı sesin transpose edilmiş halini dışarıya verirsek iki simetrik ses birbirini sönümler. Bu sayede ortam sesi kesilir, asıl kaynağın sesi kalır.

# Görev, robotun aksiyon alırken aksiyonunu bölebilmek

#print(sd.query_devices())
select_microphone(2)#Stereo Mix seçildi

while True:
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration = 0.5)
            print("Sizi dinliyorum...")
            createFile("metin")
            text = listen_Recognize(source, 5)
            
            print(f"Bunu mu söylemek istediniz? {text}.")
            text = listen_Recognize(source, 5)
            print(text)
            
            if text == "Evet":
                print(f"Bunu söylediniz: {text}.")
                file.write(text)
                process(text)       
                    
            elif text == "Hayır":
                print("Diyeceğinizi tekrar söyler misiniz?")

    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))

    except sr.UnknownValueError:
        print("Unknown error occurred!")

    except KeyboardInterrupt:
        print("Mikrofon kapatıldı.")
        """if os.path.exists('output.wav'):
            os.remove('output.wav')"""
        #file.close()
        sys.exit()

    except UnicodeEncodeError:
        print("Türkçe karakter sorunu.")
        
#Büyük boyuttaki ses dosyasını işleyebilmek için parçalara ayıran fonksiyonlar
#Metin dosyasındaki metin ile regex araması