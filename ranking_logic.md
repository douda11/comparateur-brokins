# 🎯 NOUVELLE LOGIQUE DE CLASSEMENT - Comparateur CASHedi

## 📊 **SYSTÈME DE RANKING PRÉCIS**

### **🥇 RANG 1 (Premier contrat)**
- **Critère** : Presque identique aux besoins
- **Écart maximum** : ±10%
- **Pourcentage** : 95-100%
- **Couleur** : `.coverage-excellent` (Vert foncé)
- **Exemple** : Besoin 300% → Contrat 270-330%

### **🥈 RANGS 2-3 (Deuxième et troisième contrats)**
- **Critère** : Marge acceptable
- **Écart maximum** : ±50 unités
- **Pourcentage** : 85-94%
- **Couleur** : `.coverage-high` (Vert)
- **Exemples** :
  - Besoin 300% → Contrat 250-350%
  - Besoin 200€ → Contrat 150-250€

### **🏆 RANGS 4-6 (Quatrième à sixième contrats)**
- **Critère** : Couvrent intégralement tous les besoins
- **Condition** : Peuvent dépasser mais pas en dessous
- **Pourcentage** : 75-84%
- **Couleur** : `.coverage-good` (Vert clair)
- **Logique** : Couverture complète garantie

### **📊 RANGS 7-10 (Septième à dixième contrats)**
- **Critère** : Plus éloignés mais pertinents
- **Condition** : Manques significatifs acceptés
- **Pourcentage** : 50-74%
- **Couleurs** : `.coverage-medium` / `.coverage-low` (Orange)
- **Logique** : Meilleurs parmi les restants

## 🧮 **CRITÈRES D'ÉVALUATION**

| Critère | Poids | Description |
|---------|-------|-------------|
| **Exactitude des garanties** | 40% | Précision des montants/pourcentages |
| **Couverture complète** | 30% | Tous les besoins sont couverts |
| **Proximité des montants** | 20% | Écart par rapport aux besoins |
| **Absence de manques critiques** | 10% | Pas de garanties essentielles manquantes |

## 🎨 **MAPPING COULEURS**

```typescript
function getRankingColor(rank: number, percentage: number): string {
  if (rank === 1 && percentage >= 95) return 'coverage-excellent';
  if (rank <= 3 && percentage >= 85) return 'coverage-high';
  if (rank <= 6 && percentage >= 75) return 'coverage-good';
  if (rank <= 10 && percentage >= 60) return 'coverage-medium';
  if (rank <= 10 && percentage >= 50) return 'coverage-low';
  return 'coverage-poor';
}
```

## 📈 **EXEMPLES PRATIQUES**

### Besoin utilisateur : Hospitalisation 300%

| Rang | Contrat | Couverture | Écart | Pourcentage | Couleur |
|------|---------|------------|-------|-------------|---------|
| 1 | Contrat A | 295% | -5 | 98% | Excellent |
| 2 | Contrat B | 350% | +50 | 92% | High |
| 3 | Contrat C | 250% | -50 | 87% | High |
| 4 | Contrat D | 400% | +100 | 82% | Good |
| 5 | Contrat E | 320% | +20 | 79% | Good |
| 6 | Contrat F | 380% | +80 | 76% | Good |
| 7 | Contrat G | 200% | -100 | 68% | Medium |
| 8 | Contrat H | 150% | -150 | 61% | Medium |
| 9 | Contrat I | 100% | -200 | 55% | Low |
| 10 | Contrat J | 80% | -220 | 52% | Low |

## 🔧 **IMPLÉMENTATION**

Cette logique est maintenant intégrée dans :
- `comparateur.py` : Prompt IA mis à jour
- Système de couleurs CSS : Classes correspondantes
- Frontend : Mapping automatique des couleurs selon le rang et pourcentage
