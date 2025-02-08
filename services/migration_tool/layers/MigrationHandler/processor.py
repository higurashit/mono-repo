import polars as pl
from pydantic import Field, create_model, ValidationError
from datetime import datetime
from utils import time_log

def initialize_dfs(datas):
    for idx, d in enumerate(datas):
        df = cast_to_str(d["df"])
        datas[idx]["df"] = df
    return datas

def cast_to_str(df:pl.DataFrame):
    return df.with_columns([pl.col(col).cast(pl.Utf8).alias(col) for col in df.columns])

def check_datas(datas):
    errors = []
    for data in datas:
        errors += check_data(data)
    return errors

def check_data(data):

    name = data["data_name"]
    key_cols = data["key_cols"]
    field_def = data["field_def"]
    df = data["df"]

    with time_log(f"　[チェックプロセス] {name} ({len(df)}件)のチェック処理"):
        errors = []
        # キー重複チェック
        errors += check_data_duplicate(df, key_cols)

        # 型チェック
        model = create_dynamic_model(name, field_def)
        errors += check_data_definition(df, model)

        # 許容区分値チェック
        errors += check_enum_data(df, field_def)

        return errors

def check_data_duplicate(df, key_cols):
    
    # print(f'key_cols: {key_cols}')
    # キー項目で重複しているデータを取得
    duplicates = df.filter(pl.struct(key_cols).is_duplicated())
    # エラーオブジェクトに格納して返却
    errors = [
      {
         'data': dup,
         'error': f'key is duplicated: {key_cols}'
      } for dup in duplicates.to_dicts()
    ]

    return errors

def create_dynamic_model(name, field_def):
    
    # print(f'field_def: {field_def}')

    mname = f'{name}Model'  # XXX_MasterModel
    fields = {}

    for f in field_def:
        # print(f'f: {f}')
        field_params = {
          'default': ... if f.get('null_ng') else None,
          'max_length': f.get('max_length'),
          'max_digits': f.get('max_digits'),
          'decimal_places': f.get('decimal_places'),
          'lt': f.get('lt'),
        }
        fields[f['name']] = (f['type'], Field(**field_params))

    # print(f'fields: {fields}')

    return create_model(
        mname,
        **fields
    )

def check_data_definition(df:pl.DataFrame, model):

  errors = []
  for row in df.to_dicts():
    # print(f'row: {row}')
    error = check_row_with_model(row, model)
    if error:
      errors.append(error)
      
  return errors

def check_row_with_model(row, model):
  try:
    # pydanticモデルでのチェック
    model(**row)
  except ValidationError as e:
    # エラーの場合はメッセージを設定
    return {
      "data": row,
      "error": e.errors()
    }

def check_enum_data(df, field_def):

  errors = []
  for f in field_def:
    # 許容区分値を持つ列のみ実施
    if f.get('enum'):
      # 列データの取得
      col_data = df[f.get('name')]
      # 列データのチェック
      for i, data in enumerate(col_data):
        # 許容区分値に含まれていない場合
        if data not in f.get('enum'):
          errors.append({
            "data": df[i].to_dicts(),
            "error": f"enum error: {f.get('name')} に {data} が格納されています。"
          })
  return errors


def process_src_dfs(srcs, dst):
  # 出力データ名
  dst_name = dst["data_name"]
  for idx, src in enumerate(srcs):
    # 入力データ名
    src_name = src["data_name"]
    # 個別要件のカスタマイズポイント
    # print(f'src_name: {src_name}, dst_name: {dst_name}')
    if dst_name == '001_Aマスタ':
      if src_name == 'システムB_Bマスタ':
        src["df"] = modify_001_01(src)
        srcs[idx] = src
      if src_name == 'システムC_Cマスタ':
        src["df"] = modify_001_02(src)
        srcs[idx] = src

  return srcs


def merge_dfs(datas, dst):
  final_key_cols = dst["key_cols"]
  final_field_def = dst["field_def"]

  # カラム名を最終形に統一
  for i, d in enumerate(datas):
    df = d["df"]
    df = df.select([
      pl.col(f["name"]).alias(f["final_name"]) for f in d["field_def"]
    ])
    datas[i]["df"] = df
  
  final_cols = [f["name"] for f in final_field_def]
  
  # print(f'datas: {datas}')
  # print(f'final_key_cols: {final_key_cols}')
  # print(f'final_cols: {final_cols}')

  # 両方のキーをマージし、キーのみのdfを作成
  key_only_df = pl.concat([d["df"][final_key_cols] for d in datas]).unique().sort(by=final_key_cols)
  # print(f'key: {key_only_df}')

  # 元データのdfを順番にマージ
  prev_df = key_only_df
  for d in datas:
    with time_log(f"　[マージプロセス] {d['data_name']} ({len(d['df'])}件)のマージ処理"):
      # カラム名を最終形に統一
      next_df = d["df"]

      # マージ用のクエリを生成
      merge_query = create_merge_query(
        prev_df.columns,
        next_df.columns,
        final_key_cols,
        final_cols,
      )
      # print(f'merge query: {merge_query}')
      # マージの実行
      prev_df = prev_df.join(next_df, on=final_key_cols, how='left').select(merge_query)
      # print(f'merged df: {prev_df}')
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

