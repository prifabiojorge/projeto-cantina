#!/usr/bin/env python3
"""
Gera um PDF com 10 QR codes de alunos para teste.
"""

import sys
import os
from pathlib import Path

# Garante que o script roda a partir da pasta do projeto
os.chdir(Path(__file__).parent)

import sqlite3
import qrcode
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

OUTPUT_PDF = Path(__file__).parent.parent / "qrcodes_teste.pdf"

def get_alunos():
    conn = sqlite3.connect("cantina.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT id, nome, matricula, turma, turno, qrcode_hash
        FROM alunos
        ORDER BY id
        LIMIT 10
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def make_qr_image(data: str, size_px: int = 220) -> io.BytesIO:
    """Gera imagem QR code em memória (BytesIO) no formato PNG."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=3,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def gerar_pdf(alunos):
    """Gera PDF A4 com 2 colunas e 5 linhas (10 cartões)."""

    PAGE_W, PAGE_H = A4
    MARGIN = 1.5 * cm

    c = canvas.Canvas(str(OUTPUT_PDF), pagesize=A4)
    c.setTitle("QR Codes - Sistema Cantina Escolar")
    c.setAuthor("Sistema Cantina")

    # Layout: 2 colunas × 5 linhas por página
    COLS = 2
    ROWS = 5

    card_w = (PAGE_W - 2 * MARGIN) / COLS
    card_h = (PAGE_H - 2 * MARGIN) / ROWS

    QR_SIZE = 4.2 * cm   # tamanho do QR no card
    PADDING = 0.35 * cm

    # --- Cabeçalho da página ---
    def draw_page_header():
        c.setFillColor(colors.HexColor("#1a237e"))
        c.rect(0, PAGE_H - 1.2 * cm, PAGE_W, 1.2 * cm, fill=True, stroke=False)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(PAGE_W / 2, PAGE_H - 0.85 * cm,
                            "SISTEMA CANTINA ESCOLAR  —  QR CODES DE TESTE")
        # Rodapé
        c.setFillColor(colors.HexColor("#e8eaf6"))
        c.rect(0, 0, PAGE_W, 0.7 * cm, fill=True, stroke=False)
        c.setFillColor(colors.HexColor("#3949ab"))
        c.setFont("Helvetica", 7)
        c.drawCentredString(PAGE_W / 2, 0.22 * cm,
                            "Documento gerado para testes internos  •  Sistema Cantina Escolar")

    def draw_card(index, aluno):
        col = index % COLS
        row = index // COLS

        # Coordenadas do canto inferior-esquerdo do card (PDF usa y de baixo p/ cima)
        x0 = MARGIN + col * card_w
        y0 = PAGE_H - MARGIN - (row + 1) * card_h

        # Fundo do card
        bg_color = colors.HexColor("#f5f5ff") if index % 2 == 0 else colors.HexColor("#fffde7")
        c.setFillColor(bg_color)
        c.roundRect(x0 + 0.1 * cm, y0 + 0.1 * cm,
                    card_w - 0.2 * cm, card_h - 0.2 * cm,
                    0.3 * cm, fill=True, stroke=False)

        # Borda
        c.setStrokeColor(colors.HexColor("#3949ab"))
        c.setLineWidth(0.8)
        c.roundRect(x0 + 0.1 * cm, y0 + 0.1 * cm,
                    card_w - 0.2 * cm, card_h - 0.2 * cm,
                    0.3 * cm, fill=False, stroke=True)

        # Faixa de título
        c.setFillColor(colors.HexColor("#3949ab"))
        c.rect(x0 + 0.1 * cm, y0 + card_h - 0.75 * cm - 0.1 * cm,
               card_w - 0.2 * cm, 0.75 * cm, fill=True, stroke=False)

        # Número do card
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(x0 + 0.25 * cm, y0 + card_h - 0.58 * cm, f"#{index + 1:02d}")

        # Nome do aluno (truncado se necessário)
        nome = aluno["nome"]
        c.setFont("Helvetica-Bold", 9)
        max_nome_w = card_w - 1.2 * cm
        while c.stringWidth(nome, "Helvetica-Bold", 9) > max_nome_w and len(nome) > 5:
            nome = nome[:-1]
        if nome != aluno["nome"]:
            nome += "…"
        c.drawCentredString(x0 + card_w / 2, y0 + card_h - 0.58 * cm, nome)

        # --- QR Code (centralizado no card) ---
        qr_buf = make_qr_image(aluno["qrcode_hash"])
        qr_reader = ImageReader(qr_buf)
        qr_x = x0 + (card_w - QR_SIZE) / 2
        qr_y = y0 + card_h - 0.85 * cm - QR_SIZE - PADDING
        c.drawImage(qr_reader, qr_x, qr_y, width=QR_SIZE, height=QR_SIZE,
                    preserveAspectRatio=True)

        # --- Infos abaixo do QR ---
        info_y = qr_y - 0.5 * cm
        c.setFillColor(colors.HexColor("#212121"))
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(x0 + card_w / 2, info_y,
                            f"Matricula: {aluno['matricula']}")
        info_y -= 0.38 * cm
        c.setFont("Helvetica", 7.5)
        c.setFillColor(colors.HexColor("#3949ab"))
        c.drawCentredString(x0 + card_w / 2, info_y,
                            f"Turma: {aluno['turma']}   •   Turno: {aluno['turno']}")

    # Desenha a página
    draw_page_header()
    for i, aluno in enumerate(alunos):
        draw_card(i, aluno)

    c.save()
    print(f"\n✅ PDF gerado com sucesso: {OUTPUT_PDF}")
    print(f"   Total de QR codes: {len(alunos)}")

def main():
    print("=== Gerador de QR Codes - Sistema Cantina ===\n")
    alunos = get_alunos()
    if not alunos:
        print("❌ Nenhum aluno encontrado no banco de dados.")
        sys.exit(1)

    print(f"📋 Alunos selecionados ({len(alunos)}):")
    for a in alunos:
        print(f"   • {a['nome']} ({a['matricula']}) — {a['turma']} / {a['turno']}")

    print("\n🖨️  Gerando PDF...")
    gerar_pdf(alunos)


if __name__ == "__main__":
    main()
