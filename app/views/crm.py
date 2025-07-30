"""
Blueprint CRM - Gestion clients, projets, factures
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from app import db
from app.models import (
    Client, Contact, ClientNote, 
    Project, ProjectPhase, ProjectTask,
    Quote, QuoteItem, Invoice, InvoiceItem,
    Payment, Expense
)
from app.utils.decorators import permission_required
from app.utils.pdf import generate_invoice_pdf, generate_quote_pdf
from datetime import datetime, date, timedelta
import json
from decimal import Decimal

bp = Blueprint('crm', __name__, url_prefix='/crm')

# =======================
# CLIENTS
# =======================

@bp.route('/clients')
@login_required
@permission_required('crm.view')
def clients_list():
    """Liste des clients"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', 'all')
    
    query = Client.query
    
    if search:
        query = query.filter(
            db.or_(
                Client.company_name.ilike(f'%{search}%'),
                Client.first_name.ilike(f'%{search}%'),
                Client.last_name.ilike(f'%{search}%'),
                Client.primary_email.ilike(f'%{search}%')
            )
        )
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    clients = query.order_by(Client.company_name).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('crm/clients/list.html', clients=clients)

@bp.route('/clients/new', methods=['GET', 'POST'])
@login_required
@permission_required('crm.edit')
def client_new():
    """Nouveau client"""
    if request.method == 'POST':
        client = Client()
        client.client_type = request.form.get('client_type')
        
        # Générer le code client
        last_client = Client.query.order_by(Client.id.desc()).first()
        client.client_code = f"CLI-{datetime.now().year}-{(last_client.id if last_client else 0) + 1:04d}"
        
        # Informations selon le type
        if client.client_type == 'company':
            client.company_name = request.form.get('company_name')
            client.company_registration = request.form.get('company_registration')
            client.vat_number = request.form.get('vat_number')
        else:
            client.first_name = request.form.get('first_name')
            client.last_name = request.form.get('last_name')
            client.title = request.form.get('title')
        
        # Contact
        client.primary_email = request.form.get('primary_email')
        client.primary_phone = request.form.get('primary_phone')
        client.website = request.form.get('website')
        
        # Adresse
        client.address = request.form.get('address')
        client.postal_code = request.form.get('postal_code')
        client.city = request.form.get('city')
        client.canton = request.form.get('canton')
        
        # Commercial
        client.lead_source = request.form.get('lead_source')
        client.assigned_to_id = current_user.id
        
        db.session.add(client)
        db.session.commit()
        
        flash('Client créé avec succès!', 'success')
        return redirect(url_for('crm.client_detail', client_id=client.id))
    
    return render_template('crm/clients/form.html')

@bp.route('/clients/<int:client_id>')
@login_required
@permission_required('crm.view')
def client_detail(client_id):
    """Détail d'un client"""
    client = Client.query.get_or_404(client_id)
    
    # Projets du client
    projects = Project.query.filter_by(client_id=client_id).order_by(
        Project.created_at.desc()
    ).all()
    
    # Devis et factures
    quotes = Quote.query.filter_by(client_id=client_id).order_by(
        Quote.issue_date.desc()
    ).limit(10).all()
    
    invoices = Invoice.query.filter_by(client_id=client_id).order_by(
        Invoice.issue_date.desc()
    ).limit(10).all()
    
    # Notes récentes
    notes = ClientNote.query.filter_by(client_id=client_id).order_by(
        ClientNote.created_at.desc()
    ).limit(10).all()
    
    # Statistiques
    stats = {
        'total_projects': len(projects),
        'active_projects': len([p for p in projects if p.status == 'in_progress']),
        'total_revenue': sum(i.total_amount for i in invoices if i.status == 'paid'),
        'outstanding': client.calculate_outstanding_balance()
    }
    
    return render_template('crm/clients/detail.html',
                         client=client,
                         projects=projects,
                         quotes=quotes,
                         invoices=invoices,
                         notes=notes,
                         stats=stats)

