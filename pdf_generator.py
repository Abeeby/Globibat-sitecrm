"""
Module de génération de fiches de paie PDF pour Globibat
Utilise ReportLab pour créer des PDF professionnels
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime, date, timedelta
import os
import io

def generate_payslip(employe, mois, annee, heures_travaillees, salaire_horaire=15.0):
    """
    Génère une fiche de paie PDF pour un employé
    
    Args:
        employe: Objet employé
        mois: Numéro du mois (1-12)
        annee: Année
        heures_travaillees: Total des heures travaillées
        salaire_horaire: Taux horaire (défaut: 15€)
    
    Returns:
        BytesIO object contenant le PDF
    """
    
    # Créer le buffer
    buffer = io.BytesIO()
    
    # Créer le document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    # Conteneur pour les éléments
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#0d6efd'),
        spaceAfter=30
    )
    
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#0d6efd'),
        spaceAfter=12
    )
    
    # En-tête
    elements.append(Paragraph("FICHE DE PAIE", title_style))
    elements.append(Paragraph(f"{get_month_name(mois)} {annee}", styles['Heading3']))
    elements.append(Spacer(1, 20))
    
    # Informations entreprise
    company_data = [
        ['ENTREPRISE', ''],
        ['Raison sociale:', 'GLOBIBAT SAS'],
        ['Adresse:', '123 Avenue des Champs'],
        ['', '75001 PARIS'],
        ['SIRET:', '123 456 789 00012'],
        ['Code APE:', '4120A'],
    ]
    
    company_table = Table(company_data, colWidths=[60*mm, 80*mm])
    company_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 12),
        ('ALIGN', (0, 0), (1, 0), 'LEFT'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    elements.append(company_table)
    elements.append(Spacer(1, 20))
    
    # Informations salarié
    employee_data = [
        ['SALARIE', ''],
        ['Matricule:', employe.matricule],
        ['Nom:', f"{employe.nom} {employe.prenom}"],
        ['Département:', employe.departement or 'Non défini'],
        ['Date d\'embauche:', employe.date_embauche.strftime('%d/%m/%Y')],
        ['Poste:', 'Employé'],
    ]
    
    employee_table = Table(employee_data, colWidths=[60*mm, 80*mm])
    employee_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (1, 0)),
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 12),
        ('ALIGN', (0, 0), (1, 0), 'LEFT'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    elements.append(employee_table)
    elements.append(Spacer(1, 30))
    
    # Calculs de salaire
    salaire_brut = heures_travaillees * salaire_horaire
    
    # Cotisations (approximations)
    cotis_maladie = salaire_brut * 0.0075
    cotis_vieillesse = salaire_brut * 0.0690
    cotis_chomage = salaire_brut * 0.0240
    cotis_retraite = salaire_brut * 0.0375
    csg_deductible = salaire_brut * 0.0510
    csg_non_deductible = salaire_brut * 0.024
    crds = salaire_brut * 0.005
    
    total_cotisations = (cotis_maladie + cotis_vieillesse + 
                        cotis_chomage + cotis_retraite + 
                        csg_deductible + csg_non_deductible + crds)
    
    salaire_net = salaire_brut - total_cotisations
    
    # Tableau des éléments de paie
    elements.append(Paragraph("ELEMENTS DE REMUNERATION", header_style))
    
    remuneration_data = [
        ['Libellé', 'Base', 'Taux', 'Montant'],
        ['Salaire de base', f'{heures_travaillees:.2f}', f'{salaire_horaire:.2f} €', f'{salaire_brut:.2f} €'],
        ['', '', '', ''],
        ['SALAIRE BRUT', '', '', f'{salaire_brut:.2f} €'],
    ]
    
    remuneration_table = Table(remuneration_data, colWidths=[70*mm, 30*mm, 30*mm, 40*mm])
    remuneration_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 3), (0, 3), 'Helvetica-Bold'),
        ('FONTNAME', (3, 3), (3, 3), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LINEABOVE', (0, 3), (-1, 3), 2, colors.black),
    ]))
    
    elements.append(remuneration_table)
    elements.append(Spacer(1, 20))
    
    # Tableau des cotisations
    elements.append(Paragraph("COTISATIONS SOCIALES", header_style))
    
    cotisations_data = [
        ['Libellé', 'Base', 'Taux salarial', 'Part salariale'],
        ['Maladie', f'{salaire_brut:.2f}', '0.75%', f'{cotis_maladie:.2f} €'],
        ['Vieillesse', f'{salaire_brut:.2f}', '6.90%', f'{cotis_vieillesse:.2f} €'],
        ['Chômage', f'{salaire_brut:.2f}', '2.40%', f'{cotis_chomage:.2f} €'],
        ['Retraite complémentaire', f'{salaire_brut:.2f}', '3.75%', f'{cotis_retraite:.2f} €'],
        ['CSG déductible', f'{salaire_brut:.2f}', '5.10%', f'{csg_deductible:.2f} €'],
        ['CSG non déductible', f'{salaire_brut:.2f}', '2.40%', f'{csg_non_deductible:.2f} €'],
        ['CRDS', f'{salaire_brut:.2f}', '0.50%', f'{crds:.2f} €'],
        ['', '', '', ''],
        ['TOTAL COTISATIONS', '', '', f'{total_cotisations:.2f} €'],
    ]
    
    cotisations_table = Table(cotisations_data, colWidths=[70*mm, 30*mm, 30*mm, 40*mm])
    cotisations_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 9), (0, 9), 'Helvetica-Bold'),
        ('FONTNAME', (3, 9), (3, 9), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LINEABOVE', (0, 9), (-1, 9), 2, colors.black),
    ]))
    
    elements.append(cotisations_table)
    elements.append(Spacer(1, 30))
    
    # Résumé net à payer
    net_data = [
        ['NET A PAYER', f'{salaire_net:.2f} €'],
    ]
    
    net_table = Table(net_data, colWidths=[130*mm, 40*mm])
    net_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#28a745')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (0, 0), 12),
        ('RIGHTPADDING', (1, 0), (1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    elements.append(net_table)
    elements.append(Spacer(1, 40))
    
    # Pied de page
    footer_text = f"""
    <para align="center">
    <font size="8">
    Date de paiement : {get_last_day_of_month(mois, annee).strftime('%d/%m/%Y')}<br/>
    Mode de paiement : Virement bancaire<br/>
    <br/>
    <b>CONSERVER CE BULLETIN SANS LIMITATION DE DUREE</b>
    </font>
    </para>
    """
    
    elements.append(Paragraph(footer_text, styles['Normal']))
    
    # Générer le PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer

def get_month_name(month):
    """Retourne le nom du mois en français"""
    months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
              'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
    return months[month - 1]

def get_last_day_of_month(month, year):
    """Retourne le dernier jour du mois"""
    if month == 12:
        return date(year, 12, 31)
    else:
        return date(year, month + 1, 1) - timedelta(days=1)

def generate_all_payslips(employes_data, mois, annee, salaire_horaire=15.0):
    """
    Génère les fiches de paie pour tous les employés
    
    Args:
        employes_data: Liste de tuples (employe, heures_travaillees)
        mois: Numéro du mois
        annee: Année
        salaire_horaire: Taux horaire
    
    Returns:
        BytesIO object contenant toutes les fiches de paie
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    for i, (employe, heures) in enumerate(employes_data):
        if i > 0:
            elements.append(PageBreak())
        
        # Générer la fiche pour cet employé
        payslip_buffer = generate_payslip(employe, mois, annee, heures, salaire_horaire)
        # Note: Pour combiner plusieurs PDFs, utilisez PyPDF2 ou reportlab plus avancé
    
    return buffer 