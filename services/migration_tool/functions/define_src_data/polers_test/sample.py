import polars as pl
from pydantic import create_model, ValidationError
from contextlib import contextmanager
from datetime import datetime
import time

DEBUG = True

# df_dup.is_duplicated()
# df_dup.is_unique()
# df.get_column("Integer").is_in([2, 4, 6])

def hanlder(e={}):

  # 移行定義情報をロード
  final_cols, final_key_cols, default_values, datas = read_definition()

  # 元データを初期化
  datas = initialize_dfs(datas, final_key_cols)
  # print(f'datas: {datas}')

  # 元データをチェック
  errors = check_dfs(datas)
  # print(f'errors: {errors}')

  # 元データを順にマージ
  merged_df = merge_dfs(datas, final_key_cols, final_cols)

  # デフォルト値の設定
  result_df = set_default_values(merged_df, default_values)
  print(f'result df: {result_df}')

def read_definition():
  xlsx = pl.read_excel('sample.xlsx', has_header=False)

  ret = pl.DataFrame()
  for col in xlsx:
    ret_col = pl.Series()
    for data in col:
      x = data
      print(x)
      # ret_col.
    # ret.with_columns(ret_col)

  print(xlsx)
  print(ret)

  final_cols = [
    'HOGE', 'ID_1', 'ID_2', 'other', 'name', 'age', 'birth', 'lucky_color',
    "col1", "col2", "col3", "col4", "col5", "col6", "col7", "col8", "col9", "col10",
    "col11","col12","col13","col14","col15","col16",
    'col17','col18','col19','col20','col21','col22','col23','col24','col25',
    # 'col26','col27','col28','col29','col30',
    # 'col31','col32','col33','col34','col35','col36','col37','col38','col39','col40','col41','col42','col43','col44',
    # 'col45','col46','col47','col48','col49','col50','col51','col52','col53','col54','col55','col56','col57','col58',
    # 'col59','col60','col61','col62','col63','col64','col65','col66','col67','col68','col69','col70','col71','col72',
    # 'col73','col74','col75','col76','col77','col78','col79','col80','col81','col82','col83','col84','col85','col86',
    # 'col87','col88','col89','col90','col91','col92','col93','col94','col95','col96','col97','col98','col99','col100',
    # 'col101','col102','col103','col104','col105','col106','col107','col108','col109','col110','col111','col112','col113',
    # 'col114','col115','col116','col117','col118','col119','col120','col121','col122','col123','col124','col125','col126',
    # 'col127','col128','col129','col130','col131','col132','col133','col134','col135','col136','col137','col138','col139',
    # 'col140','col141','col142','col143','col144','col145','col146','col147','col148','col149','col150','col151','col152',
    # 'col153','col154','col155','col156','col157','col158','col159','col160','col161','col162','col163','col164','col165',
    # 'col166','col167','col168','col169','col170','col171','col172','col173','col174','col175','col176','col177','col178',
    # 'col179','col180','col181','col182','col183','col184','col185','col186','col187','col188','col189','col190','col191',
    # 'col192','col193','col194','col195','col196',
  ]
  final_key_cols = ['ID_1', 'ID_2']
  default_values = {
    'other': 'No other information.',
    'name': 'No name',
    'age': 99,
    'birth': '1990/1/1',
  }
  moto1_name = 'moto1'
  moto1_def = [
    { "name": "ID1", "type": "int", "key_order": 0 },
    { "name": "ID2", "type": "int", "key_order": 1 },
    { "name": "name", "type": "str" },
    { "name": "age", "type": "int" },
    { "name": "birth", "type": "datetime" },
    { "name": "col1", "type": "str" },
    { "name": "col2", "type": "str" },
    { "name": "col3", "type": "str" },
    { "name": "col4", "type": "str" },
    { "name": "col5", "type": "str" },
    { "name": "col6", "type": "str" },
    { "name": "col7", "type": "str" },
    { "name": "col8", "type": "str" },
    { "name": "col9", "type": "str" },
    { "name": "col10", "type": "str" },
    { "name": "col11", "type": "str" },
    { "name": "col12", "type": "str" },
    { "name": "col13", "type": "str" },
    { "name": "col14", "type": "str" },
    { "name": "col15", "type": "str" },
    { "name": "col16", "type": "str" },
    { 'name': 'col17', 'type': 'str' },
    { 'name': 'col18', 'type': 'str' },
    { 'name': 'col19', 'type': 'str' },
    { 'name': 'col20', 'type': 'str' },
    { 'name': 'col21', 'type': 'str' },
    { 'name': 'col22', 'type': 'str' },
    { 'name': 'col23', 'type': 'str' },
    { 'name': 'col24', 'type': 'str' },
    { 'name': 'col25', 'type': 'str' },
    # { 'name': 'col26', 'type': 'str' },
    # { 'name': 'col27', 'type': 'str' },
    # { 'name': 'col28', 'type': 'str' },
    # { 'name': 'col29', 'type': 'str' },
    # { 'name': 'col30', 'type': 'str' },
    # { 'name': 'col31', 'type': 'str' },
    # { 'name': 'col32', 'type': 'str' },
    # { 'name': 'col33', 'type': 'str' },
    # { 'name': 'col34', 'type': 'str' },
    # { 'name': 'col35', 'type': 'str' },
    # { 'name': 'col36', 'type': 'str' },
    # { 'name': 'col37', 'type': 'str' },
    # { 'name': 'col38', 'type': 'str' },
    # { 'name': 'col39', 'type': 'str' },
    # { 'name': 'col40', 'type': 'str' },
    # { 'name': 'col41', 'type': 'str' },
    # { 'name': 'col42', 'type': 'str' },
    # { 'name': 'col43', 'type': 'str' },
    # { 'name': 'col44', 'type': 'str' },
    # { 'name': 'col45', 'type': 'str' },
    # { 'name': 'col46', 'type': 'str' },
    # { 'name': 'col47', 'type': 'str' },
    # { 'name': 'col48', 'type': 'str' },
    # { 'name': 'col49', 'type': 'str' },
    # { 'name': 'col50', 'type': 'str' },
    # { 'name': 'col51', 'type': 'str' },
    # { 'name': 'col52', 'type': 'str' },
    # { 'name': 'col53', 'type': 'str' },
    # { 'name': 'col54', 'type': 'str' },
    # { 'name': 'col55', 'type': 'str' },
    # { 'name': 'col56', 'type': 'str' },
    # { 'name': 'col57', 'type': 'str' },
    # { 'name': 'col58', 'type': 'str' },
    # { 'name': 'col59', 'type': 'str' },
    # { 'name': 'col60', 'type': 'str' },
    # { 'name': 'col61', 'type': 'str' },
    # { 'name': 'col62', 'type': 'str' },
    # { 'name': 'col63', 'type': 'str' },
    # { 'name': 'col64', 'type': 'str' },
    # { 'name': 'col65', 'type': 'str' },
    # { 'name': 'col66', 'type': 'str' },
    # { 'name': 'col67', 'type': 'str' },
    # { 'name': 'col68', 'type': 'str' },
    # { 'name': 'col69', 'type': 'str' },
    # { 'name': 'col70', 'type': 'str' },
    # { 'name': 'col71', 'type': 'str' },
    # { 'name': 'col72', 'type': 'str' },
    # { 'name': 'col73', 'type': 'str' },
    # { 'name': 'col74', 'type': 'str' },
    # { 'name': 'col75', 'type': 'str' },
    # { 'name': 'col76', 'type': 'str' },
    # { 'name': 'col77', 'type': 'str' },
    # { 'name': 'col78', 'type': 'str' },
    # { 'name': 'col79', 'type': 'str' },
    # { 'name': 'col80', 'type': 'str' },
    # { 'name': 'col81', 'type': 'str' },
    # { 'name': 'col82', 'type': 'str' },
    # { 'name': 'col83', 'type': 'str' },
    # { 'name': 'col84', 'type': 'str' },
    # { 'name': 'col85', 'type': 'str' },
    # { 'name': 'col86', 'type': 'str' },
    # { 'name': 'col87', 'type': 'str' },
    # { 'name': 'col88', 'type': 'str' },
    # { 'name': 'col89', 'type': 'str' },
    # { 'name': 'col90', 'type': 'str' },
    # { 'name': 'col91', 'type': 'str' },
    # { 'name': 'col92', 'type': 'str' },
    # { 'name': 'col93', 'type': 'str' },
    # { 'name': 'col94', 'type': 'str' },
    # { 'name': 'col95', 'type': 'str' },
    # { 'name': 'col96', 'type': 'str' },
    # { 'name': 'col97', 'type': 'str' },
    # { 'name': 'col98', 'type': 'str' },
    # { 'name': 'col99', 'type': 'str' },
    # { 'name': 'col100', 'type': 'str' },
    # { 'name': 'col101', 'type': 'str' },
    # { 'name': 'col102', 'type': 'str' },
    # { 'name': 'col103', 'type': 'str' },
    # { 'name': 'col104', 'type': 'str' },
    # { 'name': 'col105', 'type': 'str' },
    # { 'name': 'col106', 'type': 'str' },
    # { 'name': 'col107', 'type': 'str' },
    # { 'name': 'col108', 'type': 'str' },
    # { 'name': 'col109', 'type': 'str' },
    # { 'name': 'col110', 'type': 'str' },
    # { 'name': 'col111', 'type': 'str' },
    # { 'name': 'col112', 'type': 'str' },
    # { 'name': 'col113', 'type': 'str' },
    # { 'name': 'col114', 'type': 'str' },
    # { 'name': 'col115', 'type': 'str' },
    # { 'name': 'col116', 'type': 'str' },
    # { 'name': 'col117', 'type': 'str' },
    # { 'name': 'col118', 'type': 'str' },
    # { 'name': 'col119', 'type': 'str' },
    # { 'name': 'col120', 'type': 'str' },
    # { 'name': 'col121', 'type': 'str' },
    # { 'name': 'col122', 'type': 'str' },
    # { 'name': 'col123', 'type': 'str' },
    # { 'name': 'col124', 'type': 'str' },
    # { 'name': 'col125', 'type': 'str' },
    # { 'name': 'col126', 'type': 'str' },
    # { 'name': 'col127', 'type': 'str' },
    # { 'name': 'col128', 'type': 'str' },
    # { 'name': 'col129', 'type': 'str' },
    # { 'name': 'col130', 'type': 'str' },
    # { 'name': 'col131', 'type': 'str' },
    # { 'name': 'col132', 'type': 'str' },
    # { 'name': 'col133', 'type': 'str' },
    # { 'name': 'col134', 'type': 'str' },
    # { 'name': 'col135', 'type': 'str' },
    # { 'name': 'col136', 'type': 'str' },
    # { 'name': 'col137', 'type': 'str' },
    # { 'name': 'col138', 'type': 'str' },
    # { 'name': 'col139', 'type': 'str' },
    # { 'name': 'col140', 'type': 'str' },
    # { 'name': 'col141', 'type': 'str' },
    # { 'name': 'col142', 'type': 'str' },
    # { 'name': 'col143', 'type': 'str' },
    # { 'name': 'col144', 'type': 'str' },
    # { 'name': 'col145', 'type': 'str' },
    # { 'name': 'col146', 'type': 'str' },
    # { 'name': 'col147', 'type': 'str' },
    # { 'name': 'col148', 'type': 'str' },
    # { 'name': 'col149', 'type': 'str' },
    # { 'name': 'col150', 'type': 'str' },
    # { 'name': 'col151', 'type': 'str' },
    # { 'name': 'col152', 'type': 'str' },
    # { 'name': 'col153', 'type': 'str' },
    # { 'name': 'col154', 'type': 'str' },
    # { 'name': 'col155', 'type': 'str' },
    # { 'name': 'col156', 'type': 'str' },
    # { 'name': 'col157', 'type': 'str' },
    # { 'name': 'col158', 'type': 'str' },
    # { 'name': 'col159', 'type': 'str' },
    # { 'name': 'col160', 'type': 'str' },
    # { 'name': 'col161', 'type': 'str' },
    # { 'name': 'col162', 'type': 'str' },
    # { 'name': 'col163', 'type': 'str' },
    # { 'name': 'col164', 'type': 'str' },
    # { 'name': 'col165', 'type': 'str' },
    # { 'name': 'col166', 'type': 'str' },
    # { 'name': 'col167', 'type': 'str' },
    # { 'name': 'col168', 'type': 'str' },
    # { 'name': 'col169', 'type': 'str' },
    # { 'name': 'col170', 'type': 'str' },
    # { 'name': 'col171', 'type': 'str' },
    # { 'name': 'col172', 'type': 'str' },
    # { 'name': 'col173', 'type': 'str' },
    # { 'name': 'col174', 'type': 'str' },
    # { 'name': 'col175', 'type': 'str' },
    # { 'name': 'col176', 'type': 'str' },
    # { 'name': 'col177', 'type': 'str' },
    # { 'name': 'col178', 'type': 'str' },
    # { 'name': 'col179', 'type': 'str' },
    # { 'name': 'col180', 'type': 'str' },
    # { 'name': 'col181', 'type': 'str' },
    # { 'name': 'col182', 'type': 'str' },
    # { 'name': 'col183', 'type': 'str' },
    # { 'name': 'col184', 'type': 'str' },
    # { 'name': 'col185', 'type': 'str' },
    # { 'name': 'col186', 'type': 'str' },
    # { 'name': 'col187', 'type': 'str' },
    # { 'name': 'col188', 'type': 'str' },
    # { 'name': 'col189', 'type': 'str' },
    # { 'name': 'col190', 'type': 'str' },
    # { 'name': 'col191', 'type': 'str' },
    # { 'name': 'col192', 'type': 'str' },
    # { 'name': 'col193', 'type': 'str' },
    # { 'name': 'col194', 'type': 'str' },
    # { 'name': 'col195', 'type': 'str' },
    # { 'name': 'col196', 'type': 'str' },
  ]
  moto1 = pl.DataFrame({
    'ID1': [1, 2, 3, 4],
    'ID2': [11, 22, 33, 44],
    'name': ['A', 'B', 'C', 'D'],
    'age': [10, 20, 30, None],
    'birth': ['1986/12/17', None, '2025/1/17', None],
  })
  moto2_name = 'moto2'
  moto2_def = [
    { "name": "ID__1", "type": "int", "key_order": 1 },
    { "name": "ID__2", "type": "int", "key_order": 0 },
    { "name": "name", "type": "str" },
    { "name": "lucky_color", "type": "str" },
    { "name": "col1", "type": "str" },
    { "name": "col2", "type": "str" },
    { "name": "col3", "type": "str" },
    { "name": "col4", "type": "str" },
    { "name": "col5", "type": "str" },
    { "name": "col6", "type": "str" },
    { "name": "col7", "type": "str" },
    { "name": "col8", "type": "str" },
    { "name": "col9", "type": "str" },
    { "name": "col10", "type": "str" },
    { "name": "col11", "type": "str" },
    { "name": "col12", "type": "str" },
    { "name": "col13", "type": "str" },
    { "name": "col14", "type": "str" },
    { "name": "col15", "type": "str" },
    { 'name': 'col16', 'type': 'str' },
    { 'name': 'col17', 'type': 'str' },
    { 'name': 'col18', 'type': 'str' },
    { 'name': 'col19', 'type': 'str' },
    { 'name': 'col20', 'type': 'str' },
    { 'name': 'col21', 'type': 'str' },
    { 'name': 'col22', 'type': 'str' },
    { 'name': 'col23', 'type': 'str' },
    { 'name': 'col24', 'type': 'str' },
    { 'name': 'col25', 'type': 'str' },
    # { 'name': 'col26', 'type': 'str' },
    # { 'name': 'col27', 'type': 'str' },
    # { 'name': 'col28', 'type': 'str' },
    # { 'name': 'col29', 'type': 'str' },
    # { 'name': 'col30', 'type': 'str' },
    # { 'name': 'col31', 'type': 'str' },
    # { 'name': 'col32', 'type': 'str' },
    # { 'name': 'col33', 'type': 'str' },
    # { 'name': 'col34', 'type': 'str' },
    # { 'name': 'col35', 'type': 'str' },
    # { 'name': 'col36', 'type': 'str' },
    # { 'name': 'col37', 'type': 'str' },
    # { 'name': 'col38', 'type': 'str' },
    # { 'name': 'col39', 'type': 'str' },
    # { 'name': 'col40', 'type': 'str' },
    # { 'name': 'col41', 'type': 'str' },
    # { 'name': 'col42', 'type': 'str' },
    # { 'name': 'col43', 'type': 'str' },
    # { 'name': 'col44', 'type': 'str' },
    # { 'name': 'col45', 'type': 'str' },
    # { 'name': 'col46', 'type': 'str' },
    # { 'name': 'col47', 'type': 'str' },
    # { 'name': 'col48', 'type': 'str' },
    # { 'name': 'col49', 'type': 'str' },
    # { 'name': 'col50', 'type': 'str' },
    # { 'name': 'col51', 'type': 'str' },
    # { 'name': 'col52', 'type': 'str' },
    # { 'name': 'col53', 'type': 'str' },
    # { 'name': 'col54', 'type': 'str' },
    # { 'name': 'col55', 'type': 'str' },
    # { 'name': 'col56', 'type': 'str' },
    # { 'name': 'col57', 'type': 'str' },
    # { 'name': 'col58', 'type': 'str' },
    # { 'name': 'col59', 'type': 'str' },
    # { 'name': 'col60', 'type': 'str' },
    # { 'name': 'col61', 'type': 'str' },
    # { 'name': 'col62', 'type': 'str' },
    # { 'name': 'col63', 'type': 'str' },
    # { 'name': 'col64', 'type': 'str' },
    # { 'name': 'col65', 'type': 'str' },
    # { 'name': 'col66', 'type': 'str' },
    # { 'name': 'col67', 'type': 'str' },
    # { 'name': 'col68', 'type': 'str' },
    # { 'name': 'col69', 'type': 'str' },
    # { 'name': 'col70', 'type': 'str' },
    # { 'name': 'col71', 'type': 'str' },
    # { 'name': 'col72', 'type': 'str' },
    # { 'name': 'col73', 'type': 'str' },
    # { 'name': 'col74', 'type': 'str' },
    # { 'name': 'col75', 'type': 'str' },
    # { 'name': 'col76', 'type': 'str' },
    # { 'name': 'col77', 'type': 'str' },
    # { 'name': 'col78', 'type': 'str' },
    # { 'name': 'col79', 'type': 'str' },
    # { 'name': 'col80', 'type': 'str' },
    # { 'name': 'col81', 'type': 'str' },
    # { 'name': 'col82', 'type': 'str' },
    # { 'name': 'col83', 'type': 'str' },
    # { 'name': 'col84', 'type': 'str' },
    # { 'name': 'col85', 'type': 'str' },
    # { 'name': 'col86', 'type': 'str' },
    # { 'name': 'col87', 'type': 'str' },
    # { 'name': 'col88', 'type': 'str' },
    # { 'name': 'col89', 'type': 'str' },
    # { 'name': 'col90', 'type': 'str' },
    # { 'name': 'col91', 'type': 'str' },
    # { 'name': 'col92', 'type': 'str' },
    # { 'name': 'col93', 'type': 'str' },
    # { 'name': 'col94', 'type': 'str' },
    # { 'name': 'col95', 'type': 'str' },
    # { 'name': 'col96', 'type': 'str' },
    # { 'name': 'col97', 'type': 'str' },
    # { 'name': 'col98', 'type': 'str' },
    # { 'name': 'col99', 'type': 'str' },
    # { 'name': 'col100', 'type': 'str' },
    # { 'name': 'col101', 'type': 'str' },
    # { 'name': 'col102', 'type': 'str' },
    # { 'name': 'col103', 'type': 'str' },
    # { 'name': 'col104', 'type': 'str' },
    # { 'name': 'col105', 'type': 'str' },
    # { 'name': 'col106', 'type': 'str' },
    # { 'name': 'col107', 'type': 'str' },
    # { 'name': 'col108', 'type': 'str' },
    # { 'name': 'col109', 'type': 'str' },
    # { 'name': 'col110', 'type': 'str' },
    # { 'name': 'col111', 'type': 'str' },
    # { 'name': 'col112', 'type': 'str' },
    # { 'name': 'col113', 'type': 'str' },
    # { 'name': 'col114', 'type': 'str' },
    # { 'name': 'col115', 'type': 'str' },
    # { 'name': 'col116', 'type': 'str' },
    # { 'name': 'col117', 'type': 'str' },
    # { 'name': 'col118', 'type': 'str' },
    # { 'name': 'col119', 'type': 'str' },
    # { 'name': 'col120', 'type': 'str' },
    # { 'name': 'col121', 'type': 'str' },
    # { 'name': 'col122', 'type': 'str' },
    # { 'name': 'col123', 'type': 'str' },
    # { 'name': 'col124', 'type': 'str' },
    # { 'name': 'col125', 'type': 'str' },
    # { 'name': 'col126', 'type': 'str' },
    # { 'name': 'col127', 'type': 'str' },
    # { 'name': 'col128', 'type': 'str' },
    # { 'name': 'col129', 'type': 'str' },
    # { 'name': 'col130', 'type': 'str' },
    # { 'name': 'col131', 'type': 'str' },
    # { 'name': 'col132', 'type': 'str' },
    # { 'name': 'col133', 'type': 'str' },
    # { 'name': 'col134', 'type': 'str' },
    # { 'name': 'col135', 'type': 'str' },
    # { 'name': 'col136', 'type': 'str' },
    # { 'name': 'col137', 'type': 'str' },
    # { 'name': 'col138', 'type': 'str' },
    # { 'name': 'col139', 'type': 'str' },
    # { 'name': 'col140', 'type': 'str' },
    # { 'name': 'col141', 'type': 'str' },
    # { 'name': 'col142', 'type': 'str' },
    # { 'name': 'col143', 'type': 'str' },
    # { 'name': 'col144', 'type': 'str' },
    # { 'name': 'col145', 'type': 'str' },
    # { 'name': 'col146', 'type': 'str' },
    # { 'name': 'col147', 'type': 'str' },
    # { 'name': 'col148', 'type': 'str' },
    # { 'name': 'col149', 'type': 'str' },
    # { 'name': 'col150', 'type': 'str' },
    # { 'name': 'col151', 'type': 'str' },
    # { 'name': 'col152', 'type': 'str' },
    # { 'name': 'col153', 'type': 'str' },
    # { 'name': 'col154', 'type': 'str' },
    # { 'name': 'col155', 'type': 'str' },
    # { 'name': 'col156', 'type': 'str' },
    # { 'name': 'col157', 'type': 'str' },
    # { 'name': 'col158', 'type': 'str' },
    # { 'name': 'col159', 'type': 'str' },
    # { 'name': 'col160', 'type': 'str' },
    # { 'name': 'col161', 'type': 'str' },
    # { 'name': 'col162', 'type': 'str' },
    # { 'name': 'col163', 'type': 'str' },
    # { 'name': 'col164', 'type': 'str' },
    # { 'name': 'col165', 'type': 'str' },
    # { 'name': 'col166', 'type': 'str' },
    # { 'name': 'col167', 'type': 'str' },
    # { 'name': 'col168', 'type': 'str' },
    # { 'name': 'col169', 'type': 'str' },
    # { 'name': 'col170', 'type': 'str' },
    # { 'name': 'col171', 'type': 'str' },
    # { 'name': 'col172', 'type': 'str' },
    # { 'name': 'col173', 'type': 'str' },
    # { 'name': 'col174', 'type': 'str' },
    # { 'name': 'col175', 'type': 'str' },
    # { 'name': 'col176', 'type': 'str' },
    # { 'name': 'col177', 'type': 'str' },
    # { 'name': 'col178', 'type': 'str' },
    # { 'name': 'col179', 'type': 'str' },
    # { 'name': 'col180', 'type': 'str' },
    # { 'name': 'col181', 'type': 'str' },
    # { 'name': 'col182', 'type': 'str' },
    # { 'name': 'col183', 'type': 'str' },
    # { 'name': 'col184', 'type': 'str' },
    # { 'name': 'col185', 'type': 'str' },
    # { 'name': 'col186', 'type': 'str' },
    # { 'name': 'col187', 'type': 'str' },
    # { 'name': 'col188', 'type': 'str' },
    # { 'name': 'col189', 'type': 'str' },
    # { 'name': 'col190', 'type': 'str' },
    # { 'name': 'col191', 'type': 'str' },
    # { 'name': 'col192', 'type': 'str' },
    # { 'name': 'col193', 'type': 'str' },
    # { 'name': 'col194', 'type': 'str' },
    # { 'name': 'col195', 'type': 'str' },
    # { 'name': 'col196', 'type': 'str' },
  ]
  moto2 = pl.DataFrame({
    'ID__2': [1, 3, 5, 2, 4],
    'ID__1': [11, 23, 55, 22, 44],
    'name': ['AAA', 'CCC', 'EEE', None, ''],
    'lucky_color': ['red', 'yellow', 'blue', None, None]
  })
  # 行の倍数
  repeat_row_count = 20000
  repeat_column_count = 25
  # moto1の列を増やす
  new_columns = [
     pl.col(col) for col in moto1.columns
  ] + [
     pl.lit(i).alias(f'col{i}') for i in range(repeat_column_count + 1)
  ]
  moto1 = moto1.select(new_columns)
  # moto1の行を増やす
  moto1 = pl.concat([moto1] * (repeat_row_count - 1))
  moto1 = moto1.with_columns(
     (pl.arange(1, moto1.shape[0] + 1)).alias('ID1'),
     (pl.arange(1, moto1.shape[0] + 1)).alias('ID2')
  )

  # moto2の列を増やす
  new_columns = [
     pl.col(col) for col in moto2.columns
  ] + [
     pl.lit(i).alias(f'col{i}') for i in range(repeat_column_count + 1)
  ]
  moto2 = moto2.select(new_columns)
  # moto2の行を増やす
  moto2 = pl.concat([moto2] * (repeat_row_count - 1))
  moto2 = moto2.with_columns(
     (pl.arange(1, moto2.shape[0] + 1)).alias('ID__1'),
     (pl.arange(1, moto2.shape[0] + 1)).alias('ID__2')
  )
  return (
    final_cols,
    final_key_cols,
    default_values,
    [{
       "data_name": moto1_name,
       "field_def": moto1_def,
       "data": moto1
    },{
       "data_name": moto2_name,
       "field_def": moto2_def,
       "data": moto2
    }],
  )

