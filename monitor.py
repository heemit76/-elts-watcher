"""
Bilkent IELTS Sayfa Takip Botu
------------------------------
Bu script http://prep.bilkent.edu.tr/en/ielts/ sayfasını kontrol eder,
içerik değiştiyse (yeni tarih/başvuru duyurusu vb.) e-posta ile haber verir.

GitHub Actions üzerinde çalışacak şekilde tasarlandı:
- Her çalıştığında sayfayı indirir
- İçeriğin hash'ini last_hash.txt dosyasıyla karşılaştırır
- Farklıysa: e-posta gönderir ve last_hash.txt'i günceller
- last_hash.txt GitHub Actions tarafından repoya geri commit edilir (workflow dosyasına bakın)
"""

import hashlib
import os
import smtplib
import sys
from email.mime.text import MIMEText

import requests
from bs4 import BeautifulSoup

URL = "http://prep.bilkent.edu.tr/en/ielts/"
HASH_FILE = "last_hash.txt"

# E-posta ayarları ortam değişkenlerinden (GitHub Secrets) okunur
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")      # Gönderen adres (örn. Gmail)
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")    # Gmail "Uygulama Şifresi" (App Password)
TO_EMAIL_RAW = os.environ.get("TO_EMAIL")            # Bildirimin gideceği adres(ler), virgülle ayrılmış olabilir: "a@x.com,b@y.com"
TO_EMAILS = [e.strip() for e in TO_EMAIL_RAW.split(",")] if TO_EMAIL_RAW else []
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))


def fetch_content() -> str:
    """Sayfayı indirir ve sadece ana içerik metnini döndürür (menü/footer gürültüsünü azaltmak için)."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; IELTSWatcher/1.0)"}
    resp = requests.get(URL, headers=headers, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Sadece <main> veya <body> içeriğini al; script/style'ları temizle
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    main = soup.find("main") or soup.find("body")
    text = main.get_text(separator="\n", strip=True) if main else soup.get_text(strip=True)
    return text


def compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_last_hash() -> str | None:
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None


def save_hash(h: str) -> None:
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        f.write(h)


def send_email(subject: str, body: str) -> None:
    if not (EMAIL_ADDRESS and EMAIL_PASSWORD and TO_EMAILS):
        print("E-posta ayarları eksik (EMAIL_ADDRESS / EMAIL_PASSWORD / TO_EMAIL). Bildirim gönderilemedi.")
        return

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = ", ".join(TO_EMAILS)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg, from_addr=EMAIL_ADDRESS, to_addrs=TO_EMAILS)
    print(f"Bildirim e-postası gönderildi: {', '.join(TO_EMAILS)}")


def main() -> None:
    try:
        text = fetch_content()
    except Exception as e:
        print(f"Sayfa alınırken hata oluştu: {e}")
        sys.exit(0)  # workflow'u kırmamak için sessizce çık

    current_hash = compute_hash(text)
    last_hash = load_last_hash()

    if last_hash is None:
        # İlk çalıştırma: sadece referans hash'i kaydet, bildirim gönderme
        print("İlk çalıştırma. Referans hash kaydediliyor, bildirim gönderilmiyor.")
        save_hash(current_hash)
        return

    if current_hash != last_hash:
        print("Değişiklik tespit edildi! E-posta gönderiliyor...")
        snippet = text[:1500]  # e-postaya kısa bir önizleme koy
        body = (
            "Bilkent IELTS sayfasında bir değişiklik tespit edildi.\n\n"
            f"Sayfa: {URL}\n\n"
            "Sayfadaki güncel içerikten bir kesit:\n"
            "----------------------------------------\n"
            f"{snippet}\n"
            "----------------------------------------\n\n"
            "Detaylar için siteyi kontrol et."
        )
        send_email("🔔 Bilkent IELTS Sayfası Güncellendi!", body)
        save_hash(current_hash)
    else:
        print("Değişiklik yok.")


if __name__ == "__main__":
    main()
