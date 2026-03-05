
import gradio as gr
from rag_engine import query


def process_query(question: str, history: list) -> tuple:
    if not question.strip():
        return "", "Lütfen bir soru yazın."

    try:
        result = query(question)
        answer = result["answer"]

        sources_text = format_sources(result["sources"])

        return answer, sources_text

    except Exception as e:
        error_msg = f"❌ Hata oluştu: {str(e)}"
        return error_msg, ""


def format_sources(sources: list) -> str:
    if not sources:
        return "<div style='text-align: center; color: #94a3b8; padding: 20px 0;'><i>Kaynak bilgisi bulunamadı.</i></div>"

    lines = ["<div style='font-weight: 700; color: #1e293b; margin-bottom: 16px; font-size: 1.15rem; letter-spacing: -0.01em;'>📋 Referans Belgeler</div>"]

    by_file = {}
    for s in sources:
        kaynak = s.get("kaynak", "bilinmiyor")
        if kaynak not in by_file:
            by_file[kaynak] = []
        by_file[kaynak].append(s)

    icons = {
        "sozlesme.txt": "📄",
        "paket_fiyatlari.csv": "📊",
        "guncellemeler.json": "🔄",
    }

    for kaynak, items in by_file.items():
        icon = icons.get(kaynak, "📁")
        lines.append(f"<div style='background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'>")
        lines.append(f"<div style='font-weight: 600; color: #334155; margin-bottom: 10px; border-bottom: 1px solid #f1f5f9; padding-bottom: 8px; font-size: 0.95rem;'>{icon} {kaynak}</div>")

        for item in items:
            details = []
            if item.get("madde_no"):
                details.append(f"<span style='color: #475569;'><b>Madde:</b> {item['madde_no']}</span>")
            if item.get("paket_adi") and item["paket_adi"] != "tüm_paketler":
                details.append(f"<span style='color: #0284c7;'><b>Paket:</b> {item['paket_adi']}</span>")
            if item.get("tarih"):
                details.append(f"<span style='color: #16a34a;'><b>Tarih:</b> {item['tarih']}</span>")
            if item.get("tip"):
                details.append(f"<span style='color: #8b5cf6;'><b>Tip:</b> {item['tip']}</span>")

            if details:
                lines.append(f"<div style='font-size: 0.85rem; line-height: 1.5; padding-left: 10px; margin-bottom: 6px; border-left: 3px solid #cbd5e1;'>{' &nbsp;•&nbsp; '.join(details)}</div>")

        lines.append("</div>")

    return "".join(lines)


EXAMPLES = [
    "Şu anki Pro paket fiyatı nedir ve iptal edersem paramı ne zaman alırım?",
    "Enterprise paketinin kullanıcı limiti ve depolama kapasitesi nedir?",
    "Pro paket iade süresi kaç gün? Bu süre değişti mi?",
    "Basic paket ile Pro paket arasındaki farklar nelerdir?",
    "Veri güvenliği konusunda ne tür önlemler alınıyor?",
    "SLA taahhüdü nedir? Son değişiklik ne zaman yapıldı?",
    "Yıllık abonelikte iade koşulları nelerdir?",
    "Ödeme gecikirse ne olur?",
]


CUSTOM_CSS = """
/* Animasyonlar ve Yazı Tipleri */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.gradio-container {
    max-width: 1100px !important;
    margin: auto !important;
    font-family: 'Inter', sans-serif !important;
    background-color: #fafafa !important;
}
.glass-panel {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 1px solid rgba(226, 232, 240, 0.8) !important;
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05) !important;
    border-radius: 20px !important;
    padding: 24px !important;
    margin-bottom: 24px !important;
}
.source-panel {
    background: linear-gradient(145deg, #f8fafc, #f1f5f9) !important;
    border-radius: 16px !important;
    padding: 24px !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.02) !important;
}
.btn-primary {
    background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%) !important;
    border: none !important;
    box-shadow: 0 4px 14px 0 rgba(79, 70, 229, 0.39) !important;
    transition: all 0.3s ease !important;
    border-radius: 12px !important;
}
.btn-primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5) !important;
}
.btn-secondary {
    background: white !important;
    border: 1px solid #e2e8f0 !important;
    transition: all 0.2s ease !important;
    border-radius: 10px !important;
}
.btn-secondary:hover {
    border-color: #3b82f6 !important;
    color: #3b82f6 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.04) !important;
}
.header-wrapper {
    text-align: center;
    padding: 3.5rem 1.5rem;
    margin-top: 1.5rem;
    margin-bottom: 2.5rem;
    background: linear-gradient(135deg, #eff6ff 0%, #e0e7ff 100%);
    border-radius: 28px;
    box-shadow: 0 10px 30px -5px rgba(59, 130, 246, 0.15);
    border: 1px solid rgba(255,255,255,0.7);
}
.header-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(90deg, #1e3a8a, #4f46e5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1rem;
    letter-spacing: -0.03em;
}
.header-subtitle {
    color: #475569;
    font-size: 1.2rem;
    max-width: 650px;
    margin: 0 auto;
    line-height: 1.6;
}
.info-badge {
    background-color: rgba(255, 255, 255, 0.7);
    padding: 8px 18px;
    border-radius: 24px;
    font-size: 0.9rem;
    color: #4338ca;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-top: 1.5rem;
    border: 1px solid rgba(255,255,255,0.9);
    box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}
"""

