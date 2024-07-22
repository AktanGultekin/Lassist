import re
import string
from itertools import chain
import speech_recognition as sr
import pyttsx3
import numpy as np
import os
import scipy.io.wavfile as wavfile
import matplotlib.pyplot as plt

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

r = sr.Recognizer()

r.pause_threshold = 0.75
frequency_list = []

def speakTest(command):
    engine = pyttsx3.init()
    engine.say(command)
    engine.runAndWait()

def createTextFile(name):
    file = open(f"{name}.txt", "w")

def saveSentence(source):
    file.write(source)

def closeTextFile(name):
    pass

class   index:
    i = 0

#Ters ses hipotezi : Eğer bir devre vasıtasıyla dışarı ortamdan gelen sesi alarak iç ortamda aynı sesin transpose edilmiş halini dışarıya verirsek iki simetrik ses birbirini sönümler. Bu sayede ortam sesi kesilir, asıl kaynağın sesi kalır.

while(True):
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration = 0.5)
            #r.dynamic_energy_threshold = True 
            print("Sizi dinliyorum...")
            file = open("metin.txt", "w")
            audio = r.listen(source, phrase_time_limit= 5)
            metin = r.recognize_google(audio, language = "tr-TR", show_all = False)
            metin = metin.capitalize()

            print(f"Bunu mu söylemek istediniz? {metin}.")
            cevap = r.listen(source, phrase_time_limit= 5)
            cevap_metin = r.recognize_google(cevap, language = "tr-TR")
            cevap_metin = cevap_metin.capitalize()
            print(cevap_metin)
            
            if len(metin)>0 and cevap_metin == "Evet":
                print(f"Bunu söylediniz: {metin}.")
                file.write(metin)
                speakTest(metin)
                print("Konuşmaya devam etmek ister misiniz?")
                cevap = r.listen(source, phrase_time_limit= 5)
                cevap_metin = r.recognize_google(cevap, language= "tr-TR")
                cevap_metin = cevap_metin.capitalize()
                print(cevap_metin)
                if len(metin)>0 and cevap_metin == "Evet":
                    continue
                elif cevap_metin == "Hayır":
                    print("Konuşmadan çıkıyorsunuz...")
                    speakTest(metin)
                    with open(f"microphone-results({index.i}).wav", "wb") as f: #Ses dosyası oluşturma
                        f.write(audio.get_wav_data())

                        sample_rate, data = wavfile.read(f"microphone-results({index.i}).wav")

                        # Eğer stereo ise mono'ya çevir
                        if len(data.shape) == 2:
                            data = np.mean(data, axis=1)

                        # Fourier dönüşümü ile frekans spektrumunu hesapla
                        frequencies = np.fft.rfftfreq(len(data), 1/sample_rate)
                        spectrum = np.abs(np.fft.rfft(data))

                        # Maksimum frekansı bul
                        max_freq_index = np.argmax(spectrum)
                        max_freq = frequencies[max_freq_index]

                        if max_freq>0 and max_freq<160:
                            print("Ses kaynağı sol tarafta. Robot, konuşan bir yüz görene kadar sola doğru dön.")
                        elif max_freq>=160:
                            print("Ses kaynağı sağ tarafta. Robot konuşan bir yüz görene kadar sağa doğru dön.")
                        #soldan 128
                        #sağdan 247
                        """
                        Fs, aud = wavfile.read(f"microphone-results({index.i}).wav")
                        first = aud[:int(Fs*125)]
                        powerSpectrum, frequenciesFound, time, imageAxis = plt.specgram(first, Fs=Fs)
                        plt.xlabel('Time(s)')
                        plt.ylabel('Frequency(Hz)')
                        plt.show()
                        """
                        index.i = index.i + 1
                        
                    #file.write(metin)
                    file.close()
                    break
            
            elif cevap_metin == "Hayır":
                continue

        

        """with open(f"microphone-results({index.i}).wav", "wb") as f: #Ses dosyası oluşturma
            f.write(audio.get_wav_data())     """ 
            
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))

    except sr.UnknownValueError:
        print("Unknown error occurred!")

    except KeyboardInterrupt:
        print("Mikrofon kapatıldı.")
        #os.remove("metin.txt")
        #file.close()
        exit()

    except UnicodeEncodeError:
        continue

"""
def transcribe_audio(path):
    with sr.AudioFile(path) as source:
        audio_listened = r.record(source)
        text = r.recognize_google(audio_listened, language = "en-US")
    return text

def get_large_audio_transcription_on_silence(path):
    # open the audio file using pydub
    sound = AudioSegment.from_file(path)  
    # split audio sound where silence is 500 miliseconds or more and get chunks
    chunks = split_on_silence(sound,
        # experiment with this value for your target audio file
        min_silence_len = 500,
        # adjust this per requirement
        silence_thresh = sound.dBFS-14,
        # keep the silence for 1 second, adjustable as well
        keep_silence=500,
    )
    folder_name = "audio-chunks"
    # create a directory to store the audio chunks
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    # process each chunk 
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        try:
            text = transcribe_audio(chunk_filename)
        except sr.UnknownValueError as e:
            print("Error:", str(e))
        else:
            text = f"{text.capitalize()}. "
            print(chunk_filename, ":", text)
            whole_text += text
    return whole_text

path = "7601-291468-0006.wav"
print("\nFull text:", get_large_audio_transcription_on_silence(path))
"""




#Metin dosyasındaki metin ile regex araması



























"""
x = re.findall(adPatterns[3], text)
print(x) # Slicing yöntemi "Ben John Doe" kalıbıyla verildiği için 4: olarak kullanıldı.
x[0] = x[0][4:]
print(x[0])

print("\n")

x= re.findall(yas, text)
print(x)
yas = x[0] # Yaş verisi listeden çıkarıldı.
yas = yas.split() # Veri, içerdiği boşluk karakteriyle ayrıldı. Bu sayede yaş verisi salt haliyle elde edildi.
print(yas) #Kümede gözüken hali
yas = yas[0]#yas degiskenine yas verisi verildi.
print(yas)#Yaşa ulaşıldı.

print("\n")

x = re.findall(yasadigiYer, text)
il = x[0]
sehir = il[0]
print(sehir)
ikametgah, b= sehir.split("'")
print(ikametgah)

print("\n")

x = re.findall(tarih, text)
print(x)
dogumTarihi = x[0] #Doğum tarihi verisinin kümede gözüken hali
print(dogumTarihi)#Doğum Tarihine ulaşıldı.

print("\n")

print("Konuşmadaki kişinin ismi ve soyismi: {}, yaşı: {},\nyaşadığı yer: {}, doğum tarihi: {} ".format(isimSoyisim, yas, yasadigiYer, dogumTarihi))"""