def initialize_dfs(datas, final_key_cols):
  
  # マージ用にキーの名前を統一する
  # dfごとにループ
  for idx, d in enumerate(datas):
    # 全データをstrにキャスト
    df = cast_to_str(d["data"])

    query = []
    new_field_def = []
    # カラムごとにループ
    for col in d["field_def"]:
      old_key = col["name"]
      # カラムがキー項目の場合、最終出力時のカラム名に訂正
      key_order = col.get('key_order')
      if key_order is not None:
        final_key_col = final_key_cols[key_order]
        col["name"] = final_key_col
        query.append(pl.col(old_key).alias(final_key_col))
      else:
        query.append(pl.col(old_key))

      new_field_def.append(col)
    
    # カラム名変更後のdfを返却値に追加
    print(f'query: {query}')
    datas[idx]["data"] = df.select(query)

  return datas

def cast_to_str(df):
  return df.with_columns(
    # すべてのカラムをutf8にキャスト
    [pl.col(col).cast(pl.Utf8).alias(col) for col in df.columns]
  )

def get_dfs_key(data):
  dfs_key = []
  field_def = data['field_def']
  debug_print(f'field_def: {field_def}')
  for field in field_def:
      key_order = field.get('key_order')
      if key_order:
        dfs_key[key_order] = field['name']
  
  return dfs_key

