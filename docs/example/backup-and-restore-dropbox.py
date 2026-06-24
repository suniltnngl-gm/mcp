"""Backs up and restores a settings file to Dropbox (API v2)."""

import os
import sys
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

TOKEN = os.environ.get("DROPBOX_ACCESS_TOKEN", "")
LOCALFILE = 'my-file.txt'
BACKUPPATH = '/my-file-backup.txt'


def backup(dbx):
    with open(LOCALFILE, 'rb') as f:
        print("Uploading " + LOCALFILE + " to Dropbox as " + BACKUPPATH + "...")
        try:
            dbx.files_upload(f.read(), BACKUPPATH, mode=WriteMode('overwrite'))
        except ApiError as err:
            if (err.error.is_path() and
                    err.error.get_path().reason.is_insufficient_space()):
                sys.exit("ERROR: Cannot back up; insufficient space.")
            elif err.user_message_text:
                print(err.user_message_text)
                sys.exit()
            else:
                print(err)
                sys.exit()


def change_local_file(new_content):
    print("Changing contents of " + LOCALFILE + " on local machine...")
    with open(LOCALFILE, 'wb') as f:
        f.write(new_content)


def restore(dbx, rev=None):
    print("Restoring " + BACKUPPATH + " to revision " + rev + " on Dropbox...")
    dbx.files_restore(BACKUPPATH, rev)
    print("Downloading current " + BACKUPPATH + " from Dropbox...")
    dbx.files_download_to_file(LOCALFILE, BACKUPPATH, rev)


def select_revision(dbx):
    print("Finding available revisions on Dropbox...")
    entries = dbx.files_list_revisions(BACKUPPATH, limit=30).entries
    revisions = sorted(entries, key=lambda entry: entry.server_modified)
    for revision in revisions:
        print(revision.rev, revision.server_modified)
    return revisions[0].rev


if __name__ == '__main__':
    if not TOKEN:
        sys.exit("ERROR: Set DROPBOX_ACCESS_TOKEN environment variable.")

    print("Creating a Dropbox object...")
    with dropbox.Dropbox(TOKEN) as dbx:
        try:
            dbx.users_get_current_account()
        except AuthError:
            sys.exit("ERROR: Invalid access token.")

        backup(dbx)
        change_local_file(b"updated")
        backup(dbx)

        to_rev = select_revision(dbx)
        restore(dbx, to_rev)
        print("Done!")
