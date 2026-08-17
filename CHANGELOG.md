# Değişiklik günlüğü

## 0.16.0-beta.1 — geliştirme aşamasında

- Süresi sınırlı, tek kullanımlık bağlantılarla e-posta doğrulama altyapısı eklendi.
- Giriş ekranına kullanıcı varlığını ifşa etmeyen “Şifremi unuttum” akışı eklendi.
- Şifre yenileme ve doğrulama anahtarlarının yalnızca geri çevrilemeyen özeti saklanıyor.
- SMTP bilgileri kaynak koda girmeden ortam değişkenleriyle yapılandırılabiliyor.
- Ayarlar ekranına e-posta doğrulama bağlantısı isteme işlemi eklendi.

## 0.15.0-beta.1 — geliştirme aşamasında

- Kullanıcılar Ayarlar içinden mevcut şifrelerini doğrulayarak güvenli biçimde yeni şifre belirleyebiliyor.
- Yeni şifre hem istemcide hem sunucuda güç ve uzunluk kurallarıyla doğrulanıyor.
- Ağ bağlantısı kurulamadığında teknik bağlantı hatası yerine anlaşılır çevrimdışı mesajı gösteriliyor.
- Play Console mağaza metni, Data Safety çalışma belgesi ve kapalı test planı eklendi.

## 0.14.0-beta.1 — geliştirme aşamasında

- Arkadaş ekranına Olimora kodu ve kalıcı indirme bağlantısı içeren davet merkezi eklendi.
- Ayarlar'a uygulama içi fikir, hata ve deneyim geri bildirimi eklendi.
- Geri bildirimler kimliği doğrulanmış ve günlük sınırlandırılmış yeni API ile saklanıyor.
- Kişisel veri içermeyen Firebase Analytics tamamen isteğe bağlı olarak eklendi; varsayılan olarak kapalıdır.
- Gizlilik politikası anonim analitik tercihini açıkça anlatacak şekilde güncellendi.

## 0.13.0-beta.1 — geliştirme aşamasında

- Yorum geçmişi uygulamaya girildiğinde otomatik yükleniyor; kayıtlı günler doğrudan açılıyor.
- Arşivde kaydı olmayan geçmiş günler artık yanıltıcı biçimde “Kilitli” değil, “Yok” olarak gösteriliyor.
- Bugünün kişisel yorumu gün kartından oluşturulabiliyor ve hazır olduğunda aynı karttan açılıyor.
- Yorum arşivi 7 kayıt yerine son 31 kaydı gösterecek şekilde genişletildi.
- Günlük burç yorumu Olimora içinden doğrudan bir arkadaşa veya gruba gönderilebiliyor.
- Grup sohbetlerine her gün değişen, mesaj kutusuna getirilen Athena sohbet fikirleri eklendi.
- Android 7 desteğini bozan tarih API’leri giderildi ve mağaza lint denetimi temizlendi.
- Firebase bildirim kaydı gerçek FCM cihaz anahtarını kullanacak şekilde düzeltildi; anahtar yenilenince sunucu otomatik güncelleniyor.

Bu sürüm henüz GitHub’a veya test kullanıcılarına gönderilmemiş yerel geliştirme sürümüdür.

## 0.12.0-beta.1 — 2026-08-16

- Yorum arşivi, kayıt bulunan gün kartına dokunarak açılacak şekilde sadeleştirildi.
- Arkadaş karşılaştırması sohbet tepesinden kaldırılıp arkadaş işlem menüsüne taşındı.
- Harita karşılaştırması Premium deneyimi olarak konumlandırıldı.
- Kalabalık arkadaş listelerine isim ve rumuz araması eklendi.
- Gizlilik politikası, kullanım/topluluk koşulları ve web hesap silme sayfası eklendi.
- Yeni kayıtlara 13+ yaş ve gizlilik/koşul onayı eklendi.
- Doğrudan ve grup mesajlarına yerel kötüye kullanım ve bağlantı spam denetimi eklendi.
- R8 küçültme, mağaza imzalama şablonu ve Play Store yayın kontrol listesi hazırlandı.

Bu sürüm mağaza öncesi kapalı beta testidir. Gerçek Premium aboneliği ve sunucu
taraflı yetkilendirme ödeme altyapısıyla birlikte etkinleştirilecektir.

## 0.11.0-beta.1 — 2026-08-14

- Arkadaşlar arasında gerçek natal harita uyumluluk analizi eklendi.
- İletişim, duygu, çekim ve istikrar puanları ile önemli açılar gösteriliyor.
- Kullanıcının gerçek adından bağımsız sosyal rumuz belirleme desteği eklendi.
- Mesaj bildirimleri artık mesaj önizlemesini ve gönderen adını gösteriyor.
- Sistem görünümünü izleyen gerçek açık/koyu tema desteği tamamlandı.
- Kullanıcı engelleme, kullanıcı/mesaj şikâyeti ve Athena geri bildirimi eklendi.
- Kişisel günlük yorum arşivi ve favoriler eklendi.
- Güvenlik yanıt başlıkları sıkılaştırıldı.

Bu sürüm hâlâ beta testidir. Astrolojik içerikler eğlence ve öz farkındalık
amaçlıdır; bilimsel, tıbbi, hukuki veya finansal tavsiye değildir.
