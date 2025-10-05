import os
import shutil


# Dictionary mapping file extensions to folder names
FILE_CATEGORIES = {
    "Documents": [".pdf", ".docx", ".txt", ".pptx", ".xlsx", ".xls", ".odt", ".ods", ".csv"],
    "Images": [".jpg", ".png", ".jpeg", ".gif", ".svg", ".tiff", ".ai", ".raw", ".webp"],
    "Audio": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a", ".wma", ".opus"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".flv", ".3gb"],
    "Archives": [".zip", ".rar", ".tar", ".gz", ".iso", ".phg"],
    "Python Work": [".py", ".ipynb", ".pyc", ".pyd", ".pyo", ".pyw"],
    "Java Work": [".java", ".jar", ".war", ".class", ".kt"],
    "C++ Work": [".cpp", ".c", ".h", ".hpp", ".cxx", ".obj", ".cc"],
    "Js/Web Work": [".js", ".ts", ".jsx", ".tsx", ".json", ".html", ".css", ".sass"],
    "Executables": [".exe", ".msi", ".app", ".apk", ".ipa", ".rmp"],
    "Database": [".db", ".sqlite", ".sql", ".dbf", ".mdb", ".accdb"],
    "System files": [".ini", ".reg", ".bat", ".cmd", ".sys", ".bash", ".log"],
    "Others": []  # For unknown file types
}


def get_category(file_extension):
    """Find which category a file belongs to based on its extension"""
    for category, extensions in FILE_CATEGORIES.items():
        if file_extension.lower() in extensions:
            return category
    return "Others"  # Default category


def organize_files(directory_path):
    """Main function to organize files in a directory"""
    # Create all category folders if they don't exist
    for category in FILE_CATEGORIES:
        folder_path = os.path.join(directory_path, category)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Created folder: {category}")

    # Organize files
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        # Skip directories
        if os.path.isdir(file_path):
            continue

        # Get file extension
        _, file_extension = os.path.splitext(filename)
        category = get_category(file_extension)

        # New file path
        dest_folder = os.path.join(directory_path, category)
        dest_path = os.path.join(dest_folder, filename)

        try:
            shutil.move(file_path, dest_path)
            print(f"Moved: {filename} => {category}/")
        except Exception as e:
            print(f"Error moving {filename}: {str(e)}")


if __name__ == "__main__":
    target_directory = "C:/Users/ANISA GUPTA/Documents"

    if os.path.exists(target_directory):
        organize_files(target_directory)
        print("\nAll files organized successfully! 🎉")
    else:
        print("Error: Directory doesn't exist! ❌")
