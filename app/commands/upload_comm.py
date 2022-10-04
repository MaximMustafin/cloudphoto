from app import utils
import click
import boto3
from botocore.exceptions import ClientError
import os
import json
import io
import ast


def do_upload(album_name, path):
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
        # if it is new album then create new dict
        if e.response['Error']['Code'] == "404":
            album_dict['name'] = album_name
            album_dict['photo'] = {}

    # get all files' names from dir by path
    try:
        files = os.listdir(path)
    except Exception as ex:
        click.echo(click.style(f'Dir {path} is not available\n', fg='red'), err=True)
        return 1

    files = list(filter(lambda x: x.endswith(('.jpg', '.jpeg')), files))

    # check if there is photo in dir
    if len(files) == 0:
        try:
            raise ValueError(f'There is not photo in {path}')
        except ValueError as ex:
            click.echo(click.style(f'{str(ex)}\n', fg='red'), err=True)
            return 1

    for file in files:
        try:
            with open(f'{path}/{file}', 'rb') as photo:
                try:
                    # get photo's filename without full path
                    photo_filename = os.path.basename(photo.name)

                    # split filename on photo name and extension
                    split_tup = os.path.splitext(photo_filename)

                    # get extension of photo file
                    photo_extension = split_tup[1]

                    # genereate unique key out of photo name
                    photo_key = utils.get_unique_key(photo_filename)

                    # upload photo to bucket under key 'photo/generated_unique_key.extension
                    s3.upload_fileobj(photo, bucket, f'photo/{str(photo_key)}{photo_extension}')

                    click.echo(click.style(f'{file} - uploaded', fg='green'))
                    album_dict['photo'][photo_key] = photo_filename
                except ClientError as ex:
                    click.echo(click.style(f'{str(ex)}\n', fg='red'), err=True)
                    return 1  
        except Exception as ex:
            click.echo(click.style(f'{file} is not uploaded', fg='yellow'))
            continue

    # upload album json with info about photo
    try:
        s3.put_object(Bucket=bucket, Key=f'album/{album_key}.json', Body=json.dumps(album_dict))
    except Exception as ex:
        click.echo(click.style(f'{str(ex)}\n', fg='red'), err=True)
        return 1  

    click.echo(click.style('\nDone\n', fg='green'))
    return 0