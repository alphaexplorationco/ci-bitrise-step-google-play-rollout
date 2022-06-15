#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Rolling out release for: ${package_name}"

#echo "Downloading credentials from remote file"
#wget -O "${SCRIPT_DIR}/credentials.json" ${service_account_json_key_path}

if [ -z "$service_account_json_key_content" ] ; then
    echo "Downloading credentials from remote file"
    wget -O "${SCRIPT_DIR}/credentials.json" ${service_account_json_key_path}
else
    echo "Using local content credentials"
    echo "$service_account_json_key_content" > "${SCRIPT_DIR}/credentials.json"
fi

pipenv install google-api-python-client
pipenv install oauth2client

pipenv run python "${SCRIPT_DIR}/rollout.py" "${package_name}" "${SCRIPT_DIR}/credentials.json" "${track}"

rm "${SCRIPT_DIR}/credentials.json"