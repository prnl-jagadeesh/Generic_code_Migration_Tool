# AI Code Migration Tool (Working Title)

## Core Idea
This project is an AI-powered code migration tool that allows developers to convert codebases from one language or framework to another (e.g., AngularJS to Angular, JavaScript to TypeScript). This tool leverages AST (Abstract Syntax Tree) transformations to ensure accurate, robust, and maintainable code conversion.

## Current Features (as of Initial Commit)
*   Basic Gradio web interface for file uploads.
*   Support for uploading individual `.js` files or `.zip` archives containing `.js` files.
*   JavaScript code parsing into an Abstract Syntax Tree (AST) using `esprima`.
*   A simple AST transformation example: renaming a predefined variable (`oldVarName` to `newVarName`).
*   Generation of JavaScript code from the transformed AST using `escodegen`.
*   Display of the converted code in the UI.
*   Unit tests for file handling and AST processing.

## How to Run

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your_username/your_repository_name.git # Replace <repository_url> with the actual URL
    cd ai-code-migration-tool
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    python app.py
    ```
    The application should then be accessible via a local URL displayed in your terminal (usually `http://127.0.0.1:7860` or similar).

## Project Structure
*   `app.py`: Main application file using Gradio for the UI.
*   `converter/`: Module containing the core conversion logic.
    *   `file_handler.py`: Handles file uploads and extraction.
    *   `ast_processor.py`: Manages AST parsing, transformation, and code generation.
    *   `ast_comparator.py`: (Basic implementation for AST comparison).
*   `tests/`: Contains unit tests for the converter module.
