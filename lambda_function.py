import os
import hmac
import json
import logging
import boto3
from dropbox_helper import DropboxHelper
from s3_cursor_helper import S3CursorHelper
from ocr_helper import OCRHelper
from pdf_helper import PDFHelper
import hashlib


__logger = logging.getLogger()
__logger.setLevel(logging.DEBUG if 'debug' in os.environ and os.environ['debug'].lower()[0] == 't' else logging.INFO)


def lambda_handler(event, context):
    """
    Detect change to Dropbox and react
    :return: the location of the new file or none
    """
    __logger.info(event)
    httpMethod = event['requestContext']['httpMethod'].lower()
    secret = os.environ["dropbox_webhook_secret"]
    account_token = os.environ["dropbox_account_token"]
    try:
        __logger.info(event)
        req_body = event['body']
    except:
        return resp(400, json.dumps(err(msg="expected request body")))
    try:
        if 'post' == httpMethod:
            if get_signature(event) is None:
                return resp(401, "Unauthorized")
            elif not is_authorized(secret, get_signature(event), req_body):
                return resp(403, "Unauthorized")
            cursor_helper = S3CursorHelper(s3_resource=boto3.resource("s3"),
                                         s3_bucket=os.environ["s3_bucket"],
                                         s3_path=os.environ["s3_path"])
            ocr_helper = OCRHelper()
            updated = handle_changed_docs(req_body,
                                          dropbox_helper=DropboxHelper(account_token, cursor_helper, s3_resource=boto3.resource("s3")),
                                          pdf_helper=PDFHelper(),
                                          ocr_helper=ocr_helper)
            return resp(200, json.dumps({"updated": updated}))
        elif 'get' == httpMethod:
            __logger.info("dropbox webhook verification")
            try:
                return DropboxHelper(None, None).verify(event["queryStringParameters"]["challenge"])
            except Exception as e:
                return resp(400, json.dumps(err(msg="unable to verify %s") % e))
        else:
            return resp(400, json.dumps(err(msg="unsupported request type")))
    except Exception as e:
        __logger.exception(e)
        return resp(500, "Unable to match records %s" % str(e))


def get_signature(event):
    return event['headers']['X-Dropbox-Signature'] if 'X-Dropbox-Signature' in event['headers'] else None


def is_authorized(secret, signature, req_body):
    expected = hmac.new(secret.encode("utf-8"), req_body.encode("utf-8"), hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


def up():
    return json.dumps({"status": "ok"})


def err(msg):
    return json.dumps({"error": msg})


def resp(status_code, body, headers=None):
    r = {
        'statusCode': status_code,
        'body': body
    }
    r['headers'] = headers if headers else {'Content-Type': 'application/json'}
    __logger.info(r)
    return r


def handle_changed_docs(req_body, dropbox_helper, pdf_helper, ocr_helper):
    """
    Given a Dropbox changed doc webhook react to changed data.
    :param Dropbox webhook post data
    :return: a list of converted and reposted docs
    """
    __logger.debug("getting changed docs %s" % json.dumps(req_body))
    uploaded_docs = {}
    for account, doc_path in dropbox_helper.get_changed(req_body).items():
        if pdf_helper.is_image_pdf(doc_path):
            image = dropbox_helper.get_data(account, doc_path)
            text = ocr_helper.convert_image(image)
            __logger.info(text)
            __logger.debug("converting doc %s %s" % (account, doc_path))
    __logger.debug("uploaded docs %s" % uploaded_docs)
    return uploaded_docs