custom_fields = {
    "Purchase Invoice": [
        {
            "fieldname": "custom_demande_source",
            "label": "Demande Source",
            "fieldtype": "Link",
            "options": "Demande Financière",
            "insert_after": "title",
            "read_only": 1,
            "no_copy": 1,
        },
        {
            "fieldname": "custom_type_flux",
            "label": "Type de Flux",
            "fieldtype": "Data",
            "insert_after": "custom_demande_source",
            "read_only": 1,
        },
    ],
    "Expense Claim": [
        {
            "fieldname": "custom_demande_source",
            "label": "Demande Source",
            "fieldtype": "Link",
            "options": "Demande Financière",
            "insert_after": "employee_name",
            "read_only": 1,
            "no_copy": 1,
        },
    ],
    "Employee Advance": [
        {
            "fieldname": "custom_demande_source",
            "label": "Demande Source",
            "fieldtype": "Link",
            "options": "Demande Financière",
            "insert_after": "employee_name",
            "read_only": 1,
            "no_copy": 1,
        },
    ],
    "Loan": [
        {
            "fieldname": "custom_demande_source",
            "label": "Demande Source",
            "fieldtype": "Link",
            "options": "Demande Financière",
            "insert_after": "applicant_name",
            "read_only": 1,
            "no_copy": 1,
        },
    ],
    "Stock Entry": [
        {
            "fieldname": "custom_demande_source",
            "label": "Demande Source",
            "fieldtype": "Link",
            "options": "Demande Financière",
            "insert_after": "title",
            "read_only": 1,
            "no_copy": 1,
        },
        {
            "fieldname": "custom_vehicule",
            "label": "Véhicule",
            "fieldtype": "Link",
            "options": "Asset",
            "insert_after": "custom_demande_source",
            "depends_on": "eval:doc.stock_entry_type=='Material Issue'",
        },
    ],
    "Asset Repair": [
        {
            "fieldname": "custom_demande_source",
            "label": "Demande Source",
            "fieldtype": "Link",
            "options": "Demande Financière",
            "insert_after": "asset_name",
            "read_only": 1,
            "no_copy": 1,
        },
    ],
    "Payment Entry": [
        {
            "fieldname": "custom_demande_source",
            "label": "Demande Source",
            "fieldtype": "Link",
            "options": "Demande Financière",
            "insert_after": "title",
            "read_only": 1,
            "no_copy": 1,
        },
    ],
}
