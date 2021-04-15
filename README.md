App to deidentify data for the FIP partners.

# Files in this repo

* app_frontend.py: python script that launches application frontend using tkinter
* app_backend.py: python script that runs all deidentification processes.
* dist: folder with instructions to create installers


# Installing desktop app

1. Download windows installer vX.X.exe
2. Execute installer. This will install the app as a desktop app as any other program in windows, creating necessary shortcuts to run the app.
3. You can uninstall whenever you want from Control Panel

# To create installer .exe
(to install app as desktop app)

Compile `create_installer.iss` using Inno Setup Compiler

Reference: https://www.youtube.com/watch?v=DTQ-atboQiI&t=135s

# To create executable app, used to create installer
(this will be a standalone app, you can use it as standalone, but it will be significantly slower)

`pyinstaller --windowed --icon=app_icon.ico --add-data="app_icon.ico;." --add-data="ipa_logo.jpg;." app_frontend.py --noconfirm`
