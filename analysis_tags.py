# coding: utf-8

from pymongo import MongoClient
from pprint import pprint
import pandas as pd
import numpy as np
from akapriori import apriori

client = MongoClient('localhost', 27017)
collection = client.scraping.pixiv # 作品データベース

# ! データベース消去
#collection.drop()


# 年齢制限
print('件数: {}'.format(collection.count()))
print('そのうち r18 の件数: {}'\
      .format(collection.find({'age_limit': 'r18'}).count()))
print('そのうち r18-g の件数: {}'\
      .format(collection.find({'age_limit': 'r18-g'}).count()))
#print(collection.distinct('age_limit'))
print('')


# タグ分析
max_len = 10 # 1作品ごと最大タグ数
tags_projection = {'_id': False, 'id': True, 'tags': True}
jsons = list(collection.find(projection=tags_projection)) # DBから読み込み

tags_with_nan = {} # pandas に取り込むために、タグの数をnanで埋める
asc_list = []      # アソシエーション分析用
tags_len_list = []
for json in jsons:
    tags = json['tags']
    tags_len = len(tags)
    tags_len_list.append(tags_len)
    tags_with_nan[json['id']] = tags[:10] if tags_len >= max_len \
                                else tags + [np.nan] * (max_len - tags_len)
    asc_list.append(tags)

tags_column = list(range(max_len)) # 最大 max_len 個のタグ
df_tags = pd.DataFrame(tags_with_nan, index=tags_column).T
df_tags['id'] = df_tags.index

#pprint(df_tags)

df_melt = pd.melt(df_tags,
                  id_vars='id', 
                  value_vars=tags_column, value_name='tag')
df_melt.dropna(inplace=True)
del df_melt['variable']

#pprint(df_melt)

# 登場頻度の高い順にタグを表示
ignore_re = '.*[0-9]*users入り'
len_ranking = 1000

tags_dup = df_melt['tag']
tags_dropdup = tags_dup[~tags_dup.str.contains(ignore_re)] # 除外

ranking_tags = tags_dropdup.value_counts()

print('登場回数')
print(ranking_tags.iloc[:len_ranking])
print('種類: {}'.format(len(ranking_tags)))
print('')

"""
# アソシエーション分析
#rules = apriori(asc_list, confidence=0.3)
rules = apriori(asc_list, support=0.0005, confidence=0.8, lift=10)
rules_sorted = sorted(rules, key=lambda x: (x[3]), reverse=True)

print('{}, \t\t {}, \t\t {}'.format('confidence', 'word A', 'word B'))
#print('-' * 80)
for r in rules_sorted:
    A = list(r[0])[0]
    B = list(r[1])[0]
    if (A in B) or (B in A):
        continue
    if ('users入り' in A) or ('users入り' in B):
        continue
    
    print('{:.6}, \t\t {}, \t\t {}'.format(r[3], A, B))
 
"""
