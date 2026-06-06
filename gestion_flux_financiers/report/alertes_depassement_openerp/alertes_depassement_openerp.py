import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "id_ligne", "label": "ID Ligne", "fieldtype": "Data", "width": 120},
        {"fieldname": "projet", "label": "Projet", "fieldtype": "Link", "options": "Mapping Projet OpenERP", "width": 150},
        {"fieldname": "designation", "label": "Désignation", "fieldtype": "Data", "width": 200},
        {"fieldname": "quantite_prevue", "label": "Qté Prévue", "fieldtype": "Float", "width": 100},
        {"fieldname": "quantite_restante", "label": "Qté Restante", "fieldtype": "Float", "width": 100},
        {"fieldname": "depassement", "label": "Dépassement", "fieldtype": "Float", "width": 100},
    ]

    data = frappe.db.sql("""
        SELECT
            name AS id_ligne,
            projet,
            designation_originale AS designation,
            quantite_prevue,
            quantite_restante,
            ABS(quantite_restante) AS depassement
        FROM `tabMapping Ligne Commande OpenERP`
        WHERE quantite_restante < 0
        ORDER BY quantite_restante ASC
    """, as_dict=1)

    return columns, data
