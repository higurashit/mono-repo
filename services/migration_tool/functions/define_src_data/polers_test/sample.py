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
  print(f'datas: {datas}')

  # 元データをチェック
  errors = check_dfs(datas)
  print(f'errors: {errors}')

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

  final_cols = ['HOGE', 'ID_1', 'ID_2', 'other', 'name', 'age', 'birth', 'lucky_color']
  final_key_cols = ['ID_1', 'ID_2']
  default_values = {
    'other': 'No other information.',
    'name': 'No name',
    'age': 99,
    'birth': '1990/1/1',
  }
  moto1_name = 'moto1'
  moto1_def = [
    { "name": "ID1", "type": "int", "is_key": True },
    { "name": "ID2", "type": "int", "is_key": True },
    { "name": "name", "type": "str" },
    { "name": "age", "type": "int" },
    { "name": "birth", "type": "datetime" },
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
    { "name": "ID__1", "type": "int", "is_key": True },
    { "name": "ID__2", "type": "int", "is_key": True },
    { "name": "name", "type": "str" },
    { "name": "lucky_color", "type": "str" },
  ]
  moto2 = pl.DataFrame({
    'ID__1': [1, 3, 5, 2, 4],
    'ID__2': [11, 23, 55, 22, 44],
    'name': ['AAA', 'CCC', 'EEE', None, ''],
    'lucky_color': ['red', 'yellow', 'blue', None, None]
  })

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
    # キー項目を取得
    df_keys = get_dfs_key(d)
    query = []
    # カラムごとにループ
    new_field_def = []
    for idx_col, col in enumerate(d["field_def"]):
      old_key = col["name"]
      # カラムが該当dfのキーの場合、最終出力時のカラム名に訂正
      if col.get('is_key'):
        final_key_col = final_key_cols[idx_col]
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
      if field.get('is_key'):
        dfs_key.append(field['name'])
  
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
              debug_print(record.model_dump())

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