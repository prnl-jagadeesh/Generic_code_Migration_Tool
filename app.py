import gradio as gr
from converter.file_handler import process_uploaded_file, cleanup_temp_directory
from converter.ast_processor import parse_javascript_to_ast, transform_ast_rename_variable, generate_javascript_from_ast
# from converter.ast_comparator import compare_asts # Will be added later

def handle_conversion(uploaded_file, source_lang, dest_lang):
    """
    Handles the code conversion process:
    1. Processes the uploaded file (single or zip).
    2. Parses the first JavaScript file to AST.
    3. Performs a predefined AST transformation (rename a variable).
    4. Generates JavaScript code from the transformed AST.
    5. Cleans up temporary files.
    """
    if uploaded_file is None:
        return "Error: No file uploaded.", "AST comparison not yet implemented."

    temp_dir = None  # Initialize temp_dir to ensure it's available for finally block
    try:
        processed_files, temp_dir = process_uploaded_file(uploaded_file)

        if not processed_files:
            return "Error: File processing failed. Check if the file is valid (e.g., .js or .zip of .js files).", \
                   "AST comparison not yet implemented."

        # For now, process only the first file
        # TODO: Add logic to handle multiple files or let user choose
        first_file_path = processed_files[0]

        # Check if the file is a JavaScript file (basic check)
        # More robust checking might be needed for production (e.g. based on selected source_lang)
        if not first_file_path.lower().endswith(".js"):
            return f"Error: The file '{first_file_path.split('/')[-1]}' is not a JavaScript (.js) file.", \
                   "AST comparison not yet implemented."

        original_ast = parse_javascript_to_ast(first_file_path)
        if original_ast is None:
            return f"Error: Failed to parse JavaScript from '{first_file_path.split('/')[-1]}'. Check console for details.", \
                   "AST comparison not yet implemented."

        # Example Transformation: Rename 'oldVarName' to 'newVarName'
        # In a real app, these would come from user input or configuration
        transformed_ast = transform_ast_rename_variable(original_ast, "oldVarName", "newVarName")
        if transformed_ast is None: # Should not happen if original_ast was valid, but good to check
            return "Error: AST transformation failed.", "AST comparison not yet implemented."

        generated_code = generate_javascript_from_ast(transformed_ast)
        if generated_code is None:
            return "Error: Failed to generate JavaScript code from AST.", "AST comparison not yet implemented."

        # Placeholder for AST comparison display
        # original_ast_str = json.dumps(original_ast, indent=2, default=lambda o: o.__dict__ if hasattr(o, '__dict__') else str(o))
        # transformed_ast_str = json.dumps(transformed_ast, indent=2, default=lambda o: o.__dict__ if hasattr(o, '__dict__') else str(o))
        # ast_comparison_output = f"Original AST:\n{original_ast_str}\n\nTransformed AST:\n{transformed_ast_str}"
        # For now, use the placeholder as per requirements.
        ast_comparison_output_text = "AST comparison not yet implemented. (Transformed code is for 'oldVarName' -> 'newVarName')"


        return generated_code, ast_comparison_output_text

    except Exception as e:
        # Log the full error for debugging
        print(f"An unexpected error occurred in handle_conversion: {e}")
        # Provide a user-friendly error message
        return f"An unexpected error occurred: {str(e)}", "AST comparison not yet implemented."
    finally:
        if temp_dir:
            cleanup_temp_directory(temp_dir)

# Define the Gradio interface
with gr.Blocks() as iface:
    gr.Markdown("# Code Converter")
    with gr.Row():
        with gr.Column():
            file_input = gr.File(label="Upload Code File")
            source_language_dropdown = gr.Dropdown(
                label="Source Language/Framework",
                choices=["JavaScript", "Python"],
                value="JavaScript"
            )
            destination_language_dropdown = gr.Dropdown(
                label="Destination Language/Framework",
                choices=["TypeScript", "Java"],
                value="TypeScript"
            )
            convert_button = gr.Button("Convert")
        with gr.Column():
            converted_code_output = gr.Textbox(
                label="Converted Code Output",
                lines=10,
                interactive=False
            )
            ast_comparison_output = gr.Textbox(
                label="AST Comparison",
                lines=10,
                interactive=False
            )

    convert_button.click(
        fn=handle_conversion,
        inputs=[file_input, source_language_dropdown, destination_language_dropdown],
        outputs=[converted_code_output, ast_comparison_output]
    )

if __name__ == "__main__":
    iface.launch()
