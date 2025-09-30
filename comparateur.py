import json
import os
import google.generativeai as genai



def find_top_contracts(user_data):
    """
    Trouve les 5 meilleurs contrats d'assurance en fonction des données de l'utilisateur en utilisant Gemini Pro.
    
    Args:
        user_data (dict): Un dictionnaire contenant les préférences de l'utilisateur issues du formulaire.
        
    Returns:
        list: Une liste des 5 meilleurs contrats recommandés.
    """
    print("--- In find_top_contracts ---")
    print(f"User data received: {json.dumps(user_data, indent=2)}")
    
    try:
        # Assurez-vous que votre clé API est définie comme variable d'environnement
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("ERROR: GOOGLE_API_KEY environment variable not set.")
            raise ValueError("La variable d'environnement GOOGLE_API_KEY n'est pas définie.")
        
        print("Successfully retrieved GOOGLE_API_KEY.")
        genai.configure(api_key=api_key)
        
        print("Loading contracts.json...")
        with open('contracts.json', 'r', encoding='utf-8') as f:
            contracts = json.load(f)
        print("Successfully loaded contracts.json.")
            
        prompt = f"""
Bonjour ! Vous allez analyser attentivement une liste de contrats afin de recommander **les 10 meilleurs** en fonction de leur adéquation avec les **besoins précis de l'utilisateur**.

Prenez **tout le temps nécessaire** pour effectuer une évaluation **rigoureuse, complète et méthodique**. La précision doit être **absolue (100%)** : chaque correspondance ou écart entre les besoins et les garanties doit être justifié avec soin.

Voici les informations à prendre en compte :

Besoins de l'utilisateur :
{json.dumps(user_data, indent=2, ensure_ascii=False)}

Contrats disponibles :
{json.dumps(contracts, indent=2, ensure_ascii=False)}

**Instructions spécifiques de sélection avec logique de classement précise :**

**RANG 1 (Premier contrat) :**
- Doit être **presque identique** aux besoins utilisateur
- Garanties **exactement similaires** ou **très proches** (écart maximum ±10%)
- Correspondance de **95-100%**

**RANGS 2-3 (Deuxième et troisième contrats) :**
- Garanties dans une **marge acceptable** de **±50** par rapport aux besoins
- Exemple : si besoin 300%, accepter 250% à 350%
- Si besoin 200€, accepter 150€ à 250€
- Correspondance de **85-94%**

**RANGS 4-6 (Quatrième, cinquième et sixième contrats) :**
- Doivent **couvrir intégralement tous les besoins** exprimés par l'utilisateur
- Peuvent dépasser les besoins mais ne doivent pas être en dessous
- Correspondance de **75-84%**

**RANGS 7-10 (Septième à dixième contrats) :**
- Les plus **éloignés** des besoins mais restant pertinents
- Peuvent avoir des **manques significatifs** ou des **écarts importants**
- Se rapprochent le plus des besoins parmi les contrats restants
- Correspondance de **50-74%**

**Critères d'évaluation pour le calcul du pourcentage :**
- **Proximité exacte des garanties** (50% du score) - Chaque garantie est évaluée individuellement :
  * Identique ou ±5% = Vert foncé (score max)
  * ±5-20% = Vert standard
  * ±20-50% = Vert clair  
  * ±50-100% = Orange clair
  * ±100-200% = Orange foncé
  * >200% ou absence = Rouge
- **Couverture complète des besoins** (30% du score)
- **Cohérence globale du contrat** (20% du score)

Votre mission est d'identifier les **10 contrats les plus pertinents** selon cette logique précise et de les présenter sous forme de **tableau Markdown**, selon le format suivant :

| Contrat | Pourcentage de correspondance | Points forts | Points faibles |
|--------|-------------------------------|--------------|----------------|

Pour chaque contrat sélectionné, vous devez :

1. Indiquer **le nom exact du contrat**.
2. Fournir un **"Pourcentage de correspondance"** (de 50% à 100%) qui reflète **l'adéquation globale** selon la logique de classement ci-dessus.
3. Lister précisément les **"Points forts"** : les garanties qui **répondent ou surpassent les attentes** de l'utilisateur.
4. Identifier clairement les **"Points faibles"** : les garanties **insuffisantes, absentes ou inadaptées** par rapport aux besoins.

⚠️ **IMPORTANT :** Respectez impérativement la logique de classement définie ci-dessus. Le rang 1 doit être quasi-parfait, les rangs 2-3 dans la marge ±50, les rangs 4-6 couvrent tout, les rangs 7-10 sont les plus éloignés.

⚠️ Veuillez **retourner uniquement le tableau Markdown**, sans texte, commentaire ou formatage supplémentaire.

Soyez **exhaustif, objectif et précis au maximum**.
"""
        print("Prompt generated. Preparing to call the generative model.")


        model = genai.GenerativeModel('gemini-2.5-pro')

        print("Calling generate_content...")
        response = model.generate_content(
            prompt
        )
        print("Successfully received response from the model.")
        
        # Since we expect a markdown table, we will return the text directly
        print(f"Model response text (first 500 chars): {response.text[:500]}")
        return response.text

    except (ValueError, json.JSONDecodeError) as e:
        print(f"A validation or JSON error occurred: {e}")
        # En cas d'erreur, renvoyer un message d'erreur au frontend
        return {"error": str(e)}
    except Exception as e:
        print(f"An unexpected error occurred in find_top_contracts: {e}")
        return {"error": "Une erreur inattendue est survenue lors de la comparaison des contrats."}
