import polars as pl

# df_dup.is_duplicated()
# df_dup.is_unique()
# df.get_column("Integer").is_in([2, 4, 6])

def hanlder(e={}):
  # test_concat()
  test_concat2()
  # test3()

def test3():
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

def test_concat2():
  final_cols = ['ID_1', 'ID_2', 'other', 'name', 'age', 'birth', 'lucky_color']
  key_cols = ['ID_1', 'ID_2']
  default_values = {
    'other': 'defult_other',
    'name': '',
    'age': 0,
    'birth': '',
  }
  moto1 = pl.DataFrame({
    'ID_1': [1, 2, 3, 4],
    'ID_2': [11, 22, 33, 44],
    'name': ['A', 'B', 'C', 'D'],
    'age': [10, 20, 30, None],
    'birth': ['1986/12/17', None, '2025/1/17', None],
  })
  moto2 = pl.DataFrame({
    'ID_1': [1, 3, 5, 2, 4],
    'ID_2': [11, 23, 55, 22, 44],
    'name': ['AAA', 'CCC', 'EEE', None, ''],
    'lucky_color': ['red', 'yellow', 'blue', None, None]
  })

  # 両方のキーをマージ
  key = pl.concat([moto1[key_cols], moto2[key_cols]]).unique().sort(by=key_cols)
  print(f'key: {key}')

  # データをマージ
  prev_df = key
  for next_df in [moto1, moto2]:
    # マージ用のクエリを生成
    merge_query = create_merge_query(
      final_cols,
      prev_df.columns,
      next_df.columns,
      key_cols,
      default_values,
    )
    print(f'merge query: {merge_query}')
    # マージ
    prev_df = prev_df.join(next_df, on=key_cols, how='left').select(merge_query)
    print(f'merged df: {prev_df}')

def create_merge_query(final_cols, prev_cols, next_cols, key_cols, default_values):
  query = []
  # 最終結果用のカラムごとにループ
  for col in final_cols:
    # キーの場合は変更なし
    if col in key_cols:
      query.append(pl.col(col))
      continue
    
    if col in prev_cols:
      # 元データ、先データ両方に存在する場合、
      # かつ、先データがnullでなく空文字でもない場合は先データ(_right)で上書き
      if col in next_cols:
        next_col = f'{col}_right'
        query.append(
          pl.when(
            (pl.col(next_col).is_null())
            | (pl.col(next_col) == '')
          ).then(pl.col(col))
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
      # 元データ、先データのどちらにも存在しない場合はデフォルト値を設定
      else:
        default_value = ''
        if col in default_values:
          default_value = default_values.get(col)
        query.append(pl.lit(default_value).alias(col))
  
  return query

def test_concat():
  # 最終データ
  saki = [
      pl.col('ID'),
      pl.col('name1').fill_null(''),
      pl.col('name2').fill_null(''),
      # pl.col('name3').fill_null(''),
      # pl.col('name4').fill_null('999'),
  ]

  # name2, 3, 4は無い元データ
  moto1 = pl.DataFrame({
   'ID': [1, 2, 3],
   'name1': ['n1', 'n2', 'n3']
  })

  # name1が上書き、name3,4は無い元データ
  moto2 = pl.DataFrame({
   'ID': [1, 2, 3],
   'name1': ['l1', 'm2', 'n3'],
   'name2': ['n1', 'n2', 'n3']
  })

  result = moto1
  for df in [moto2]:
    result = result.join(df, on='ID', how='full') \
      .select(saki)
  
  print(result)


if __name__ == '__main__':
    hanlder()