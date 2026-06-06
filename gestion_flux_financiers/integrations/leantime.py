import frappe
import requests

@frappe.whitelist()
def sync_leantime():
    """Bouton manuel + tâche planifiée pour synchroniser Leantime."""
    config = frappe.get_doc("Configuration Intégration")
    if not config.leantime_url or not config.leantime_api_key:
        frappe.throw("Configuration Leantime incomplète (URL ou clé API manquante).")

    headers = {"apiKey": config.leantime_api_key}
    base_url = config.leantime_url.rstrip("/")

    try:
        # --- Projets ---
        resp = requests.get(f"{base_url}/api/projects", headers=headers, timeout=30)
        resp.raise_for_status()
        projects = resp.json()

        for p in projects:
            if not frappe.db.exists("Mapping Projet Leantime", {"id_projet_leantime": str(p.get("id"))}):
                doc = frappe.new_doc("Mapping Projet Leantime")
                doc.id_projet_leantime = str(p.get("id"))
                doc.nom_projet = p.get("name", "Sans nom")
                doc.description = p.get("details", "")
                doc.date_derniere_sync = frappe.utils.now()
                doc.insert()
            else:
                existing = frappe.get_doc("Mapping Projet Leantime", {"id_projet_leantime": str(p.get("id"))})
                existing.nom_projet = p.get("name", existing.nom_projet)
                existing.description = p.get("details", existing.description)
                existing.date_derniere_sync = frappe.utils.now()
                existing.save()

        # --- Tâches par projet ---
        for projet in frappe.get_all("Mapping Projet Leantime", fields=["name", "id_projet_leantime"]):
            resp = requests.get(
                f"{base_url}/api/tickets?projectId={projet.id_projet_leantime}",
                headers=headers, timeout=30
            )
            resp.raise_for_status()
            tickets = resp.json()

            for t in tickets:
                if not frappe.db.exists("Mapping Tâche Leantime", {"id_tache_leantime": str(t.get("id"))}):
                    doc = frappe.new_doc("Mapping Tâche Leantime")
                    doc.id_tache_leantime = str(t.get("id"))
                    doc.nom_tache = t.get("headline", "Sans nom")
                    doc.projet = projet.name
                    doc.statut = t.get("status", "")
                    doc.insert()
                else:
                    existing = frappe.get_doc("Mapping Tâche Leantime", {"id_tache_leantime": str(t.get("id"))})
                    existing.nom_tache = t.get("headline", existing.nom_tache)
                    existing.statut = t.get("status", existing.statut)
                    existing.save()

        frappe.msgprint("Synchronisation Leantime terminée avec succès.")
    except requests.exceptions.RequestException as e:
        frappe.throw(f"Erreur de connexion Leantime : {str(e)}")


def sync_leantime_hourly():
    """Hook scheduler_events hourly."""
    config = frappe.get_doc("Configuration Intégration")
    if config.frequence_sync_auto == "Toutes les heures":
        sync_leantime()
