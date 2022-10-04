from app import utils
import click
import boto3
from botocore.exceptions import ClientError
import os
import io
import ast

def do_download(album_name, path):
    s3 = utils.get_s3_client()

    bucket = utils.get_credentials()['bucket']

    album_dict = {}

    album_key = utils.get_unique_key(album_name)

    # if album exists then get existing album's json file from bucket
    try:
        s3.head_object(Bucket=bucket, Key=f'album/{album_key}.json')
        r = io.BytesIO()
        s3.download_fileobj(bucket, f'album/{album_key}.json', r)
        data = r.getbuffer()
        data_str = data.tobytes().decode('utf-8')
        album_dict = ast.literal_eval(data_str)
    except ClientError as e:
        click.echo(click.style(f'There is no album with name \"{album_name}\" in bucket \"{bucket}\"\n', fg='red'), err=True)
        return 1

    if not os.path.isdir(path):
        try:
            raise ValueError(f'Directory {path} is not available for downloading')
        except ValueError as ex:
            click.echo(click.style(f'{str(ex)}\n', fg='red'), err=True)
            return 1

    for photo_key in album_dict['photo']:
        photo_name = album_dict['photo'][photo_key]
        try:    
            # download photo from bucket using key 'photo/generated_unique_key.jpg from album.json
            s3.download_file(bucket, f'photo/{photo_key}{os.path.splitext(photo_name)[1]}', f'{path}/{photo_name}')
            click.echo(click.style(f'{photo_name} - downloaded', fg='green'))
        except ClientError as ex:
            click.echo(click.style(f'{str(ex)}\n', fg='red'), err=True)
            return 1  

    click.echo(click.style('\nDone\n', fg='green'))
    return 0