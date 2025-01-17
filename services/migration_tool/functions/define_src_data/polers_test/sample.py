import polars as pl

# df_dup.is_duplicated()
# df_dup.is_unique()
# df.get_column("Integer").is_in([2, 4, 6])

def hanlder(e={}):

  final_cols = ['HOGE', 'ID_1', 'ID_2', 'other', 'name', 'age', 'birth', 'lucky_color']
  key_cols = ['ID_1', 'ID_2']
  default_values = {
    'other': 'No other information.',
    'name': 'No name',
    'age': 99,
    'birth': '1990/1/1',
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

  # 元データを順番にマージ
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
    # マージの実行
    prev_df = prev_df.join(next_df, on=key_cols, how='left').select(merge_query)
    print(f'merged df: {prev_df}')

  # 全データを文字列型に変換
  result_df = cast_to_str(prev_df)
  # デフォルト値の設定
  result_df = set_default_values(result_df, default_values)
  print(f'result df: {result_df}')

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

def cast_to_str(df):
  return df.with_columns(
    [pl.col(col).cast(pl.Utf8).alias(col) for col in df.columns]
  )

def set_default_values(df, default_values):
  query = []
  for col in df.columns:
    # 初期値設定がある場合は、Null, 空文字を初期値で上書き
    if col in default_values:
      default_value = default_values.get(col)
      query.append(
        pl.when(
          (pl.col(col).is_null())
          | (pl.col(col) == '')
        ).then(pl.lit(default_value))
        .otherwise(pl.col(col))
        .alias(col)
      )
    else:
      # 初期値設定が無い場合は、何もしない
      query.append(pl.col(col))

  return df.select(query)


def read_excel():
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

if __name__ == '__main__':
    hanlder()