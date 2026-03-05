
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from data_loaders import load_all_documents

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o"
RETRIEVER_K = 12


def get_embeddings():
    return OpenAIEmbeddings(model=EMBEDDING_MODEL)


def get_llm():
    return ChatOpenAI(
        model=LLM_MODEL,
        temperature=0.1,
    )


def build_vectorstore(documents):
    embeddings = get_embeddings()
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="rag_collection",
    )
    return vectorstore


SYSTEM_PROMPT = """Sen TechCloud Bilişim Hizmetleri'nin yapay zeka destekli müşteri asistanısın.
Sana verilen bağlam bilgilerini kullanarak müşteri sorularını doğru ve eksiksiz yanıtla.

ÖNEMLİ KURALLAR:
1. SADECE verilen bağlam bilgilerini kullan, kendi bilgini ekleme.
2. Eğer aynı konuda farklı kaynaklardan çelişkili bilgi varsa, EN GÜNCEL TARİHLİ güncelleme kaydını (guncellemeler.json) baz al.
3. Güncelleme kayıtlarındaki bilgiler, sözleşme ve fiyat tablosundaki bilgilerden DAHA GÜNCELDİR.
4. Cevabının sonunda "📋 Kaynaklar" başlığı altında:
   - Hangi dosyalardan bilgi aldığını
   - İlgili güncelleme tarihlerini
   - Referans verilen madde numaralarını listele.
5. Cevabı Türkçe ver.
6. Fiyat bilgilerini TL cinsinden ve net olarak belirt.
7. Eğer soruyla ilgili yeterli bilgi yoksa, bunu açıkça belirt.

BAĞLAM BİLGİLERİ:
{context}
"""

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "{question}"),
    ]
)


def format_docs(docs):
    formatted = []
    for i, doc in enumerate(docs, 1):
        meta = doc.metadata
        kaynak = meta.get("kaynak", "bilinmiyor")
        tip = meta.get("tip", "")
        tarih = meta.get("tarih", "")
        madde = meta.get("madde_no", "")
        paket = meta.get("paket_adi", "")

        header = f"[Kaynak {i}: {kaynak}"
        if tip:
            header += f" | Tip: {tip}"
        if tarih:
            header += f" | Tarih: {tarih}"
        if madde:
            header += f" | {madde}"
        if paket:
            header += f" | Paket: {paket}"
        header += "]"

        formatted.append(f"{header}\n{doc.page_content}")

    return "\n\n---\n\n".join(formatted)


def query(question: str) -> dict:
    documents = load_all_documents()

    vectorstore = build_vectorstore(documents)
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": RETRIEVER_K},
    )

    retrieved_docs = retriever.invoke(question)

    llm = get_llm()
    chain = (
        {"context": lambda x: format_docs(retrieved_docs), "question": RunnablePassthrough()}
        | PROMPT
        | llm
        | StrOutputParser()
    )

    answer = chain.invoke(question)

    sources = []
    seen = set()
    for doc in retrieved_docs:
        meta = doc.metadata
        source_key = f"{meta.get('kaynak', '')}-{meta.get('tarih', '')}-{meta.get('madde_no', '')}-{meta.get('paket_adi', '')}"
        if source_key not in seen:
            seen.add(source_key)
            sources.append(
                {
                    "kaynak": meta.get("kaynak", ""),
                    "tip": meta.get("tip", ""),
                    "tarih": meta.get("tarih", ""),
                    "madde_no": meta.get("madde_no", ""),
                    "paket_adi": meta.get("paket_adi", ""),
                }
            )

    vectorstore.delete_collection()

    return {"answer": answer, "sources": sources}


if __name__ == "__main__":
    test_questions = [
        "Pro paket fiyatı nedir?",
        "İptal edersem paramı ne zaman alırım?",
        "Enterprise paketinin kullanıcı limiti nedir?",
    ]
    for q in test_questions:
        print(f"\n{'='*60}")
        print(f"SORU: {q}")
        print("=" * 60)
        result = query(q)
        print(f"\nCEVAP:\n{result['answer']}")
        print(f"\nKAYNAKLAR: {result['sources']}")

