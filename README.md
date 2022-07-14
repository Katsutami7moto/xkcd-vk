# xkcd-vk

A tool to automate publishing xkcd comics to a VK club.

### How to install

Python3 should be already installed.
Download the [ZIP archive](https://github.com/Katsutami7moto/xkcd-vk/archive/refs/heads/main.zip) of the code and unzip it.
Then open terminal form unzipped directory and use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```commandline
pip install -r requirements.txt
```
Before you run any of the scripts, you will need to configure environmental variables:

1. Go to the unzipped directory and create a file with the name `.env` (yes, it has only the extension).
It is the file to contain environmental variables that usually store data unique to each user, thus you will need to create your own.
2. Copy and paste this to `.env` file:
```dotenv
VK_APP_ACCESS_TOKEN='{vk_app_access_token}'
VK_GROUP_ID={vk_group_id}
```
3. Replace `{vk_app_access_token}` with access token you will receive with [Implicit Flow](https://dev.vk.com/api/access-token/implicit-flow-user) procedure. You will need to add `photos`, `groups`, `wall` and `offline` to the scope parameter. The request URL will look like that (yes, without "necessary" `redirect_uri`):
```
https://oauth.vk.com/authorize?client_id={vk_app_client_id}&display=page&scope=photos+groups+wall+offline&response_type=token&v=5.131&state=123456
```
You will be redirected to page with this URL:
```
https://oauth.vk.com/blank.html#access_token={vk_app_access_token}&expires_in=0&user_id={your_vk_user_id}&state=123456
```
4. Replace `{vk_group_id}` with the ID of VK club you have created. When you just have created it, the ID is in the URL: `https://vk.com/club{vk_group_id}`.
5. 

### How to use

[WIP]

### Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).
