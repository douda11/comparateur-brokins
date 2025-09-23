import json
import os
import time
import threading
import google.generativeai as genai

# Protection contre les appels simultanés
_extraction_lock = threading.Lock()
_last_extraction_time = 0
MIN_DELAY_BETWEEN_CALLS = 2  # 2 secondes minimum entre les appels


def extract_contract_level_from_pdf(pdf_path, level_name, append_to_file=0):
    """
    Extrait les données structurées d'un niveau de contrat d'assurance à partir d'un fichier PDF
    en utilisant Gemini 2.5 Pro.

    Args:
        pdf_path (str): Le chemin vers le fichier PDF à analyser.
        level_name (str): Le nom du niveau à extraire (ex. "Niveau 1").
        append_to_file (int): Si 1, le JSON extrait est ajouté à contracts.json. Par défaut à 0.

    Returns:
        str or dict: Une chaîne JSON contenant les garanties extraites, ou un dictionnaire d'erreur.
    """
    global _last_extraction_time
    
    # Protection contre les appels simultanés et rate limiting
    with _extraction_lock:
        current_time = time.time()
        time_since_last_call = current_time - _last_extraction_time
        
        if time_since_last_call < MIN_DELAY_BETWEEN_CALLS:
            sleep_time = MIN_DELAY_BETWEEN_CALLS - time_since_last_call
            print(f"⏳ Rate limiting: Attente de {sleep_time:.1f}s avant l'appel API...")
            time.sleep(sleep_time)
        
        _last_extraction_time = time.time()
    
    contract_file_gai = None
    rules_file_gai = None
    try:
        # 1. API Key
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("La variable d'environnement GOOGLE_API_KEY n'est pas définie.")
        
        genai.configure(api_key=api_key)

        # 2. Load example JSON structure
        with open("examples.json", "r", encoding="utf-8") as f:
            examples = json.load(f)

        if not isinstance(examples, list) or len(examples) == 0:
            raise ValueError("Le fichier examples.json est vide ou mal formaté.")

        example_json = json.dumps(examples[0], indent=2, ensure_ascii=False)

        # 3. Prepare prompt
        prompt = f"""
Tu es une IA experte en extraction de données contractuelles à partir de documents PDF.

**Ta mission est double :**
1.  **Analyser le PDF de règles (`regles.pdf`)** pour comprendre les instructions d'extraction.
2.  **Extraire les données du PDF du contrat** en suivant scrupuleusement ces règles.

L'extraction concerne le niveau **"{level_name}"**.

Le format de sortie doit être un **JSON strict**, comme cet exemple :
```json
{example_json}
```

🔍 **Instruction cruciale :** Le PDF `regles.pdf` fourni contient les directives impératives pour l'extraction. Tu dois t'y conformer.

➡️ Retourne exclusivement le JSON, sans explication ou texte additionnel.
"""

        # 4. Upload files to Google AI
        print("Uploading contract file to Google AI...")
        contract_file_gai = genai.upload_file(path=pdf_path, display_name=os.path.basename(pdf_path))
        print(f"Contract file uploaded successfully: {contract_file_gai.uri}")

        rules_pdf_path = "regles.pdf"
        if not os.path.exists(rules_pdf_path):
            raise FileNotFoundError("Le fichier regles.pdf est introuvable.")

        print("Uploading rules file to Google AI...")
        rules_file_gai = genai.upload_file(path=rules_pdf_path, display_name="regles.pdf")
        print(f"Rules file uploaded successfully: {rules_file_gai.uri}")

        # 5. Call Gemini Pro 2.5 avec retry logic
        model = genai.GenerativeModel("gemini-2.5-pro")
        
        print("Generating content with Gemini...")
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = model.generate_content([prompt, rules_file_gai, contract_file_gai])
                print("Content generation complete.")
                break
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 30  # 30s, 60s, 90s
                        print(f"⚠️ Quota épuisé (tentative {attempt + 1}/{max_retries}). Attente de {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                raise e

        extracted_text = response.text.strip()

        if append_to_file == 1:
            try:
                new_contract_data = json.loads(extracted_text)

                contracts_file = "contracts.json"
                contracts_data = []

                if os.path.exists(contracts_file):
                    try:
                        with open(contracts_file, "r", encoding="utf-8") as f:
                            content = f.read()
                            if content:
                                contracts_data = json.loads(content)
                    except (json.JSONDecodeError, IOError) as e:
                        print(f"Warning: Could not read or parse {contracts_file}. It will be overwritten. Error: {e}")
                        contracts_data = []
                
                if not isinstance(contracts_data, list):
                    print(f"Warning: Data in {contracts_file} is not a list. It will be overwritten with a new list.")
                    contracts_data = []

                contracts_data.append(new_contract_data)

                with open(contracts_file, "w", encoding="utf-8") as f:
                    json.dump(contracts_data, f, indent=2, ensure_ascii=False)
                
                print(f"Successfully appended extracted data to {contracts_file}")

            except json.JSONDecodeError:
                print("Error: Extracted content is not valid JSON. Cannot append to file.")
            except Exception as e:
                print(f"An unexpected error occurred while appending to file: {e}")

        return extracted_text

    except (ValueError, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Erreur : {e}")
        return {"error": str(e)}

    except Exception as e:
        print(f"Erreur inattendue : {e}")
        return {"error": "Une erreur inattendue est survenue lors de l'extraction du contrat depuis le PDF."}

    finally:
        if contract_file_gai:
            print(f"Deleting uploaded contract file: {contract_file_gai.name}")
            genai.delete_file(contract_file_gai.name)
            print("Contract file deleted.")
        if rules_file_gai:
            print(f"Deleting uploaded rules file: {rules_file_gai.name}")
            genai.delete_file(rules_file_gai.name)
            print("Rules file deleted.")