import os
import re
import argparse

def rename_files_to_folder_name(folder_path):
    # Get the name of the folder
    folder_name = os.path.basename(folder_path.rstrip("/\\"))

    # Iterate through all the files in the folder
    for filename in os.listdir(folder_path):
        # Full path to the current file
        full_path = os.path.join(folder_path, filename)

        # Skip if it's not a file
        if not os.path.isfile(full_path):
            continue

        # Find patterns in the filename
        match = re.search(r'(_snv|_sv|_cn|_fusion)', filename)

        # If no pattern is found, skip this file
        if not match:
            continue

        # Construct the new filename
        new_filename = folder_name + filename[match.start():]
        new_full_path = os.path.join(folder_path, new_filename)

        # Rename the file
        os.rename(full_path, new_full_path)
        print(f'Renamed: {filename} -> {new_filename}')

def main():
    # Setup argparse
    parser = argparse.ArgumentParser(description="Rename files in a folder to match the folder name, retaining specific suffix patterns.")
    parser.add_argument(
        "folder_path",
        type=str,
        help="The path to the folder containing files to be renamed"
    )

    # Parse arguments
    args = parser.parse_args()

    # Validate folder path
    if not os.path.isdir(args.folder_path):
        print(f"Error: The provided path '{args.folder_path}' is not a valid directory.")
        return

    # Call the function to rename files
    rename_files_to_folder_name(args.folder_path)

if __name__ == "__main__":
    main()
import os
import re
import argparse

def rename_files_to_folder_name(folder_path):
    # Get the name of the folder
    folder_name = os.path.basename(folder_path.rstrip("/\\"))

    # Iterate through all files in the folder
    for filename in os.listdir(folder_path):
        # Full path to the current file
        full_path = os.path.join(folder_path, filename)

        # Skip if it's not a file
        if not os.path.isfile(full_path):
            continue

        # Find patterns in the filename
        match = re.search(r'(_snv|_sv|_cn|_fusion)', filename)

        # If no pattern is found, skip this file
        if not match:
            continue

        # Construct the new filename
        new_filename = folder_name + filename[match.start():]
        new_full_path = os.path.join(folder_path, new_filename)

        # Rename the file
        os.rename(full_path, new_full_path)
        print(f'Renamed: {filename} -> {new_filename}')

def process_all_subfolders(main_folder_path):
    # Walk through the main folder and its subfolders
    for root, dirs, files in os.walk(main_folder_path):
        # Skip the main folder itself, only process subfolders
        if root == main_folder_path:
            continue
        print(f"Processing folder: {root}")
        rename_files_to_folder_name(root)

def main():
    # Setup argparse
    parser = argparse.ArgumentParser(description="Rename files in subfolders to match their folder names, retaining specific suffix patterns.")
    parser.add_argument(
        "main_folder_path",
        type=str,
        help="The path to the main folder containing subfolders and files to be renamed"
    )

    # Parse arguments
    args = parser.parse_args()

    # Validate main folder path
    if not os.path.isdir(args.main_folder_path):
        print(f"Error: The provided path '{args.main_folder_path}' is not a valid directory.")
        return

    # Process all subfolders within the main folder
    process_all_subfolders(args.main_folder_path)

if __name__ == "__main__":
    main()
