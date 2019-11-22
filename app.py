# ローカルHTMLサーバのポート解放。自動起動


################# モジュール準備 ##################
import os
import pprint
import json
import sqlite3
import flask
import random, string
from PIL import Image
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
#for basic
from time import sleep
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()
from werkzeug import secure_filename
app = Flask(__name__)

from aliyunsdkcore.client import AcsClient
import base64
import aliyunsdkimagesearch.request.v20190325.AddImageRequest as AddImageRequest
import aliyunsdkimagesearch.request.v20190325.DeleteImageRequest as DeleteImageRequest
import aliyunsdkimagesearch.request.v20190325.SearchImageRequest as SearchImageRequest

####### bootstrapのモジュール追加 #######
from flask_bootstrap import Bootstrap

####### bootstrapを起動 ########
bootstrap = Bootstrap(app)

########### Basic ##########
users = {
    "a": "a"
}

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None

########## Access　Data　Setting　###########
client = AcsClient(
   "AccessKey ID",
   "AccessKey PASS",
   "ap-northeast-1"
#from System reply:endpoint  imagesearch.ap-northeast-1.aliyuncs.com

)
###########################################



UPLOAD_FOLDER = '/root/bootstrap/static'

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.urandom(24)


############  HTMLトップ画面表示 ##########
@app.route('/')
# for basic
@auth.login_required
def index():
      return render_template('bootstrap.html')

##########################################

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


##########################################

def GetRandomStr(num):
    # 英数字をすべて取得
    dat = string.digits + string.ascii_lowercase + string.ascii_uppercase

    # 英数字からランダムに取得
    return ''.join([random.choice(dat) for i in range(num)])


################ Main ###################

@app.route('/',  methods=['GET', 'POST'])
def search():
            img_file = request.files['img_file']
            filename = secure_filename(img_file.filename)
            hisyatai = GetRandomStr(10) +".jpg" 
            img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], hisyatai))
           
            select = flask.request.form.get('categoly')
            print(filename)            
            print(select)
            img_url = UPLOAD_FOLDER + '/' + hisyatai


            #画像のサイズ調整　IphoneからだとTimeoutしてしまう。写真の画素数が大きいので容量が大きく転送に時間がかかってしまうためリサイズする
            img = Image.open(img_url)
            width,height=640,480
            img = img.resize((width,height))
            img.save(os.path.join(app.config['UPLOAD_FOLDER'],'img_resize.jpg'))

            img_urlX = UPLOAD_FOLDER + '/' + 'img_resize.jpg'
      

            requester = SearchImageRequest.SearchImageRequest()
            #requests = SearchImageRequest.SearchItemRequest()
            requester.set_endpoint("imagesearch.cn-hongkong.aliyuncs.com")

            requester.set_InstanceName("imagesearch00hk")

            ## Search setting 
            requester.set_CategoryId(select)
            #requester.set_CategoryId("88888888")
            requester.set_Num("3")

            img_url0='static' + '/' + 'img_resize.jpg'
            print('static' + '/' + hisyatai)


            with open(img_urlX, 'rb') as imgfile:
             #ファイル読み込み
             img = imgfile.read()
            #エンコード
             encoded_pic_content = base64.b64encode(img)
             requester.set_PicContent(encoded_pic_content)
            #インスタンスへのアクション＝ImageSearchインスタンスへ
            #辞書型で返ってくる。
            response = client.do_action_with_exception(requester)
                       
            pprint.pprint(response)
            #sleep(2)            
            str_data = json.loads(response)
            #上記を入れないと型エラーが発生　TypeError: byte indices must be integers or slices, not str
            #print(str_data["Auctions"][0]["PicName"])
            #辞書型配列のため、上記のように選択する必要があった
            
            print(filename)

            return render_template('bootstrap.html', img_url0='static' + '/' + hisyatai ,img_url1="https://image-demo-oss-hk.oss-cn-hongkong.aliyuncs.com/demo/" + str_data["Auctions"][0]["PicName"], img_url2="https://image-demo-oss-hk.oss-cn-hongkong.aliyuncs.com/demo/" + str_data["Auctions"][1]["PicName"], img_url3="https://image-demo-oss-hk.oss-cn-hongkong.aliyuncs.com/demo/" + str_data["Auctions"][2]["PicName"],result=response)

                    

#########　Setting ##########
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8008)
     #FLASKのサーバ公開フォーマット　ローカルホストの適当なポートでWEBサーバ起動。debugをオンに設定
#

