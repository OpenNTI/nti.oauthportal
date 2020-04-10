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
  required from the platform using this portal, e.g. the signer secret
  from the dataserver-signer configuration section.  This can be provided
  in the ini file as `signer.secret` and `signer.salt`, or on the command
  line with `SIGNER_SECRET` AND `SIGNER_SALT` environmental variables.

    env/bin/pserve development.ini

  or

    SIGNER_SECRET=<signer-secret> SIGNER_SALT=<signer-salt> env/bin/pserve development.ini
