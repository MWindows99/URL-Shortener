# URL-Shortener
This is a simple URL shortener written in Python using FastAPI and SQLite3.

This URL shortening service supports custom URLs and URL removal.
It is possible to create a custom URL and associate it with a destination URL.

## Installation
Install the dependencies using `pip install -U -r requirements.txt`.

## Usage
Run the server using `python main.py`. (Use the `nohup` command to keep it running.)

## Configuration
The configuration is done in the `config.ini` file. The following options are available:

**[API]**
 - `HOST` (String): The host to listen on. (Default: `localhost`)
 - `PORT` (Int): The port to listen on. (Default: `8000`

**[DATABASE]**
 - `PATH` (String): The path to the database file. (Default: `data.db`)

**[DOMAIN]**
 - `DOMAIN` (String): The domain to use for short URLs. (Default: `http://localhost:8000`)

**[DOCS]**
 - `SWAGGER` (Boolean): Change to `True` to enable the document. (Default: `False`)
 - `REDOC` (Boolean): Change to `True` to enable the document. (Default: `False`)

## API Specification
Requests to the API are done using JSON. The following endpoints are available:
 - `/shorten` [Method: `POST`] : Shortens a URL. The request body must contain a URL. If you want to use a custom short URL, you can add a 'key' in the request body. The delete key cannot be customized.<br>*The response contains the short URL and a boolean indicating if the operation was successful.<br>
**Status**: 201(Success) / 400(Error)
 - `/delete` [Method: `DELETE`] : Deletes a short URL. The request body must contain a 'short_key' which is the short URL and the 'delete_key' which is the key of the short URL.<br>*The response contains a boolean indicating if the deletion was successful.<br>
**Status**: 200(Success) / 404(Error) / 400(Error)

## Example
### ･Requests
#### 1. Shorten
```bash
curl -X 'POST' \
  'http://localhost:8000/shorten/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "https://umamusume.jp/character/detail/?name=specialweek",
  "key": "short"
}'
```

#### 2. Delete
```bash
curl -X 'DELETE' \
  'http://localhost:8000/delete/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "short_key": "short",
  "delete_key": "eklR8RWkL7"
}'
```

### ･Response
#### 1. Shorten
 - Success Response
```json
{
    "status": 201,
    "error": false,
    "data": {
        "short_url": "http://localhost:8000/short",
        "keys": {
            "short_key": "short",
            "delete_key": "eklR8RWkL7"
        }
    }
}
```
 - Error Response
```json
{
    "status": 400,
    "error": true,
    "data": "Invalid URL encoring."
}
```

#### 2. Delete
 - Success Response
```json
{
    "status": 200,
    "error": false,
    "message": "Success"
}
```
 - Error Response
```json
{
    "status": 400,
    "error": true,
    "message": "Wrong delete key."
}
```

## License
Please watch the [License](https://github.com/MWindows99/URL-Shortener/blob/main/LICENSE) file for more information.

## Report a bug
Please send from [Issues](https://github.com/MWindows99/URL-Shortener/issues/new) tab.
