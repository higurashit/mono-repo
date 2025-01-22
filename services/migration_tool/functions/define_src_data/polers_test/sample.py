import polars as pl
from pydantic import Field, create_model, ValidationError
from openpyxl import Workbook
from decimal import Decimal
from contextlib import contextmanager
from datetime import datetime
import time

DEBUG = True

# df_dup.is_duplicated()
# df_dup.is_unique()
# df.get_column("Integer").is_in([2, 4, 6])

def hanlder(e={}):

  with time_log(f"[処理全体] 移行データの作成処理"):
    with time_log(f"移行定義情報のファイル読み込み処理"):
      dst, srcs = read_definition()

    with time_log(f"元データの初期化処理"):
      srcs = initialize_dfs(srcs)
      # print(f'datas: {datas}')

    with time_log(f"元データのチェック処理"):
      src_errors = check_dfs(srcs)
      print(f'src_errors: {src_errors}')

    with time_log(f"データのマージ処理"):
      merged_df = merge_dfs(srcs, dst["key_cols"], dst["field_def"])

    with time_log(f"結果データへの初期値設定処理"):
      result_df = set_default_values(merged_df, dst["field_def"])
      print(f'result df: {result_df}')

    with time_log(f"結果データのチェック処理"):
      dst_errors = check_df("result", result_df, dst["key_cols"], dst["field_def"])
      print(f'dst_errors: {dst_errors}')

    with time_log(f"結果データのファイル出力処理"):
      output_excel(result_df, dst)

def read_definition():
  file_path = '移行定義FMT.xlsx'
  sheet_name = '1_Aマスタ'
  xlsx = pl.read_excel(file_path, sheet_name=sheet_name, has_header=False)
  # print(f'xlsx: {xlsx}')

  # excel読み込み定義（行列が変わる場合はここを変更すること）
  data_row_num = 8 # 9行目以降がデータ行
  final_cols_num = 19 # 19列目までが最終形の定義
  columns_per_src = 7

  # データ行を取り出し
  data_rows = xlsx[data_row_num:]
  # 1列目までが最終形の定義
  final_definition = data_rows.select([
     data_rows[f'column_{i+1}'] for i in range(final_cols_num)
  ])
  final_definition.columns = [xlsx[f'column_{i+1}'][data_row_num-1] for i in range(final_cols_num)]

  # 最終形のカラム名
  field_def = []
  for i, x in enumerate(final_definition["論理名"].to_list()):
    # print(f'i: {i}, x: {x}')
    f = {
      "name": x,
    }
    f = add_field_definition(f, final_definition[i])
    field_def.append(f)

  # 最終形のキー項目
  final_key_cols = []
  for f in field_def:
    if f["is_key"]:
      final_key_cols.append(f["name"])

  dst_definitions = {
    "definition": final_definition,
    "key_cols": final_key_cols,
    "field_def": field_def,
    "output_path": f'{sheet_name}.xlsx',
  }
  # print(f'dst_definitions: {dst_definitions}')

  # 元データを取り出し
  # 元データの数
  src_cols_num = (len(xlsx.columns) - (final_cols_num + 1))
  src_data_num, x = divmod(src_cols_num, columns_per_src)
  # 列数が不正の場合はException
  if x != 0:
    print(f"元データの列数が不正です。xlsx.columns: {len(xlsx.columns)}, src_cols_num: {src_cols_num}, columns_per_src: {columns_per_src}, src_data_num: {src_data_num}, x: {x}")
  # print(src_data_num)

  # 元データの定義
  src_definitions = []
  for i in range(src_data_num):
    # 対象範囲
    start_col_num = final_cols_num + 1 + i * columns_per_src
    end_col_num = start_col_num + columns_per_src
    # print(f'start_col_num: {start_col_num}, end_col_num: {end_col_num}')
    # 名称生成
    sys_name = xlsx[f'column_{start_col_num + 1}'][2]
    mst_name = xlsx[f'column_{start_col_num + 1}'][3]
    data_name = f'{sys_name}_{mst_name}'
    # print(f'data_name: {data_name}')
    # 定義取得
    definition = data_rows.select([
      data_rows[f'column_{i+1}'] for i in range(start_col_num, end_col_num)
    ])
    definition.columns = [xlsx[f'column_{i+1}'][data_row_num-1] for i in range(start_col_num, end_col_num)]
    
    field_def = []
    for i, x in enumerate(definition["論理名"]):
      # print(f'i: {i}, x: {x}')
      if x != '' and x != '-':
        f = {
          "name": x,
          "final_name": dst_definitions["field_def"][i]["name"],
        }
        f = add_field_definition(f, definition[i])
        field_def.append(f)

    key_cols = []
    for f in field_def:
      if f["is_key"]:
        key_cols.append(f["name"])
        
    # print(f'field_def: {field_def}')
    # データ取得
    file_path = xlsx[f'column_{start_col_num + 1}'][4]
    schema_overrides = {f["name"]: pl.Utf8 for f in field_def} # 0埋め数字の0が取れてしまうため、すべてUtf8にキャスト
    # print(f'file_path: {file_path}, dtypes: {dtypes}')
    src_df = pl.read_csv(file_path, schema_overrides=schema_overrides)
    src_definition = {
      "definition": definition,
      "data_name": data_name,
      "key_cols": key_cols,
      "field_def": field_def,
      "data": src_df
    }
    src_definitions.append(src_definition)
  
  # print(src_definitions)

  return (
    dst_definitions,
    src_definitions,
  )

