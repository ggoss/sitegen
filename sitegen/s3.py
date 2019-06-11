#!/usr/bin/env python3
# encoding: utf-8

# upload.py

from sitegen import *

"""
To use this, you should set up an IAM user in AWS. Place a copy of its credentials in '~/.aws/credentials,' with the
following:

    [default]
    aws_access_key_id = YOUR_ACCESS_KEY_ID
    aws_secret_access_key = YOUR_SECRET_ACCESS_KEY

You should also have a file at '~/.aws/config,' with the following:

    [default]
    region = YOUR_PREFERRED_REGION
    
"""


def sync() -> None:
    subprocess.run(f'aws s3 sync {Params.OUTPUT_PATH} s3://{Params.BUCKET_NAME}', shell=True, capture_output=True)
