import frappe
from frappe.tests.utils import FrappeTestCase

class TestDemandeFinanciere(FrappeTestCase):
    def test_calcul_montant(self):
        df = frappe.get_doc({
            "doctype": "Demande Financière",
            "categorie_flux": "Achat pièces maintenance",
            "demandeur": "Administrator",
            "date_demande": "2026-01-01",
            "lignes_demande": [
                {"designation": "Test", "quantite": 2, "prix_unitaire": 100}
            ]
        })
        df.insert()
        self.assertEqual(df.montant_total_demande, 200)
