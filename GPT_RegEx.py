import re
import string
from itertools import chain


#Fikirler
"""
*Bir otel json dosyası ve komut json dosyası düşün. Kullanıcı bir komut söylediğinde komut
dosyasındaki bir komuta erişilip aktive edilecek.

*Kullanıcı, robot ile sohbet sırasında konuştuğu şeylerden elimizde bulunan anahtar kelimeler eğer konuşma
içindeki bir cümlede geçiyorsa o cümleyi tamamiyle alıp tutabiliriz. Bu sayede ilerdeki sohbetlerde bu
verileri kullanarak müşteri memnuniyetini arttırabiliriz.

*Bu tuttuğumuz cümlelerden yüzde 50'si dahi işe yarar veriler içerse yine de bize avantaj sağlar.
"""

#Bazı örnek textler
text = """Merhaba. ben Ahmet Bitik. 25 yaşındayım. İnşaat ustasıyım. Ankara'da oturuyorum. Doğum tarihim 05.04.2002"""
text2= """Selam, bana Akif Taşlı derler. Yaşım 22. İşçiyim. Tokat'da yaşıyorum. Doğum tarihim 09.11.2001"""
text3= """Selam, ben Doktor Veysel. Yaşım 35. İşçiyim. Malatya'da yaşıyorum. Doğum tarihim 04.1989"""
text4 = """Selam, ben Akman. Yaşım 58'dir. İşçiyim. Erzurum'da yaşıyorum. Doğum tarihim 06.08.1966"""
text5 = """Selam, ben Hasan. 63 yaşındayım. İşçiyim. Çanakkale'da yaşıyorum. Doğum tarihim 2.10.1961. Yani 2 Ekim 1961 doğumluyum."""
sample_text ="""Merhaba, ben Mehmet Kaya. 2015 yılında Sakarya Üniversitesi İnsan Kaynakları Yönetimi Bölümü’nden mezun oldum. 
Üniversite eğitimim boyunca Migros ve n11.com başta olmak üzere birçok kurumda staj yaptım. 
Stajyer pozisyonunda görev aldığım kurumlarda insan kaynakları planlaması, işe alım süreçleri ve bordrolama alanlarını öğrendim."""

#Text listesi
texts = [text,text2, text3, text4, text5] # Ne zaman mikrofondan ses alınırsa bir metin değişkenine kaydedilip onu texts listesine eklenilecek.


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

isimAyiklama() #Çalışıyor
print("\n")
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

yasAyiklama() #Çalışıyor
print("\n")

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

sehirAyiklama() # Çalışıyor
print("\n")
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
tarihAyiklama()
print("\n")
#<----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------->

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
