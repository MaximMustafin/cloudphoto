from app import application
import click
import os


@click.group()
def cli():
    pass


@cli.command()
def init():
    aws_access_key_id = input('aws_access_key_id = ')
    aws_secret_access_key = input('aws_secret_access_key = ')
    bucket = input('bucket = ')

    click.echo(click.style(f'\naws_access_key_id = {aws_access_key_id}\n' 
                           f'aws_secret_access_key = {aws_secret_access_key}\n'
                           f'bucket = {bucket}\n', 
                           fg='red'), err=True)


@cli.command()
@click.option('--album', required=True, type=str, help='Album\'s name')
@click.option('--path', type=str, help='Photos directory\'s path', default=os.getcwd())
def upload(album, path):
    click.echo(f'ALBUM={album}, PHOTO_DIR={path}')


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