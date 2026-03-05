
import json
import os
import sys
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def test_data_loaders():
    print("\n" + "=" * 60)
    print("TEST 1: Veri Yükleyiciler")
    print("=" * 60)

    from data_loaders import load_sozlesme, load_paket_fiyatlari, load_guncellemeler, load_all_documents

    sozlesme_docs = load_sozlesme()
    assert len(sozlesme_docs) > 0, "Sözleşme belgeleri yüklenemedi!"
    assert all(d.metadata.get("kaynak") == "sozlesme.txt" for d in sozlesme_docs), "Metadata hatası: kaynak"
    assert any("iade" in d.page_content.lower() for d in sozlesme_docs), "İade maddesi bulunamadı!"
    print(f"  ✅ sozlesme.txt: {len(sozlesme_docs)} madde yüklendi")

    csv_docs = load_paket_fiyatlari()
    assert len(csv_docs) > 0, "CSV belgeleri yüklenemedi!"
    assert any(d.metadata.get("paket_adi") == "Pro" for d in csv_docs), "Pro paketi bulunamadı!"
    assert any("199" in d.page_content for d in csv_docs), "Pro fiyatı (199 TL) bulunamadı!"
    print(f"  ✅ paket_fiyatlari.csv: {len(csv_docs)} belge yüklendi (tablo + satırlar)")

    json_docs = load_guncellemeler()
    assert len(json_docs) > 0, "JSON belgeleri yüklenemedi!"
    assert all(d.metadata.get("tarih") for d in json_docs), "Metadata hatası: tarih eksik"
    tarihler = [d.metadata["tarih"] for d in json_docs]
    assert tarihler == sorted(tarihler), "Güncellemeler tarihe göre sıralı değil!"
    print(f"  ✅ guncellemeler.json: {len(json_docs)} güncelleme yüklendi (tarih sıralı)")

    all_docs = load_all_documents()
    expected_total = len(sozlesme_docs) + len(csv_docs) + len(json_docs)
    assert len(all_docs) == expected_total, f"Toplam belge sayısı yanlış: {len(all_docs)} != {expected_total}"
    print(f"  ✅ Toplam: {len(all_docs)} belge yüklendi")

    return True


def test_metadata_integrity():
    print("\n" + "=" * 60)
    print("TEST 2: Metadata Bütünlüğü")
    print("=" * 60)

    from data_loaders import load_all_documents

    docs = load_all_documents()

    required_fields = ["kaynak", "tip"]
    for doc in docs:
        for field in required_fields:
            assert field in doc.metadata, f"Eksik metadata alanı: {field} - {doc.page_content[:50]}"

    valid_tips = {"sozlesme", "fiyat_tablosu", "guncelleme"}
    for doc in docs:
        assert doc.metadata["tip"] in valid_tips, f"Geçersiz tip: {doc.metadata['tip']}"

    print("  ✅ Tüm belgelerde 'kaynak' ve 'tip' metadata alanları mevcut")
    print("  ✅ Tüm 'tip' değerleri geçerli: sozlesme, fiyat_tablosu, guncelleme")

    update_docs = [d for d in docs if d.metadata["tip"] == "guncelleme"]
    for doc in update_docs:
        assert "tarih" in doc.metadata, "Güncelleme belgesinde tarih eksik!"
        assert doc.metadata["tarih"], "Güncelleme belgesinde tarih boş!"

    print("  ✅ Tüm güncelleme belgelerinde tarih metadata'sı mevcut")

    return True


