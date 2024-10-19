from gevent import monkey
monkey.patch_all()
import musicapi
from flask import Flask, jsonify, request, redirect, make_response
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
from gevent.pool import Pool

application = Flask(__name__, static_folder='templates/static')
application.json.ensure_ascii = False
CORS(application, resources=r'/*')

def __set_no_cache(res):
    response = make_response(redirect(res, code=301))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = "0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Content-Type"] = "application/x-www-form-urlencoded; charset=utf-8"
    return response

@application.route(rule="/wyy/<song_id>", methods=["GET", "POST"])
def wyy_url(song_id):
    MusicApi = musicapi.MusicApi_wyy('')
    print(song_id)
    ret = MusicApi.get_wyy_url(song_id)
    return __set_no_cache(ret)


@application.route(rule="/wyy/lrc/<song_id>.lrc", methods=["GET", "POST"])
def wyy_lrc(song_id):
    MusicApi = musicapi.MusicApi_wyy('')
    ret = MusicApi.get_wyy_lrc(song_id)
    return ret


if __name__ == "__main__":
    print("MusicApi start run")
    http_server = WSGIServer(('0.0.0.0', 5050), application, spawn=Pool(50))
    http_server.serve_forever()
