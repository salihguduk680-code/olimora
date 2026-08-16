# Olimora mağaza yayın kontrol listesi

## Kod ve güvenlik

- [x] HTTPS dışındaki Android trafiği kapalı.
- [x] Oturum anahtarı Android Keystore ile şifreleniyor.
- [x] Android yedekleme kapalı; oturum verisi cihaz yedeğine girmiyor.
- [x] Uygulama içinden hesap ve ilişkili veriler silinebiliyor.
- [x] Uygulamaya erişemeyen kullanıcı için web hesap silme sayfası var.
- [x] Mesaj bildirme, kullanıcı engelleme ve dar kapsamlı içerik/spam filtresi var.
- [x] API anahtarları APK içinde değil, yalnızca sunucuda.
- [ ] Gerçek yükleme anahtarı oluştur; `android/keystore.properties` dosyasını Git'e ekleme.
- [ ] Railway üretim ortamında `APP_ENV=production`, güçlü `AUTH_SECRET` ve tek güncel OpenAI anahtarı kullan.
- [ ] Üretim veritabanının otomatik yedeğini ve geri yükleme denemesini yapılandır.

## Play Console

- [ ] Kalıcı destek/gizlilik e-postası belirle. GitHub Issues tek başına mağaza desteği için yeterli değildir.
- [ ] Gizlilik politikası: `https://olimora-production.up.railway.app/privacy`
- [ ] Hesap silme: `https://olimora-production.up.railway.app/account-deletion`
- [ ] Kullanım/topluluk koşulları: `https://olimora-production.up.railway.app/terms`
- [ ] Data Safety formunda e-posta, kullanıcı kimliği, kullanıcı içeriği/mesajlar, doğum bilgileri ve kullanıcı tarafından seçilen konum verisini doğru beyan et.
- [ ] Railway, Firebase Cloud Messaging ve OpenAI'ı hizmet sağlayıcı olarak beyan et.
- [ ] İçerik derecelendirmesi, 13+ hedef kitle, reklam içermediği ve astrolojinin eğlence amaçlı olduğu bilgilerini doldur.
- [ ] Uygulama simgesi, telefon ekran görüntüleri, özellik görseli ve Türkçe kısa/uzun açıklama hazırla.
- [ ] AAB üret, Play App Signing'i etkinleştir ve önce kapalı test kanalına yükle.
- [ ] En az iki farklı fiziksel cihazda kayıt, giriş, hesap silme, bildirim, sohbet, engelleme/bildirme ve koyu tema testini tamamla.

## Yayın engelleri

1. Kalıcı destek/gizlilik e-postası henüz belirlenmedi.
2. Parola sıfırlama ve e-posta doğrulama henüz yok; mağaza için mutlak engel değildir fakat genel kullanıma açılmadan önerilir.
3. Moderasyon taleplerine kim tarafından ve kaç saat içinde cevap verileceği belirlenmeli.
4. Uygulamanın koşulları ve gizlilik metni gerçek yayından önce hukuki incelemeden geçirilmeli.
