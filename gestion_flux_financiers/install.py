import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from gestion_flux_financiers.custom_fields import custom_fields

def after_install():
    """Crée les Custom Fields sur les DocTypes natifs ERPNext après installation de l'app."""
    frappe.logger().info("Installation de Gestion des Flux Financiers — création des Custom Fields")
    # ignore_validate=True contourne la validation stricte de l'options Link
    # vers un DocType fraîchement créé par la même app
    create_custom_fields(custom_fields, ignore_validate=True)
    frappe.db.commit()
