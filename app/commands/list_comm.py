from app import utils
import click
import boto3
from botocore.exceptions import ClientError
import os
import io
import ast


def do_list(album_name):
    s3 = utils.get_s3_client()
    
    s3_resource = utils.get_s3_resource()

    bucket_name = utils.get_credentials()['bucket']

    bucket = s3_resource.Bucket(bucket_name)

    r = io.BytesIO()

    if album_name == None:
        albums = bucket.objects.filter(Prefix='album/')

        if len(list(albums)) == 0:
            try:
                raise ValueError(f'There is no albums in \"{bucket_name}\"')
            except ValueError as ex:
                click.echo(click.style(f'{str(ex)}\n', fg='red'), err=True)
            return 1

        for album in albums:
            try:
                s3.head_object(Bucket=bucket_name, Key=str(album.key))
                r = io.BytesIO()
                s3.download_fileobj(bucket_name, album.key, r)
                data = r.getbuffer()
                data_str = data.tobytes().decode('utf-8')
                album_dict = ast.literal_eval(data_str)
                print(album_dict['name'])
            except ClientError as e:
                click.echo(click.style(f'There is no album with name \"{album_name}\" in bucket \"{bucket}\"\n', fg='red'), err=True)
                return 1
        
    else:
        album_dict = {}

        album_key = utils.get_unique_key(album_name)

        # if album exists then get existing album's json file from bucket
        try:
            s3.head_object(Bucket=bucket_name, Key=f'album/{album_key}.json')
            r = io.BytesIO()
            s3.download_fileobj(bucket_name, f'album/{album_key}.json', r)
            data = r.getbuffer()
            data_str = data.tobytes().decode('utf-8')
            album_dict = ast.literal_eval(data_str)
        except ClientError as e:
            click.echo(click.style(f'There is no album with name \"{album_name}\" in bucket \"{bucket_name}\"\n', fg='red'), err=True)
            return 1

        if len(album_dict['photo']) == 0:
            try:
                raise ValueError(f"There is no photo in {album_dict['name']} album")
            except ValueError as ex:
                click.echo(click.style(f'{str(ex)}\n', fg='red'), err=True)
            return 1

        for photo_key in album_dict['photo']:
            print(album_dict['photo'][photo_key])

    click.echo(click.style('\nDone\n', fg='green'))
    return 0