def check_dfs(datas):
  errors = []

  for d in datas:
    model = create_dynamic_model(d["data_name"], d["field_def"])
    errors = errors + check_data(d["data"], model)
  
  return errors

def create_dynamic_model(name, migration_definition):
    mname = f'{name}Model'  # XXX_MasterModel
    fields = {}

    for md in migration_definition:
        fields[md['name']] = (md['type'], ...)

    return create_model(
        mname,
        **fields
    )

def check_data(df, model):
  errors = []
  with time_log(f"{len(df)}件のチェック処理"):
      rows = df.to_dicts()
      for target in rows:
          try:
              record = model(**target)
              # debug_print(record.model_dump())

          except ValidationError as e:
              errors.append({
                 "data": target,
                 "error": e.errors()
              })

  return errors

def merge_dfs(datas, final_key_cols, final_cols):

  # 両方のキーをマージし、キーのみのdfを作成
  key_only_df = pl.concat([d["data"][final_key_cols] for d in datas]).unique().sort(by=final_key_cols)
  print(f'key: {key_only_df}')

  # 元データのdfを順番にマージ
  prev_df = key_only_df
  for d in datas:
    with time_log(f"{len(d['data'])}件のマージ処理"):
      next_df = d["data"]
      # マージ用のクエリを生成
      merge_query = create_merge_query(
        prev_df.columns,
        next_df.columns,
        final_key_cols,
        final_cols,
      )
      print(f'merge query: {merge_query}')
      # マージの実行
      prev_df = prev_df.join(next_df, on=final_key_cols, how='left').select(merge_query)
      print(f'merged df: {prev_df}')
  return prev_df

