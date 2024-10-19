import http.cookies
import json
import base64
import execjs
import codecs
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

class MusicApi_wyy_sign:
    def __init__(self, param):
        self.param = param

    def to_16(self, key):
        while len(key) % 16 != 0:
            key += '\0'
        return str.encode(key)

    @property
    def AES_encrypt(self):
        key = '0CoJUm6Qyw8W8jud'
        iv = "0102030405060708"
        bs = AES.block_size
        pad2 = lambda s: s + (bs - len(s) % bs) * chr(bs - len(s) % bs)
        encryptor = AES.new(self.to_16(key), AES.MODE_CBC, self.to_16(iv))
        pd2 = pad(str.encode(pad2(self.param)), 16)
        encrypt_aes = encryptor.encrypt(pd2)
        encrypt_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')
        return encrypt_text

    @property
    def RSA_encrypt(self):
        get_i = execjs.compile(r"""
            function a(a) {
                var d, e, b = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", c = "";
                for (d = 0; a > d; d += 1)
                    e = Math.random() * b.length,
                    e = Math.floor(e),
                    c += b.charAt(e);
                return c
            }
        """)
        i = get_i.call('a', 16)
        i = i[::-1]
        c = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
        rs = int(codecs.encode(i.encode('utf-8'), 'hex_codec'), 16) ** int("010001", 16) % int(c, 16)
        return format(rs, 'x').zfill(256)

class MusicApi:
    def __init__(self, song_id, HOST=None):
        """初始化"""
        self.HOST = HOST if HOST else "http://127.0.0.1:5050"
        self.cookie = None
        self.mid = "734618958373461895837346189583"
        self.userid = "7917695051"
        self.song_id = song_id
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        }

    def MusicApi_set_cookie(self, cookie):
        self.cookie = cookie
        self.headers["Cookie"] = self.cookie

    @property
    def cookie_to_dict(self):
        cookie_dict = {}
        if self.cookie:
            cookies = http.cookies.SimpleCookie()
            cookies.load(self.cookie)
            for key, morsel in cookies.items():
                cookie_dict[key] = morsel.value
        return cookie_dict
 
class MusicApi_wyy(MusicApi):
    def __init__(self, song_id):
        super(MusicApi_wyy, self).__init__(song_id)
        self.csrf_token = self.cookie_to_dict.get("csrf_token", "")

    def get_wyy_url(self, music_id):
        """
        获取网易云音乐源地址
        :param music_id: 音乐id
        :return:
        """
        url = "https://music.163.com/weapi/song/enhance/player/url/v1?csrf_token=" + self.csrf_token
        encText = json.dumps(
            {
                "ids": "[" + str(music_id) + "]",
                "encodeType": "aac",
                "csrf_token": self.csrf_token,
                "level": "standard",
            }, separators=(",", ":")
        )
        params = MusicApi_wyy_sign(encText).AES_encrypt
        params = MusicApi_wyy_sign(params).AES_encrypt
        data = {
            "params": params,
            "encSecKey": MusicApi_wyy_sign(encText).RSA_encrypt
        }
        headers = {
            "User-Agent": self.headers['User-Agent'],
            "Referer": 'https://music.163.com/',
            "Content-Type": 'application/x-www-form-urlencoded',
            "Cookie": self.cookie
        }
        try:
            ret = requests.post(url, headers=headers, data=data).json()
            download_url = ret['data'][0]['url']
        except Exception as e:
            download_url = self.__get_wyy_url(music_id)
        return download_url
    
    def __get_wyy_url(self, music_id):
        """
        获取网易音乐源地址2
        :param music_id: 音乐id
        :return:
        """
        url = f'https://music.163.com/api/song/enhance/player/url?id={music_id}&ids=%5B{music_id}%5D&br=3200000'
        self.headers["Cookie"] = self.cookie
        ret = requests.get(url, headers=self.headers).json()
        download_url = ret['data'][0]['url']
        msg = download_url if download_url else {'msg': '出现了错误，错误位置：获取音乐源'}
        return msg

    def get_wyy_lrc(self, music_id):
        """
        获取歌词
        :param music_id: 音乐id
        :return:
        """
        url = f'https://music.163.com/api/song/lyric?id={music_id}&lv=1&kv=1&tv=-1'
        ret = requests.get(url).json()
        lrc = ret['lrc']['lyric']
        if lrc == '':
            lrc = ret['klyric']['lyric']
        return lrc