# ruff: noqa: E501

from html import escape

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

_STYLE = """
body{font-family:system-ui,-apple-system,sans-serif;max-width:760px;margin:0 auto;padding:32px 20px;line-height:1.65;color:#241b2d;background:#fbf8ff}
h1,h2{line-height:1.25}a{color:#7540aa}.card{background:#fff;border:1px solid #e4d9ec;border-radius:18px;padding:20px;margin:18px 0}
input,button{font:inherit;width:100%;box-sizing:border-box;padding:12px;margin:7px 0;border-radius:10px;border:1px solid #cdbddd}button{background:#7540aa;color:white;border:0;font-weight:600;cursor:pointer}.muted{color:#695d70;font-size:.92rem}
"""
_SUPPORT = "https://github.com/salihguduk680-code/olimora/issues"


def _page(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(
        "<!doctype html><html lang='tr'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<title>{escape(title)} · Olimora</title><style>{_STYLE}</style></head>"
        f"<body><p>✦ OLIMORA</p><h1>{escape(title)}</h1>{body}"
        f"<p class='muted'>Son güncelleme: 17 Ağustos 2026 · <a href='{_SUPPORT}'>Destek</a></p>"
        "</body></html>"
    )


@router.get("/privacy", response_class=HTMLResponse)
async def privacy_policy() -> HTMLResponse:
    return _page(
        "Gizlilik Politikası",
        """
<div class='card'><h2>Topladığımız veriler</h2><p>Hesap için e-posta adresi ve parola özeti; harita için ad veya rumuz, doğum tarihi, saat, şehir/ilçe ve bunlardan hesaplanan astrolojik yerleşimler saklanır. Sosyal özellikleri kullanırsan arkadaşlıklar, grup üyelikleri, mesajlar, durum ve bildirim cihaz kimliği saklanır.</p></div>
<h2>Nasıl kullanıyoruz?</h2><p>Veriler yalnızca hesabı çalıştırmak, doğum haritasını hesaplamak, istediğin yorumları üretmek, mesajları iletmek, kötüye kullanımı önlemek ve bildirim göndermek için kullanılır. Reklam profili oluşturmayız ve kişisel verileri satmayız.</p>
<h2>Yapay zekâ</h2><p>Athena yorumu istediğinde astroloji motorunun sonuçları ile doğum profilindeki gerekli bilgiler OpenAI API hizmetine gönderilebilir. Arkadaş mesajları ve grup sohbetleri Athena yorumuna gönderilmez.</p>
<h2>Hizmet sağlayıcılar</h2><p>Sunucu ve veritabanı için Railway, bildirimler için Firebase Cloud Messaging, isteğe bağlı Athena yorumları için OpenAI kullanılır. Ayarlardan açıkça izin verirsen Firebase Analytics yalnızca özellik kullanım olaylarını toplar; isim, e-posta, doğum bilgisi, konum, mesaj içeriği veya arkadaş kimliği analitiğe gönderilmez. Analitik iznini istediğin zaman kapatabilirsin. Bu sağlayıcılar veriyi kendi güvenlik ve gizlilik koşulları kapsamında işler.</p>
<h2>Saklama ve silme</h2><p>Hesabın açık olduğu sürece gerekli kayıtlar saklanır. Ayarlar → Hesabımı ve verilerimi sil yoluyla veya hesap silme sayfasından hesabını ve ilişkili verileri kalıcı olarak silebilirsin. Güvenlik ve yasal yükümlülükler nedeniyle sınırlı kayıtlar zorunlu süre boyunca tutulabilir.</p>
<h2>Çocukların gizliliği</h2><p>Olimora 13 yaşın altındaki kişiler için tasarlanmamıştır. 13 yaşın altında olduğunu öğrendiğimiz bir hesabı ve ilişkili verileri sileriz.</p>
<h2>İletişim</h2><p>Gizlilik veya veri talebi için <a href='https://github.com/salihguduk680-code/olimora/issues'>destek kanalımıza</a> ulaşabilirsin.</p>
""",
    )


@router.get("/terms", response_class=HTMLResponse)
async def terms_of_use() -> HTMLResponse:
    return _page(
        "Kullanım ve Topluluk Koşulları",
        """
<p>Olimora'yı kullanarak bu koşulları kabul edersin. Uygulama 13 yaş ve üzeri kullanıcılar içindir.</p>
<h2>Astroloji içeriği</h2><p>Haritalar ve Athena yorumları eğlence ve öz farkındalık amaçlıdır; bilimsel gerçek, sağlık, hukuk, güvenlik veya yatırım tavsiyesi değildir. Önemli kararlarını yalnızca bu içeriklere dayandırma.</p>
<h2>Topluluk kuralları</h2><p>Tehdit, taciz, nefret, zorbalık, dolandırıcılık, spam, kişisel bilgileri izinsiz paylaşma, çocukların cinsel istismarı veya hukuka aykırı içerik yasaktır. İçerikler sınırlı otomatik kontrollerden geçebilir; kullanıcılar mesajı bildirebilir ve kişileri engelleyebilir.</p>
<h2>Uygulama</h2><p>Kuralları ihlal eden içerikleri kaldırabilir, özellikleri sınırlandırabilir veya hesabı kapatabiliriz. Beta özellikleri değişebilir ya da kaldırılabilir.</p>
<h2>Açık kaynak</h2><p>Kaynak kodu AGPL-3.0 altında yayımlanır. Swiss Ephemeris bileşeni ayrıca kendi lisans koşullarına tabidir.</p>
""",
    )


@router.get("/account-deletion", response_class=HTMLResponse)
async def account_deletion_page() -> HTMLResponse:
    return _page(
        "Olimora hesabını sil",
        """
<p>En kolay yol uygulamada <strong>Ayarlar → Hesabımı ve verilerimi sil</strong> seçeneğidir. Uygulamaya erişemiyorsan aşağıdaki formu kullanabilirsin.</p>
<div class='card'><form id='delete-form'><label>E-posta</label><input id='email' type='email' autocomplete='email' required><label>Şifre</label><input id='password' type='password' autocomplete='current-password' minlength='8' required><button type='submit'>Hesabımı ve verilerimi kalıcı olarak sil</button><p id='result' class='muted'></p></form></div>
<script>
document.getElementById('delete-form').addEventListener('submit', async (event) => {
 event.preventDefault();
 if (!confirm('Hesabın ve ilişkili verilerin kalıcı olarak silinecek. Devam edilsin mi?')) return;
 const result=document.getElementById('result'); result.textContent='İşlem yapılıyor…';
 const response=await fetch('/api/v1/auth/delete-account',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:document.getElementById('email').value,password:document.getElementById('password').value})});
 result.textContent=response.ok?'Hesabın ve ilişkili verilerin silindi.':(await response.json()).detail||'Hesap silinemedi.';
 if(response.ok) document.getElementById('delete-form').reset();
});
</script>
""",
    )


@router.get("/verify-email", response_class=HTMLResponse)
async def verify_email_page() -> HTMLResponse:
    return _page(
        "E-posta adresini doğrula",
        """
<div class='card'><p id='result'>Bağlantı doğrulanıyor…</p></div>
<script>
(async () => {
 const token=new URLSearchParams(location.search).get('token');
 const result=document.getElementById('result');
 if(!token){result.textContent='Doğrulama bağlantısı eksik.';return;}
 const response=await fetch('/api/v1/auth/verify-email',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token})});
 result.textContent=response.ok?'E-posta adresin doğrulandı. Artık Olimora uygulamasına dönebilirsin.':((await response.json()).detail||'Bağlantı doğrulanamadı.');
})();
</script>
""",
    )


@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page() -> HTMLResponse:
    return _page(
        "Yeni şifre belirle",
        """
<div class='card'><form id='reset-form'><label>Yeni şifre</label><input id='password' type='password' autocomplete='new-password' minlength='10' required><label>Yeni şifre tekrar</label><input id='confirmation' type='password' autocomplete='new-password' minlength='10' required><button type='submit'>Şifremi yenile</button><p id='result' class='muted'>En az 10 karakter, bir harf ve bir rakam kullan.</p></form></div>
<script>
document.getElementById('reset-form').addEventListener('submit',async(event)=>{
 event.preventDefault(); const result=document.getElementById('result');
 const token=new URLSearchParams(location.search).get('token');
 const password=document.getElementById('password').value;
 if(!token){result.textContent='Şifre yenileme bağlantısı eksik.';return;}
 if(password!==document.getElementById('confirmation').value){result.textContent='Şifreler eşleşmiyor.';return;}
 if(password.length<10||!/[A-Za-zÇĞİÖŞÜçğıöşü]/.test(password)||!/[0-9]/.test(password)){result.textContent='Şifre en az 10 karakter, bir harf ve bir rakam içermeli.';return;}
 result.textContent='Şifre güncelleniyor…';
 const response=await fetch('/api/v1/auth/reset-password',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token,new_password:password})});
 result.textContent=response.ok?'Şifren güncellendi. Artık uygulamadan giriş yapabilirsin.':((await response.json()).detail||'Şifre güncellenemedi.');
 if(response.ok) document.getElementById('reset-form').reset();
});
</script>
""",
    )
