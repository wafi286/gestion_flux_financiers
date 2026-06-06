frappe.ui.form.on('Demande Financière', {
    refresh(frm) {
        // Filtre dynamique : tâches Leantime par projet
        frm.set_query('tache_leantime', 'lignes_demande', function(doc, cdt, cdn) {
            return {
                filters: {
                    projet: doc.projet_leantime
                }
            };
        });

        // Filtre dynamique : lignes OpenERP par projet
        frm.set_query('ligne_commande_openerp', 'lignes_demande', function(doc, cdt, cdn) {
            return {
                filters: {
                    projet: doc.projet_openerp
                }
            };
        });

        // Bouton Synchroniser Leantime (si admin / intégrateur)
        if (frappe.user.has_role('System Manager')) {
            frm.add_custom_button(__('Sync Leantime'), function() {
                frappe.call({
                    method: 'gestion_flux_financiers.integrations.leantime.sync_leantime',
                    callback: function(r) {
                        if (!r.exc) {
                            frappe.msgprint(__('Synchronisation terminée.'));
                        }
                    }
                });
            }, __('Actions'));

            frm.add_custom_button(__('Sync OpenERP'), function() {
                frappe.call({
                    method: 'gestion_flux_financiers.integrations.openerp_n8n.sync_openerp_projects',
                    callback: function(r) {
                        if (!r.exc) {
                            frappe.msgprint(__('Synchronisation OpenERP terminée.'));
                        }
                    }
                });
            }, __('Actions'));
        }
    },

    categorie_flux(frm) {
        // Réinitialiser les champs spécifiques si changement de catégorie
        frm.set_value('vehicule', '');
        frm.set_value('employe', '');
        frm.set_value('beneficiaire', '');
    },

    validate(frm) {
        if (frm.doc.workflow_state === 'Rejetée' && !frm.doc.motif_rejet) {
            frappe.msgprint(__('Veuillez renseigner le motif de rejet.'), __('Erreur'));
            frappe.validated = false;
        }
    }
});

frappe.ui.form.on('Ligne de Demande', {
    quantite(frm, cdt, cdn) {
        calculate_ligne(cdt, cdn);
    },
    prix_unitaire(frm, cdt, cdn) {
        calculate_ligne(cdt, cdn);
    },
    ligne_commande_openerp(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.ligne_commande_openerp) {
            frappe.db.get_value('Mapping Ligne Commande OpenERP', row.ligne_commande_openerp,
                ['designation_originale', 'quantite_restante', 'prix_unitaire'],
                function(r) {
                    if (r) {
                        frappe.model.set_value(cdt, cdn, 'designation', r.designation_originale);
                        frappe.model.set_value(cdt, cdn, 'quantite_commande_restante', r.quantite_restante);
                        frappe.model.set_value(cdt, cdn, 'prix_unitaire', r.prix_unitaire);
                        calculate_ligne(cdt, cdn);

                        if (row.quantite > r.quantite_restante) {
                            frappe.model.set_value(cdt, cdn, 'alerte_depassement',
                                '<span class="badge badge-danger" style="font-size:12px">⚠ Dépassement Qté</span>');
                        } else {
                            frappe.model.set_value(cdt, cdn, 'alerte_depassement', '');
                        }
                    }
                }
            );
        }
    }
});

function calculate_ligne(cdt, cdn) {
    let row = locals[cdt][cdn];
    let montant = (row.quantite || 0) * (row.prix_unitaire || 0);
    frappe.model.set_value(cdt, cdn, 'montant_ligne', montant);
}
