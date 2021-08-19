App to deidentify financial data from FIP partners.

# Main files in this repo

* app_frontend.py: python script that launches application frontend using tkinter
* app_backend.py: python script that runs all deidentification processes.

# Running locally

First, create a file called `password.py` in this directory, and fill it with the following code:

```
def get_password_hash():
    return 'sha256_of_the_password'
```

To compute the value of 'sha256_of_the_password' you can run the following piece of code

```
from hashlib import sha256
print(sha256((str(password)).encode('utf-8')).hexdigest())
```

Once password.py file is ready, launch the app running

`python app_frontend.py`


# Installing desktop app

1. Download latest windows installer from [releases](https://github.com/PovertyAction/fip_deidentification/releases/latest)
2. Execute installer. This will install the app as a desktop app as any other program in windows, creating necessary shortcuts to run the app.
3. You can uninstall whenever you want from Control Panel

# To create executable app, used to create installer
(this will be a standalone app, you can use it as standalone, but it will be significantly slower)

`pyinstaller --windowed --icon=app_icon.ico --add-data="app_icon.ico;." --add-data="ipa_logo.jpg;." app_frontend.py --noconfirm`

# To create installer .exe
(to install app as desktop app)

Compile `create_installer.iss` using Inno Setup Compiler

Reference: https://www.youtube.com/watch?v=DTQ-atboQiI&t=135s
