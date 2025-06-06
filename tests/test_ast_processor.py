import unittest
import tempfile
import os
import shutil # For cleaning up temp dirs if needed, though individual files are easier
from converter.ast_processor import parse_javascript_to_ast, transform_ast_rename_variable, generate_javascript_from_ast
import esprima # To check AST node types, e.g. Program

class TestAstProcessor(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for test files if multiple tests need it
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)

    def _create_temp_js_file(self, content, filename="test.js"):
        file_path = os.path.join(self.test_dir, filename)
        with open(file_path, "w") as f:
            f.write(content)
        return file_path

    def test_parse_javascript_to_ast(self):
        js_content = "var oldVarName = 10;"
        file_path = self._create_temp_js_file(js_content)

        ast = parse_javascript_to_ast(file_path)

        self.assertIsNotNone(ast, "AST should not be None for valid JS.")
        self.assertEqual(ast.type, "Program", f"AST type should be Program, got {ast.type}")
        self.assertTrue(hasattr(ast, 'body') and len(ast.body) > 0, "AST body is empty or missing.")
        # os.remove(file_path) # Cleaned by tearDown

    def test_parse_invalid_javascript_to_ast(self):
        js_content = "var oldVarName = 10; let const = ;" # Invalid JS
        file_path = self._create_temp_js_file(js_content, "invalid.js")

        ast = parse_javascript_to_ast(file_path)

        self.assertIsNone(ast, "AST should be None for invalid JS.")
        # os.remove(file_path) # Cleaned by tearDown

    def test_transform_ast_rename_variable(self):
        js_content = "var oldVarName = 5; console.log(oldVarName);"
        # No need to write to file, parse directly for this test unit
        ast = esprima.parseScript(js_content)

        self.assertIsNotNone(ast, "Initial AST parsing failed for transformation test.")

        transformed_ast = transform_ast_rename_variable(ast, "oldVarName", "newVarName")
        self.assertIsNotNone(transformed_ast, "Transformation returned None.")

        # Check by generating code and inspecting it
        generated_code = generate_javascript_from_ast(transformed_ast)
        self.assertIsNotNone(generated_code, "Code generation failed for transformed AST.")
        self.assertIn("newVarName", generated_code, "newVarName not found in generated code.")
        self.assertNotIn("oldVarName", generated_code, "oldVarName should not be in generated code.")
        # Expected: "var newVarName = 5; console.log(newVarName);" (escodegen might add/remove semicolon or format)
        self.assertTrue("var newVarName = 5;" in generated_code or "var newVarName=5;" in generated_code)
        self.assertTrue("console.log(newVarName);" in generated_code)


    def test_generate_javascript_from_ast(self):
        js_content = "var x = 1;"
        ast = esprima.parseScript(js_content) # parseScript returns an AST object
        self.assertIsNotNone(ast, "AST parsing failed for generation test.")

        generated_code = generate_javascript_from_ast(ast)

        self.assertIsNotNone(generated_code, "Generated code should not be None.")
        self.assertIsInstance(generated_code, str, "Generated code should be a string.")
        # escodegen typically adds a trailing semicolon if not present for var/let/const
        # and might add a newline at the end.
        self.assertEqual(generated_code.strip(), "var x = 1;")

    def test_generate_from_none_ast(self):
        generated_code = generate_javascript_from_ast(None)
        self.assertIsNone(generated_code, "Generating code from None AST should return None.")

if __name__ == "__main__":
    unittest.main()
