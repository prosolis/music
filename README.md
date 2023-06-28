# Prosolis Radio

## Setting up Dev environment on Debian

1. ``sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev``

2. [Setup/Recomplie Python 3.11.2](https://techviewleo.com/how-to-install-python-3-on-debian/)

3. Make sure to have to setup a [Python Virtual Environment](https://docs.python.org/3/library/venv.html) to minimize risk of breaking other python programs.

4. Run ``pip install -r requirements.txt`` at the root of the repo

5. Setup System Environment Variables - in the process of moving to dotenv module

6. Validate you can execute python code
