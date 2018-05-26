# coding: utf-8

from pixivpy3 import *
import json
from time import sleep
import os
from password import *


# ログイン処理
def loginPixiv():
    api = PixivAPI()
    api.login(USERNAME, PASSWORD)
    return api


api = loginPixiv()

# ここでIDを指定します.
STARTID = 200000 # 11: ピクシブ事務局
ENDID = 300000
SCORE = 5000

cnt_no_id = 0


for ID in range(STARTID, ENDID):
    # アーティスト検索から情報取得
    try:
        artist_pixiv_id = ID

        # ここのper_pageの値を変えることで一人の絵師さんから持ってくる最大数を定義できます.
        json_result = api.users_works(artist_pixiv_id, per_page=300)
        info = json_result.response[0]
        score = info.stats.score
    
        # 僕はscoreが500以上の人を収集対象にしました.
        # よりクオリティの高い画像のみを集めたい場合はこの閾値を変更してください.
        if score < SCORE:
            cnt_no_id = 0
            continue
    
        total_works = json_result.pagination.total
        illust = json_result.response[0]
    
        
        aapi = AppPixivAPI()
        separator = '------------------------------------------------------------'


        # 画像の保存先を定義しています.
        # 特に指定先に希望がない場合はこのままでokです.
        # このまま走らせると, このスクリプトがあるディレクトリの直下に
        # "pixiv_images"フォルダが作成され画像が DLされます.
        if not os.path.exists("./artists_images"):
            os.mkdir("./artists_images")
        saving_direcory_path = './artists_images'

        
        # ダウンロード
        print(separator)
        print('Artist: %s' % illust.user.name)
        print('Works: %d' % total_works)
        print('Score: %d' % score)
        print('')

        # 絵師さんごとにディレクトリを分けたい場合は以下の２行を
        # アンコメントアウトしてください.
        # 一つのディレクトリにまとめたい場合はそのままでokです.

        tmp_str = str(ID).zfill(6) + '_' \
                  + str(score).zfill(6) + '_' \
                  + illust.user.name
        saving_direcory_path = os.path.join(saving_direcory_path, tmp_str)
        if not os.path.exists(saving_direcory_path):
            os.mkdir(saving_direcory_path)
        else:
            cnt_no_id = 0
            continue

        for work_no in range(0, total_works):
            illust = json_result.response[work_no]
            print('Procedure: %d/%d:%d, Title: %s' \
                  % (work_no + 1, total_works, ID, illust.title))
            #print(separator)
            
            aapi.download(illust.image_urls.large, \
                          prefix=str(work_no).zfill(3)+'_', \
                          path=saving_direcory_path)
            sleep(1)

        cnt_no_id = 0
        print('\nThat\'s all.')
                
    except:
        cnt_no_id += 1
        print("Error: ID = %d, CNT = %d" % (ID, cnt_no_id))
        if cnt_no_id > 100:
            sleep(120)    # 2分待ってリトライ
            api = loginPixiv()
            cnt_no_id = 0
        continue
