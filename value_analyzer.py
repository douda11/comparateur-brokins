"""
Analyseur de valeurs pour l'extraction automatique des garanties
Détecte le type de valeur (euros, pourcentage) et configure les sliders appropriés
"""

import re
import json
from typing import Dict, List, Tuple, Union

class ValueType:
    """Types de valeurs supportés"""
    PERCENTAGE = "percentage"
    EUROS = "euros"
    MIXED = "mixed"
    UNKNOWN = "unknown"

class GuaranteeAnalyzer:
    """Analyseur de garanties pour déterminer les types de valeurs et configurer les sliders"""
    
    def __init__(self):
        # Patterns de reconnaissance
        self.percentage_patterns = [
            r'(\d+(?:\.\d+)?)\s*%',           # 100%, 125.5%
            r'(\d+(?:\.\d+)?)\s*% BR',        # 100% BR
            r'(\d+(?:\.\d+)?)\s*% BRSS',      # 500% BRSS
            r'\+(\d+(?:\.\d+)?)\s*% BR',      # +100% BR
        ]
        
        self.euros_patterns = [
            r'(\d+(?:\.\d+)?)\s*€',           # 100€, 125.50€
            r'(\d+(?:\.\d+)?)\s*euros?',      # 100 euro, 125 euros
            r'\+(\d+(?:\.\d+)?)\s*€',         # +30€
        ]
        
        # Configuration des sliders par défaut
        self.default_slider_configs = {
            ValueType.PERCENTAGE: {
                "min": 0,
                "max": 500,
                "step": 25,
                "unit": "%",
                "suffix": "% BR"
            },
            ValueType.EUROS: {
                "min": 0,
                "max": 1000,
                "step": 10,
                "unit": "€",
                "suffix": "€"
            }
        }
    
    def analyze_value(self, value: str) -> Dict:
        """
        Analyse une valeur extraite et détermine son type
        
        Args:
            value (str): Valeur extraite (ex: "125 % BR", "30 €", "+100% BR")
            
        Returns:
            Dict: Informations sur la valeur analysée
        """
        if not value or value == "-" or value.lower() in ["non couvert", "nc"]:
            return {
                "type": ValueType.UNKNOWN,
                "numeric_value": 0,
                "original_value": value,
                "unit": "",
                "is_addition": False
            }
        
        # Nettoyer la valeur
        clean_value = str(value).strip()
        
        # Détecter si c'est un ajout (+)
        is_addition = clean_value.startswith('+')
        
        # Analyser les pourcentages
        for pattern in self.percentage_patterns:
            match = re.search(pattern, clean_value, re.IGNORECASE)
            if match:
                numeric_value = float(match.group(1))
                return {
                    "type": ValueType.PERCENTAGE,
                    "numeric_value": numeric_value,
                    "original_value": value,
                    "unit": "%",
                    "is_addition": is_addition,
                    "display_value": f"{numeric_value}% BR"
                }
        
        # Analyser les euros
        for pattern in self.euros_patterns:
            match = re.search(pattern, clean_value, re.IGNORECASE)
            if match:
                numeric_value = float(match.group(1))
                return {
                    "type": ValueType.EUROS,
                    "numeric_value": numeric_value,
                    "original_value": value,
                    "unit": "€",
                    "is_addition": is_addition,
                    "display_value": f"{numeric_value}€"
                }
        
        # Si aucun pattern ne correspond, essayer d'extraire un nombre
        number_match = re.search(r'(\d+(?:\.\d+)?)', clean_value)
        if number_match:
            numeric_value = float(number_match.group(1))
            return {
                "type": ValueType.UNKNOWN,
                "numeric_value": numeric_value,
                "original_value": value,
                "unit": "",
                "is_addition": is_addition,
                "display_value": str(numeric_value)
            }
        
        return {
            "type": ValueType.UNKNOWN,
            "numeric_value": 0,
            "original_value": value,
            "unit": "",
            "is_addition": False,
            "display_value": value
        }
    
    def analyze_contract_benefits(self, benefits: Dict) -> Dict:
        """
        Analyse toutes les garanties d'un contrat
        
        Args:
            benefits (Dict): Dictionnaire des garanties du contrat
            
        Returns:
            Dict: Analyse complète avec configuration des sliders
        """
        analysis = {
            "guarantees": {},
            "slider_configs": {},
            "summary": {
                "total_guarantees": 0,
                "percentage_count": 0,
                "euros_count": 0,
                "unknown_count": 0
            }
        }
        
        for category, guarantees in benefits.items():
            if not isinstance(guarantees, dict):
                continue
                
            analysis["guarantees"][category] = {}
            
            for guarantee_name, guarantee_value in guarantees.items():
                # Analyser la valeur
                value_analysis = self.analyze_value(guarantee_value)
                analysis["guarantees"][category][guarantee_name] = value_analysis
                
                # Générer la configuration du slider
                slider_config = self.generate_slider_config(guarantee_name, value_analysis)
                analysis["slider_configs"][f"{category}_{guarantee_name}"] = slider_config
                
                # Mettre à jour le résumé
                analysis["summary"]["total_guarantees"] += 1
                if value_analysis["type"] == ValueType.PERCENTAGE:
                    analysis["summary"]["percentage_count"] += 1
                elif value_analysis["type"] == ValueType.EUROS:
                    analysis["summary"]["euros_count"] += 1
                else:
                    analysis["summary"]["unknown_count"] += 1
        
        return analysis
    
    def generate_slider_config(self, guarantee_name: str, value_analysis: Dict) -> Dict:
        """
        Génère la configuration d'un slider basée sur l'analyse de la valeur
        
        Args:
            guarantee_name (str): Nom de la garantie
            value_analysis (Dict): Analyse de la valeur
            
        Returns:
            Dict: Configuration du slider
        """
        value_type = value_analysis["type"]
        numeric_value = value_analysis["numeric_value"]
        
        # Configuration de base selon le type
        if value_type == ValueType.PERCENTAGE:
            config = self.default_slider_configs[ValueType.PERCENTAGE].copy()
            # Ajuster le max selon la valeur extraite
            if numeric_value > 300:
                config["max"] = max(500, int(numeric_value * 1.2))
        elif value_type == ValueType.EUROS:
            config = self.default_slider_configs[ValueType.EUROS].copy()
            # Ajuster le max selon la valeur extraite
            if numeric_value > 500:
                config["max"] = max(1000, int(numeric_value * 1.5))
        else:
            # Configuration par défaut pour les valeurs inconnues
            config = {
                "min": 0,
                "max": max(100, int(numeric_value * 2)) if numeric_value > 0 else 100,
                "step": 1,
                "unit": "",
                "suffix": ""
            }
        
        # Personnalisations spécifiques par garantie
        config.update(self.get_guarantee_specific_config(guarantee_name, value_type))
        
        # Valeur par défaut du slider
        config["default_value"] = numeric_value
        config["extracted_value"] = value_analysis["display_value"]
        config["guarantee_name"] = guarantee_name
        config["value_type"] = value_type
        
        return config
    
    def get_guarantee_specific_config(self, guarantee_name: str, value_type: str) -> Dict:
        """
        Configurations spécifiques par type de garantie
        
        Args:
            guarantee_name (str): Nom de la garantie
            value_type (str): Type de valeur
            
        Returns:
            Dict: Configuration spécifique
        """
        specific_configs = {
            "chambre_particuliere": {
                ValueType.EUROS: {"max": 200, "step": 5}
            },
            "honoraires_chirurgien_optam": {
                ValueType.PERCENTAGE: {"max": 600, "step": 25}
            },
            "consultation_generaliste_optam": {
                ValueType.PERCENTAGE: {"max": 400, "step": 25}
            },
            "implantologie": {
                ValueType.EUROS: {"max": 2000, "step": 50}
            },
            "orthodontie": {
                ValueType.PERCENTAGE: {"max": 300, "step": 25},
                ValueType.EUROS: {"max": 1500, "step": 50}
            },
            "verres_complexes": {
                ValueType.EUROS: {"max": 800, "step": 25}
            }
        }
        
        if guarantee_name in specific_configs and value_type in specific_configs[guarantee_name]:
            return specific_configs[guarantee_name][value_type]
        
        return {}
    
    def generate_frontend_config(self, analysis: Dict) -> Dict:
        """
        Génère la configuration pour le frontend Angular
        
        Args:
            analysis (Dict): Analyse complète du contrat
            
        Returns:
            Dict: Configuration pour le frontend
        """
        frontend_config = {
            "sliders": [],
            "form_structure": {},
            "validation_rules": {}
        }
        
        for slider_key, slider_config in analysis["slider_configs"].items():
            category, guarantee = slider_key.split("_", 1)
            
            slider_info = {
                "id": slider_key,
                "category": category,
                "guarantee": guarantee,
                "label": self.format_guarantee_label(guarantee),
                "type": slider_config["value_type"],
                "min": slider_config["min"],
                "max": slider_config["max"],
                "step": slider_config["step"],
                "default": slider_config["default_value"],
                "unit": slider_config["unit"],
                "suffix": slider_config["suffix"],
                "extracted_value": slider_config["extracted_value"]
            }
            
            frontend_config["sliders"].append(slider_info)
            
            # Structure du formulaire
            if category not in frontend_config["form_structure"]:
                frontend_config["form_structure"][category] = []
            frontend_config["form_structure"][category].append(slider_info)
        
        return frontend_config
    
    def format_guarantee_label(self, guarantee_name: str) -> str:
        """
        Formate le nom de la garantie pour l'affichage
        
        Args:
            guarantee_name (str): Nom technique de la garantie
            
        Returns:
            str: Nom formaté pour l'affichage
        """
        label_mapping = {
            "honoraires_chirurgien_optam": "Honoraires Chirurgien OPTAM",
            "chambre_particuliere": "Chambre Particulière",
            "consultation_generaliste_optam": "Consultation Généraliste OPTAM",
            "soins_dentaires": "Soins Dentaires",
            "implantologie": "Implantologie",
            "orthodontie": "Orthodontie",
            "verres_complexes": "Verres Complexes"
        }
        
        return label_mapping.get(guarantee_name, guarantee_name.replace("_", " ").title())

