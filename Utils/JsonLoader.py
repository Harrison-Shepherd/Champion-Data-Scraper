import os
import json
import logging


def load_json_fields():
    """
    Load JSON field mappings for each table from the JSON files.
    """

    # Set the base directory and JSON directory
    base_dir = os.path.abspath(os.path.dirname(__file__))
    json_dir = os.path.join(base_dir, '..', 'Assets', 'jsons', 'unique fields')
    json_fields = {}


    # Load JSON field mappings for each table
    try:
        with open(os.path.join(json_dir, 'fixtureFields.json'), 'r') as file: #fixtureFields.json
            data = json.load(file)
            json_fields['fixture_fields'] = data.get('fixture_fields', {}) 
        
        with open(os.path.join(json_dir, 'matchFields.json'), 'r') as file: #matchFields.json
            data = json.load(file)
            json_fields['match_fields'] = data.get('match_fields', {})
        
        with open(os.path.join(json_dir, 'periodFields.json'), 'r') as file: #periodFields.json
            data = json.load(file)
            json_fields['period_fields'] = data.get('period_fields', {})
        
        with open(os.path.join(json_dir, 'scoreFlowFields.json'), 'r') as file: #scoreFlowFields.json
            data = json.load(file)
            json_fields['score_flow_fields'] = data.get('score_flow_fields', {})

        # Load player fields
        with open(os.path.join(json_dir, 'playerFields.json'), 'r') as file: #playerFields.json
            data = json.load(file)
            json_fields['player_fields'] = data.get('player_fields', {})

        # Load squad fields
        with open(os.path.join(json_dir, 'squadFields.json'), 'r') as file: #squadFields.json
            data = json.load(file)
            json_fields['squad_fields'] = data.get('squad_fields', {})

        # Load sport fields
        with open(os.path.join(json_dir, 'sportFields.json'), 'r') as file: #sportFields.json
            data = json.load(file)
            json_fields['sport_fields'] = data.get('sport_fields', {})

        # Log success message
        logging.info("JSON field mappings loaded successfully.")
        return json_fields

    # Handle exceptions
    except Exception as e:
        logging.error(f"Error loading JSON fields: {e}")
        raise
