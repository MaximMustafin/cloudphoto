from app import utils
import click
import boto3
from botocore.exceptions import ClientError
import os
import re
import io
import ast
import json
import bs4


def do_mksite():
    s3 = utils.get_s3_client()

    s3_resource = utils.get_s3_resource()

    bucket_name = utils.get_credentials()['bucket']

    bucket = s3_resource.Bucket(bucket_name)

    albums = bucket.objects.filter(Prefix='album/')

    # if len(list(albums)) == 0:
    #     try:
    #         raise ValueError(f'There is no albums in \"{bucket_name}\"')
    #     except ValueError as ex:
    #         click.echo(click.style(f'{str(ex)}\n', fg='red'), err=True)
    #     return 1

    file_path = os.path.abspath(__file__)
    dir_path = os.path.dirname(file_path)

    with open(f'{dir_path}/html/index.html') as index:
        index_txt = index.read()
        index_soup = bs4.BeautifulSoup(index_txt, 'html.parser')

    ul_tag = index_soup.new_tag('ul')
    i = 1

    albums_dict = []

    for album in albums:
        try:
            s3.head_object(Bucket=bucket_name, Key=str(album.key))
            r = io.BytesIO()
            s3.download_fileobj(bucket_name, album.key, r)
            data = r.getbuffer()
            data_str = data.tobytes().decode('utf-8')
            album_dict = ast.literal_eval(data_str)

            albums_dict.append(album_dict)
            li_tag = index_soup.new_tag('li')
            a_tag = index_soup.new_tag('a', href=f'album{i}.html')
            i += 1
            a_tag.string = str(album_dict['name'])
            li_tag.append(a_tag)

            ul_tag.append(li_tag)
            
        except ClientError as e:
            click.echo(click.style(f'There is no album with name \"{album_name}\" in bucket \"{bucket}\"\n', fg='red'), err=True)
            return 1

    
    index_soup.body.append(ul_tag)

    with open(f'{dir_path}/html/album.html') as album_html:
        album_html_txt = album_html.read()
        album_soup = bs4.BeautifulSoup(album_html_txt, 'html.parser')

    img_tags = bs4.BeautifulSoup('', 'html.parser')

    albums_html = []

    for album in albums_dict:
        for photo_key in album['photo']:
            photo_name = album['photo'][photo_key]
            photo_extension = os.path.splitext(photo_name)[1]  
            url = f"{utils.get_credentials()['endpoint_url']}/{bucket_name}/photo/{photo_key}{photo_extension}"
            img_tag = album_soup.new_tag('img', src=url, title=photo_name)
            img_tags.append(img_tag)

        div_tag = bs4.BeautifulSoup(f'<div class="galleria">{img_tags}</div>', 'html.parser')
        album_soup.body.p.insert_before(div_tag)
        albums_html.append(album_soup)
        img_tags = bs4.BeautifulSoup('', 'html.parser')
        album_soup = bs4.BeautifulSoup(album_html_txt, 'html.parser')

    with open(f'{dir_path}/html/error.html') as error:
        error_txt = error.read()
        error_soup = bs4.BeautifulSoup(error_txt, 'html.parser')

    # print(index_soup.prettify())

    # for x in albums_html:
    #     print(x.prettify())

    # print(error_soup.prettify())

    i = 1

    for album_page in albums_html:
        try:
            s3.put_object(Bucket=bucket_name, Key=f'album{i}.html', Body=album_page.prettify())
            i += 1
        except Exception as ex:
            click.echo(click.style(f'{str(ex)}\n', fg='red'), err=True)
            return 1  

    try:
        s3.put_object(Bucket=bucket_name, Key='index.html', Body=index_soup.prettify())
        s3.put_object(Bucket=bucket_name, Key='error.html', Body=error_soup.prettify())
    except ClientError as ex:
        click.echo(click.style(f'{str(ex)}\n', fg='red'), err=True)
        return 1  


    website_configuration = {
    'ErrorDocument': {'Key': 'error.html'},
    'IndexDocument': {'Suffix': 'index.html'},
    }

    try:
        s3.put_bucket_website(Bucket=bucket_name,
                      WebsiteConfiguration=website_configuration)
        s3.put_bucket_acl(
            ACL = 'public-read',
            Bucket=bucket_name
        )
    except ClientError as ex:
        click.echo(click.style(f'{str(ex)}\n', fg='red'), err=True)
        return 1 

    print(f'https://{bucket_name}.website.yandexcloud.net/')

    click.echo(click.style('\nDone\n', fg='green'))
    return 0