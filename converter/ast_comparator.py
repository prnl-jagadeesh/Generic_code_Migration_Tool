import json

def _ast_to_serializable_string(ast_node):
    """
    Converts an AST node to a sorted JSON string for comparison.
    Esprima AST nodes are generally dictionary-like and directly serializable.
    We remove 'loc' and 'range' fields as they often differ even for structurally identical ASTs
    if the original code formatting was different, and they don't affect the structure.
    """
    if ast_node is None:
        return None

    def remove_location_data(node):
        if isinstance(node, dict):
            # Create a new dict without 'loc' and 'range'
            new_node = {k: remove_location_data(v) for k, v in node.items() if k not in ['loc', 'range', 'line', 'column', 'source', 'start', 'end']}
            return new_node
        elif isinstance(node, list):
            return [remove_location_data(item) for item in node]
        else:
            return node

    try:
        # First, remove location data which can cause false negatives
        simplified_ast = remove_location_data(ast_node.__dict__ if hasattr(ast_node, '__dict__') else ast_node)
        # Then, dump to a sorted JSON string
        return json.dumps(simplified_ast, sort_keys=True, indent=2)
    except TypeError as e:
        print(f"Error serializing AST node: {e}. Node type: {type(ast_node)}")
        # Fallback for nodes that might not be dicts at the root but are still part of esprima's structure
        if isinstance(ast_node, list): # e.g. Program.body is a list
             simplified_ast = remove_location_data(ast_node)
             return json.dumps(simplified_ast, sort_keys=True, indent=2)
        return None # Or raise an error, or handle more specific cases

def compare_asts(ast1, ast2):
    """
    Compares two AST objects by converting them to sorted JSON strings.

    Args:
        ast1: The first AST object (e.g., from esprima).
        ast2: The second AST object (e.g., from esprima).

    Returns:
        A tuple: (are_same, json_str1, json_str2)
        - are_same (bool): True if the ASTs are considered the same, False otherwise.
        - json_str1 (str or None): Sorted JSON string representation of ast1.
        - json_str2 (str or None): Sorted JSON string representation of ast2.
    """
    if ast1 is None and ast2 is None:
        return True, "AST1 was None", "AST2 was None"
    if ast1 is None:
        return False, "AST1 was None", _ast_to_serializable_string(ast2)
    if ast2 is None:
        return False, _ast_to_serializable_string(ast1), "AST2 was None"

    json_str1 = _ast_to_serializable_string(ast1)
    json_str2 = _ast_to_serializable_string(ast2)

    if json_str1 is None or json_str2 is None:
        # This indicates an error during serialization
        return False, json_str1, json_str2

    are_same = json_str1 == json_str2
    return are_same, json_str1, json_str2
