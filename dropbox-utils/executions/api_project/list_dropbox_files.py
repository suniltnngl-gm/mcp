import os
import sys
import dropbox
from dotenv import load_dotenv

load_dotenv()

# --- Functions ---

def list_dropbox_files(dbx):
    """Lists the contents of the root folder."""
    try:
        print("\nListing contents of root Dropbox folder...")
        result = dbx.files_list_folder(path="")

        if not result.entries:
            print("Your Dropbox folder is empty.")
        else:
            print("-" * 30)
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FolderMetadata):
                    print(f"[Folder] {entry.name}")
                elif isinstance(entry, dropbox.files.FileMetadata):
                    print(f"[File]   {entry.name} (Size: {entry.size} bytes)")
            print("-" * 30)

    except dropbox.exceptions.ApiError as err:
        # Specifically handle path not found errors for clarity
        if isinstance(err.error, dropbox.files.ListFolderError) and \
           err.error.is_path() and \
           err.error.get_path().is_not_found():
            print(f"Error: The path '' (root folder) was not found.")
        else:
            print(f"*** API Error: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def list_file_revisions(dbx, file_path):
    """Lists the revisions of a specific file."""
    try:
        print(f"\nListing revisions for file: '{file_path}'...")
        result = dbx.files_list_revisions(path=file_path, limit=20)
        
        revisions = result.entries

        if not revisions:
            print("No revisions found for this file.")
        else:
            print("-" * 50)
            print(f"{ 'Revision':<15} {'Last Modified (UTC)':<25} {'Size (bytes)':<10}")
            print("-" * 50)
            for entry in revisions:
                modified_time = entry.server_modified.strftime('%Y-%m-%d %H:%M:%S')
                print(f"{entry.rev:<15} {modified_time:<25} {entry.size:<10}")
            print("-" * 50)

    except dropbox.exceptions.ApiError as err:
        if isinstance(err.error, dropbox.files.ListRevisionsError) and \
           err.error.is_path() and \
           err.error.get_path().is_not_found():
            print(f"Error: The file path '{file_path}' was not found.")
        else:
            print(f"*** API Error: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def main():
    """
    Main function to connect to Dropbox and perform actions based on CLI arguments.
    """
    access_token = os.environ.get('DROPBOX_ACCESS_TOKEN')
    if not access_token:
        print("Error: The 'DROPBOX_ACCESS_TOKEN' environment variable is not set.")
        return

    try:
        dbx = dropbox.Dropbox(access_token)
        print("Successfully connected to Dropbox.")
    except Exception as e:
        print(f"Error connecting to Dropbox: {e}")
        return

    # --- Argument Parsing ---
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] == 'list'):
        list_dropbox_files(dbx)
    elif len(sys.argv) > 1 and sys.argv[1] == 'revisions':
        if len(sys.argv) > 2:
            file_path = sys.argv[2]
            # Add a leading slash if it's missing, as Dropbox paths need it
            if not file_path.startswith('/'):
                file_path = '/' + file_path
            list_file_revisions(dbx, file_path)
        else:
            print("Error: 'revisions' command requires a file path.")
            print("Usage: ./run.sh revisions <path/to/file>")
    else:
        print(f"Error: Unknown command '{sys.argv[1]}'")


if __name__ == "__main__":
    main()