import os
import zipfile
import tempfile
import shutil

def process_uploaded_file(file_obj):
    """
    Processes an uploaded file object from Gradio.

    If the file is a .zip archive, it extracts its contents into a temporary directory.
    If it's a single file, it copies it to a temporary directory.

    Args:
        file_obj: The file object from gr.File(). It has a 'name' attribute
                  which is the path to the uploaded file.

    Returns:
        A tuple: (list_of_file_paths, temp_dir_path).
        'list_of_file_paths' contains absolute paths to the processed file(s).
        'temp_dir_path' is the path to the temporary directory created.
        Returns (None, None) if an error occurs.
    """
    temp_dir_path = tempfile.mkdtemp()
    processed_files = []

    try:
        file_path = file_obj.name  # Path to the uploaded file

        # Heuristic: if filename ends with .zip but is_zipfile is false, treat as error
        if file_path.lower().endswith(".zip") and not zipfile.is_zipfile(file_path):
            print(f"Error: File '{file_path}' has .zip extension but is not a valid zip file.")
            cleanup_temp_directory(temp_dir_path)
            return None, None

        if zipfile.is_zipfile(file_path):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir_path)
            for root, _, files in os.walk(temp_dir_path):
                for file in files:
                    # Skip __MACOSX and other hidden/system files if necessary
                    if not file.startswith('.') and '__MACOSX' not in root:
                        processed_files.append(os.path.join(root, file))
            # If zip contained files at the root, they are already in temp_dir_path
            # If they were in a subdirectory, os.walk handles it.
            # We need to ensure we are not adding the .zip file itself if it was extracted.
            # The current logic correctly lists only extracted contents.
        else:
            # Single file, copy it to the temp directory
            base_name = os.path.basename(file_path)
            new_file_path = os.path.join(temp_dir_path, base_name)
            shutil.copy2(file_path, new_file_path)
            processed_files.append(new_file_path)

        return processed_files, temp_dir_path
    except zipfile.BadZipFile:
        print(f"Error: Invalid or corrupted zip file: {file_path}")
        cleanup_temp_directory(temp_dir_path)
        return None, None
    except Exception as e:
        print(f"An error occurred during file processing: {e}")
        cleanup_temp_directory(temp_dir_path)
        return None, None

def cleanup_temp_directory(temp_dir_path):
    """
    Removes the specified temporary directory and its contents.

    Args:
        temp_dir_path: The path to the temporary directory to be removed.
    """
    if temp_dir_path and os.path.exists(temp_dir_path):
        try:
            shutil.rmtree(temp_dir_path)
            print(f"Successfully removed temporary directory: {temp_dir_path}")
        except Exception as e:
            print(f"Error removing temporary directory {temp_dir_path}: {e}")
    else:
        print(f"Temporary directory {temp_dir_path} not found or already removed.")
