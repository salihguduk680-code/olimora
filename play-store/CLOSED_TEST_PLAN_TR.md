# Kapalı test planı

## Test grubu

- En az 12 gönüllü test kullanıcısı
- En az 2 farklı Android üreticisi
- Android 7, 10, 13 ve güncel Android sürümlerinden mümkün olan kombinasyon
- Açık ve koyu tema kullanan cihazlar

## Her testçinin tamamlayacağı akış

1. Yeni hesap aç ve şifre tekrar alanını doğrula.
2. Çıkış yapıp yeniden giriş yap.
3. Türkiye veya Suriye'den doğum yeri seçip harita oluştur.
4. Uygulamayı kapat/aç; kayıtlı haritanın tekrar yorum ürettirmeden açıldığını doğrula.
5. Günlük yorumu iste, geçmişten aç ve favoriye ekle.
6. Arkadaş kodunu paylaş, arkadaşlık kur ve mesaj gönder.
7. Bildirimin doğru uygulama simgesi, gönderen ve mesaj önizlemesiyle geldiğini kontrol et.
8. Grup kur, mesaj gönder ve gruptan ayrıl.
9. Bir kullanıcıyı bildirip engelle.
10. Şifreyi Ayarlar'dan değiştir ve yeni şifreyle giriş yap.
11. İnterneti kapat; anlaşılır hata gösterildiğini ve uygulamanın çökmediğini doğrula.
12. Analitik tercihini açıp kapat ve seçimin korunduğunu doğrula.
13. Hesabı ve ilişkili verileri uygulama içinden sil.

## Geri bildirim kaydı

Her hata için cihaz modeli, Android sürümü, izlenen adımlar, beklenen sonuç,
gerçek sonuç ve mümkünse ekran görüntüsü alınır. Parola, e-posta, doğum tarihi,
mesaj içeriği veya API anahtarı ekran görüntüsüne eklenmez.

## Yayına geçiş ölçütü

- Kayıt, giriş, harita, günlük yorum ve hesap silmede engelleyici hata yok.
- Kritik veya yüksek güvenlik açığı yok.
- Bildirim ve sohbet en az iki fiziksel cihazda doğrulandı.
- Crash-free kullanıcı oranı kapalı test boyunca en az %99.
- Gizlilik, Data Safety ve içerik derecelendirme cevapları kodla uyumlu.