@bp.route('/clients/<int:client_id>/note', methods=['POST'])
@login_required
@permission_required('crm.edit')
def client_add_note(client_id):
    """Ajouter une note client"""
    client = Client.query.get_or_404(client_id)
    
    note = ClientNote(
        client_id=client_id,
        note_type=request.form.get('note_type'),
        subject=request.form.get('subject'),
        content=request.form.get('content'),
        created_by_id=current_user.id
    )
    
    # Suivi
    follow_up_date = request.form.get('follow_up_date')
    if follow_up_date:
        note.follow_up_date = datetime.strptime(follow_up_date, '%Y-%m-%d').date()
    
    db.session.add(note)
    
    # Mettre à jour la date de dernier contact
    client.last_contact_date = date.today()
    
    db.session.commit()
    
    flash('Note ajoutée avec succès!', 'success')
    return redirect(url_for('crm.client_detail', client_id=client_id))

# =======================
# PROJETS
# =======================

@bp.route('/projects')
@login_required
@permission_required('crm.view')
def projects_list():
    """Liste des projets"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    
    query = Project.query
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    projects = query.order_by(Project.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('crm/projects/list.html', projects=projects)

@bp.route('/projects/new', methods=['GET', 'POST'])
@login_required
@permission_required('crm.edit')
def project_new():
    """Nouveau projet"""
    if request.method == 'POST':
        project = Project()
        
        # Informations générales
        project.name = request.form.get('name')
        project.description = request.form.get('description')
        project.project_type = request.form.get('project_type')
        project.building_type = request.form.get('building_type')
        
        # Client
        project.client_id = request.form.get('client_id', type=int)
        
        # Adresse du chantier
        project.site_address = request.form.get('site_address')
        project.site_postal_code = request.form.get('site_postal_code')
        project.site_city = request.form.get('site_city')
        project.site_canton = request.form.get('site_canton')
        
        # Dates
        start_date = request.form.get('start_date')
        if start_date:
            project.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        end_date = request.form.get('planned_end_date')
        if end_date:
            project.planned_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Budget
        project.estimated_budget = request.form.get('estimated_budget', type=float)
        
        # Responsables
        project.project_manager_id = request.form.get('project_manager_id', type=int)
        project.created_by_id = current_user.id
        
        db.session.add(project)
        db.session.commit()
        
        flash('Projet créé avec succès!', 'success')
        return redirect(url_for('crm.project_detail', project_id=project.id))
    
    # Liste des clients pour le formulaire
    clients = Client.query.filter_by(status='active').order_by(Client.company_name).all()
    users = User.query.filter_by(is_active=True).all()
    
    return render_template('crm/projects/form.html', clients=clients, users=users)

@bp.route('/projects/<int:project_id>')
@login_required
@permission_required('crm.view')
def project_detail(project_id):
    """Détail d'un projet"""
    project = Project.query.get_or_404(project_id)
    
    # Phases du projet
    phases = ProjectPhase.query.filter_by(project_id=project_id).order_by(
        ProjectPhase.phase_order
    ).all()
    
    # Tâches
    tasks = ProjectTask.query.filter_by(project_id=project_id).order_by(
        ProjectTask.due_date
    ).all()
    
    # Documents
    documents = ProjectDocument.query.filter_by(project_id=project_id).order_by(
        ProjectDocument.uploaded_at.desc()
    ).all()
    
    # Statistiques
    stats = {
        'tasks_total': len(tasks),
        'tasks_completed': len([t for t in tasks if t.status == 'completed']),
        'budget_used': project.current_cost or 0,
        'budget_percentage': ((project.current_cost or 0) / project.approved_budget * 100) if project.approved_budget else 0
    }
    
    return render_template('crm/projects/detail.html',
                         project=project,
                         phases=phases,
                         tasks=tasks,
                         documents=documents,
                         stats=stats)

@bp.route('/projects/<int:project_id>/task', methods=['POST'])
@login_required
@permission_required('crm.edit')
def project_add_task(project_id):
    """Ajouter une tâche au projet"""
    project = Project.query.get_or_404(project_id)
    
    task = ProjectTask(
        project_id=project_id,
        title=request.form.get('title'),
        description=request.form.get('description'),
        task_type=request.form.get('task_type'),
        assigned_to_id=request.form.get('assigned_to_id', type=int),
        priority=request.form.get('priority', 'normal')
    )
    
    # Dates
    due_date = request.form.get('due_date')
    if due_date:
        task.due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
    
    db.session.add(task)
    db.session.commit()
    
    flash('Tâche ajoutée avec succès!', 'success')
    return redirect(url_for('crm.project_detail', project_id=project_id))

