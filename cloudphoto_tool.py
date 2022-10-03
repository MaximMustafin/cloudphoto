from app.commands import init_comm
from app.commands import upload_comm
import click
import os
import sys

@click.group()
def cli():
    pass


@cli.command()
def init():
    bucket = input('bucket = ')
    aws_access_key_id = input('aws_access_key_id = ')
    aws_secret_access_key = input('aws_secret_access_key = ')
    
    status_code = init_comm.do_init(bucket, aws_access_key_id, aws_secret_access_key)
    sys.exit(status_code)

    
@cli.command()
@click.option('--album', required=True, type=str, help='Album\'s name')
@click.option('--path', type=str, help='Photos directory\'s path', default=os.getcwd())
def upload(album, path):
    status_code = upload_comm.do_upload(album, path)
    sys.exit(status_code)


@cli.command()
@click.option('--album', required=True, type=str, help='Album\'s name')
@click.option('--path', type=str, help='Photos directory\'s path', default=os.getcwd())
def download(album, path):
    click.echo(f'ALBUM={album}, PHOTO_DIR={path}')


@cli.command()
@click.option('--album', type=str, help='Album\'s name')
def list(album):
    click.echo(f'ALBUM={album}')


@cli.command()
@click.option('--album', required=True, type=str, help='Album\'s name')
@click.option('--photo', type=str, help='Photo\'s name')
def delete(album, photo):
    click.echo(f'ALBUM={album}, PHOTO={photo}')


@cli.command()
def mksite():
    click.echo(f'mksite command')