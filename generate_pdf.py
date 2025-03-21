from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_etiquetas_pdf(cliente, num_etiquetas):
    print("Cliente recebido:", cliente)  # Para depuração

    pdf_path = "etiquetas.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)

    label_width = 350  # Largura da etiqueta
    label_height = 150  # Altura da etiqueta
    x_margin = 100  # Margem lateral para centralizar melhor
    y_margin = 650  # Margem superior ajustada para mais espaço
    spacing = 30  # Espaçamento entre etiquetas

    # Definindo o número máximo de etiquetas por página
    etiquetas_por_linha = 1  # Número de etiquetas por linha
    etiquetas_por_coluna = 4  # Número de etiquetas por coluna
    etiquetas_por_pagina = etiquetas_por_linha * etiquetas_por_coluna  # Total de etiquetas por página

    x_offset = 0  # Deslocamento horizontal (a cada linha)
    y_offset = 0  # Deslocamento vertical (a cada coluna)

    # Calculando a posição inicial para a primeira etiqueta
    for i in range(num_etiquetas):
        if i % etiquetas_por_pagina == 0 and i != 0:
            c.showPage()  # Adiciona uma nova página
            y_offset = 0  # Reseta o deslocamento vertical para a nova página

        x = x_margin + (i % etiquetas_por_linha) * (label_width + spacing)
        y = y_margin - (y_offset * (label_height + spacing))

        # Desenhar a borda da etiqueta
        c.rect(x, y, label_width, label_height)

        # Definir fonte e tamanhos
        c.setFont("Helvetica-Bold", 14)  # Aumentado
        c.drawCentredString(x + label_width / 2, y + 130, "DESTINATÁRIO")  # Centralizado no topo

        # Nome do cliente em caixa alta e centralizado
        c.setFont("Helvetica-Bold", 14)  # Aumentado
        c.drawCentredString(x + label_width / 2, y + 110, cliente[1].upper())

        # Cidade/Estado e telefone
        c.setFont("Helvetica", 14)  # Aumentado
        c.drawString(x + 10, y + 90, f"{cliente[6]} - {cliente[7]}")  # Cidade - Estado
        c.drawString(x + 200, y + 90, f"Fone: {cliente[8]}")  # Telefone alinhado à direita

        # CEP
        c.drawString(x + 10, y + 75, f"CEP: {cliente[2]}")

        # Rua e número
        c.drawString(x + 10, y + 60, f"{cliente[3]}, {cliente[4]}")

        # Quantidade de volumes
        c.setFont("Helvetica-Bold", 14)  # Aumentado
        c.drawString(x + 10, y + 40, f"Volume: {i + 1} / {num_etiquetas}")

        # Transportadora centralizada
        c.setFont("Helvetica-Bold", 14)  # Aumentado
        c.drawCentredString(x + label_width / 2, y + 25, "TRANSPORTADORA")

        # Nome da transportadora
        transportadora = cliente[-1] if len(cliente) > 9 and cliente[-1] else "Transportadora não informada"
        c.setFont("Helvetica", 12)  # Aumentado
        c.drawCentredString(x + label_width / 2, y + 10, transportadora)

        y_offset += 1  # Move para a próxima linha

    c.save()

    return pdf_path
