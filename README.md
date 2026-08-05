# Olimora

Olimora; doğum tarihi, saati ve konumundan deterministik natal harita hesaplayan,
sonucu Android uygulamasında gösteren ve isteğe bağlı olarak Athena isimli yapay
zekâ yorumuyla açıklayan açık kaynaklı bir deneme projesidir.

> Astroloji yorumları eğlence ve öz farkındalık amaçlıdır; bilimsel, tıbbi,
> hukuki veya finansal tavsiye değildir.

## Proje yapısı

- `app/`: Python 3.12, FastAPI, PostgreSQL ve Swiss Ephemeris kullanan API
- `android/`: Kotlin ve Jetpack Compose ile yazılmış Android istemcisi
- `tests/`: API, hesaplama ve yorumlama testleri
- `alembic/`: PostgreSQL veritabanı şema geçişleri

## Yerel kurulum

Docker Desktop açıkken PostgreSQL'i başlatın:

```powershell
docker compose up -d postgres
```

Python ortamını hazırlayın ve veritabanını güncelleyin:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\alembic.exe upgrade head
```

`.env.example` dosyasını `.env` adıyla kopyalayın. Athena yorumunu kullanmak
istiyorsanız kendi OpenAI API anahtarınızı yalnızca yerel `.env` dosyasına yazın.
Gerçek anahtarları Git'e eklemeyin.

API'yi başlatın:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger arayüzü: `http://127.0.0.1:8000/docs`

## Kalite kontrolleri

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m mypy app
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider
cd android
.\gradlew.bat testDebugUnitTest assembleDebug
```

## Güvenlik

- `.env`, API anahtarları, veritabanı şifreleri ve Android imzalama anahtarları
  kaynak koduna veya APK içine eklenmemelidir.
- Mobil uygulama OpenAI ile doğrudan konuşmaz; istekler sunucu üzerinden yapılır.
- Deneme sürümü üretim güvenliği için hazırlanmış kabul edilmemelidir.

Güvenlik açığı bulursanız herkese açık issue açmak yerine depo sahibine özel
olarak bildirin.

## Lisans

Bu proje [GNU Affero General Public License v3.0](LICENSE) altında sunulur.
Uygulamayı ağ üzerinden kullanan kişilere karşılık gelen kaynak kodu edinme
imkânı verilmelidir.

Astroloji motorunda kullanılan Swiss Ephemeris ayrıca kendi çift lisans
koşullarına tabidir. Olimora bu aşamada Swiss Ephemeris'in AGPL seçeneğini esas
alır. Kapalı kaynak veya farklı ticari dağıtım için Astrodienst'in profesyonel
lisansı ayrıca değerlendirilmelidir.
