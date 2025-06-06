import esprima
import escodegen

# Custom Visitor class to rename identifiers
class RenameTransformer(esprima.NodeVisitor):
    def __init__(self, old_name, new_name):
        super().__init__()
        self.old_name = old_name
        self.new_name = new_name

    def visit_Identifier(self, node):
        if node.name == self.old_name:
            node.name = self.new_name
        # We don't need to visit children of an Identifier, so no super().visit_Identifier(node)
        return node # Return the modified node (or original if no change)

def parse_javascript_to_ast(file_path):
    """
    Parses a JavaScript file into an Abstract Syntax Tree (AST) using esprima.

    Args:
        file_path (str): The path to the JavaScript file.

    Returns:
        esprima.nodes.Node: The AST object if parsing is successful,
                            None otherwise.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            code = file.read()
        # Attempt to parse as a script first.
        # For ES6 modules (import/export), parseModule would be needed.
        # Adding 'tolerant' option to potentially recover from minor syntax errors.
        # 'comment' and 'tokens' can be useful for more advanced transformations.
        ast = esprima.parseScript(code, options={'loc': True, 'range': True, 'tolerant': True})
        return ast
    except esprima.Error as e:
        # Adding more context to the error message
        # Esprima errors in Python typically have 'message' or can be stringified.
        # Accessing e.description was incorrect. Let's use str(e) or e.message.
        # e.message usually contains the description along with line/column.
        print(f"Esprima parsing error in file '{file_path}': {e.message if hasattr(e, 'message') else str(e)}")
        return None
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while parsing {file_path}: {e}")
        return None

def transform_ast_rename_variable(ast_object, old_name, new_name):
    """
    Transforms an AST by renaming specified identifiers.

    Args:
        ast_object: The AST object (from esprima).
        old_name (str): The current name of the identifier to be renamed.
        new_name (str): The new name for the identifier.

    Returns:
        The modified AST object. Returns the original if ast_object is None.
    """
    if not ast_object:
        return None

    transformer = RenameTransformer(old_name, new_name)
    # The visit method of NodeVisitor modifies the AST in-place if nodes are mutable,
    # and returns the root of the (potentially) modified tree.
    modified_ast = transformer.visit(ast_object)
    return modified_ast

def generate_javascript_from_ast(ast_object):
    """
    Generates JavaScript code from an AST object using escodegen.

    Args:
        ast_object: The AST object (from esprima, possibly modified).

    Returns:
        str: The generated JavaScript code as a string.
             Returns None if the ast_object is None or if an error occurs.
    """
    if not ast_object:
        print("AST object is None, cannot generate code.")
        return None

    try:
        # You can customize code generation with options if needed,
        # e.g., escodegen.generate(ast_object, format={'compact': True})
        generated_code = escodegen.generate(ast_object)
        return generated_code
    except Exception as e:
        # escodegen might raise various errors if the AST is malformed
        print(f"An error occurred during JavaScript code generation: {e}")
        return None
