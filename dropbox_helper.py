import json
from dropbox import Dropbox
from dropbox.files import DeletedMetadata, FolderMetadata


class DropboxHelper(object):

    def __init__(self, account_token, cursor_helper, s3_resource):
        self.__account_token = account_token
        self.__cursor_helper = cursor_helper
        self.__s3_resource =s3_resource

    def get_changed(self, req_body):
        """
        Given a Dropbox webhook post detect changes.
        :param req_body: the Dropbox webhook post request body
        :param cursor_helper: a mwans of storing hte current sync cursor location
        :return: the dropbox paths to the changed files
        """
        changed = {}
        for account in json.loads(req_body)['list_folder']['accounts']:
            changed[account] = self.get_changed_for_account(account, self.__account_token, self.get_cursor(account))
        return changed

    def get_data(self, dropbox_path, account):
        dropbox = Dropbox(self.__account_token)
        _, resp = dropbox.files_download(dropbox_path)
        return resp.Content

    def get_cursor(self, account):
        return self.__cursor_helper.get_cursor(self.__s3_resource, account)

    def set_cursor(self, account, cursor):
        self.__cursor_helper.set_cursor(account, cursor)

    def get_changed_for_account(self, account, account_token, cursor):
        dropbox = Dropbox(account_token)
        print("getting dropbox changed paths for account %s" % account)
        has_more = True
        dropbox_paths = []
        while has_more:
            if cursor is None:
                result = dropbox.files_list_folder(path="")
            else:
                result = dropbox.files_list_folder_continue(cursor)
            dropbox_paths += [e.path_lower for e in result.entries if not isinstance(e, FolderMetadata) and not isinstance(e, DeletedMetadata)]
            has_more = result.has_more
        print(dropbox_paths)
        return dropbox_paths

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