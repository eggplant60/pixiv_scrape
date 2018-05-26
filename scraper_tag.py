# coding: utf-8

from pixivpy3 import *
import json
from time import sleep
import os
import sys
from password import *


# ログイン処理
def loginPixiv():
    api = PixivAPI()
    api.login(USERNAME, PASSWORD)
    return api



if __name__ == '__main__':

    api = loginPixiv()

    MAX_PAGE = 100
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
    for page in range(1,MAX_PAGE):
        json_result = api.search_works(sys.argv[1], page=page, per_page=PER_PAGE,
                                       mode='exact_tag', types=['illustration'])
        try:
            for i in range(PER_PAGE):
                #print(separator)
                info = json_result.response[i]
            
                if info.stats.views_count < VIEWS_CNT:
                    continue
                if info.stats.score < ARTIST_SCR:
                    continue
            
                print(separator)
                print('{}/{}'.format((page-1)*PER_PAGE+i, MAX_PAGE*PER_PAGE-1))
                print('    {} origin url: {}'.format(info.title, info.image_urls['large']))
                print('    Artist: {}, Score: {}'.format(info.user.name, info.stats.score))
            
                # download
                aapi.download(info.image_urls.large,
                              prefix=str(page).zfill(4)+'_'+str(i).zfill(4)+'_',
                              path=saving_direcory_path)
                dl_cnt += 1
                sleep(1)

        except:
            print("Re-Login")
            sleep(120)
            api = loginPixiv()
            continue
    
    print("\nCollected {} images.".format(dl_cnt))           
    print("That\'s all.")
