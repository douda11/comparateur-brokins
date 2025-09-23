import json
import os

def delete_contract_by_id(level_id_to_delete):
    """
    Deletes a contract from contracts.json based on its level_id.

    Args:
        level_id_to_delete (str): The level_id of the contract to delete.

    Returns:
        tuple: A tuple containing a boolean indicating success and a message.
    """
    contracts_file = "contracts.json"
    
    if not os.path.exists(contracts_file):
        return False, f"Error: {contracts_file} not found."

    try:
        with open(contracts_file, "r", encoding="utf-8") as f:
            # Handle empty file
            content = f.read()
            if not content:
                contracts = []
            else:
                contracts = json.loads(content)
    except (json.JSONDecodeError, IOError) as e:
        return False, f"Error reading or parsing {contracts_file}: {e}"

    if not isinstance(contracts, list):
        return False, f"Error: Data in {contracts_file} is not a list."

    initial_count = len(contracts)
    contracts_after_deletion = [
        contract for contract in contracts if contract.get("level_id") != level_id_to_delete
    ]
    
    if len(contracts_after_deletion) < initial_count:
        try:
            with open(contracts_file, "w", encoding="utf-8") as f:
                json.dump(contracts_after_deletion, f, indent=2, ensure_ascii=False)
            return True, f"Successfully deleted contract with level_id: {level_id_to_delete}"
        except IOError as e:
            return False, f"Error writing to {contracts_file}: {e}"
    else:
        return False, f"Contract with level_id '{level_id_to_delete}' not found."
