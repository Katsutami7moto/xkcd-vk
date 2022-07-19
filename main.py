from pathlib import Path
from urllib.parse import unquote, urlsplit, urljoin

import requests
from environs import Env


def get_file_name_from_url(url: str) -> str:
    return Path(unquote(urlsplit(url).path)).name


def download_image(images_dir_path: Path, image_url: str) -> Path:
    image_response = requests.get(image_url)
    image_response.raise_for_status()
    image_path = images_dir_path.joinpath(
        get_file_name_from_url(image_url)
    )
    with open(image_path, 'wb') as file:
        file.write(image_response.content)
    return image_path


def get_comic_metadata(comic_url: str) -> dict:
    response = requests.get(
        urljoin(comic_url, 'info.0.json')
    )
    response.raise_for_status()
    return response.json()


def get_random_comic_url() -> str:
    xkcd_random_url = 'https://c.xkcd.com/random/comic/'
    response = requests.get(xkcd_random_url)
    response.raise_for_status()
    random_comic_url = response.history[1].url
    return random_comic_url


def get_vk_api_response(api_method: str, method_params: dict) -> dict:
    vk_api_url = 'https://api.vk.com/method/'
    method_url = urljoin(vk_api_url, api_method)
    method_response = requests.get(
        url=method_url,
        params=method_params
    )
    method_response.raise_for_status()
    return method_response.json().get('response')


def get_vk_upload_server_url(group_id: int, access_token: str,
                             vk_api_version: str) -> str:
    return get_vk_api_response(
        api_method='photos.getWallUploadServer',
        method_params={
            'group_id': group_id,
            'access_token': access_token,
            'v': vk_api_version
        }
    ).get('upload_url')


def upload_image(image_path: Path, upload_url: str) -> list:
    with open(image_path, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(upload_url, files=files)
        response.raise_for_status()
    return response.json().values()


def save_image_in_club_album(group_id: int, access_token: str,
                             vk_api_version: str,
                             server: int, photo: str, hash_: str) -> tuple:
    saved_wall_photo_response = get_vk_api_response(
        api_method='photos.saveWallPhoto',
        method_params={
            'group_id': group_id,
            'photo': photo,
            'server': server,
            'hash': hash_,
            'access_token': access_token,
            'v': vk_api_version
        }
    )
    return tuple(
        saved_wall_photo_response[0].get(key)
        for key in ('owner_id', 'id')
    )


def post_uploaded_image(group_id: int, access_token: str,
                        vk_api_version: str, author_comment: str,
                        image_attachment: str) -> int:
    return get_vk_api_response(
        api_method='wall.post',
        method_params={
            'owner_id': -group_id,
            'from_group': True,
            'message': author_comment,
            'attachments': image_attachment,
            'access_token': access_token,
            'v': vk_api_version
        }
    ).get('post_id')


def post_image_on_vk_club_wall(image_path: Path, group_id: int,
                               access_token: str, author_comment: str) -> int:
    vk_api_version = '5.131'

    upload_url = get_vk_upload_server_url(group_id, access_token,
                                          vk_api_version)

    media_owner_id, media_id = save_image_in_club_album(
        group_id,
        access_token,
        vk_api_version,
        *(upload_image(image_path, upload_url))
    )
    image_attachment = f'photo{media_owner_id}_{media_id}'

    return post_uploaded_image(
        group_id,
        access_token,
        vk_api_version,
        author_comment,
        image_attachment
    )


def main():
    env = Env()
    env.read_env()
    vk_app_access_token: str = env('VK_APP_ACCESS_TOKEN')
    vk_group_id: int = env.int('VK_GROUP_ID')

    images_dir_path = Path('images')
    images_dir_path.mkdir(parents=True, exist_ok=True)

    comic_url = get_random_comic_url()
    comic_metadata = get_comic_metadata(comic_url)
    image_url: str = comic_metadata.get('img')
    author_comment: str = comic_metadata.get('alt')

    image_path = download_image(images_dir_path, image_url)
    post_id = post_image_on_vk_club_wall(
        image_path,
        vk_group_id,
        vk_app_access_token,
        author_comment
    )
    print(f'Post #{post_id} - success!')
    image_path.unlink()


if __name__ == "__main__":
    main()
