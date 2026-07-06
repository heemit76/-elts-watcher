# Bilkent IELTS Sayfa Takip Botu - Kurulum

Bu bot, GitHub Actions üzerinde ücretsiz çalışır. Kendi bilgisayarının açık
olmasına gerek yoktur.

## 1. GitHub hesabı ve repo oluştur
1. github.com üzerinden ücretsiz bir hesap aç (yoksa).
2. Yeni bir **public** repo oluştur, örn: `ielts-watcher`.
   - Public seçmen önemli: bu sayede GitHub Actions dakikaları tamamen
     ücretsiz ve sınırsız oluyor (5 dakikada bir kontrol için gerekli).
   - Merak etme: e-posta adresin/şifren yine "Secrets" olarak saklanacak,
     repo public olsa bile bunlar kimseye görünmez. Sadece monitor.py ve
     workflow dosyası (yani sitenin nasıl kontrol edildiği) herkese açık
     olur, bu da hassas bir bilgi değil.
3. Bu klasördeki tüm dosyaları (monitor.py, requirements.txt, .github/ klasörü)
   o repoya yükle. (GitHub web arayüzünden "Add file > Upload files" ile
   sürükle-bırak yapabilirsin, .github klasörünü de dahil et.)

## 2. Gmail "Uygulama Şifresi" oluştur
Bildirim göndermek için normal Gmail şifreni KULLANMA, Google artık bunu
engelliyor. Bunun yerine:
1. https://myaccount.google.com/apppasswords adresine git
   (2 adımlı doğrulamanın açık olması gerekir).
2. "Uygulama şifreleri" bölümünden yeni bir şifre oluştur (isim: "IELTS Bot").
3. Sana verilen 16 haneli kodu kopyala (bu, EMAIL_PASSWORD olacak).

Gmail kullanmak istemezsen, Outlook/Yandex gibi başka bir SMTP servisi de
kullanılabilir; sadece monitor.py'deki SMTP_SERVER / SMTP_PORT ortam
değişkenlerini o servise göre ayarlaman gerekir.

## 3. GitHub'da "Secrets" ekle
Repo sayfasında: **Settings > Secrets and variables > Actions > New repository secret**
Şu üç secret'ı ekle:
- `EMAIL_ADDRESS` → bildirim gönderecek Gmail adresin (örn. senin@gmail.com)
- `EMAIL_PASSWORD` → yukarıda oluşturduğun 16 haneli uygulama şifresi
- `TO_EMAIL` → bildirimlerin gideceği adres(ler). İki kişiye birden göndermek
  için aralarına virgül koy, örn: `birinci@gmail.com,ikinci@gmail.com`
  (boşluk fark etmez, script kendisi temizliyor)

## Önemli: Bot ne zaman mail atar?
- Script her 5 dakikada bir sadece **kontrol** eder, siteyi indirip
  önceki haliyle karşılaştırır.
- Sayfa **değişmediyse hiçbir mail gönderilmez** (workflow sessizce biter).
- Sadece sayfa gerçekten değiştiğinde (yeni tarih, yeni duyuru vb.) her iki
  adrese de mail gider.
- İlk çalıştırmada da mail gitmez, sadece referans (mevcut hali) kaydedilir.

## 4. Çalıştır
- Actions sekmesine gidip "IELTS Sayfa Takibi" workflow'unu bul,
  "Run workflow" ile bir kere elle çalıştır. İlk çalıştırma sadece referans
  hash'i kaydeder, bildirim göndermez (bu normal).
- Sonrasında her 15 dakikada bir otomatik çalışacak ve sayfa değiştiğinde
  sana e-posta gönderecek.

## Notlar
- Kontrol sıklığını değiştirmek istersen `.github/workflows/watch.yml`
  içindeki `cron: "*/5 * * * *"` satırını değiştir. 5 dakikanın altına
  inmemeni öneririm; GitHub yoğun saatlerde daha sık istekleri geciktirebilir.
- Sayfa yapısı çok küçük şeyler (tarih/saat, ziyaretçi sayacı gibi) için de
  her seferinde "değişti" diyebilir. Eğer çok fazla gereksiz bildirim
  gelirse, monitor.py içindeki fetch_content() fonksiyonunu sayfanın sadece
  ilgili bölümünü (örn. tarih tablosu) hedefleyecek şekilde daraltabiliriz -
  bunu istersen ben güncelleyebilirim.
