import io
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class PDFGeneratorAdapter:
    """Generates PDF binary stream for a DidacticPlan (UC1 / UC4 / RF03)"""
    @staticmethod
    def generate_plan_pdf(
        prof_nome: str,
        disciplina_codigo: str,
        disciplina_nome: str,
        periodo_str: str,
        campos: Dict[str, Any]
    ) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=1,
            spaceAfter=12
        )
        subtitle_style = ParagraphStyle(
            'SubTitleStyle',
            parent=styles['Heading2'],
            fontSize=12,
            alignment=1,
            spaceAfter=18
        )
        normal_style = styles['Normal']

        # Institutional Header
        story.append(Paragraph("<b>MINISTÉRIO DA EDUCAÇÃO</b>", title_style))
        story.append(Paragraph("<b>CENTRO FEDERAL DE EDUCAÇÃO TECNOLÓGICA DE MINAS GERAIS</b>", subtitle_style))
        story.append(Paragraph("<b>PLANO DIDÁTICO DE DISCIPLINA</b>", title_style))
        story.append(Spacer(1, 12))

        # Fixed Information Table
        info_data = [
            [Paragraph("<b>Professor Responsável:</b>", normal_style), Paragraph(prof_nome, normal_style)],
            [Paragraph("<b>Disciplina:</b>", normal_style), Paragraph(f"{disciplina_codigo} - {disciplina_nome}", normal_style)],
            [Paragraph("<b>Período Letivo:</b>", normal_style), Paragraph(periodo_str, normal_style)],
        ]
        t = Table(info_data, colWidths=[150, 390])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 18))

        # Dynamic Fields Table
        story.append(Paragraph("<b>Campos Específicos do Plano</b>", styles['Heading3']))
        story.append(Spacer(1, 6))

        for k, v in campos.items():
            field_title = k.replace('_', ' ').capitalize()
            field_value = str(v) if v is not None else ""
            field_data = [
                [Paragraph(f"<b>{field_title}</b>", styles['Heading4'])],
                [Paragraph(field_value.replace('\n', '<br/>'), normal_style)]
            ]
            field_table = Table(field_data, colWidths=[540])
            field_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(field_table)
            story.append(Spacer(1, 10))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
