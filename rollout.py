import copy
import sys

import httplib2
from apiclient.discovery import build
from oauth2client.client import AccessTokenRefreshError
from oauth2client.service_account import ServiceAccountCredentials


# To run: rollout package_name json_credentials_path
def main():
    PACKAGE_NAME = sys.argv[1]
    TRACK = sys.argv[3]

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        sys.argv[2], scopes="https://www.googleapis.com/auth/androidpublisher"
    )

    http = credentials.authorize(httplib2.Http())

    service = build("androidpublisher", "v3", http=http)

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
                rolloutPercentage = release["userFraction"]
                if rolloutPercentage < 1.0:
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
            if len(completed_releases) == 2:
                track_data["releases"].remove(completed_releases[1])

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

    except AccessTokenRefreshError:
        raise SystemExit("The credentials provided are not authorized")


if __name__ == "__main__":
    main()
