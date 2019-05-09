# -*- coding: utf-8 -*-
"""
.. module: Serverless Thumbnails Creator
    :platform: AWS
    :copyright: (c) 2019 Mystique.,
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Mystique
.. contactauthor:: miztiik@github issues
"""

import boto3
import os
import sys
import uuid
import logging

from PIL import Image

# Initialize Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def set_global_vars():
    global_vars = {'status': False}
    try:
        global_vars['Owner']                    = "Mystique"
        global_vars['Environment']              = "Prod"
        global_vars['region_name']              = "us-east-1"
        global_vars['tag_name']                 = "serverless-thumbnails-creator"
        global_vars['sizes']                    = {
            'cover': [ 250, 250],
            'profile': [ 200, 200 ],
            'thumbnail': [ 100, 100 ]
        }
        global_vars['status']                   = True
    except Exception as e:
        logger.error("Unable to set Global Environment variables. Exiting")
        global_vars['error_message']            = str(e)
    return global_vars


def is_extension_valid(key):
    """ Verifies if the file extension is valid.
    Valid formats are JPG and PNG.
    """
    extension = os.path.splitext(key)[1].lower()
    if extension.lower() in [
        '.jpg',
        '.jpeg',
        '.png',
    ]:
        return True
    else:
        raise ValueError('File format not supported')


def img_resize_factory(src_path, tgt_path, size):
    """ Resize the image for the given sized  """
    with Image.open(src_path) as img:
        img.thumbnail(size, Image.ANTIALIAS)
        img.save(tgt_path)


def _get_img_from_s3(bucket_name, key, download_path ):
        s3Client = boto3.client('s3')
        s3Client.download_file(bucket_name, key, download_path)


def _put_img_to_s3(upload_path, bucket_name, key ):
        s3Client = boto3.client('s3')
        s3Client.upload_file(upload_path, bucket_name, key)


def _resize_factory_assembly(key, src_bucket, des_bucket):
    try:
        global_vars = set_global_vars()
        # Generate all size of images
        for img_size in global_vars.get('sizes'):
            download_path   = f"/tmp/{uuid.uuid4()}-{key}"
            _get_img_from_s3(src_bucket, key, download_path )
            img_resize_factory(download_path, f"/tmp/{img_size}-{key}", global_vars.get('sizes').get(img_size) )
            _put_img_to_s3( f"/tmp/{img_size}-{key}" , des_bucket, f"{img_size}/{key}")
        return True
    except Exception as e:
        logger.error(f"Unable to resize image. ERROR:{e}")
        return False


def lambda_handler(event, context):
    resp = {'status': False }
    
    if 'Records' not in event:
        resp = {'status': False, "error_message" : 'No Records found in Event' }
        return resp

    # Destination bucket check, If we use same src bucket we will be triggering infinite loop
    des_bucket = os.getenv("DESTINATION_BUCKET")
    if not des_bucket:
        resp = {'status': False, "error_message" : 'No destination S3 bucket provided' }
        return resp

    for record in event['Records']:
        src_bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        factory_running = _resize_factory_assembly(key, src_bucket, des_bucket)
        if factory_running:
            resp = {'status': True }
        else:
            break
    return resp


if __name__ == '__main__':
    lambda_handler(None, None)