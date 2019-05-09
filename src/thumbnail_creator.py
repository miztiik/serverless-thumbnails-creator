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
from resizeimage import resizeimage

# Initialize Logger
logger = logging.getLogger()
# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

def set_global_vars():
    global_vars = {'status': False}
    try:
        global_vars['Owner']                    = "Mystique"
        global_vars['Environment']              = "Prod"
        global_vars['region_name']              = "us-east-1"
        global_vars['tag_name']                 = "serverless-thumbnails-creator"
        global_vars['S3-SourceBucketName']      = "serverless-image-processor"
        global_vars['S3-DestBucketName']        = "processed-image-data"
        global_vars['img_sizes']               = {
            'cover' : [250, 250],
            'profile' : [200, 200],
            'thumbnail' : [200, 150]
        }
        global_vars['status']                   = True
    except Exception as e:
        logger.error("Unable to set Global Environment variables. Exiting")
        global_vars['error_message']            = str(e)
    return global_vars


def gen_cover(image_source_path, resized_cover_path, sizes):
    """ Create the cover sized image    """
    with Image.open(image_source_path) as image:
        cover = resizeimage.resize_cover( image, sizes.get('cover') )
        cover.save(resized_cover_path, image.format)


def gen_profile(image_source_path, resized_profile_path, sizes):
    """ Create the profile sized image  """
    with Image.open(image_source_path) as image:
        profile = resizeimage.resize_cover( image, sizes.get('profile') )
        profile.save(resized_profile_path, image.format)


def gen_thumbnail(image_source_path, resized_thumbnail_path, sizes):
    """ Create the thumbnail sized image """
    with Image.open(image_source_path) as image:
        thumbnail = resizeimage.resize_thumbnail(image, sizes.get('thumbnail') )
        thumbnail.save(resized_thumbnail_path, image.format)


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
        return False

def img_resize_factory(src_path, tgt_path, size):
    """ Resize the image for the given sized  """
    with Image.open(src_path) as img:
        img.thumbnail( size )
        #image.thumbnail(tuple(x / 2 for x in image.size))
        img.save(tgt_path)

def _get_img_from_s3(bucket_name, key, download_path ):
        s3Client = boto3.client('s3')
        # s3Client.download_file(global_vars['S3-SourceBucketName'], key, download_path)
        s3Client.download_file(bucket_name, key, download_path)


def _put_img_to_s3(bucket_name, key, upload_path ):
        s3Client = boto3.client('s3')
        s3Client.upload_file(upload_path, bucket_name, key)

def lambda_handler(event, context):
    resp = {'status': False, 'TotalItems': {} , 'Items': [] }
    
    global_vars = set_global_vars()

    if 'Records' not in event:
        resp = {'status': False, "error_message" : 'No Records found in Event' }
        return resp

    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)
        upload_path_cover = '/tmp/cover-{}'.format(key)
        upload_path_profile = '/tmp/profile-{}'.format(key)
        upload_path_thumbnail = '/tmp/thumbnail-{}'.format(key)
 
        _get_img_from_s3(global_vars['S3-SourceBucketName'], key, download_path )
        fname=key.rsplit('.', 1)[0]
        fextension=key.rsplit('.', 1)[1]

        img_resize_factory(download_path, upload_path_cover, global_vars.get('img_sizes').get('cover'))
        _put_img_to_s3( global_vars['S3-DestBucketName'], 'cover/{0}-cover.{1}'.format(fname,fextension), upload_path_cover )
        
        """
        gen_cover( download_path, upload_path_cover, global_vars.get('img_sizes') )
        s3Client.upload_file(upload_path_cover, global_vars['S3-DestBucketName'], 'cover/{0}-cover.{1}'.format(fname,fextension))
 
        gen_profile(download_path, upload_path_profile, global_vars.get('img_sizes') )
        s3Client.upload_file(upload_path_profile, global_vars['S3-DestBucketName'], 'profile/{0}-profile.{1}'.format(fname,fextension))
 
        gen_thumbnail(download_path, upload_path_thumbnail, global_vars.get('img_sizes') )
        s3Client.upload_file(upload_path_thumbnail, global_vars['S3-DestBucketName'], 'thumbnail/{0}-thumbnail.{1}'.format(fname,fextension))
        """
    return key


if __name__ == '__main__':
    lambda_handler(None, None)