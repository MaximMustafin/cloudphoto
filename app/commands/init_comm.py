from pathlib import Path
from app import utils
from configparser import ConfigParser
import sys
import click
import os
import boto3
from botocore.exceptions import ClientError

def do_init(bucket, aws_access_key_id, aws_secret_access_key):
    try:
        os.mkdir(utils.CONFIGFILE_DIR_PATH)
    except FileExistsError:
        pass

    config = ConfigParser()

    try:
        config.read(utils.CONFIGFILE_PATH)
    except Exception as ex:
        click.echo(click.style(f'{str(ex)}\n', fg='red'), err=True)
        return 1

    config.set('DEFAULT', 'bucket', str(bucket))
    config.set('DEFAULT', 'aws_access_key_id', str(aws_access_key_id))
    config.set('DEFAULT', 'aws_secret_access_key', str(aws_secret_access_key))
    config.set('DEFAULT', 'region', 'ru-central1')
    config.set('DEFAULT', 'endpoint_url', 'https://storage.yandexcloud.net')

    session = boto3.session.Session()
  
    s3 = session.client(
    service_name ='s3',
    endpoint_url = 'https://storage.yandexcloud.net',
    aws_access_key_id = str(aws_access_key_id),
    aws_secret_access_key = str(aws_secret_access_key)
    )

    try:
        result = s3.head_bucket(Bucket=bucket)
    except ClientError:
        try:
            s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={
                            'LocationConstraint': 'ru-central1'})
        except:
            click.echo(click.style(f'Check your credentials!', fg='red'), err=True)
            return 1

        click.echo(f'Created new bucket "{bucket}"')

    try:
        with open(utils.CONFIGFILE_PATH, 'w') as configfile:
            config.write(configfile)    
    except Exception as ex:
        click.echo(click.style(f'{str(ex)}\n', fg='red'), err=True)
        return 1

    click.echo(click.style('Done\n', fg='green'))
    return 0