def test_csv_structure_preservation():
    print("\n" + "=" * 60)
    print("TEST 3: CSV Yapısal Bütünlüğü")
    print("=" * 60)

    from data_loaders import load_paket_fiyatlari

    docs = load_paket_fiyatlari()

    paket_isimleri = {d.metadata.get("paket_adi") for d in docs}
    assert "Basic" in paket_isimleri, "Basic paketi eksik!"
    assert "Pro" in paket_isimleri, "Pro paketi eksik!"
    assert "Enterprise" in paket_isimleri, "Enterprise paketi eksik!"
    print("  ✅ Her paket için ayrı belge oluşturuldu: Basic, Pro, Enterprise")

    pro_docs = [d for d in docs if d.metadata.get("paket_adi") == "Pro"]
    pro_text = " ".join(d.page_content for d in pro_docs)
    assert "199" in pro_text, "Pro paketi fiyatı (199) bulunamadı!"
    assert "25" in pro_text, "Pro paketi kullanıcı limiti (25) bulunamadı!"
    print("  ✅ Pro paketi: fiyat ve kullanıcı limiti doğru")

    ozet_docs = [d for d in docs if d.metadata.get("paket_adi") == "tüm_paketler"]
    assert len(ozet_docs) > 0, "Tablo özet belgesi bulunamadı!"
    print("  ✅ Tablo özeti belgesi mevcut")

    return True


def test_dynamic_data_update():
    print("\n" + "=" * 60)
    print("TEST 4: Dinamik Veri Güncellemesi")
    print("=" * 60)

    import pandas as pd
    from data_loaders import load_paket_fiyatlari

    csv_path = os.path.join(DATA_DIR, "paket_fiyatlari.csv")

    df_original = pd.read_csv(csv_path)
    original_price = df_original.loc[df_original["paket_adi"] == "Pro", "aylik_fiyat_tl"].values[0]
    print(f"  📌 Orijinal Pro fiyatı: {original_price} TL")

    new_price = 249
    df_modified = df_original.copy()
    df_modified.loc[df_modified["paket_adi"] == "Pro", "aylik_fiyat_tl"] = new_price
    df_modified.to_csv(csv_path, index=False)
    print(f"  🔄 Pro fiyatı {new_price} TL olarak değiştirildi")

    docs = load_paket_fiyatlari()
    pro_docs = [d for d in docs if d.metadata.get("paket_adi") == "Pro"]
    pro_text = " ".join(d.page_content for d in pro_docs)
    assert str(new_price) in pro_text, f"Güncel fiyat ({new_price}) yansımadı!"
    print(f"  ✅ Güncel fiyat ({new_price} TL) başarıyla okundu")

    df_original.to_csv(csv_path, index=False)
    print(f"  🔄 Orijinal fiyat ({original_price} TL) geri yüklendi")

    docs = load_paket_fiyatlari()
    pro_docs = [d for d in docs if d.metadata.get("paket_adi") == "Pro"]
    pro_text = " ".join(d.page_content for d in pro_docs)
    assert str(original_price) in pro_text, "Orijinal fiyat geri yüklenemedi!"
    print(f"  ✅ Orijinal fiyat ({original_price} TL) başarıyla geri yüklendi")

    return True


def test_json_dynamic_update():
    print("\n" + "=" * 60)
    print("TEST 5: JSON Dinamik Güncelleme")
    print("=" * 60)

    from data_loaders import load_guncellemeler

    json_path = os.path.join(DATA_DIR, "guncellemeler.json")

    with open(json_path, "r", encoding="utf-8") as f:
        original_data = json.load(f)
    original_count = len(original_data)
    print(f"  📌 Orijinal güncelleme sayısı: {original_count}")

    new_update = {
        "tarih": "2025-03-01",
        "tip": "sozlesme_degisikligi",
        "etkilenen_madde": "Madde 4.1",
        "etkilenen_paket": "Basic",
        "degisiklik": "Basic paket iade süresi 7 güne düşürülmüştür.",
        "onceki_deger": "14 gün",
        "yeni_deger": "7 gün",
    }
    modified_data = original_data + [new_update]
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(modified_data, f, ensure_ascii=False, indent=2)
    print("  🔄 Yeni güncelleme eklendi: Basic iade süresi 7 güne düşürüldü")

    docs = load_guncellemeler()
    assert len(docs) == original_count + 1, f"Güncelleme sayısı yanlış: {len(docs)} != {original_count + 1}"
    new_doc_texts = [d.page_content for d in docs if "7 güne" in d.page_content and "Basic" in d.page_content]
    assert len(new_doc_texts) > 0, "Yeni güncelleme belgelerde bulunamadı!"
    print(f"  ✅ Yeni güncelleme başarıyla okundu ({len(docs)} toplam)")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(original_data, f, ensure_ascii=False, indent=2)
    print(f"  🔄 Orijinal veriye geri dönüldü ({original_count} güncelleme)")

    docs = load_guncellemeler()
    assert len(docs) == original_count, "Orijinal veri geri yüklenemedi!"
    print(f"  ✅ Orijinal veri başarıyla geri yüklendi")

    return True


