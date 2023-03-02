import re
import random
import string
import sqlite3
import configparser
import uvicorn
import urllib.parse
from pydantic import BaseModel
from fastapi import FastAPI, Response
from fastapi.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware

config = configparser.ConfigParser()
config.read("config.ini")

APP_HOST = str(config.get("API", "HOST"))
APP_PORT = int(config.get("API", "PORT"))
HOST_URL = str(config.get("DOMAIN", "DOMAIN"))
DATABASE = str(config.get("DATABASE", "PATH"))
SWA_DOCS = config.getboolean("DOCS", "SWAGGER")
RED_DOCS = config.getboolean("DOCS", "REDOC")

if SWA_DOCS or RED_DOCS:
    open_api = "/openapi.json"
    swagger_docs = None
    redoc_docs = None
    if SWA_DOCS:
        swagger_docs = "/docs"
    if RED_DOCS:
        redoc_docs = "/redoc"
else:
    open_api = None
    swagger_docs = None
    redoc_docs = None

app = FastAPI(docs_url=swagger_docs, redoc_url=redoc_docs, openapi_url=open_api)

class PostModel(BaseModel):
    url: str               # Required
    key: str | None = None # Option

class DeleteModel(BaseModel):
    short_key: str         # Required
    delete_key: str        # Required

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

database_connect = (DATABASE)
conn = sqlite3.connect(database_connect, isolation_level=None)
cursor = conn.cursor()

sql = """CREATE TABLE IF NOT EXISTS URLShorten(ID TEXT, URL TEXT, DELETE_KEY TEXT)"""
cursor.execute(sql)
conn.commit()

def db_contact(SQL, DATA, IS_OPERATION):
    if IS_OPERATION:
        cursor.execute(SQL, DATA)
        conn.commit()
    else:
        row = cursor.execute(SQL, (DATA,))
        result = row.fetchall()
        if any(result):
            return True, result[0]
        else:
            return False, None

def random_url(url_data):
    key = "".join(random.choices(string.ascii_letters+string.digits, k=7))
    short_url = HOST_URL + "/" + key
    redirect_check = short_url == url_data
    sql = """SELECT * FROM URLShorten WHERE ID = ?"""
    db_result = db_contact(sql, key, False)[0]
    while db_result or redirect_check:
        key = "".join(random.choices(string.ascii_letters+string.digits, k=7))
        db_result = db_contact(sql, key, False)[0]
        short_url = HOST_URL + "/" + key
        redirect_check = short_url == url_data
    return key, short_url

@app.post("/shorten/", status_code=201)
async def shorten(LongURL: PostModel, response: Response):
    url_data = LongURL.url
    url_key = LongURL.key
    url_pattern = "https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
    if not re.match(url_pattern, url_data):
        response.status_code = 400
        return {"status": 400, "error": True, "data": "Invalid URL encoding."}
    url_data = urllib.parse.quote(url_data, safe=":/?=&#")
    sql = """SELECT * FROM URLShorten WHERE URL = ?"""
    db_result, db_data = db_contact(sql, url_data, False)
    if db_result:
        short_key = db_data[0]
        short_url = HOST_URL + "/" + short_key
        del_key = db_data[2]
    else:
        if url_key is None:
            short_key, short_url = random_url(url_data)
        else:
            url_key = url_key.replace(" ", "")
            check_length = len(url_key)
            reject_symbols = '[!"#$%&\'\\\\()*+,-./:;<=>?@[\\]^_`{|}~「」〔〕“”〈〉『』【】＆＊・（）＄＃＠。、？！｀＋￥％]'
            if check_length < 3:
                response.status_code = 400
                return {"status": 400, "error": True, "data": "Custom URL key must be at least 3 characters long."}
            elif check_length > 10:
                response.status_code = 400
                return {"status": 400, "error": True, "data": "Custom URL key must be 10 characters or less in length."}
            if re.compile(reject_symbols).search(url_key):
                response.status_code = 400
                return {"status": 400, "error": True, "data": "Symbols cannot be used in custom URL key."}
            call_sql = """SELECT * FROM URLShorten WHERE ID = ?"""
            db_result = db_contact(call_sql, url_key, False)[0]
            if db_result:
                response.status_code = 400
                return {"status": 400, "error": True, "data": "This URL key already exists and cannot be used."}
            short_url = HOST_URL + "/" + url_key
            if url_data == short_url:
                response.status_code = 400
                return {"status": 400, "error": True, "data": "A combination was detected that could result in a redirect loop."}
            short_key = url_key
        del_key = "".join(random.choices(string.ascii_letters+string.digits, k=10))
        save_sql = """INSERT INTO URLShorten VALUES(?, ?, ?)"""
        data = ((short_key, url_data, del_key))
        db_contact(save_sql, data, True)
    result_data = {"short_url": short_url , "keys": {"short_key": short_key, "delete_key": del_key}}
    return {"status": 201, "error": False, "data": result_data}

@app.delete("/delete/", status_code=200)
async def delete(DeleteKey: DeleteModel, response: Response):
    shorten_key = DeleteKey.short_key
    delete_key = DeleteKey.delete_key
    sql = """SELECT * FROM URLShorten WHERE ID = ?"""
    db_result, db_data = db_contact(sql, shorten_key, False)
    if db_result:
        if db_data[2] == delete_key:
            will_del = (db_data[0],)
            del_sql = """DELETE FROM URLShorten WHERE ID = ?"""
            db_contact(del_sql, will_del, True)
        else:
            response.status_code = 400
            return {"status": 400, "error": True, "message": "Wrong delete key."}
    else:
        response.status_code = 404
        return {"status": 404, "error": True, "message": "The key you requested was not found."}
    return {"status": 200, "error": False, "message": "Success"}

@app.get("/{key}", status_code=302)
async def redirect(key: str):
    sql = """SELECT * FROM URLShorten WHERE ID = ?"""
    db_result, db_data = db_contact(sql, key, False)
    if db_result:
        long_url = db_data[1]
        return RedirectResponse(long_url)
    else:
        return RedirectResponse(HOST_URL)

if __name__ == "__main__":
    uvicorn.run(app, host=APP_HOST, port=APP_PORT)
