import frappe

def sync_payment_to_demande(doc, method):
    """Met à jour le reste à payer et le workflow_state d'une Demande Financière
    lorsqu'un Payment Entry est soumis ou annulé."""
    if not doc.custom_demande_source:
        return

    total_paid = frappe.db.sql("""
        SELECT SUM(paid_amount) 
        FROM `tabPayment Entry` 
        WHERE custom_demande_source = %s AND docstatus = 1
    """, doc.custom_demande_source)[0][0] or 0

    demande = frappe.get_doc("Demande Financière", doc.custom_demande_source)
    demande.reste_a_payer = max(0, demande.montant_total_demande - total_paid)

    if demande.reste_a_payer <= 0 and demande.workflow_state == "En paiement":
        demande.workflow_state = "Payée"
    elif demande.reste_a_payer > 0 and method == "on_cancel" and demande.workflow_state == "Payée":
        demande.workflow_state = "En paiement"

    demande.save(ignore_permissions=True)


def sync_pi_status(doc, method):
    """Synchronise le statut depuis Purchase Invoice vers Demande Financière."""
    if not doc.custom_demande_source:
        return
    demande = frappe.get_doc("Demande Financière", doc.custom_demande_source)
    if method == "after_submit":
        demande.document_natif_reference = doc.name
    elif method == "on_cancel":
        demande.document_natif_reference = ""
    demande.save(ignore_permissions=True)


def sync_ec_status(doc, method):
    if not doc.custom_demande_source:
        return
    demande = frappe.get_doc("Demande Financière", doc.custom_demande_source)
    if method == "after_submit":
        demande.document_natif_reference = doc.name
    elif method == "on_cancel":
        demande.document_natif_reference = ""
    demande.save(ignore_permissions=True)


def sync_ea_status(doc, method):
    if not doc.custom_demande_source:
        return
    demande = frappe.get_doc("Demande Financière", doc.custom_demande_source)
    demande.document_natif_reference = doc.name
    demande.save(ignore_permissions=True)


def sync_loan_status(doc, method):
    if not doc.custom_demande_source:
        return
    demande = frappe.get_doc("Demande Financière", doc.custom_demande_source)
    demande.document_natif_reference = doc.name
    demande.save(ignore_permissions=True)


def sync_asset_repair_status(doc, method):
    if not doc.custom_demande_source:
        return
    demande = frappe.get_doc("Demande Financière", doc.custom_demande_source)
    if method == "after_submit":
        demande.document_natif_reference = doc.name
    demande.save(ignore_permissions=True)


def sync_stock_entry_status(doc, method):
    if not doc.custom_demande_source:
        return
    demande = frappe.get_doc("Demande Financière", doc.custom_demande_source)
    if method == "after_submit":
        demande.document_natif_reference = doc.name
    demande.save(ignore_permissions=True)
