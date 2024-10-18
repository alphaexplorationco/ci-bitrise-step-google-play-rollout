#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Rolling out release for: ${package_name}"

echo "Downloading credentials from service account file path"
wget -O "${SCRIPT_DIR}/credentials.json" ${service_account_json_key_path}

python3.10 -m pip install --upgrade pip
python3.10 -m pip install pipenv==2024.1.0
pipenv install google-api-python-client==2.145.0
pipenv install oauth2client==4.1.3

pipenv run python "${SCRIPT_DIR}/rollout.py" "${package_name}" "${SCRIPT_DIR}/credentials.json" "${track}"

rm "${SCRIPT_DIR}/credentials.json"
