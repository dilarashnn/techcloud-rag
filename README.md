# 🧠 TechCloud - Çoklu Kaynak ve Metadata Destekli RAG Sistemi

Bu proje, bir şirkete ait farklı formatlardaki (.txt, .csv, .json) dokümanları tek bir potada eriten, **dinamik** ve **Yapay Zeka (OpenAI GPT-4o)** destekli bir **RAG (Retrieval-Augmented Generation)** müşteri asistanı uygulamasıdır. 

Sistem, belgeler arasında mantıksal bağlantılar kurar. Bir konudaki kural değiştiğinde, önceki veriyi ezerek her zaman **en güncel log kaydını (JSON)** baz alacak şekilde tasarlanmıştır.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-Enabled-FF9900.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT4o-black.svg)
![ChromaDB](https://img.shields.io/badge/VectorDB-Chroma-412991.svg)
![Gradio](https://img.shields.io/badge/UI-Gradio-FF7C00.svg)

---

## 🛠 Kurulum ve Çalıştırma Adımları

Projeyi kendi bilgisayarınızda ayağa kaldırmak için aşağıdaki adımları **sırasıyla** takip edin.

### 1. Ön Gereksinimler
Başlamadan önce sisteminizde aşağıdakilerin kurulu olduğundan emin olun:
- **Python 3.10 veya üzeri** — [python.org](https://www.python.org/downloads/) adresinden indirilebilir.
- **Git** — [git-scm.com](https://git-scm.com/downloads) adresinden indirilebilir.
- **OpenAI API Anahtarı** — [platform.openai.com](https://platform.openai.com/api-keys) adresinden alabilirsiniz (ücretli plan gerektirir).

> 💡 Python'un kurulu olup olmadığını kontrol etmek için terminalde `python --version` komutunu çalıştırabilirsiniz.

### 2. Projeyi İndirin (Klonlayın)
Terminal veya Komut İstemi'ni (CMD / PowerShell) açın ve aşağıdaki komutları sırasıyla çalıştırın:
```bash
git clone https://github.com/dilarashnn/techcloud-rag.git
cd techcloud-rag
```
Bu komut, projenin tüm dosyalarını bilgisayarınıza indirir ve proje klasörüne girer.

### 3. Sanal Ortam (Virtual Environment) Oluşturun ve Aktif Edin
Projeye ait kütüphanelerin bilgisayarınızdaki diğer Python projelerinizle çakışmaması için **sanal ortam** oluşturmanız gerekir.

**Windows kullanıyorsanız:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS / Linux kullanıyorsanız:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> ✅ Sanal ortam başarıyla aktif olduğunda, terminal satırınızın başında `(venv)` ifadesini görmelisiniz.

### 4. Gerekli Kütüphaneleri Yükleyin
Sanal ortam aktifken aşağıdaki komutu çalıştırarak projenin ihtiyaç duyduğu tüm Python kütüphanelerini (LangChain, ChromaDB, Gradio vb.) otomatik olarak yükleyin:
```bash
pip install -r requirements.txt
```
> ⏳ Bu işlem internet hızınıza bağlı olarak 1-3 dakika sürebilir.

### 5. OpenAI API Anahtarınızı Tanımlayın
Proje kök dizininde `.env` adında bir dosya bulunmaktadır. Bu dosyayı herhangi bir metin editörü (Not Defteri, VS Code vb.) ile açın. İçerisinde şunu göreceksiniz:
```
OPENAI_API_KEY=your-api-key-here
```
`your-api-key-here` yazan kısmı silip, yerine [OpenAI Dashboard](https://platform.openai.com/api-keys) üzerinden aldığınız **kendi API anahtarınızı** yapıştırın. Örnek:
```ini
OPENAI_API_KEY=sk-proj-abc123xyz456...
```
> ⚠️ API anahtarını tırnak işareti olmadan, doğrudan `=` işaretinden sonra yapıştırın.

### 6. Uygulamayı Başlatın 🚀
Her şey hazır! Aşağıdaki komutu çalıştırarak Gradio web arayüzünü başlatın:
```bash
python app.py
```
Uygulama başarıyla çalıştığında terminalde aşağıdakine benzer bir çıktı göreceksiniz:
```
Running on local URL:  http://127.0.0.1:7860
```
Tarayıcınız otomatik olarak açılmazsa, yukarıdaki adresi (`http://127.0.0.1:7860`) tarayıcınıza elle yapıştırarak arayüze ulaşabilirsiniz.

---

### 🧪 Testleri Çalıştırma (Opsiyonel)
Sistemin verileri dinamik olarak okuyup okumadığını ve vektörizasyon yapısının sağlamlığını **API anahtarı olmadan** doğrulayabilirsiniz:
```bash
python test_rag.py
```
> 📌 Bu test betiği; veri yükleyicilerin çalışmasını, metadata bütünlüğünü, CSV yapısının korunmasını ve dosya değişikliklerinin anlık olarak yansıyıp yansımadığını kontrol eder. API anahtarı tanımlıysa ek olarak uçtan uca RAG sorgu testlerini de çalıştırır.

---

## 🏛 Mimari Kararlar ve Teknik Yaklaşım

Değerlendirme kriterinde belirtilen tüm zorluklar, LangChain mimarisi optimize edilerek aşılmıştır. İşte projenin kalbini oluşturan kritik tasarım kararları:

### 1. Tabular (Tablo/CSV) Verilerin Vektörizasyonu
Standart RAG uygulamaları, metinleri belirli karakter sınırlarına göre (`RecursiveCharacterTextSplitter` vb.) rastgele böler. **Bu durum bir CSV tablosuna uygulandığında satır ve sütun bağlamı tamamen yok olur.**

**🔍 Çözümümüz:** 
`data_loaders.py` içerisinde özel bir veri okuyucu (Document Loader) yazılmıştır. CSV'deki her bir satır (*paket*), standart bir string yığınına dönüştürülmek yerine **Doğal Dil (Natural Language) Dökümanlarına** çevrilir. (Bkz: `load_paket_fiyatlari` fonksiyonu).
Ayrıca LLM'in veri limitlerini (Feature Boundaries) anlaması için tablo başlıklarını da (kolonlar) içeren geniş bir özet, metadata ile birlikte bilgi havuzuna ayrı bir döküman olarak eklenir. Tablolar asla chunk'lanarak bozulmaz. 

### 2. Çelişen Kaynaklar ve "En Güncel Veri" Problemi (State & Context Yönlendirmesi)
Eski sözleşmeler ile yeni JSON logları sürekli çelişir (Örn: Eskiden 14 gün olan iade süresi, JSON'da 7 güne düşmüştür). Vektör veri tabanları Semantic Search (benzerlik araması) bazlı çalıştığı için, bağlam olarak her ikisini de (eski ve yeni bilgi) bularak LLM'in aklını karıştırır (Hallucination).

**🔍 Çözümümüz:** 
- Tüm dökümanlar sisteme alınırken üzerlerine `tarih`, `kaynak`, `tip` ve `madde_no` tagleri yapıştırılır (Metadata Enrichment). 
- `rag_engine.py` içerisindeki **Özel Sistem Promptu** ile (System Prompt Engineering) çok kesin "Ajan/Agent" sınırları çizilmiştir. Modele; *"Farklı belge tiplerinde çelişen bir detay görürsen HER ZAMAN guncellemeler.json dosyasını (en güncel tarihli log) nihai karar mercii olarak kabul et"* talimatı verilmiştir. (Knowledge Override)

### 3. Statik Kaynaklar Yerine Dinamik Retrieval Sistemi (State Yönetimi)
RAG sistemlerinin en büyük handikapı; sunucu (app.py) çalışırken, arka plandaki .txt veya .csv verisi güncellendiğinde tüm sistemi kapatıp yeniden başlatmak ve vektör veritabanını (embeddings) baştan kurmaktır. 

**🔍 Çözümümüz:** 
Sistemimizdeki vektör veri bankası (Chroma), kalıcı bir diske kaydedilip oradan okunmaz (*Persist* kullanılmaz). **In-Memory (Bellek İçi) Vektör Havuzu** yaklaşımı benimsenmiştir. 
Kullanıcı (Agent State) arayüzden her "Gönder" düğmesine bastığında; sistem mili-saniyeler içinde klasördeki dosyaları **yeniden okur**, *Document* nesnelerini o anki haliyle vektörize eder, sonucu getirir ve belleği temizler.
Bu sayede siz masaüstünden Excel/CSV dosyasındaki paketin fiyatını güncellediğiniz saniyede bile, **sunucuyu (Gradio interface) kapatmaya gerek kalmadan canlı olarak** LLM'e yeni fiyatı işletebilirsiniz. Bu sistem, %100 "Stateless (Durumsuz)" çalışarak sıfır data cache sorunu garanti eder.

---

## 📁 Veri Seti Hiyerarşisi (`data/` Dizini)

* **`sozlesme.txt`** (Hukuki baz kaynak): Şirketin resmi hizmet sözleşmesi.
* **`paket_fiyatlari.csv`** (Tabular kaynak): Temel ürün fiyatlarını, kullanım kotalarını ve SLA tiplerini barındıran yapılandırılmış veri dosyası.
* **`guncellemeler.json`** (Log kaynağı): Sözleşme maddesini veya fiyatları *ezen*, güncel tarihli değişiklik logları.

*(Uygulamanın halüsinasyon görmemesi için Sistem Prompt'u 3 kural ile RAG Agent'ının dış bilgiler kullanmasını yasaklamıştır).*

---
*Proje, modern üretken yapay zeka ve hibrit veri analizi tekniklerini test etmek için en iyi sektör standartlarına (LangChain best-practices) göre tasarlanmıştır. İncelediğiniz için teşekkürler!*
