import os
from lxml import etree
from flask import current_app

def validate_xml(xml_content, schema_name='TransXChange_registration.xsd'):
    """
    Validate XML content against a specific schema
    
    Args:
        xml_content (bytes): The XML content to validate
        schema_name (str): The name of the schema file in the schema directory
        
    Returns:
        tuple: (is_valid, error_messages) where is_valid is a boolean indicating 
               whether the XML is valid and error_messages is a list of error messages
    """
    try:
        schema_path = os.path.join(current_app.config['SCHEMA_DIR'], schema_name)
        
        # Use lxml for validation instead of xmlschema
        with open(schema_path, 'rb') as schema_file:
            schema_doc = etree.parse(schema_file)
            schema = etree.XMLSchema(schema_doc)
            
        # Parse the XML content
        xml_doc = etree.fromstring(xml_content)
        
        # Validate
        schema.assertValid(xml_doc)
        return True, []
    except etree.DocumentInvalid as e:
        return False, [str(e)]
    except Exception as e:
        return False, [f"Unexpected error: {str(e)}"]
