# Olimora iOS yolu

Android arayüzü iPhone'da doğrudan çalışmaz; mevcut Python/FastAPI sunucusu ve PostgreSQL veritabanı ise aynen kullanılabilir. En sağlam yol aynı API'ye bağlanan yerel bir **SwiftUI** istemcisidir.

## Önerilen sıra

1. Android sürümünü kapalı testte kararlı hale getir ve API sözleşmesini sabitle.
2. Mac + Xcode ve Apple Developer üyeliğini hazırla.
3. SwiftUI uygulamasında kayıt/giriş, profil, doğum haritası, Athena ve sosyal ekranlarını mevcut REST API ile kur.
4. Oturum anahtarını Keychain'de sakla; Firebase/APNs bildirimlerini bağla.
5. Hesap silme, bildirme/engelleme, gizlilik ve koşullar bağlantılarını Android ile aynı davranışta tut.
6. TestFlight ile arkadaş testine aç, ardından App Store incelemesine gönder.

PWA veya basit WebView daha hızlı görünse de uygulama yeterince yerel işlev sunmazsa App Store'un minimum işlevsellik incelemesinde risk oluşturur. Bu nedenle gerçek yayın için SwiftUI önerilir.
