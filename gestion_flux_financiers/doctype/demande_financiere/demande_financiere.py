import frappe
from frappe.model.document import Document

class DemandeFinanciere(Document):
    def validate(self):
        self.calculate_totals()
        self.validate_rejet()
        self.validate_depassement_openerp()

    def calculate_totals(self):
        total = 0.0
        for ligne in self.lignes_demande:
            if ligne.quantite and ligne.prix_unitaire:
                ligne.montant_ligne = ligne.quantite * ligne.prix_unitaire
            else:
                ligne.montant_ligne = 0.0
            total += ligne.montant_ligne or 0.0
        self.montant_total_demande = total

    def validate_rejet(self):
        if self.workflow_state == "Rejetée" and not self.motif_rejet:
            frappe.throw("Le motif de rejet est obligatoire pour passer à l'état Rejetée.")

    def validate_depassement_openerp(self):
        for ligne in self.lignes_demande:
            if ligne.ligne_commande_openerp and ligne.quantite:
                mapping = frappe.get_doc("Mapping Ligne Commande OpenERP", ligne.ligne_commande_openerp)
                if mapping.quantite_restante is not None and ligne.quantite > mapping.quantite_restante:
                    frappe.msgprint(
                        f"Alerte : la ligne {ligne.designation or ligne.idx} dépasse la quantité restante OpenERP ({mapping.quantite_restante}).",
                        indicator="orange",
                        alert=True
                    )

    def on_update(self):
        if self.workflow_state == "Validée" and not self.document_natif_reference:
            self.generate_native_document()
            self.workflow_state = "En traitement"
            self.save()

    def generate_native_document(self):
        type_flux = frappe.get_doc("Type de Flux", self.categorie_flux)
        cible = type_flux.doctype_natif_cible

        if cible == "Purchase Invoice":
            self.create_purchase_invoice(type_flux)
        elif cible == "Expense Claim":
            self.create_expense_claim()
        elif cible == "Employee Advance":
            self.create_employee_advance()
        elif cible == "Loan":
            self.create_loan()
        elif cible == "Asset Repair":
            self.create_asset_repair()
        elif cible == "Stock Entry":
            self.create_stock_entry()
        elif cible == "Subscription":
            self.create_subscription()
        else:
            frappe.msgprint(f"Aucun document natif généré pour la cible : {cible}")
            return

        self.document_natif_genere = cible

    def create_purchase_invoice(self, type_flux):
        if not self.beneficiaire:
            frappe.throw("Bénéficiaire (Supplier) obligatoire pour générer une Purchase Invoice.")

        pi = frappe.new_doc("Purchase Invoice")
        pi.supplier = self.beneficiaire
        pi.posting_date = self.date_demande
        pi.due_date = self.date_paiement_prevue
        pi.custom_demande_source = self.name
        pi.custom_type_flux = self.categorie_flux

        for ligne in self.lignes_demande:
            sous_type = frappe.db.get_value("Sous Type Flux", {
                "parent": self.categorie_flux,
                "sous_type_nom": ligne.get("sous_type") or ""
            }, "item_code_par_defaut") or "Service générique"

            pi.append("items", {
                "item_code": sous_type,
                "description": ligne.designation,
                "qty": ligne.quantite,
                "rate": ligne.prix_unitaire,
                "amount": ligne.montant_ligne,
            })

        pi.insert(ignore_permissions=True)
        pi.submit()
        self.document_natif_reference = pi.name
        frappe.msgprint(f"Purchase Invoice {pi.name} créée.")

    def create_expense_claim(self):
        if not self.employe:
            frappe.throw("Employé obligatoire pour générer une Expense Claim.")

        ec = frappe.new_doc("Expense Claim")
        ec.employee = self.employe
        ec.posting_date = self.date_demande
        ec.custom_demande_source = self.name

        for ligne in self.lignes_demande:
            ec.append("expenses", {
                "expense_type": "Frais de mission",
                "description": ligne.designation,
                "amount": ligne.montant_ligne,
                "sanctioned_amount": ligne.montant_ligne,
            })

        ec.insert(ignore_permissions=True)
        ec.submit()
        self.document_natif_reference = ec.name
        frappe.msgprint(f"Expense Claim {ec.name} créée.")

    def create_employee_advance(self):
        if not self.employe:
            frappe.throw("Employé obligatoire pour générer un Employee Advance.")

        ea = frappe.new_doc("Employee Advance")
        ea.employee = self.employe
        ea.posting_date = self.date_demande
        ea.advance_amount = self.montant_total_demande
        ea.purpose = self.description_motif or "Avance"
        ea.repay_unclaimed_amount_from_salary = 0
        ea.custom_demande_source = self.name

        ea.insert(ignore_permissions=True)
        ea.submit()
        self.document_natif_reference = ea.name
        frappe.msgprint(f"Employee Advance {ea.name} créée.")

    def create_loan(self):
        if not self.employe:
            frappe.throw("Employé obligatoire pour générer un Loan.")

        loan = frappe.new_doc("Loan")
        loan.applicant_type = "Employee"
        loan.applicant = self.employe
        loan.loan_type = "Prêt personnel"
        loan.loan_amount = self.montant_total_demande
        loan.rate_of_interest = 0
        loan.repayment_method = "Repay Fixed Amount per Period"
        loan.repayment_start_date = self.date_paiement_prevue
        loan.custom_demande_source = self.name

        loan.insert(ignore_permissions=True)
        loan.submit()
        self.document_natif_reference = loan.name
        frappe.msgprint(f"Loan {loan.name} créé.")

    def create_asset_repair(self):
        if not self.vehicule:
            frappe.throw("Véhicule (Asset) obligatoire pour générer un Asset Repair.")

        ar = frappe.new_doc("Asset Repair")
        ar.asset = self.vehicule
        ar.repair_status = "Pending"
        ar.failure_date = self.date_demande
        ar.description = self.description_motif
        ar.repair_cost = self.montant_total_demande
        ar.custom_demande_source = self.name

        ar.insert(ignore_permissions=True)
        self.document_natif_reference = ar.name
        frappe.msgprint(f"Asset Repair {ar.name} créé (brouillon, à compléter par Maintenance).")

    def create_stock_entry(self):
        se = frappe.new_doc("Stock Entry")
        se.stock_entry_type = "Material Issue"
        se.custom_demande_source = self.name
        se.custom_vehicule = self.vehicule

        for ligne in self.lignes_demande:
            se.append("items", {
                "item_code": ligne.designation,
                "qty": ligne.quantite,
            })

        se.insert(ignore_permissions=True)
        self.document_natif_reference = se.name
        frappe.msgprint(f"Stock Entry {se.name} créé (brouillon).")

    def create_subscription(self):
        frappe.msgprint("Subscription : création manuelle recommandée (paramétrage de la périodicité requis).")
        self.document_natif_reference = "MANUEL"
