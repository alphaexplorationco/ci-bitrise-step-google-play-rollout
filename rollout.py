import copy
import sys

from google.auth.exceptions import RefreshError
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google_auth_httplib2 import AuthorizedHttp

import httplib2


# To run: rollout package_name json_credentials_path track
def main():
    PACKAGE_NAME = sys.argv[1]
    TRACK = sys.argv[3]

    credentials = service_account.Credentials.from_service_account_file(
        filename=sys.argv[2],
        scopes=["https://www.googleapis.com/auth/androidpublisher"],
    )

    http = httplib2.Http()
    authorized_http = AuthorizedHttp(credentials, http)
    service = build("androidpublisher", "v3", http=authorized_http)

    try:
        edit_request = service.edits().insert(body={}, packageName=PACKAGE_NAME)
        result = edit_request.execute()
        edit_id = result["id"]

        track_data = (
            service.edits()
            .tracks()
            .get(editId=edit_id, packageName=PACKAGE_NAME, track=TRACK)
            .execute()
        )
        original_track_data = copy.deepcopy(track_data)

        print("Current status: ", track_data)
        for release in track_data["releases"]:
            if "userFraction" in release:
                rollout_percentage = release["userFraction"]
                status = release["status"]
                if rollout_percentage < 1.0 and status == "inProgress":
                    del release["userFraction"]
                    release["status"] = "completed"
                else:
                    print("Release already fully rolled out or halted")
                    continue

        if original_track_data != track_data:
            completed_releases = list(
                filter(
                    lambda release: release["status"] == "completed",
                    track_data["releases"],
                )
            )
            track_data["releases"] = completed_releases[:1]

            print("Updating status: ", track_data)

            service.edits().tracks().update(
                editId=edit_id, track=TRACK, packageName=PACKAGE_NAME, body=track_data
            ).execute()

            commit_request = (
                service.edits()
                .commit(editId=edit_id, packageName=PACKAGE_NAME)
                .execute()
            )

            print("✅ Edit ", commit_request["id"], " has been committed")
        else:
            print("✅ No rollout needed")

    except RefreshError:
        raise SystemExit("The credentials provided are not authorized")


if __name__ == "__main__":
    main()