def is_null_or_blank(column):
  return (pl.col(column).is_null()) | (pl.col(column) == '')

def set_default_values(df, dst):
  final_field_def = dst["field_def"]
  # print(f'final_field_def: {final_field_def}')

  default_values = {f["name"]: f["default"] for f in final_field_def}
  query = []
  for col in df.columns:
    # 初期値設定がある場合
    if col in default_values:
      val = default_values.get(col)
      # 動的な初期値
      if val == '連番':
        default_value = pl.arange(1, df.height + 1)
      elif val == '現在日':
        today = datetime.today().strftime('%Y-%m-%d 00:00:00')
        default_value = pl.lit(today)
      # 静的な初期値
      else:
        default_value = pl.lit(val)
      
      # Null or 空文字の場合、初期値で上書きする
      query.append(
        pl.when(is_null_or_blank(col))
        .then(default_value)
        .otherwise(pl.col(col))
        .alias(col)
      )
    else:
      # 初期値設定が無い場合は、何もしない
      query.append(pl.col(col))

  return df.select(query)

# 出力用の変換クエリを作成
def prepare_output_df(row_nums, col_names, aliases, dst):
  # print(f'dst: {dst}')
  # 出力列数の配列を取得
  row_nums_without_null = list(filter(lambda x: x != '' and x != '-', row_nums.to_list()))
  if len(row_nums_without_null) == 0:
    return []
  # 出力列の最大値を取得
  max_row_nums = max([int(x) for x in row_nums_without_null])
  query = [pl.lit('').alias(f'col_{i}') for i in range(max_row_nums)]
  for idx, row_num in enumerate(row_nums.to_list()):
    # print(f'{idx}: {row_num}: {cols[idx]}')
    # 数値が設定されている場合
    if row_num != '' and row_num != '-':
      # 設定されている数値を列番号として、当該列を設定
      query_idx = int(row_num) - 1
      col_name = col_names[idx]
      alias = aliases[idx]
      query[query_idx] = pl.col(col_name).alias(alias)
      # CSVかつdatetimeの場合、フォーマット変換する
      output_type = dst['output']['type']      
      typestr = dst['field_def'][idx]['typestr']
      if typestr == "datetime":
        result_fmt = '%Y-%m-%d %H:%M:%S'
        if output_type == 'csv':
          result_fmt = '%Y-%m-%d|%H:%M:%S'
        # 年月日と時刻の間に|を入れる
        query[query_idx] = (
          pl.coalesce(
            strptime_with_fmt(col_name, "%Y-%m-%d %H:%M:%S"),
            strptime_with_fmt(col_name, "%Y-%m-%d"),
            strptime_with_fmt(col_name, "%Y/%m/%d %H:%M:%S"),
            strptime_with_fmt(col_name, "%Y/%m/%d"),
          ).dt.strftime(result_fmt).alias(alias)
        )
        # print(f'idx: {query_idx}, query: {query[query_idx]}')

  # print(f'query: {query}')
  return dst["df"].select(query)

def strptime_with_fmt(column, date_fmt) -> pl.Expr:
  # カラム値がすべてnullの場合にカラム型がnullになる
  # カラム型がnullの場合、空文字に変換してからstrptimeメソッドを実行
  return (
    pl.col(column)
    .fill_null('')
    .str.strptime(pl.Datetime, date_fmt, strict=False)
  )

##################
# 個別編集要件
##################
def modify_001_01(src):
  df:pl.DataFrame = src["df"]
  query = []
  for f in src["field_def"]:
    col = f["name"]
    # 8桁未満の場合は、8桁になるまで先頭0埋め
    if col == 'Bコード':
      query.append(pl.col(col).str.zfill(8))
    else:
      query.append(pl.col(col))
  return df.select(query)

def modify_001_02(src):
  df:pl.DataFrame = src["df"]
  query = []
  for f in src["field_def"]:
    col = f["name"]
    # 8桁未満の場合は、8桁になるまで先頭0埋め
    if col == 'Cコード':
      query.append(pl.col(col).str.zfill(8))
    else:
      query.append(pl.col(col))
  return df.select(query)
