import io
import json
from dropbox import Dropbox
from dropbox.files import DeletedMetadata, FolderMetadata, WriteMode

class DropboxHelper(object):

    def __init__(self, app_token, cursor_helper, s3_resource, dropbox_input_path):
        self.__app_token = app_token
        self.__cursor_helper = cursor_helper
        self.__s3_resource = s3_resource
        self.__dropbox_input_path = dropbox_input_path

    def get_changed(self, req_body):
        """
        Given a Dropbox webhook post detect changes.
        :param req_body: the Dropbox webhook post request body
        :param cursor_helper: a mwans of storing hte current sync cursor location
        :return: the dropbox paths to the changed files
        """
        changed = {}
        for account in json.loads(req_body)['list_folder']['accounts']:
            account_changed, new_cursor = self.get_changed_for_account(account,
                                                                       self.__app_token,
                                                                       self.get_cursor(account),
                                                                       self.__dropbox_input_path)
            if account_changed:
                changed[account] = account_changed
            if new_cursor:
                self.set_cursor(account, new_cursor)
        return changed

    def download_file(self, dropbox_path, local_path):
        dropbox = Dropbox(self.__app_token)
        return dropbox.files_download_to_file(local_path, dropbox_path)

    def store_data(self, data, dropbox_path):
        dropbox = Dropbox(self.__app_token)
        print("storing %s" % dropbox_path)
        return dropbox.files_upload(data.encode("utf-8"), dropbox_path, mode=WriteMode.overwrite)

    def delete(self, dropbox_path):
        dropbox = Dropbox(self.__app_token)
        print("deleting %s" % dropbox_path)
        return dropbox.files_delete_v2(dropbox_path)


    def get_cursor(self, account):
        return self.__cursor_helper.get_cursor(self.__s3_resource, account)

    def set_cursor(self, account, cursor):
        print("updating cursor for %s to %s" % (account, cursor))
        self.__cursor_helper.set_cursor(self.__s3_resource, account, cursor)

    def get_changed_for_account(self, account, account_token, cursor, input_path="/app/input"):
        dropbox = Dropbox(account_token)
        print("getting dropbox changed paths for account %s" % account)
        has_more = True
        dropbox_paths = []
        new_cursor = None
        while has_more:
            if cursor is None:
                result = dropbox.files_list_folder(path=input_path)
            else:
                result = dropbox.files_list_folder_continue(cursor)
            print(result)
            dropbox_paths += [e.path_lower for e in result.entries if not isinstance(e, FolderMetadata) and not isinstance(e, DeletedMetadata)]
            has_more = result.has_more
            new_cursor = result.cursor
        print(dropbox_paths)
        return dropbox_paths, new_cursor

    def verify(self, challenge):
        """
        Respond to the standard Dropbox webhook verification request
        :param req: the request passed by dropbox
        :return: the response to successfully verify
        """
        return {
            "statusCode": 200,
            "body": challenge,
            "headers": {
                "Content-Type": "text/plain",
                "X-Content-Type-Options": "nosniff"
            }
        }