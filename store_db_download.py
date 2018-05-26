# coding: utf-8

from pixivpy3 import *

from pymongo import MongoClient
from password import *

import json
import argparse
from time import sleep
import os
from pprint import pprint

from PIL import Image


# ログイン処理
def loginPixiv():
    api = PixivAPI()
    api.login(USERNAME, PASSWORD)
    return api



def main():
    parser = argparse.ArgumentParser(description='Download pictures and store their infomation.')
    parser.add_argument('--startid', '-s', type=int, default=12)  # 11: ピクシブ事務局
    parser.add_argument('--endid', '-e', type=int, default=100000)    # 73286: しぶぞー
    parser.add_argument('--min_score', '-m', type=int, default=10000,
                        help='minimum scores of pictures')  # 絵のしきい値
    parser.add_argument('--per_page', '-p', type=int, default=300,
                        help='download size per page')      # 一人の絵師さんから持ってくる最大数
    parser.add_argument('--out', '-o', type=str,
                        default='/raid/work/image/pixiv_scrape/artists_images_score10000',
                        help='dicectory of download files') # 画像の保存場所
    
    args = parser.parse_args()
    startid = args.startid
    endid   = args.endid
    min_score = args.min_score
    per_page  = args.per_page
    out = args.out

    api = loginPixiv()
    aapi = AppPixivAPI()

    client = MongoClient('localhost', 27017)
    collection = client.scraping.pixiv
    collection.create_index('id', unique=True)
    
    #collection.delete_one({'id': 8070375})
    #exit()
    
    # ダウンロードディレクトリ
    if not os.path.exists(out):
        os.mkdir(out)

    cnt_no_id = 0 # 連続して取得を失敗した回数
    
    # アーティスト検索から情報取得
    for artist_pixiv_id in range(startid, endid):
        
        try:
            # 絵師ごとに作品情報を取得
            json_result = api.users_works(artist_pixiv_id, per_page=per_page)
            sleep(1)
            
            artist_info = json_result.response[0].user # 先頭の作品からユーザー情報を取得
            total_works = json_result.pagination.total

            # 情報を表示
            print('-' * 80)
            print('Artist: %s' % artist_info.name)
            print('Works: %d' % total_works)
            print('')

            # 作品ごとのループ
            for work_no in range(0, total_works):
                illust = json_result.response[work_no]
                
                # スコアがしきい値以下は何もしない
                if illust.stats.score < min_score:
                    continue

                # イラストのみ対象
                if illust['type'] != 'illustration':
                    continue

                # 縦に長いイラストは4コマの可能性が高いので外す
                if float(illust['height']) / illust['width'] > 2.0:
                    continue

                # ダウンロードディレクトリの下に絵師ごとのディレクトリを作る
                tmp_str = str(artist_pixiv_id).zfill(6) + '_' + illust.user.name
                saving_directory_path = os.path.join(out, tmp_str)
                if not os.path.exists(saving_directory_path):
                    os.mkdir(saving_directory_path)

                # DB に作品情報を格納
                entry = collection.find_one({'id': illust['id']}) # MongoDB から key に該当するデータを検索
                if not entry:
                    illust['local_path'] = os.path.join(saving_directory_path, file_name)
                    collection.insert_one(illust)
                else:
                    continue

                # ダウンロード
                print('Procedure: %d/%d, Title: %s' \
                      % (work_no + 1, total_works, illust.title))
                file_name = str(work_no).zfill(3) + '_' + \
                            os.path.basename(illust.image_urls.large)
                aapi.download(illust.image_urls.large,
                              name=file_name,
                              path=saving_directory_path)
                
                # # 画像を読み込めなかったらDBから消去
                # try:
                #     Image.open(illust['local_path'])
                # except:
                #     collection.delete_one({'id': illust['id']})
                #     print('Read Error: Ignore this entry {}'.format(illust['id']))                    
                sleep(1)

            cnt_no_id = 0
            print('\nComplete for this artist.')
                
        except:
            cnt_no_id += 1
            print('-' * 80)
            print("Error: ID = %d, CNT = %d" % (artist_pixiv_id, cnt_no_id))
            # 100回連続で失敗した場合
            if cnt_no_id > 100:
                sleep(120)    # 120 sec 待ってリトライ
                api = loginPixiv()
                aapi = AppPixivAPI()
                cnt_no_id = 0  # リセット

                
if __name__ == '__main__':
    main()
