import io
from datetime import datetime
from django.utils import timezone
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable


def generate_excel_report(data, top_areas, top_programs, offers_list, active_companies, apps_list, placements_list):
    wb = openpyxl.Workbook()

    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="0D9488", end_color="0D9488", fill_type="solid")
    sub_fill = PatternFill(start_color="0F766E", end_color="0F766E", fill_type="solid")
    bold_font = Font(name="Calibri", size=11, bold=True)
    title_font = Font(name="Calibri", size=16, bold=True, color="0F172A")
    subtitle_font = Font(name="Calibri", size=10, italic=True, color="64748B")
    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    # Hoja 1: Indicadores y Resumen
    ws1 = wb.active
    ws1.title = "Indicadores y Resumen"
    ws1.views.sheetView[0].showGridLines = True

    ws1["A1"] = "UNIVERSIDAD COOPERATIVA DE COLOMBIA - SEDE MONTERÍA"
    ws1["A1"].font = title_font
    ws1["A2"] = f"Reporte Ejecutivo de PPOL · Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    ws1["A2"].font = subtitle_font

    ws1["A4"] = "INDICADORES CLAVE DEL PROGRAMA (KPIs)"
    ws1["A4"].font = bold_font

    kpi_headers = ["Indicador", "Total Registrado", "Estado / Observación"]
    ws1.append([])
    ws1.append(kpi_headers)
    kpi_row = 6
    for col in range(1, 4):
        c = ws1.cell(row=kpi_row, column=col)
        c.font = header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="center", vertical="center")

    rows_kpis = [
        ("Ofertas publicadas", data.get("ofertas", 0), "Convocatorias activas y en proceso"),
        ("Empresas participantes", data.get("empresas_activas", 0), "Organizaciones con ofertas"),
        ("Postulaciones recibidas", data.get("postulaciones", 0), "Total de aplicaciones de estudiantes"),
        ("Vinculaciones exitosas", data.get("vinculaciones", 0), "Estudiantes aceptados en prácticas/empleo"),
    ]
    for r in rows_kpis:
        ws1.append(list(r))
        for col in range(1, 4):
            c = ws1.cell(row=ws1.max_row, column=col)
            c.border = thin_border
            if col == 2:
                c.alignment = Alignment(horizontal="center")
                c.font = bold_font

    # Top Áreas
    start_row = ws1.max_row + 3
    ws1.cell(row=start_row, column=1, value="ÁREAS PROFESIONALES CON MAYOR DEMANDA").font = bold_font
    ws1.cell(row=start_row + 1, column=1, value="Área").font = header_font
    ws1.cell(row=start_row + 1, column=1).fill = sub_fill
    ws1.cell(row=start_row + 1, column=2, value="N° Postulaciones").font = header_font
    ws1.cell(row=start_row + 1, column=2).fill = sub_fill

    for a in top_areas:
        ws1.append([a.get("offer__area__name") or "Sin área", a.get("n", 0)])
        for col in range(1, 3):
            ws1.cell(row=ws1.max_row, column=col).border = thin_border

    # Top Programas
    start_row2 = ws1.max_row + 3
    ws1.cell(row=start_row2, column=1, value="PROGRAMAS ACADÉMICOS CON MAYOR PARTICIPACIÓN").font = bold_font
    ws1.cell(row=start_row2 + 1, column=1, value="Programa Académico").font = header_font
    ws1.cell(row=start_row2 + 1, column=1).fill = sub_fill
    ws1.cell(row=start_row2 + 1, column=2, value="N° Postulaciones").font = header_font
    ws1.cell(row=start_row2 + 1, column=2).fill = sub_fill

    for p in top_programs:
        ws1.append([p.get("student__student__program") or "Sin programa", p.get("n", 0)])
        for col in range(1, 3):
            ws1.cell(row=ws1.max_row, column=col).border = thin_border

    ws1.column_dimensions["A"].width = 45
    ws1.column_dimensions["B"].width = 25
    ws1.column_dimensions["C"].width = 35

    # Hoja 2: Convocatorias
    ws2 = wb.create_sheet(title="Convocatorias")
    ws2.views.sheetView[0].showGridLines = True
    headers_conv = ["ID", "Título", "Empresa", "Tipo", "Modalidad", "Área", "Ciudad", "Cierre", "Estado", "Postulantes"]
    ws2.append(headers_conv)
    for col in range(1, len(headers_conv) + 1):
        c = ws2.cell(row=1, column=col)
        c.font = header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="center")

    for o in offers_list:
        ws2.append([
            o.id, o.title, o.company.name, o.get_kind_display(), o.get_mode_display(),
            o.area.name if o.area else "N/A", o.city, o.deadline.strftime("%d/%m/%Y"),
            o.get_status_display(), getattr(o, "apps_count", o.applications.count())
        ])
        for col in range(1, len(headers_conv) + 1):
            ws2.cell(row=ws2.max_row, column=col).border = thin_border

    for col in "ABCDEFGHIJ":
        ws2.column_dimensions[col].width = 18
    ws2.column_dimensions["B"].width = 32
    ws2.column_dimensions["C"].width = 25

    # Hoja 3: Postulaciones y Vinculaciones
    ws3 = wb.create_sheet(title="Postulaciones")
    ws3.views.sheetView[0].showGridLines = True
    headers_post = ["ID", "Estudiante", "Código", "Programa", "Convocatoria", "Empresa", "Fecha", "Estado"]
    ws3.append(headers_post)
    for col in range(1, len(headers_post) + 1):
        c = ws3.cell(row=1, column=col)
        c.font = header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="center")

    for a in apps_list:
        stu_prof = getattr(a.student, "student", None)
        ws3.append([
            a.id, a.student.get_full_name() or a.student.email,
            stu_prof.code if stu_prof else "N/A",
            stu_prof.program if stu_prof else "N/A",
            a.offer.title, a.offer.company.name,
            a.created.strftime("%d/%m/%Y %H:%M"),
            a.get_status_display()
        ])
        for col in range(1, len(headers_post) + 1):
            ws3.cell(row=ws3.max_row, column=col).border = thin_border

    for col in "ABCDEFGH":
        ws3.column_dimensions[col].width = 20
    ws3.column_dimensions["B"].width = 26
    ws3.column_dimensions["E"].width = 30
    ws3.column_dimensions["F"].width = 24

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    return stream.getvalue()


