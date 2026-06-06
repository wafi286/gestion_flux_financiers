# Gestion des Flux Financiers

Custom App ERPNext v16 — Hub transverse des demandes financières.

## Architecture

- **Hub** : `Demande Financière` (workflow métier, métadonnées externes)
- **Spokes** : DocTypes natifs ERPNext (Purchase Invoice, Expense Claim, Employee Advance, Loan, Asset Repair, Stock Entry, Subscription)
- **Zéro modification du core** : tout passe par Custom Fields, Server Scripts, Hooks et Workflows.

## DocTypes internes

| DocType | Type | Rôle |
|---------|------|------|
| Demande Financière | Document | Maître — demande + workflow |
| Ligne de Demande | Child Table | Lignes de la demande |
| Type de Flux | Document | Référentiel catégories A-G |
| Sous Type Flux | Child Table | Sous-catégories par type |
| Mapping Projet Leantime | Document | Sync projets Leantime |
| Mapping Tâche Leantime | Document | Sync tâches Leantime |
| Mapping Projet OpenERP | Document | Sync projets OpenERP 7 |
| Mapping Ligne Commande OpenERP | Document | Sync lignes commande OpenERP 7 |
| Configuration Intégration | Single | Paramètres API externes |

## Installation

```bash
bench get-app https://github.com/wafi286/gestion_flux_financiers.git
bench --site site1.local install-app gestion_flux_financiers
bench --site site1.local migrate
bench build --app gestion_flux_financiers
```

## Développement

1. Cloner dans un environnement Frappe de développement (pas en production).
2. Modifier les DocTypes via l'UI, puis exporter :
   ```bash
   bench --site dev.localhost export-fixtures --app gestion_flux_financiers
   ```
3. Commiter et pousser sur GitHub.
4. Déployer sur Portainer/Production via `git pull` + `bench migrate`.

## Workflows & Rôles

- `Demandeur_Flux` : création, édition (uniquement ses documents)
- `DGA_Flux` : validation finale, clôture
- `Comptable_Flux` : traitement paiement
- `RH_Flux`, `Superviseur_Flux`, `Maintenance_Flux`, `ParcAuto_Flux`, `OfficeManager_Flux`, `Juridique_Flux`, `AdminCharges_Flux` : validation par domaine

## Intégrations

- **Leantime** : API REST directe (`requests`)
- **OpenERP 7** : via webhook n8n (recommandé) ou XML-RPC/PostgreSQL direct

## Licence

MIT
