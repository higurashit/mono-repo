import polars as pl

# df_dup.is_duplicated()
# df_dup.is_unique()
# df.get_column("Integer").is_in([2, 4, 6])

def hanlder(e={}):

  # 移行定義情報をロード
  final_cols, final_key_cols, default_values, dfs, dfs_keys = read_definition()

  # 元データを初期化
  dfs = initialize_dfs(dfs, dfs_keys, final_key_cols)
  print(f'dfs: {dfs}')
  
  # 元データを順にマージ
  merged_df = merge_dfs(dfs, final_key_cols, final_cols)

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

  final_cols = ['HOGE', 'ID_1', 'ID_2', 'other', 'name', 'age', 'birth', 'lucky_color']
  final_key_cols = ['ID_1', 'ID_2']
  default_values = {
    'other': 'No other information.',
    'name': 'No name',
    'age': 99,
    'birth': '1990/1/1',
  }
  moto1 = pl.DataFrame({
    'ID1': [1, 2, 3, 4],
    'ID2': [11, 22, 33, 44],
    'name': ['A', 'B', 'C', 'D'],
    'age': [10, 20, 30, None],
    'birth': ['1986/12/17', None, '2025/1/17', None],
  })
  moto1_key_cols = ['ID1', 'ID2']
  moto2 = pl.DataFrame({
    'ID__1': [1, 3, 5, 2, 4],
    'ID__2': [11, 23, 55, 22, 44],
    'name': ['AAA', 'CCC', 'EEE', None, ''],
    'lucky_color': ['red', 'yellow', 'blue', None, None]
  })
  moto2_key_cols = ['ID__1', 'ID__2']

  return (
    final_cols,
    final_key_cols,
    default_values,
    [moto1, moto2],
    [moto1_key_cols, moto2_key_cols]
  )

def initialize_dfs(dfs, dfs_keys, final_key_cols):
  # 全データをstrにキャスト
  dfs = [cast_to_str(df) for df in dfs]
  
  # マージ用にキーの名前を統一する
  result_dfs = []
  # dfごとにループ
  for idx_df, df in enumerate(dfs):
    query = []
    # カラムごとにループ
    for idx_col, col in enumerate(df.columns):
      # カラムが該当dfのキーの場合、最終出力時のカラム名に訂正
      if col in dfs_keys[idx_df]:
        query.append(pl.col(col).alias(final_key_cols[idx_col]))
      else:
        query.append(pl.col(col))
    
    # カラム名変更後のdfを返却値に追加
    print(f'query: {query}')
    result_dfs.append(df.select(query))

  return result_dfs

def cast_to_str(df):
  return df.with_columns(
    # すべてのカラムをutf8にキャスト
    [pl.col(col).cast(pl.Utf8).alias(col) for col in df.columns]
  )

def merge_dfs(dfs, final_key_cols, final_cols):
  # 両方のキーをマージし、キーのみのdfを作成
  key_only_df = pl.concat([df[final_key_cols] for df in dfs]).unique().sort(by=final_key_cols)
  print(f'key: {key_only_df}')

  # 元データのdfを順番にマージ
  prev_df = key_only_df
  for next_df in dfs:
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

def is_null_or_blank(column):
  return (pl.col(column).is_null()) | (pl.col(column) == '')

if __name__ == '__main__':
    hanlder()