def generate_pdf_report(data, top_areas, top_programs, offers_list, placements_list, filter_summary=""):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=14
    )
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0D9488'),
        spaceBefore=12,
        spaceAfter=8
    )
    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#1E293B')
    )
    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#0F172A')
    )

    elements = []

    # Encabezado institucional
    elements.append(Paragraph("UNIVERSIDAD COOPERATIVA DE COLOMBIA", title_style))
    elements.append(Paragraph("Plataforma de Prácticas y Oportunidades Laborales (PPOL) · Informe de Indicadores", subtitle_style))
    elements.append(Paragraph(f"<b>Fecha de emisión:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')} | <b>Filtros:</b> {filter_summary or 'Todos los registros'}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0D9488'), spaceBefore=2, spaceAfter=14))

    # Resumen de KPIs
    elements.append(Paragraph("1. RESUMEN EJECUTIVO (KPIs)", section_style))
    kpi_data = [
        [Paragraph("<b>Indicador</b>", cell_bold), Paragraph("<b>Total</b>", cell_bold), Paragraph("<b>Descripción</b>", cell_bold)],
        [Paragraph("Ofertas Registradas", cell_style), Paragraph(str(data.get("ofertas", 0)), cell_bold), Paragraph("Convocatorias de prácticas y empleo publicadas", cell_style)],
        [Paragraph("Empresas Activas", cell_style), Paragraph(str(data.get("empresas_activas", 0)), cell_bold), Paragraph("Organizaciones con ofertas vigentes", cell_style)],
        [Paragraph("Postulaciones Totales", cell_style), Paragraph(str(data.get("postulaciones", 0)), cell_bold), Paragraph("Aplicaciones realizadas por estudiantes", cell_style)],
        [Paragraph("Vinculaciones Exitosas", cell_style), Paragraph(str(data.get("vinculaciones", 0)), cell_bold), Paragraph("Candidatos seleccionados y vinculados", cell_style)],
    ]
    t_kpis = Table(kpi_data, colWidths=[160, 70, 310])
    t_kpis.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    elements.append(t_kpis)
    elements.append(Spacer(1, 14))

    # Áreas y Programas Top
    elements.append(Paragraph("2. DEMANDA ACADÉMICA Y PROFESIONAL", section_style))
    col_areas = [
        [Paragraph("<b>Área Profesional</b>", cell_bold), Paragraph("<b>Postulaciones</b>", cell_bold)]
    ]
    for a in top_areas[:5]:
        col_areas.append([
            Paragraph(a.get("offer__area__name") or "Sin área", cell_style),
            Paragraph(str(a.get("n", 0)), cell_bold)
        ])
    if len(col_areas) == 1:
        col_areas.append([Paragraph("Sin datos en el período", cell_style), Paragraph("0", cell_style)])

    col_programs = [
        [Paragraph("<b>Programa Académico</b>", cell_bold), Paragraph("<b>Postulaciones</b>", cell_bold)]
    ]
    for p in top_programs[:5]:
        col_programs.append([
            Paragraph(p.get("student__student__program") or "Sin programa", cell_style),
            Paragraph(str(p.get("n", 0)), cell_bold)
        ])
    if len(col_programs) == 1:
        col_programs.append([Paragraph("Sin datos en el período", cell_style), Paragraph("0", cell_style)])

    t_areas = Table(col_areas, colWidths=[180, 80])
    t_areas.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#CCFBF1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#99F6E4')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))

    t_progs = Table(col_programs, colWidths=[200, 80])
    t_progs.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E0E7FF')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#C7D2FE')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))

    side_by_side = Table([[t_areas, t_progs]], colWidths=[270, 270])
    side_by_side.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(side_by_side)
    elements.append(Spacer(1, 14))

    # Vinculaciones destacadas
    elements.append(Paragraph("3. VINCULACIONES DESTACADAS (ACEPTADAS)", section_style))
    vinc_data = [
        [Paragraph("<b>Estudiante</b>", cell_bold), Paragraph("<b>Programa</b>", cell_bold), Paragraph("<b>Empresa</b>", cell_bold), Paragraph("<b>Oferta</b>", cell_bold)]
    ]
    for a in placements_list[:8]:
        stu = a.student
        stu_prof = getattr(stu, "student", None)
        vinc_data.append([
            Paragraph(stu.get_full_name() or stu.email, cell_style),
            Paragraph(stu_prof.program if stu_prof else "N/A", cell_style),
            Paragraph(a.offer.company.name, cell_style),
            Paragraph(a.offer.title, cell_style)
        ])
    if len(vinc_data) == 1:
        vinc_data.append([Paragraph("No hay vinculaciones registradas con los filtros actuales.", cell_style), Paragraph("", cell_style), Paragraph("", cell_style), Paragraph("", cell_style)])

    t_vinc = Table(vinc_data, colWidths=[140, 140, 130, 130])
    t_vinc.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DCFCE7')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BBF7D0')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(t_vinc)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