def analyze_extracted_contract(contract_data: Dict) -> Dict:
    """
    Fonction principale pour analyser un contrat extrait
    
    Args:
        contract_data (Dict): Données du contrat extrait
        
    Returns:
        Dict: Analyse complète avec configuration des sliders
    """
    analyzer = GuaranteeAnalyzer()
    
    if "benefits" not in contract_data:
        return {"error": "Aucune garantie trouvée dans le contrat"}
    
    analysis = analyzer.analyze_contract_benefits(contract_data["benefits"])
    frontend_config = analyzer.generate_frontend_config(analysis)
    
    return {
        "contract_info": {
            "insurer": contract_data.get("insurer", ""),
            "contract_name": contract_data.get("contract_name", ""),
            "level_name": contract_data.get("level_name", "")
        },
        "analysis": analysis,
        "frontend_config": frontend_config
    }

# Exemple d'utilisation
if __name__ == "__main__":
    # Test avec les données d'exemple
    with open("examples.json", "r", encoding="utf-8") as f:
        examples = json.load(f)
    
    for example in examples:
        print(f"\n🔍 Analyse du contrat: {example['contract_name']} - {example['level_name']}")
        print("=" * 60)
        
        result = analyze_extracted_contract(example)
        
        if "error" in result:
            print(f"❌ Erreur: {result['error']}")
            continue
        
        print(f"📊 Résumé:")
        summary = result["analysis"]["summary"]
        print(f"  - Total garanties: {summary['total_guarantees']}")
        print(f"  - Pourcentages: {summary['percentage_count']}")
        print(f"  - Euros: {summary['euros_count']}")
        print(f"  - Inconnus: {summary['unknown_count']}")
        
        print(f"\n🎛️ Configuration des sliders:")
        for slider in result["frontend_config"]["sliders"]:
            print(f"  - {slider['label']}: {slider['extracted_value']} → Slider {slider['min']}-{slider['max']}{slider['unit']} (défaut: {slider['default']}{slider['unit']})")
