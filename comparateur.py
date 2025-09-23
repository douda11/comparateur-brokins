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

**Instructions spécifiques de sélection :**

1. Pour les **3 premiers contrats**, vous devez impérativement privilégier ceux qui **couvrent intégralement l'ensemble des besoins exprimés par l'utilisateur**.
2. Pour les **7 contrats suivants**, sélectionnez ceux qui **se rapprochent le plus des besoins**, même s'ils ne les couvrent pas entièrement.
3. Classez l'ensemble des 10 contrats dans l'ordre décroissant de pertinence, en commençant par le plus adapté.

Votre mission est d'identifier les **10 contrats les plus pertinents** et de les présenter sous forme de **tableau Markdown**, selon le format suivant :

| Contrat | Pourcentage de correspondance | Points forts | Points faibles |
|--------|-------------------------------|--------------|----------------|

Pour chaque contrat sélectionné, vous devez :

1. Indiquer **le nom exact du contrat**.
2. Fournir un **"Pourcentage de correspondance"** (de 0 % à 100 %) qui reflète **l'adéquation globale** entre le contrat et les besoins exprimés.
3. Lister précisément les **"Points forts"** : les garanties qui **répondent ou surpassent les attentes** de l'utilisateur.
4. Identifier clairement les **"Points faibles"** : les garanties **insuffisantes, absentes ou inadaptées** par rapport aux besoins.

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
