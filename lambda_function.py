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


__max_workers = int(os.environ["max_workers"]) if "max_workers" in os.environ else 4
__resolution = int(os.environ["resolution"]) if "resolution" in os.environ else 120
__upload_dir = int(os.environ["upload_dir"]) if "upload_dir" in os.environ else "output"
if __upload_dir[0] is not "/":
    __upload_dir = "/%s" % __upload_dir
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
    app_token = os.environ["dropbox_app_token"]
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
                                          dropbox_helper=DropboxHelper(app_token, cursor_helper, s3_resource=boto3.resource("s3")),
                                          pdf_helper=PDFHelper(ocr_helper))
            return resp(200, json.dumps({"updated": updated}))
        elif 'get' == httpMethod:
            __logger.info("dropbox webhook verification")
            try:
                return DropboxHelper(None, None, None).verify(event["queryStringParameters"]["challenge"])
            except Exception as e:
                return resp(400, json.dumps(err(msg="unable to verify %s") % e))
        else:
            return resp(400, json.dumps(err(msg="unsupported request type")))
    except Exception as e:
        __logger.exception(e)
        return resp(500, "Unable to react to changes %s" % str(e))


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


def handle_changed_docs(req_body, dropbox_helper, pdf_helper):
    """
    Given a Dropbox changed doc webhook react to changed data.
    :param Dropbox webhook post data
    :return: a list of converted and reposted docs
    """
    __logger.debug("getting changed docs %s" % json.dumps(req_body))
    uploaded_docs = []
    for account, dropbox_doc_paths in dropbox_helper.get_changed(req_body).items():
        for dropbox_doc_path in dropbox_doc_paths:
            text = None
            if dropbox_doc_path[-4:] == '.doc':
                local_doc_path = "/tmp%s" % dropbox_doc_path
                resp = dropbox_helper.download_file(dropbox_doc_path, local_doc_path)
                print(resp)
                with open(local_doc_path, "rb") as f:
                    data = f.read()
                    print("downloaded %d bytes" % len(data))
                    import subprocess
                    try:
                        print(subprocess.check_output(['ls', '-l', '/usr/share']))
                    except Exception as e:
                        print(e)
                    try:
                        print(subprocess.check_output(['mkdir', '-p', '/usr/local/share']))
                    except Exception as e:
                        print(e)
                    try:
                        print(subprocess.check_output(['cp', '-r', '/opt/share/', '/usr/local/share']))
                    except Exception as e:
                        print(e)
                    try:
                        text = subprocess.check_output(['antiword', local_doc_path])
                    except subprocess.CalledProcessError as exc:
                        print("Status : FAIL", exc.returncode, exc.output)
            if pdf_helper.is_pdf(dropbox_doc_path) and dropbox_doc_paths[-1 * len(__upload_dir):] != __upload_dir:
                local_doc_path = "/tmp%s" % dropbox_doc_path
                resp = dropbox_helper.download_file(dropbox_doc_path, local_doc_path)
                print(resp)
                with open(local_doc_path, "rb") as f:
                    data = f.read()
                    print("downloaded %d bytes" % len(data))
                text = pdf_helper.get_text(local_doc_path, resolution=__resolution, max_workers=__max_workers)
            if text:
                __logger.info(text)
                __logger.debug("converted doc %s %s" % (account, dropbox_doc_path))
                upload_path = "%s%s.txt" % (__upload_dir, ".".join(dropbox_doc_path.split(".")[:-1]))
                result = dropbox_helper.store_data(text, upload_path)
                print(result)
                uploaded_docs.append(upload_path)
    __logger.debug("uploaded docs %s" % uploaded_docs)
    return uploaded_docs
