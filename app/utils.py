from pathlib import Path
from configparser import ConfigParser
from botocore.exceptions import ClientError
import click
import sys
import boto3
import json
import hashlib


CONFIGFILE_DIR_PATH = f'{Path.home()}/.config/cloudphoto'
CONFIGFILE_PATH = f'{CONFIGFILE_DIR_PATH}/cloudphotorc.ini'


def get_credentials():
    config = ConfigParser()

    try:
        config.read(CONFIGFILE_PATH)
    except Exception as ex:
        click.echo(click.style(f'{str(ex)}\n', fg='red'), err=True)
        sys.exit(1)

    return {
        'bucket': config.get('DEFAULT', 'bucket'),
        'aws_access_key_id': config.get('DEFAULT', 'aws_access_key_id'),
        'aws_secret_access_key': config.get('DEFAULT', 'aws_secret_access_key'),
        'region': config.get('DEFAULT', 'region'),
        'endpoint_url': config.get('DEFAULT', 'endpoint_url')
    }


def is_valid_credentials():
    credentials = get_credentials()

    is_valid = False

    session = boto3.session.Session()

    s3 = session.client(
    service_name ='s3',
    endpoint_url = credentials['endpoint_url'],
    aws_access_key_id = credentials['aws_access_key_id'],
    aws_secret_access_key = credentials['aws_secret_access_key']
    )

    try:
        s3.head_bucket(Bucket=credentials['bucket'])
        is_valid = True
    except Exception as ex:
        click.echo(click.style(f'Wrong credentials!\n', fg='red'), err=True)
        is_valid = False

    return is_valid


def get_s3_client():
    if is_valid_credentials():
        credentials = get_credentials()

        session = boto3.session.Session()

        s3 = session.client(
        service_name ='s3',
        endpoint_url = credentials['endpoint_url'],
        aws_access_key_id = credentials['aws_access_key_id'],
        aws_secret_access_key = credentials['aws_secret_access_key']
        )

        return s3
    else:
        sys.exit(1)


def get_s3_resource():
    if is_valid_credentials():
        credentials = get_credentials()

        s3_resource = boto3.resource('s3', region_name = credentials['region'], 
                                    endpoint_url=credentials['endpoint_url'],
                                    aws_access_key_id = credentials['aws_access_key_id'],
                                    aws_secret_access_key = credentials['aws_secret_access_key'])

        return s3_resource
    else:
        sys_exit(1)


def get_unique_key(text):
    m = hashlib.md5()
    m.update(str(text).encode('utf-8'))
    key = str(int(m.hexdigest(), 16))[0:12]
    return key

    



