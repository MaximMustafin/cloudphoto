from app import utils
import click
import boto3
from botocore.exceptions import ClientError
import sys
import os
import json
import io
import ast


def do_upload(album_name, path):
    s3 = utils.get_s3_client()

    bucket = utils.get_credentials()['bucket']

    album_dict = {}

    album_key = utils.get_unique_key(album_name)

    try:
        s3.head_object(Bucket=bucket, Key=f'album/{album_key}.json')
        r = io.BytesIO()
        s3.download_fileobj(bucket, f'album/{album_key}.json', r)
        data = r.getbuffer()
        data_str = data.tobytes().decode('utf-8')
        album_dict = ast.literal_eval(data_str)
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            album_dict['name'] = album_name
            album_dict['photo'] = {}

    print(album_dict)

    try:
        files = os.listdir(path)
    except Exception as ex:
        click.echo(click.style(f'{str(ex)}\n', fg='red'), err=True)
        return 1

    files = list(filter(lambda x: x.endswith(('.jpg', '.jpeg')), files))

    if len(files) == 0:
        try:
            raise ValueError(f'There is not photo in {path}')
        except ValueError as ex:
            click.echo(click.style(f'{str(ex)}\n', fg='red'), err=True)
            return 1

    for file in files:
        with open(f'{file}', 'rb') as photo:
            try:
                split_tup = os.path.splitext(photo.name)
                photo_name = split_tup[0]
                photo_extension = split_tup[1]
                photo_key = utils.get_unique_key(photo_name)
                s3.upload_fileobj(photo, bucket, f'photo/{str(photo_key)}{photo_extension}')
                click.echo(click.style(f'{file} - uploaded', fg='green'))
                album_dict['photo'][photo_key] = photo.name
            except Exception as ex:
                click.echo(click.style(f'{str(ex)}\n', fg='red'), err=True)
                return 1  

    try:
        s3.put_object(Bucket=bucket, Key=f'album/{album_key}.json', Body=json.dumps(album_dict))
    except Exception as ex:
        click.echo(click.style(f'{str(ex)}\n', fg='red'), err=True)
        return 1  

    click.echo(click.style('Done\n', fg='green'))
    return 0