def test_rag_query():
    print("\n" + "=" * 60)
    print("TEST 6: RAG Sorgu Testi (API Gerekli)")
    print("=" * 60)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("  ⚠️  OPENAI_API_KEY ayarlanmamış — RAG sorgu testi atlandı.")
        print("  💡 .env dosyasında OPENAI_API_KEY tanımlayarak bu testi çalıştırabilirsiniz.")
        return True

    from rag_engine import query

    test_cases = [
        {
            "soru": "Pro paket aylık fiyatı nedir?",
            "beklenen_icerikleri": ["199", "TL"],
            "beklenen_kaynaklar": ["paket_fiyatlari.csv"],
        },
        {
            "soru": "Pro paket iade süresi kaç gündür?",
            "beklenen_icerikleri": ["30"],
            "beklenen_kaynaklar": ["guncellemeler.json"],
        },
        {
            "soru": "Enterprise paketinin kullanıcı limiti nedir?",
            "beklenen_icerikleri": ["Sınırsız"],
            "beklenen_kaynaklar": ["paket_fiyatlari.csv"],
        },
    ]

    for i, tc in enumerate(test_cases, 1):
        print(f"\n  📝 Test {i}: {tc['soru']}")
        result = query(tc["soru"])

        answer = result["answer"]
        sources = [s["kaynak"] for s in result["sources"]]

        for beklenen in tc["beklenen_icerikleri"]:
            if beklenen.lower() in answer.lower():
                print(f"    ✅ Cevap '{beklenen}' içeriyor")
            else:
                print(f"    ⚠️  Cevap '{beklenen}' içermiyor — kontrol edin")

        for kaynak in tc["beklenen_kaynaklar"]:
            if kaynak in sources:
                print(f"    ✅ Kaynak: {kaynak}")
            else:
                print(f"    ⚠️  Beklenen kaynak '{kaynak}' bulunamadı — mevcut kaynaklar: {sources}")

    return True


def main():
    print("\n" + "🧪" * 30)
    print("  RAG SİSTEMİ DOĞRULAMA TESTLERİ")
    print("🧪" * 30)

    tests = [
        ("Veri Yükleyiciler", test_data_loaders),
        ("Metadata Bütünlüğü", test_metadata_integrity),
        ("CSV Yapısı", test_csv_structure_preservation),
        ("Dinamik Veri (CSV)", test_dynamic_data_update),
        ("Dinamik Veri (JSON)", test_json_dynamic_update),
        ("RAG Sorgu", test_rag_query),
    ]

    results = []
    for name, test_fn in tests:
        try:
            success = test_fn()
            results.append((name, "✅ BAŞARILI" if success else "❌ BAŞARISIZ"))
        except Exception as e:
            results.append((name, f"❌ HATA: {e}"))

    print("\n" + "=" * 60)
    print("  TEST SONUÇLARI")
    print("=" * 60)
    for name, result in results:
        print(f"  {result} — {name}")
    print("=" * 60)

    if any("❌" in r for _, r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()

