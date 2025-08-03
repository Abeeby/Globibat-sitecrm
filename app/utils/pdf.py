"""
Génération de documents PDF (factures, devis, fiches de paie)
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfgen import canvas
from io import BytesIO
import qrcode
from datetime import datetime
import os

def generate_invoice_pdf(invoice):
    """Générer une facture PDF avec QR-facture suisse"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # En-tête avec logo
    header_data = [
        ['GLOBIBAT SA', '', 'FACTURE'],
        ['Route de Chancy 123', '', f'N° {invoice.invoice_number}'],
        ['1213 Petit-Lancy', '', f'Date: {invoice.issue_date.strftime("%d.%m.%Y")}'],
        ['Genève, Suisse', '', ''],
        ['TVA: CHE-XXX.XXX.XXX', '', '']
    ]
    
    header_table = Table(header_data, colWidths=[100*mm, 40*mm, 60*mm])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 16),
        ('FONTSIZE', (2, 0), (2, 0), 16),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 20*mm))
    
    # Informations client
    client_data = [
        ['FACTURÉ À:'],
        [invoice.client.display_name],
        [invoice.client.address],
        [f'{invoice.client.postal_code} {invoice.client.city}'],
    ]
    
    if invoice.project:
        client_data.append([''])
        client_data.append([f'Projet: {invoice.project.name}'])
    
    client_table = Table(client_data, colWidths=[120*mm])
    client_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(client_table)
    story.append(Spacer(1, 10*mm))
    
    # Lignes de facture
    items_data = [['Description', 'Quantité', 'Unité', 'Prix unit.', 'Total']]
    
    for item in invoice.items.order_by('position'):
        items_data.append([
            item.description,
            f'{item.quantity:.2f}',
            item.unit or '',
            f'CHF {item.unit_price:.2f}',
            f'CHF {item.total:.2f}'
        ])
    
    # Totaux
    items_data.append(['', '', '', '', ''])
    items_data.append(['', '', '', 'Sous-total:', f'CHF {invoice.subtotal:.2f}'])
    
    if invoice.discount_amount > 0:
        items_data.append(['', '', '', f'Remise ({invoice.discount_percentage}%):', f'CHF -{invoice.discount_amount:.2f}'])
    
    items_data.append(['', '', '', f'TVA ({invoice.tax_rate}%):', f'CHF {invoice.tax_amount:.2f}'])
    items_data.append(['', '', '', 'TOTAL:', f'CHF {invoice.total_amount:.2f}'])
    
    items_table = Table(items_data, colWidths=[80*mm, 25*mm, 20*mm, 35*mm, 35*mm])
    items_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEABOVE', (3, -4), (-1, -4), 1, colors.black),
        ('LINEABOVE', (3, -1), (-1, -1), 2, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 20*mm))
    
    # Conditions de paiement
    payment_info = f"""
    <b>Conditions de paiement:</b><br/>
    Échéance: {invoice.due_date.strftime('%d.%m.%Y')}<br/>
    IBAN: CH93 0076 2011 6238 5295 7<br/>
    BIC: XXXXXXXXXXXX
    """
    story.append(Paragraph(payment_info, styles['Normal']))
    
    # QR-Facture (partie inférieure)
    # TODO: Implémenter la génération complète du QR-facture suisse
    
    # Générer le PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_quote_pdf(quote):
    """Générer un devis PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Structure similaire à la facture mais avec:
    # - Titre "DEVIS" au lieu de "FACTURE"
    # - Date de validité
    # - Conditions spécifiques aux devis
    # - Options si présentes
    
    # [Code similaire à generate_invoice_pdf avec adaptations pour devis]
    
    buffer.seek(0)
    return buffer

def generate_timesheet_pdf(employee, attendances, start_date, end_date):
    """Générer une feuille de temps PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # En-tête
    header_data = [
        ['GLOBIBAT SA', '', 'FEUILLE DE TEMPS'],
        ['', '', f'{start_date.strftime("%d.%m.%Y")} - {end_date.strftime("%d.%m.%Y")}']
    ]
    
    header_table = Table(header_data, colWidths=[100*mm, 40*mm, 60*mm])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 14),
        ('FONTSIZE', (2, 0), (2, 0), 14),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 15*mm))
    
    # Informations employé
    employee_info = [
        ['Employé:', employee.full_name],
        ['Matricule:', employee.employee_code],
        ['Département:', employee.department or '-']
    ]
    
    employee_table = Table(employee_info, colWidths=[30*mm, 90*mm])
    employee_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    story.append(employee_table)
    story.append(Spacer(1, 10*mm))
    
    # Tableau des présences
    attendance_data = [
        ['Date', 'Jour', 'Arrivée', 'Départ midi', 'Retour', 'Départ', 'Total', 'Heures sup.', 'Lieu/Projet']
    ]
    
    total_hours = 0
    total_overtime = 0
    
    for att in attendances:
        day_name = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'][att.date.weekday()]
        
        attendance_data.append([
            att.date.strftime('%d.%m'),
            day_name,
            att.check_in_morning.strftime('%H:%M') if att.check_in_morning else '-',
            att.check_out_lunch.strftime('%H:%M') if att.check_out_lunch else '-',
            att.check_in_afternoon.strftime('%H:%M') if att.check_in_afternoon else '-',
            att.check_out_evening.strftime('%H:%M') if att.check_out_evening else '-',
            f'{att.total_hours:.2f}' if att.total_hours else '0.00',
            f'{att.overtime_hours:.2f}' if att.overtime_hours else '-',
            att.location_name or (att.project.name if att.project else '-')
        ])
        
        total_hours += att.total_hours or 0
        total_overtime += att.overtime_hours or 0
    
    # Ligne de total
    attendance_data.append(['', '', '', '', '', 'TOTAL:', f'{total_hours:.2f}', f'{total_overtime:.2f}', ''])
    
    attendance_table = Table(attendance_data, colWidths=[18*mm, 15*mm, 20*mm, 20*mm, 20*mm, 20*mm, 20*mm, 20*mm, 42*mm])
    attendance_table.setStyle(TableStyle([
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('ALIGN', (-1, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (5, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEABOVE', (5, -1), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
    ]))
    story.append(attendance_table)
    
    # Résumé
    story.append(Spacer(1, 15*mm))
    summary_data = [
        ['Résumé de la période', ''],
        ['Jours travaillés:', f'{len(attendances)}'],
        ['Heures normales:', f'{total_hours - total_overtime:.2f}'],
        ['Heures supplémentaires:', f'{total_overtime:.2f}'],
        ['Total heures:', f'{total_hours:.2f}']
    ]
    
    summary_table = Table(summary_data, colWidths=[50*mm, 30*mm])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(summary_table)
    
    # Signatures
    story.append(Spacer(1, 30*mm))
    signature_data = [
        ['Signature de l\'employé:', '________________', 'Date:', '________________'],
        ['', '', '', ''],
        ['Validation manager:', '________________', 'Date:', '________________']
    ]
    
    signature_table = Table(signature_data, colWidths=[40*mm, 50*mm, 20*mm, 40*mm])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    story.append(signature_table)
    
    # Générer le PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_payslip_pdf(payroll):
    """Générer une fiche de paie PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    employee = payroll.employee
    
    # En-tête entreprise
    header_data = [
        ['GLOBIBAT SA', '', 'BULLETIN DE SALAIRE'],
        ['Rie des Tattes d\'Oie 93', '', f'{payroll.month:02d}/{payroll.year}'],
        ['1260 Nyon', '', ''],
        ['Vaud, Suisse', '', '']
    ]
    
    header_table = Table(header_data, colWidths=[100*mm, 40*mm, 60*mm])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 14),
        ('FONTSIZE', (2, 0), (2, 0), 14),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 20*mm))
    
    # Informations employé
    employee_data = [
        ['EMPLOYÉ:', employee.full_name],
        ['Matricule:', employee.employee_code],
        ['Département:', employee.department or '-'],
        ['Fonction:', employee.position or '-'],
        ['Date d\'entrée:', employee.hire_date.strftime('%d.%m.%Y')]
    ]
    
    employee_table = Table(employee_data, colWidths=[40*mm, 80*mm])
    employee_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(employee_table)
    story.append(Spacer(1, 15*mm))
    
    # Détails du salaire
    salary_data = [
        ['DESCRIPTION', 'BASE', 'TAUX/NOMBRE', 'MONTANT CHF'],
        ['', '', '', ''],
        ['REVENUS', '', '', ''],
        ['Salaire de base', f'{payroll.regular_hours:.2f} h', f'{employee.hourly_rate:.2f}' if employee.hourly_rate else '-', f'{payroll.base_amount:.2f}'],
    ]
    
    if payroll.overtime_hours > 0:
        salary_data.append(['Heures supplémentaires', f'{payroll.overtime_hours:.2f} h', '125%', f'{payroll.overtime_amount:.2f}'])
    
    if payroll.bonuses > 0:
        salary_data.append(['Primes', '', '', f'{payroll.bonuses:.2f}'])
    
    salary_data.extend([
        ['', '', '', ''],
        ['SALAIRE BRUT', '', '', f'{payroll.gross_salary:.2f}'],
        ['', '', '', ''],
        ['DÉDUCTIONS', '', '', ''],
        ['AVS/AI/APG', '', '5.25%', f'-{payroll.social_security:.2f}'],
        ['AC', '', '1.1%', f'-{payroll.unemployment:.2f}'],
        ['LPP', '', '7.5%', f'-{payroll.pension:.2f}'],
        ['LAA', '', '0.81%', f'-{payroll.accident_insurance:.2f}'],
        ['Impôt à la source', '', f'{(payroll.tax_deduction/payroll.gross_salary*100):.1f}%', f'-{payroll.tax_deduction:.2f}'],
        ['', '', '', ''],
        ['TOTAL DÉDUCTIONS', '', '', f'-{payroll.gross_salary - payroll.net_salary:.2f}'],
        ['', '', '', ''],
        ['SALAIRE NET', '', '', f'{payroll.net_salary:.2f}']
    ])
    
    salary_table = Table(salary_data, colWidths=[70*mm, 35*mm, 35*mm, 40*mm])
    salary_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 2), (0, 2), 'Helvetica-Bold'),
        ('FONTNAME', (0, 7), (0, 7), 'Helvetica-Bold'),
        ('FONTNAME', (0, 9), (0, 9), 'Helvetica-Bold'),
        ('FONTNAME', (0, -3), (0, -3), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEABOVE', (0, 7), (-1, 7), 1, colors.black),
        ('LINEABOVE', (0, -3), (-1, -3), 1, colors.black),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(salary_table)
    
    # Pied de page
    footer_text = """
    <small>
    Ce bulletin de salaire est établi sous réserve d'erreur ou d'omission.<br/>
    Pour toute question, veuillez contacter le service RH: rh@globibat.ch
    </small>
    """
    story.append(Spacer(1, 20*mm))
    story.append(Paragraph(footer_text, styles['Normal']))
    
    # Générer le PDF
    doc.build(story)
    buffer.seek(0)
    return buffer