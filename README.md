App to deidentify data for the FIP partners.

## Files in this repo

* app_frontend.py: python script that launches application frontend using tkinter
* app_backend.py: python script that runs all deidentification processes.
* dist: folder with .exe

## To create .exe from source file
`pyinstaller --onefile --windowed --icon=app_icon.ico --add-data="app_icon.ico;." --add-data="ipa_logo.jpg;." app_frontend.py`
