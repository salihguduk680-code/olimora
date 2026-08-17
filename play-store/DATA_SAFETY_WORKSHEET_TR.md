# Play Console Data Safety çalışma belgesi

Bu belge Play Console formuna cevap verirken kullanılacak teknik çalışma
notudur; yayımlamadan önce Google'ın güncel soru metniyle yeniden doğrulanmalıdır.

## Toplanan veri sınıfları

| Veri | Amaç | Zorunluluk | Aktarım / paylaşım notu |
|---|---|---|---|
| E-posta adresi | Hesap ve giriş | Hesap açmak için gerekli | Railway üzerinde işlenir; satılmaz |
| Kullanıcı kimliği | Hesap, arkadaşlık ve güvenlik | Gerekli | Sunucu içinde kullanılır |
| Doğum tarihi ve saati | Harita hesabı | Harita için gerekli | Athena istenirse gerekli bağlam OpenAI'a gönderilebilir |
| Kullanıcının seçtiği şehir/ilçe ve koordinat | Harita hesabı | Harita için gerekli | GPS'ten gizlice alınmaz; kullanıcı seçer |
| Rumuz ve durum | Sosyal profil | İsteğe bağlı | Arkadaşlara/gruplara gösterilir |
| Özel ve grup mesajları | Mesajlaşma | Sosyal özellik kullanılırsa | Alıcılara iletilir; Athena'ya gönderilmez |
| Cihaz bildirim anahtarı | Bildirim | İsteğe bağlı | Firebase Cloud Messaging ile işlenir |
| Ürün kullanım olayları | Ürün iyileştirme | Tamamen isteğe bağlı | Firebase Analytics; varsayılan kapalı, kişisel alan içermez |
| Geri bildirim ve şikâyet | Destek ve güvenlik | İsteğe bağlı | Yetkili ekip tarafından incelenir |

## Güvenlik ve kullanıcı kontrolü

- Aktarım HTTPS ile şifrelenir.
- Parolalar PBKDF2 ile tuzlanmış özet olarak saklanır.
- Android oturum anahtarı Keystore ile şifrelenir ve yedeklemeye alınmaz.
- Kullanıcı uygulama içinden hesabını ve ilişkili verilerini silebilir.
- Uygulamaya erişemeyen kullanıcı için web hesap silme sayfası vardır.
- Anonim analitik Ayarlar'dan açılıp kapatılabilir.
- Kişisel veriler reklam amacıyla satılmaz veya reklam profili için kullanılmaz.

## Hizmet sağlayıcılar

- Railway: API ve PostgreSQL barındırma
- Firebase Cloud Messaging: bildirim teslimi
- Firebase Analytics: yalnız açık rıza sonrası kişisel alansız ürün olayları
- OpenAI API: yalnız kullanıcı Athena yorumu istediğinde yorum üretimi