def create_merge_query(prev_cols, next_cols, final_key_cols, final_cols):
  query = []
  # 最終結果用のカラムごとにループ
  for col in final_cols:
    # キーの場合は変更なし
    if col in final_key_cols:
      query.append(pl.col(col))
      continue
    
    if col in prev_cols:
      # 元データ、先データ両方に存在する場合、
      # かつ、先データがnullでなく空文字でもない場合は先データ(_right)で上書き
      if col in next_cols:
        next_col = f'{col}_right'
        query.append(
          pl.when(is_null_or_blank(next_col))
          .then(pl.col(col))
          .otherwise(pl.col(next_col)
          .alias(col))
        )
      # 元データのみ存在する場合は元データを利用
      else:
        query.append(pl.col(col))
    else:
      # 先データのみ存在する場合は先データを利用
      if col in next_cols:
        query.append(pl.col(col))
      # 元データ、先データのどちらにも存在しない場合はnull値を設定
      else:
        query.append(pl.lit(None).alias(col))
  
  return query

def set_default_values(df, default_values):
  query = []
  for col in df.columns:
    # 初期値設定がある場合は、Null, 空文字を初期値で上書き
    if col in default_values:
      default_value = default_values.get(col)
      query.append(
        pl.when(is_null_or_blank(col))
        .then(pl.lit(default_value))
        .otherwise(pl.col(col))
        .alias(col)
      )
    else:
      # 初期値設定が無い場合は、何もしない
      query.append(pl.col(col))

  return df.select(query)


@contextmanager
def time_log(msg:str):
    """ with time_log("処理A"):
            proc_A()
    """
    print(f"{msg} - 開始")
    st_tm:float = time.time()
    yield
    ed_tm:float = time.time()
    print(f"{msg} - 終了:所要時間 {ed_tm-st_tm:.3f} [秒]")

def debug_print(data):
    if DEBUG:
        print(data)

def is_null_or_blank(column):
  return (pl.col(column).is_null()) | (pl.col(column) == '')


if __name__ == '__main__':
    hanlder()