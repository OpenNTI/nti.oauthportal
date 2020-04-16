authentication
==============

Getting Started
---------------

- Change directory into your newly created project.

    cd nti.oauthportal

- Create a Python virtual environment.

    python3 -m venv env

- Upgrade packaging tools.

    env/bin/pip install --upgrade pip setuptools

- Install the project in editable mode with its testing requirements.

    env/bin/pip install -e ".[testing]"

- Run your project's tests.

    env/bin/pytest

- Run your project.

  When running the server, the proper signer secret and salt will be
  required to match those from the platform using this portal, e.g.
  the signer secret from the ``dataserver-signer`` configuration section.
  This can be provided in the ini file as ``signer.secret`` and
  ``signer.salt``:

    env/bin/nti_pserve --paste development.ini

  or provided on the command line with ``SIGNER_SECRET`` and
  ``SIGNER_SALT`` environmental variables:

    SIGNER_SECRET=<signer-secret> SIGNER_SALT=<signer-salt> env/bin/nti_pserve --paste development.ini

