
import os
import re
import json
import pandas as pd
from langchain_core.documents import Document

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def load_sozlesme() -> list[Document]:
    filepath = os.path.join(DATA_DIR, "sozlesme.txt")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    sections = re.split(r"(?=Madde \d+)", content)

    documents = []
    for section in sections:
        section = section.strip()
        if not section:
            continue

        madde_match = re.match(r"Madde (\d+)", section)
        madde_no = madde_match.group(0) if madde_match else "Başlık"

        alt_maddeler = re.findall(r"(\d+\.\d+):", section)

        doc = Document(
            page_content=section,
            metadata={
                "kaynak": "sozlesme.txt",
                "tip": "sozlesme",
                "madde_no": madde_no,
                "alt_maddeler": ", ".join(alt_maddeler) if alt_maddeler else "",
                "dosya_yolu": filepath,
            },
        )
        documents.append(doc)

    return documents


def load_paket_fiyatlari() -> list[Document]:
    filepath = os.path.join(DATA_DIR, "paket_fiyatlari.csv")
    df = pd.read_csv(filepath)

    documents = []

    tablo_ozeti = "PAKET FİYATLARI TABLOSU\n"
    tablo_ozeti += "=" * 40 + "\n"
    tablo_ozeti += f"Mevcut paketler: {', '.join(df['paket_adi'].tolist())}\n"
    tablo_ozeti += f"Sütunlar: {', '.join(df.columns.tolist())}\n\n"
    tablo_ozeti += df.to_string(index=False)

    documents.append(
        Document(
            page_content=tablo_ozeti,
            metadata={
                "kaynak": "paket_fiyatlari.csv",
                "tip": "fiyat_tablosu",
                "paket_adi": "tüm_paketler",
                "dosya_yolu": filepath,
            },
        )
    )

    for _, row in df.iterrows():
        paket_adi = row["paket_adi"]
        text = f"{paket_adi} Paketi Detayları:\n"
        text += f"- Aylık Fiyat: {row['aylik_fiyat_tl']} TL\n"
        text += f"- Yıllık Fiyat: {row['yillik_fiyat_tl']} TL\n"
        text += f"- Kullanıcı Limiti: {row['kullanici_limiti']}\n"
        text += f"- Depolama Limiti: {row['depolama_limiti_gb']} GB\n"
        text += f"- Destek Tipi: {row['destek_tipi']}\n"
        text += f"- İade Süresi: {row['iade_suresi_gun']} gün\n"
        text += f"- API Erişimi: {row['api_erisimi']}\n"
        text += f"- Özel Entegrasyon: {row['ozel_entegrasyon']}\n"

        doc = Document(
            page_content=text,
            metadata={
                "kaynak": "paket_fiyatlari.csv",
                "tip": "fiyat_tablosu",
                "paket_adi": paket_adi,
                "aylik_fiyat": str(row["aylik_fiyat_tl"]),
                "yillik_fiyat": str(row["yillik_fiyat_tl"]),
                "dosya_yolu": filepath,
            },
        )
        documents.append(doc)

    return documents


def load_guncellemeler() -> list[Document]:
    filepath = os.path.join(DATA_DIR, "guncellemeler.json")
    with open(filepath, "r", encoding="utf-8") as f:
        updates = json.load(f)

    updates.sort(key=lambda x: x["tarih"])

    documents = []
    for update in updates:
        tarih = update["tarih"]
        tip = update.get("tip", "bilinmiyor")
        degisiklik = update["degisiklik"]
        onceki = update.get("onceki_deger", "")
        yeni = update.get("yeni_deger", "")
        etkilenen_paket = update.get("etkilenen_paket", "")
        etkilenen_madde = update.get("etkilenen_madde", "")

        text = f"Güncelleme Kaydı ({tarih}):\n"
        text += f"- Değişiklik Tipi: {tip}\n"
        if etkilenen_paket:
            text += f"- Etkilenen Paket: {etkilenen_paket}\n"
        if etkilenen_madde:
            text += f"- Etkilenen Madde: {etkilenen_madde}\n"
        text += f"- Açıklama: {degisiklik}\n"
        if onceki:
            text += f"- Önceki Değer: {onceki}\n"
        if yeni:
            text += f"- Yeni Değer: {yeni}\n"

        doc = Document(
            page_content=text,
            metadata={
                "kaynak": "guncellemeler.json",
                "tip": "guncelleme",
                "tarih": tarih,
                "degisiklik_tipi": tip,
                "etkilenen_paket": etkilenen_paket,
                "etkilenen_madde": etkilenen_madde,
                "dosya_yolu": filepath,
            },
        )
        documents.append(doc)

    return documents


def load_all_documents() -> list[Document]:
    all_docs = []
    all_docs.extend(load_sozlesme())
    all_docs.extend(load_paket_fiyatlari())
    all_docs.extend(load_guncellemeler())
    return all_docs


if __name__ == "__main__":
    docs = load_all_documents()
    print(f"Toplam {len(docs)} belge yüklendi.\n")
    for i, doc in enumerate(docs):
        print(f"--- Belge {i+1} ---")
        print(f"Kaynak: {doc.metadata.get('kaynak')}")
        print(f"Tip: {doc.metadata.get('tip')}")
        print(f"İçerik (ilk 100 karakter): {doc.page_content[:100]}...")
        print()

