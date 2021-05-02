# Scalade Web Service

### Prerequisites ###

* Python version [**3.9**](https://www.python.org/downloads/release/python-390/) (with [pip](https://pip.pypa.io/en/stable/))

### Setup ###
Ensure that python3.9 is installed in your machine and that python3.9 binary is in your PATH.
```
export PATH="$PATH:<dir_to_your_python_installatin>/bin>"
```

Install **poetry** for easier dependency management:
```
python3.9 -m pip install poetry
```

Environment installation (this creates a virtual environemnt and installs all development required packages):
```
poetry install
```

Spawn a shell within the virtual environment and begin to work:
```
poetry shell
sh dev_setup.sh
python manage.py runserver
```

### Development Notes
* A superuser is created at setup for development with **username**: admin **password**: admin

### Tests ###

* TODO

### Contributors ###
* Guillem L—pez Garcia