# =======================
# DEVIS
# =======================

@bp.route('/quotes')
@login_required
@permission_required('crm.view')
def quotes_list():
    """Liste des devis"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    
    query = Quote.query
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    quotes = query.order_by(Quote.issue_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('crm/quotes/list.html', quotes=quotes)

@bp.route('/quotes/new', methods=['GET', 'POST'])
@login_required
@permission_required('crm.edit')
def quote_new():
    """Nouveau devis"""
    if request.method == 'POST':
        quote = Quote()
        
        # Client
        quote.client_id = request.form.get('client_id', type=int)
        
        # Projet
        quote.project_name = request.form.get('project_name')
        quote.project_description = request.form.get('project_description')
        
        # Validité
        valid_days = request.form.get('valid_days', 30, type=int)
        quote.valid_until = date.today() + timedelta(days=valid_days)
        
        # Textes
        quote.introduction_text = request.form.get('introduction_text')
        quote.payment_terms = request.form.get('payment_terms', 'Paiement à 30 jours')
        
        # TVA
        quote.tax_rate = request.form.get('tax_rate', 7.7, type=float)
        
        quote.created_by_id = current_user.id
        
        db.session.add(quote)
        db.session.flush()  # Pour obtenir l'ID
        
        # Ajouter les lignes
        items_data = json.loads(request.form.get('items', '[]'))
        for idx, item_data in enumerate(items_data):
            item = QuoteItem(
                quote_id=quote.id,
                description=item_data['description'],
                quantity=item_data['quantity'],
                unit=item_data['unit'],
                unit_price=Decimal(str(item_data['unit_price'])),
                position=idx
            )
            item.calculate_total()
            db.session.add(item)
        
        # Calculer les totaux
        quote.calculate_totals()
        
        db.session.commit()
        
        flash('Devis créé avec succès!', 'success')
        return redirect(url_for('crm.quote_detail', quote_id=quote.id))
    
    # Liste des clients
    clients = Client.query.filter_by(status='active').order_by(Client.company_name).all()
    
    return render_template('crm/quotes/form.html', clients=clients)

@bp.route('/quotes/<int:quote_id>')
@login_required
@permission_required('crm.view')
def quote_detail(quote_id):
    """Détail d'un devis"""
    quote = Quote.query.get_or_404(quote_id)
    
    # Vérifier l'expiration
    quote.check_expiry()
    db.session.commit()
    
    return render_template('crm/quotes/detail.html', quote=quote)

@bp.route('/quotes/<int:quote_id>/pdf')
@login_required
@permission_required('crm.view')
def quote_pdf(quote_id):
    """Générer le PDF d'un devis"""
    quote = Quote.query.get_or_404(quote_id)
    
    # Générer le PDF
    pdf_buffer = generate_quote_pdf(quote)
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'devis_{quote.quote_number}.pdf'
    )

@bp.route('/quotes/<int:quote_id>/accept', methods=['POST'])
@login_required
@permission_required('crm.edit')
def quote_accept(quote_id):
    """Accepter un devis"""
    quote = Quote.query.get_or_404(quote_id)
    
    quote.status = 'accepted'
    quote.accepted_at = datetime.utcnow()
    
    # Créer le projet si demandé
    if request.form.get('create_project') == 'yes':
        project = Project(
            name=quote.project_name,
            description=quote.project_description,
            client_id=quote.client_id,
            estimated_budget=quote.total_amount,
            approved_budget=quote.total_amount,
            created_by_id=current_user.id
        )
        db.session.add(project)
        db.session.flush()
        
        quote.converted_to_project_id = project.id
    
    db.session.commit()
    
    flash('Devis accepté!', 'success')
    return redirect(url_for('crm.quote_detail', quote_id=quote_id))

# =======================
# FACTURES
# =======================

