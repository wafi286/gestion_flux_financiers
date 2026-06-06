import frappe
import requests

@frappe.whitelist()
def sync_openerp_projects():
    """Synchronise les projets et lignes de commande OpenERP 7 via n8n."""
    config = frappe.get_doc("Configuration Intégration")
    if config.openerp_mode_connexion != "n8n":
        frappe.msgprint("Mode n8n non activé dans la Configuration Intégration.")
        return

    if not config.openerp_n8n_webhook_url or not config.openerp_n8n_api_key:
        frappe.throw("Configuration n8n incomplète (webhook ou clé API manquante).")

    headers = {"X-n8n-Auth": config.openerp_n8n_api_key}

    try:
        # --- Projets ---
        payload = {"action": "get_projects"}
        resp = requests.post(
            config.openerp_n8n_webhook_url,
            json=payload, headers=headers, timeout=60
        )
        resp.raise_for_status()
        data = resp.json()

        for p in data.get("projects", []):
            if not frappe.db.exists("Mapping Projet OpenERP", {"id_projet_openerp": str(p.get("id"))}):
                doc = frappe.new_doc("Mapping Projet OpenERP")
                doc.id_projet_openerp = str(p.get("id"))
                doc.nom_projet = p.get("name", "")
                doc.numero_projet = p.get("code", "")
                doc.client_nom = p.get("client", "")
                doc.date_derniere_sync = frappe.utils.now()
                doc.insert()
            else:
                existing = frappe.get_doc("Mapping Projet OpenERP", {"id_projet_openerp": str(p.get("id"))})
                existing.nom_projet = p.get("name", existing.nom_projet)
                existing.numero_projet = p.get("code", existing.numero_projet)
                existing.client_nom = p.get("client", existing.client_nom)
                existing.date_derniere_sync = frappe.utils.now()
                existing.save()

        # --- Lignes de commande ---
        payload_lines = {"action": "get_sale_order_lines"}
        resp_lines = requests.post(
            config.openerp_n8n_webhook_url,
            json=payload_lines, headers=headers, timeout=60
        )
        resp_lines.raise_for_status()
        lines_data = resp_lines.json()

        for l in lines_data.get("lines", []):
            projet_ref = None
            if l.get("project_id"):
                projet_ref = frappe.db.get_value("Mapping Projet OpenERP", {"id_projet_openerp": str(l.get("project_id"))}, "name")

            if not frappe.db.exists("Mapping Ligne Commande OpenERP", {"id_ligne_openerp": str(l.get("id"))}):
                doc = frappe.new_doc("Mapping Ligne Commande OpenERP")
                doc.id_ligne_openerp = str(l.get("id"))
                doc.projet = projet_ref
                doc.ref_article = l.get("product_code", "")
                doc.designation_originale = l.get("name", "")
                doc.quantite_prevue = l.get("quantity", 0)
                doc.prix_unitaire = l.get("unit_price", 0)
                doc.devise = l.get("currency", "")
                doc.insert()
            else:
                existing = frappe.get_doc("Mapping Ligne Commande OpenERP", {"id_ligne_openerp": str(l.get("id"))})
                existing.projet = projet_ref
                existing.ref_article = l.get("product_code", existing.ref_article)
                existing.designation_originale = l.get("name", existing.designation_originale)
                existing.quantite_prevue = l.get("quantity", existing.quantite_prevue)
                existing.prix_unitaire = l.get("unit_price", existing.prix_unitaire)
                existing.devise = l.get("currency", existing.devise)
                existing.save()

        frappe.msgprint("Synchronisation OpenERP via n8n terminée.")
    except requests.exceptions.RequestException as e:
        frappe.throw(f"Erreur de connexion n8n/OpenERP : {str(e)}")


def sync_openerp_daily():
    """Hook scheduler_events daily."""
    config = frappe.get_doc("Configuration Intégration")
    if config.frequence_sync_auto == "Quotidien":
        sync_openerp_projects()
