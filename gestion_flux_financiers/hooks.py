# Copyright (c) 2026, Votre Organisation
# For license information, please see license.txt

app_name = "gestion_flux_financiers"
app_title = "Gestion des Flux Financiers"
app_publisher = "ASTALAVISTA Group"
app_description = "Hub transverse des demandes financières pour ERPNext"
app_email = "it@astalavista-dz.com"
app_license = "mit"

# DocTypes à exporter automatiquement en fixtures
fixtures = [
    "Workflow",
    "Workflow State",
    "Workflow Action",
    "Workflow Action Master",
    "Role",
    "Custom DocPerm",
    "Workspace",
    "Number Card",
    "Dashboard Chart",
    "Print Format",
    "Client Script",
    "Server Script",
]

# Hooks d'installation
after_install = "gestion_flux_financiers.install.after_install"

# Hooks sur DocTypes natifs (synchronisation inverse)
doc_events = {
    "Payment Entry": {
        "after_submit": "gestion_flux_financiers.utils.sync_payment_to_demande",
        "on_cancel": "gestion_flux_financiers.utils.sync_payment_to_demande",
    },
    "Purchase Invoice": {
        "after_submit": "gestion_flux_financiers.utils.sync_pi_status",
        "on_cancel": "gestion_flux_financiers.utils.sync_pi_status",
    },
    "Expense Claim": {
        "after_submit": "gestion_flux_financiers.utils.sync_ec_status",
        "on_cancel": "gestion_flux_financiers.utils.sync_ec_status",
    },
    "Employee Advance": {
        "after_submit": "gestion_flux_financiers.utils.sync_ea_status",
    },
    "Loan": {
        "after_submit": "gestion_flux_financiers.utils.sync_loan_status",
    },
    "Asset Repair": {
        "after_submit": "gestion_flux_financiers.utils.sync_asset_repair_status",
    },
    "Stock Entry": {
        "after_submit": "gestion_flux_financiers.utils.sync_stock_entry_status",
    },
}

# Tâches planifiées
scheduler_events = {
    "hourly": [
        "gestion_flux_financiers.integrations.leantime.sync_leantime_hourly"
    ],
    "daily": [
        "gestion_flux_financiers.integrations.openerp_n8n.sync_openerp_daily"
    ],
}

# Permissions par défaut (seront surchargées par fixtures)
# has_permission = {
#     "Demande Financière": "gestion_flux_financiers.permissions.demande_financiere_has_permission",
# }

# Jinja
# jinja = {
#     "methods": "gestion_flux_financiers.jinja_methods"
# }
