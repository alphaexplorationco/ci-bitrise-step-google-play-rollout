#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Rolling out release for: ${package_name}"

echo "Downloading credentials from service account file path"
wget -O "${SCRIPT_DIR}/credentials.json" ${service_account_json_key_path}

python3 --version
pip3 install -r "${SCRIPT_DIR}/requirements.txt"
python3 "${SCRIPT_DIR}/rollout.py" "${package_name}" "${SCRIPT_DIR}/credentials.json" "${track}"

# Clean up
rm "${SCRIPT_DIR}/credentials.json"