@bp.route('/invoices')
@login_required
@permission_required('finance.view')
def invoices_list():
    """Liste des factures"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    
    query = Invoice.query
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    invoices = query.order_by(Invoice.issue_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Statistiques
    stats = {
        'total_pending': db.session.query(
            func.sum(Invoice.total_amount - Invoice.paid_amount)
        ).filter(
            Invoice.status.in_(['sent', 'partial', 'overdue'])
        ).scalar() or 0,
        'overdue_count': Invoice.query.filter_by(status='overdue').count()
    }
    
    return render_template('crm/invoices/list.html', 
                         invoices=invoices,
                         stats=stats)

@bp.route('/invoices/new', methods=['GET', 'POST'])
@login_required
@permission_required('finance.edit')
def invoice_new():
    """Nouvelle facture"""
    if request.method == 'POST':
        invoice = Invoice()
        
        # Client et projet
        invoice.client_id = request.form.get('client_id', type=int)
        invoice.project_id = request.form.get('project_id', type=int)
        
        # Dates
        invoice.due_date = date.today() + timedelta(days=30)
        
        # TVA
        invoice.tax_rate = request.form.get('tax_rate', 7.7, type=float)
        
        # Devis source
        quote_id = request.form.get('quote_id', type=int)
        if quote_id:
            invoice.quote_id = quote_id
        
        invoice.created_by_id = current_user.id
        
        db.session.add(invoice)
        db.session.flush()
        
        # Ajouter les lignes
        if quote_id:
            # Copier depuis le devis
            quote = Quote.query.get(quote_id)
            for quote_item in quote.items:
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    description=quote_item.description,
                    quantity=quote_item.quantity,
                    unit=quote_item.unit,
                    unit_price=quote_item.unit_price,
                    position=quote_item.position
                )
                item.calculate_total()
                db.session.add(item)
        else:
            # Nouvelles lignes
            items_data = json.loads(request.form.get('items', '[]'))
            for idx, item_data in enumerate(items_data):
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    description=item_data['description'],
                    quantity=item_data['quantity'],
                    unit=item_data['unit'],
                    unit_price=Decimal(str(item_data['unit_price'])),
                    position=idx
                )
                item.calculate_total()
                db.session.add(item)
        
        # Calculer les totaux
        invoice.calculate_totals()
        
        db.session.commit()
        
        flash('Facture créée avec succès!', 'success')
        return redirect(url_for('crm.invoice_detail', invoice_id=invoice.id))
    
    # Données pour le formulaire
    clients = Client.query.filter_by(status='active').order_by(Client.company_name).all()
    projects = Project.query.filter_by(status='in_progress').all()
    quotes = Quote.query.filter_by(status='accepted').filter(
        ~Quote.invoices.any()
    ).all()
    
    return render_template('crm/invoices/form.html',
                         clients=clients,
                         projects=projects,
                         quotes=quotes)

@bp.route('/invoices/<int:invoice_id>')
@login_required
@permission_required('finance.view')
def invoice_detail(invoice_id):
    """Détail d'une facture"""
    invoice = Invoice.query.get_or_404(invoice_id)
    
    # Mettre à jour le statut
    invoice.update_status()
    db.session.commit()
    
    return render_template('crm/invoices/detail.html', invoice=invoice)

@bp.route('/invoices/<int:invoice_id>/pdf')
@login_required
@permission_required('finance.view')
def invoice_pdf(invoice_id):
    """Générer le PDF d'une facture"""
    invoice = Invoice.query.get_or_404(invoice_id)
    
    # Générer le PDF avec QR-facture suisse
    pdf_buffer = generate_invoice_pdf(invoice)
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'facture_{invoice.invoice_number}.pdf'
    )

@bp.route('/invoices/<int:invoice_id>/payment', methods=['POST'])
@login_required
@permission_required('finance.edit')
def invoice_add_payment(invoice_id):
    """Ajouter un paiement"""
    invoice = Invoice.query.get_or_404(invoice_id)
    
    payment = Payment(
        invoice_id=invoice_id,
        amount=request.form.get('amount', type=float),
        payment_method=request.form.get('payment_method'),
        bank_reference=request.form.get('bank_reference'),
        recorded_by_id=current_user.id
    )
    
    payment_date = request.form.get('payment_date')
    if payment_date:
        payment.payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
    
    db.session.add(payment)
    
    # Mettre à jour le montant payé
    invoice.paid_amount += payment.amount
    invoice.update_status()
    
    db.session.commit()
    
    flash('Paiement enregistré avec succès!', 'success')
    return redirect(url_for('crm.invoice_detail', invoice_id=invoice_id))