Automatic File Organizer

Python Programming – Week 2 | Intermediate Python CLI Automation Project

1. Project Overview

Automatic File Organizer is a Python-based command-line automation tool that organizes messy folders by automatically sorting files into category folders based on their file extensions.

The application helps keep directories such as Downloads clean and organized while preventing accidental file overwrites and preserving existing files.

It uses Python's built-in modules to scan directories, identify file extensions, create category folders, and safely move files.

2. Features
Automatically organizes files based on their extensions.
Supports images, documents, videos, audio, and archives.
Moves unknown file types into an Others folder.
Handles uppercase file extensions such as .JPG.
Supports filenames containing multiple dots.
Prevents accidental overwriting of existing files.
Renames duplicate files using incrementing numbers.
Skips hidden files and subdirectories.
Creates category folders only when required.
Provides a dry-run preview before moving files.
Handles missing folders and filesystem errors.
Displays an execution summary.
Records file operations using Python logging.
3. Technology Stack
Technology	Purpose
Python 3.14.6	Main programming language
pathlib	File and directory handling
os	Operating system operations
shutil	Moving files
argparse	Command-line arguments
logging	Activity and error logging
unittest	Automated testing

No third-party packages are required for the core application.

4. Project Structure
text
file-organizer/
│
├── organizer.py
├── config.py
├── utils.py
│
├── sample_folder/
│
├── tests/
│   ├── __init__.py
│   ├── test_organizer.py
│   └── test_cases.md
│
├── logs/
│   └── organizer.log
│
├── screenshots/
│
└── README.md

5. File Categorization

The application categorizes files using their extensions.

Category	Supported Extensions
Images	.jpg, .jpeg, .png, .gif
Documents	.pdf, .docx, .txt, .xlsx, .pptx
Videos	.mp4, .mkv, .avi
Audio	.mp3, .wav
Archives	.zip, .rar
Others	Unknown extensions and files without extensions

File extensions are converted to lowercase before category lookup.

Examples:

photo.JPG → Images
archive.backup.zip → Archives
notes.txt → Documents
data → Others
6. Requirements
Python 3.14.6
Windows, Linux, or macOS
Terminal or command prompt

Verify your Python installation:

bash
python --version


Expected version:

text
Python 3.14.6

7. Installation
Step 1: Clone the repository
bash
git clone https://github.com/Sreevalli20/skill3.git

Step 2: Navigate to the project folder
bash
cd skill3/file-organizer

Step 3: Verify Python
bash
python --version


No additional package installation is required for the core application.

8. How to Run
Normal file organization
bash
python organizer.py "sample_folder"


This command scans the specified folder and organizes its files into category folders.

Dry-run preview
bash
python organizer.py "sample_folder" --dry-run


This previews planned file movements without modifying the original folder.

Display help
bash
python organizer.py --help

9. Example
Before organization
text
sample_folder/
├── photo.jpg
├── photo.JPG
├── notes.txt
├── song.mp3
├── document.pdf
├── video.mp4
├── archive.backup.zip
└── data

After organization
text
sample_folder/
├── Images/
│   ├── photo.jpg
│   └── photo.JPG
│
├── Documents/
│   ├── notes.txt
│   └── document.pdf
│
├── Audio/
│   └── song.mp3
│
├── Videos/
│   └── video.mp4
│
├── Archives/
│   └── archive.backup.zip
│
└── Others/
    └── data


The original filenames are preserved unless a destination filename already exists.

10. Duplicate File Handling

The application checks whether a destination filename already exists before moving a file.

If duplicate filenames are found, incrementing numbers are added to prevent overwriting.

Example:

text
report.pdf
report_1.pdf
report_2.pdf


Existing files are never intentionally overwritten.

11. Safety and Error Handling

The application includes the following safety measures:

Skips hidden files.
Skips directories and nested folders.
Checks destination filenames before moving files.
Generates unique filenames to prevent overwrites.
Handles missing directories.
Handles permission errors and filesystem exceptions.
Continues processing other files when an individual operation fails.
Provides dry-run mode for safe previews.
12. Testing

The project uses Python's built-in unittest framework.

Run automated tests from the project directory:

bash
python -m unittest discover -s tests -v


The test suite covers:

Mixed file types.
Extension mapping.
Uppercase extensions.
Multi-dot filenames.
Files without extensions.
Duplicate filenames.
Hidden files.
Nested directories.
Empty folders.
Missing folder paths.
Dry-run functionality.
Filesystem error handling.
Repeated execution.

Manual test cases and their actual execution results are documented in:

tests/test_cases.md

13. Logging

Application activity is recorded in:

logs/organizer.log

The log can contain information about:

Successfully moved files.
Skipped files.
Duplicate filename handling.
Filesystem errors.
14. Screenshots

The screenshots/ directory is intended to contain genuine before-and-after screenshots demonstrating file organization.

Screenshots should be captured from actual application execution.

15. Limitations
The application organizes only files directly inside the selected folder.
Nested directories are skipped rather than recursively organized.
Only configured extensions receive dedicated categories.
Unknown extensions are placed in Others.
File movement may fail when files are locked or permissions are insufficient.
Undo functionality is optional and must only be used if implemented and tested.
16. GitHub Repository

Repository: https://github.com/Sreevalli20/skill3.git

This project is part of the Python Programming academic coursework.

17. Author

Sreevalli

Python Programming – Week 2 Project

Built using Python 3.14.6 and Python standard-library modules.
