import json
from pathlib import Path
from urllib.parse import unquote, urlsplit, urljoin

import requests
from environs import Env


def get_file_name_from_url(url: str) -> str:
    return Path(unquote(urlsplit(url).path)).name


def download_image(images_dir_path: Path, image_url: str) -> Path:
    img_response = requests.get(image_url)
    img_response.raise_for_status()
    image_path = images_dir_path.joinpath(
        get_file_name_from_url(image_url)
    )
    with open(image_path, 'wb') as file:
        file.write(img_response.content)
    return image_path


def get_comic_metadata(comic_url: str) -> dict:
    response = requests.get(
        urljoin(comic_url, 'info.0.json')
    )
    response.raise_for_status()
    return response.json()


def get_pretty_json(data: dict):
    return json.dumps(
        data,
        indent=4,
        ensure_ascii=False
    )


def get_vk_api_response(api_method: str, method_params: dict) -> dict:
    vk_api_url = 'https://api.vk.com/method/'
    method_url = urljoin(vk_api_url, api_method)
    method_response = requests.get(
        url=method_url,
        params=method_params
    )
    method_response.raise_for_status()
    return method_response.json()['response']


def post_image_on_vk_club_wall(image_path: Path,
                               group_id: int, access_token: str):
    vk_api_version = '5.131'

    photos_get_wall_upload_server_response = get_vk_api_response(
        api_method='photos.getWallUploadServer',
        method_params={
            'group_id': group_id,
            'access_token': access_token,
            'v': vk_api_version
        }
    )

    upload_url = photos_get_wall_upload_server_response.get('upload_url')
    with open(image_path, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(upload_url, files=files)
        response.raise_for_status()
        response_after_upload: dict = response.json()

    server, photo, hash_ = response_after_upload.values()
    photos_save_wall_photo_response = get_vk_api_response(
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
    print(get_pretty_json(photos_save_wall_photo_response))


def main():
    env = Env()
    env.read_env()
    vk_app_client_id: int = env.int('VK_APP_CLIENT_ID')
    vk_app_access_token: str = env('VK_APP_ACCESS_TOKEN')
    vk_group_id: int = env.int('VK_GROUP_ID')
    images_dir_path = Path('images')
    images_dir_path.mkdir(parents=True, exist_ok=True)
    comic_url = 'https://xkcd.com/353/'
    comic_metadata = get_comic_metadata(comic_url)
    image_url: str = comic_metadata['img']
    author_comment: str = comic_metadata['alt']
    image_path = download_image(images_dir_path, image_url)
    print(author_comment)
    post_image_on_vk_club_wall(image_path, vk_group_id, vk_app_access_token)


if __name__ == "__main__":
    main()
