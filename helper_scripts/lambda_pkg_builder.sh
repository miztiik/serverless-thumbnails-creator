#!/bin/bash
set -ex

# Change to your own unique S3 bucket name:
region_name="us-east-1"
func_name="serverless-image-resize-factory"

# Remove Old file
rm -rf /var/${func_name}

export PATH=~/.local/bin:$PATH
yum -y install curl zip python3
source ~/.bash_profile
pip3 install --upgrade pip
pip3 install --user virtualenv
virtualenv /var/${func_name}
cd /var/${func_name}

source bin/activate
pip3 install Pillow
pip3 freeze > requirements.txt

cd $VIRTUAL_ENV/lib/python3.7/site-packages

# Remove Old Package
rm -rf /var/${func_name}.zip
zip -r9q /var/${func_name}.zip .

# Add our resizer code to the zip file
cd $VIRTUAL_ENV
curl -O https://raw.githubusercontent.com/miztiik/serverless-thumbnails-creator/master/src/thumbnail_creator.py
curl -O https://raw.githubusercontent.com/miztiik/serverless-thumbnails-creator/master/src/serverless-s3-event-processor.py
zip -g /var/${func_name}.zip thumbnail_creator.py
zip -g /var/${func_name}.zip serverless-s3-event-processor.py

# Upload zip file to S3 bucket
# lmda_src_bkt="sam-templates-011"
# aws s3 cp /var/${func_name}.zip s3://"${lmda_src_bkt}"

