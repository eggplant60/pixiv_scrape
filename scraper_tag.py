# coding: utf-8

from pixivpy3 import *
import json
from time import sleep
import os
import sys
from password import *
import glob


# ログイン処理
def loginPixiv():
    api = PixivAPI()
    api.login(USERNAME, PASSWORD)
    return api



if __name__ == '__main__':

    api = loginPixiv()

    START_PAGE = 1
    MAX_PAGE = 300
    PER_PAGE = 100

    # 閲覧数のしきい値
    VIEWS_CNT = 200

    # 絵師のスコアのしきい値
    ARTIST_SCR = 2000

    # 画像の保存先を定義しています.
    saving_direcory_path = './images_{}'.format(sys.argv[1])
    if not os.path.exists(saving_direcory_path):
        os.mkdir(saving_direcory_path)

    aapi = AppPixivAPI()


    separator = '------------------------------------------------------------'
    dl_cnt = 0
    for page in range(START_PAGE, MAX_PAGE+1):

        json_result = api.search_works(sys.argv[1], page=page, per_page=PER_PAGE,
                                       mode='exact_tag', types=['illustration'])
        sleep(1)

        try:
            N = len(json_result.response)
            print(N)
        except:
            print('no result')
            continue
            
        for i in range(1,N+1):
            
            info = json_result.response[i-1]
            

            if info.stats.views_count < VIEWS_CNT:
                continue
            if info.stats.score < ARTIST_SCR:
                continue

            print(separator)
            print('{}/{}'.format((page-1)*PER_PAGE+i, MAX_PAGE*PER_PAGE))
            print('    {} origin url: {}'.format(info.title, info.image_urls['large']))
            print('    Artist: {}, Score: {}'.format(info.user.name, info.stats.score))

            # すでにダウンロード済みの場合はスキップ
            
            w_card = '????_????_' + str(info.id) + '_p0.*'
            if glob.glob(os.path.join(saving_direcory_path, w_card)):
                #print(w_card)
                continue

            try:
                prefix = str(page).zfill(4)+'_'+str(i).zfill(4)+'_'
                aapi.download(info.image_urls.large,
                              prefix=prefix,
                              path=saving_direcory_path)
                dl_cnt += 1
                sleep(1)

            except:
                print("Re-Login")
                sleep(100)
                api = loginPixiv()
                continue
    
    print("\nCollected {} images.".format(dl_cnt))           
    print("That\'s all.")
