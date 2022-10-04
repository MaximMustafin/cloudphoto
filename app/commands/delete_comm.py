from app import utils
import click
import boto3
from botocore.exceptions import ClientError
import os
import io
import ast
import json


def do_delete(album_name, photo_name):
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

    # delete photo and album
    if photo_name == None:
        try:
            for photo_key in album_dict['photo']:
                file_extension = os.path.splitext(album_dict['photo'][photo_key])[1]
                s3.delete_object(Bucket=bucket, Key=f'photo/{photo_key}{file_extension}')
                click.echo(click.style(f"Photo {album_dict['photo'][photo_key]} - deleted from cloud", fg='green'))
        except ClientError as ex:
            click.echo(click.style(f'{str(ex)}', fg='red'), err=True)
            return 1

        try:
            s3.delete_object(Bucket=bucket, Key=f'album/{album_key}.json')
            click.echo(click.style(f"Album {album_dict['name']} - deleted from cloud", fg='green'))
        except ClientError as ex:
            click.echo(click.style(f'{str(ex)}', fg='red'), err=True)
            return 1
    # delete only photo from album
    else:
        photo_key = utils.get_unique_key(photo_name)
        if not photo_key in album_dict['photo']:
            print("not")
            try:
                raise ValueError(f'There is not photo "{photo_name}"')
            except ValueError as ex:
                click.echo(click.style(f'{str(ex)}\n', fg='red'), err=True)
                return 1

        try:
            file_extension = os.path.splitext(album_dict['photo'][photo_key])[1]
            s3.delete_object(Bucket=bucket, Key=f'photo/{photo_key}{file_extension}')
            click.echo(click.style(f"Photo {album_dict['photo'][photo_key]} - deleted from cloud", fg='green'))
            del album_dict['photo'][photo_key]
            s3.put_object(Bucket=bucket, Key=f'album/{album_key}.json', Body=json.dumps(album_dict))
        except ClientError as ex:
            click.echo(click.style(f'{str(ex)}', fg='red'), err=True)
            return 1  


    click.echo(click.style('\nDone\n', fg='green'))
    return 0