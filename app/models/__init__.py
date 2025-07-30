"""
Modèles de données pour Globibat CRM
"""
from .user import User, Role
from .employee import Employee, Attendance, Leave, Payroll
from .client import Client, Contact, ClientNote
from .project import Project, ProjectPhase, ProjectTask, ProjectDocument
from .finance import Invoice, Quote, Expense, Payment
from .inventory import Material, Equipment, Supplier, PurchaseOrder
from .planning import Schedule, Meeting, Reminder

__all__ = [
    'User', 'Role',
    'Employee', 'Attendance', 'Leave', 'Payroll',
    'Client', 'Contact', 'ClientNote',
    'Project', 'ProjectPhase', 'ProjectTask', 'ProjectDocument',
    'Invoice', 'Quote', 'Expense', 'Payment',
    'Material', 'Equipment', 'Supplier', 'PurchaseOrder',
    'Schedule', 'Meeting', 'Reminder'
]