def add_field_definition(field, definition):

  # print(f'field: {field}, definition: {definition}')

  defi = get_def_dict(definition)
  # print(f'defi: {defi}')

  # 型, 桁数
  if defi["型"] == 'varchar':
    field["type"] = str
    if defi["桁数"] != '' and defi["桁数"] != '-':
      field["max_length"] = int(defi["桁数"])
  elif defi["型"] == 'timestamp':
    field["type"] = datetime
  elif defi["型"] == 'numeric':
    field["type"] = int
    if defi["桁数"] != '' and defi["桁数"] != '-':
      # 整数部分をn, 小数部分をfで定義
      n = defi["桁数"]
      f = 0
      # 小数を含む場合、整数部分と小数部分を取得
      if ',' in defi["桁数"]:
        [n, f] = defi["桁数"].split(',')
      # print(f'n: {n}, float: {float}')
      # 整数
      if int(f) == 0:
        field["lt"] = 10 ** int(n)
      # 小数
      if int(f) > 0:
        field["type"] = Decimal
        field["max_digits"] = int(n)
        field["decimal_places"] = int(f)
  # NULL NG
  field["null_ng"] = True if defi["NULL"] == "NG" else False
  # キー
  field["is_key"] = True if defi["業務キー"] == "〇" else False
  # 許容区分値
  if defi.get("許容区分値") and defi.get("許容区分値") != '-':
    field["enum"] = defi["許容区分値"].split(',')
  # 初期値
  if defi.get("初期値") and defi.get("初期値") != '-':
    field["default"] = defi["初期値"]
  else:
    field["default"] = None
    # 初期値がない場合は、型もNoneを許容する
    field["type"] = field["type"] | None
  
  # print(f'field: {field}')
  return field

def get_def_dict(defi):
  return {
    d: defi[d][0] for d in defi.columns
  }

def initialize_dfs(datas):

  # print(f'datas: {datas}')

  # マージ用にキーの名前を統一する
  # dfごとにループ
  for idx, d in enumerate(datas):
    # 全データをstrにキャスト
    df = cast_to_str(d["data"])
    datas[idx]["data"] = df

  return datas

def cast_to_str(df):
  return df.with_columns(
    # すべてのカラムをutf8にキャスト
    [pl.col(col).cast(pl.Utf8).alias(col) for col in df.columns]
  )

def check_dfs(datas):
  errors = []

  for d in datas:
    errors = check_df(d["data_name"], d["data"], d["key_cols"], d["field_def"])

  return errors

def check_df(name, df, key_cols, field_def):

  with time_log(f"[{name}] {len(df)}件のチェック処理"):
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

def check_data_definition(df, model):

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

def merge_dfs(datas, final_key_cols, final_field_def):

  # カラム名を最終形に統一
  for i, d in enumerate(datas):
    df = d["data"]
    df = df.select([
      pl.col(f["name"]).alias(f["final_name"]) for f in d["field_def"]
    ])
    datas[i]["data"] = df
  
  final_cols = [f["name"] for f in final_field_def]
  
  # print(f'datas: {datas}')
  # print(f'final_key_cols: {final_key_cols}')
  # print(f'final_cols: {final_cols}')

  # 両方のキーをマージし、キーのみのdfを作成
  key_only_df = pl.concat([d["data"][final_key_cols] for d in datas]).unique().sort(by=final_key_cols)
  print(f'key: {key_only_df}')

  # 元データのdfを順番にマージ
  prev_df = key_only_df
  for d in datas:
    with time_log(f"[{d['data_name']}] {len(d['data'])}件のマージ処理"):
      # カラム名を最終形に統一
      next_df = d["data"]

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

def set_default_values(df, final_field_def):
  
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

def output_excel(df:pl.DataFrame, dst):
  file_path = dst["output_path"]
  definition = dst["definition"]
  cols = [f["name"] for f in dst["field_def"]]

  # Create a new workbook
  wb = Workbook()
  # grab the active worksheet
  ws = wb.active
  ws.title = '元データ'
  ws.append(df.columns)
  for d in df.to_dicts():
    ws.append(list(d.values()))

  columuns = definition.columns
  sheets = definition.select(columuns[9:18])
  print(f'sheets: {sheets}')
  for sheet_name, sheet_row_nums in sheets.to_dict().items():
    row_nums_without_null = list(filter(lambda x: x != '' and x != '-', sheet_row_nums.to_list()))
    if len(row_nums_without_null) == 0:
      continue
    max_row_nums = max([int(x) for x in row_nums_without_null])
    print(f'{sheet_name}: {row_nums_without_null}: max => {max_row_nums}')

    # 初期値は空白
    query = [pl.lit(None).alias(f'col_{i}') for i in range(max_row_nums)]
    is_output = False
    for idx, row_num in enumerate(sheet_row_nums.to_list()):
      # print(f'{idx}: {row_num}: {cols[idx]}')
      # 数値が設定されている場合
      if row_num != '' and row_num != '-':
        # 設定されている数値を列番号として、当該列を設定
        query[int(row_num) - 1] = pl.col(cols[idx])
        is_output = True
    if is_output:
      ws = wb.create_sheet(title=sheet_name)
      # print(f'query: {query}')
      ret_df = df.select(query)
      ws.append(ret_df.columns)
      for d in ret_df.to_dicts():
        ws.append(list(d.values()))
      
  # Save the file
  wb.save(file_path)


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
