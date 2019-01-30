import boto3


class S3CursorHelper(object):

    def __init__(self, s3_resource, s3_bucket, s3_path):
        s3_bucket = s3_bucket[:-1] if s3_bucket[-1] == "/" else s3_bucket
        s3_path = s3_path[:-1] if s3_path[-1] == "/" else s3_path
        s3_path = s3_path[1:] if s3_path[0] == "/" else s3_path
        self.__s3_resource =s3_resource
        self.__s3_bucket = s3_bucket
        self.__s3_path = s3_path

    def get_cursor(self, s3_resource, account):
        """
        Get the current sync position for an account
        :param s3_resource: an s3 resource object from boto3
        :param s3_bucket: an s3 bucket name
        :param account: a dropbox account name
        :return: the current cursor position
        """
        try:
            return s3_resource.Object(self.__s3_bucket, self.cursor_path(account)).get()['Body'].read().decode("utf-8")
        except Exception as e:
            if "NoSuchKey" in str(e):
                print("no cursor exists at %s" % self.cursor_path(account))
            else:
                print("warning: %s" % e)
            return None

    def set_cursor(self, s3_resource, account, cursor):
        """
        Set the current sync position for an account
        :param s3_resource: an s3 resource object from boto3
        :param s3_bucket: an s3 bucket name
        :param account: a dropbox account name
        :return: the current cursor position
        """
        try:
            s3_resource.Object(self.__s3_bucket, self.cursor_path(account)).put(Body=cursor)
        except Exception as e:
            print(e)
            return None

    def cursor_path(self, account):
        return "%s/%s" % (self.__s3_path, account)