with gr.Blocks(
    title="TechCloud RAG Asistanı",
    theme=gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="blue",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
    ),
    css=CUSTOM_CSS,
) as app:

    gr.HTML(
        """
        <div class="header-wrapper">
            <h1 class="header-title">✨ TechCloud RAG Asistanı</h1>
            <p class="header-subtitle">
                Şirket sözleşmeleri, paket fiyatları ve güncelleme loglarını okuyarak bağlam kurabilen <b>gelişmiş yapay zeka</b> müşteri destek sistemi.
            </p>
            <div class="info-badge">
                <span>🔄</span> Sistem arkadaki verileri dinamik olarak yeniden okur.
            </div>
        </div>
        """
    )

    with gr.Row():
        with gr.Column(scale=7, elem_classes=["glass-panel"]):
            question_input = gr.Textbox(
                label="💬 Size Nasıl Yardımcı Olabilirim?",
                placeholder="Örn: Pro paket fiyatı nedir ve iptal edersem paramı ne zaman alırım?",
                lines=3,
            )
            submit_btn = gr.Button("✨ Sorunu Gönder", variant="primary", size="lg", elem_classes=["btn-primary"])

            gr.HTML("<hr style='border: none; border-top: 1px dashed #cbd5e1; margin: 28px 0;'>")
            
            answer_output = gr.Markdown(
                label="🤖",
                value="<div style='text-align: center; color: #94a3b8; padding: 30px 0;'><i>Sistemin cevap üretmesi için bir soru sorun...</i></div>",
            )

        with gr.Column(scale=3):
            sources_output = gr.Markdown(
                label="📋",
                value="<div style='text-align: center; color: #94a3b8; padding: 20px 0;'><i>Referans belgeler değerlendirme sonrası burada görünür...</i></div>",
                elem_classes=["source-panel"],
            )

    gr.Markdown("<h3 style='color: #1e293b; margin-top: 1.5rem; font-weight: 800; letter-spacing: -0.02em;'>💡 Popüler Kullanıcı Soruları</h3>")
    with gr.Row():
        for i in range(0, len(EXAMPLES), 2):
            with gr.Column():
                for j in range(i, min(i + 2, len(EXAMPLES))):
                    example_btn = gr.Button(
                        EXAMPLES[j],
                        variant="secondary",
                        size="sm",
                        elem_classes=["btn-secondary"]
                    )
                    example_btn.click(
                        fn=process_query,
                        inputs=[example_btn, gr.State([])],
                        outputs=[answer_output, sources_output],
                    )

    submit_btn.click(
        fn=process_query,
        inputs=[question_input, gr.State([])],
        outputs=[answer_output, sources_output],
    )

    question_input.submit(
        fn=process_query,
        inputs=[question_input, gr.State([])],
        outputs=[answer_output, sources_output],
    )

    gr.HTML(
        """
        <div style="text-align: center; color: #64748b; font-size: 0.9rem; margin-top: 2rem; border-top: 1px solid #e2e8f0; padding-top: 1.5rem;">
            <b>📁 Konfigüre Edilmiş Veri Kaynakları:</b> <code>data/sozlesme.txt</code> &nbsp;•&nbsp; <code>data/paket_fiyatlari.csv</code> &nbsp;•&nbsp; <code>data/guncellemeler.json</code><br>
            <span style="color: #94a3b8; font-size: 0.85rem; margin-top: 0.75rem; display: inline-block;">
                <b>🚀 Geliştirilmiş Mimari:</b> LangChain + ChromaDB + OpenAI GPT-4o
            </span>
        </div>
        """
    )


if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
    )

