import polars as pl
from pydantic import create_model, ValidationError
from openpyxl import Workbook
from contextlib import contextmanager
from datetime import datetime
import time

DEBUG = True

# df_dup.is_duplicated()
# df_dup.is_unique()
# df.get_column("Integer").is_in([2, 4, 6])

def hanlder(e={}):

  # 移行定義情報をロード
  dst, srcs = read_definition()

  # 元データを初期化
  srcs = initialize_dfs(srcs)
  # print(f'datas: {datas}')

  # 元データをチェック
  errors = check_dfs(srcs)
  print(f'errors: {errors}')

  # 元データを順にマージ
  merged_df = merge_dfs(srcs, dst["key_cols"], dst["cols"])

  # デフォルト値の設定
  result_df = set_default_values(merged_df, dst["default_values"])
  print(f'result df: {result_df}')

  # 結果を出力
  output_excel(result_df, dst)

def read_definition():
  file_path = '移行定義FMT.xlsx'
  sheet_name = '1_Aマスタ'
  xlsx = pl.read_excel(file_path, sheet_name=sheet_name, has_header=False)
  print(f'xlsx: {xlsx}')

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
  print(f'final_definition: {final_definition}')

  # 最終形のカラム名
  final_cols = final_definition["論理名"].to_list()
  print(final_cols)

  # 業務キー
  final_key_cols = []
  for i, x in enumerate(final_definition["業務キー"]):
    if x == '〇':
      final_key_cols.append(final_cols[i])
  print(final_key_cols)

  # 初期値
  default_values = {}
  for i, x in enumerate(final_definition["初期値"]):
    if x != '':
      default_values[final_cols[i]] = x
  print(default_values)

  # 元データを取り出し
  # 元データの数
  src_cols_num = (len(xlsx.columns) - (final_cols_num + 1))
  src_data_num, x = divmod(src_cols_num, columns_per_src)
  # 列数が不正の場合はException
  if x != 0:
    print(f"元データの列数が不正です。xlsx.columns: {len(xlsx.columns)}, src_cols_num: {src_cols_num}, columns_per_src: {columns_per_src}, src_data_num: {src_data_num}, x: {x}")
  print(src_data_num)

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
    key_cols = []
    key_order = 0
    for i, x in enumerate(definition["論理名"]):
      if x != '' and x != '-':
        d = {
          "name": x,
          "final_name": final_cols[i],
          "type": definition["型"][i],
          "null_ng": True if definition["NULL"][i] == "NG" else False,
        }
        if definition["結合キー"][i] == '〇':
          d["key_order"] = key_order
          key_cols.append((key_order, x))
          key_order += 1
        if definition["許容区分値"][i] != '' and definition["許容区分値"][i] != '-':
          d["enum"] = definition["許容区分値"][i].split(',')

        field_def.append(d)

    # print(f'field_def: {field_def}')
    # データ取得
    file_path = xlsx[f'column_{start_col_num + 1}'][4]
    dtypes = {f["name"]: pl.Utf8 for f in field_def} # 0埋め数字の0が取れてしまうため、すべてUtf8にキャスト
    # print(f'file_path: {file_path}, dtypes: {dtypes}')
    src_df = pl.read_csv(file_path, dtypes=dtypes)
    src_definition = {
      "definition": definition,
      "data_name": data_name,
      "key_cols": key_cols,
      "field_def": field_def,
      "data": src_df
    }
    src_definitions.append(src_definition)
  
  # print(src_definitions)
  dst_definitions = {
    "definition": final_definition,
    "cols": final_cols,
    "key_cols": final_key_cols,
    "default_values": default_values,
    "output_path": f'{sheet_name}.xlsx',
  }

  return (
    dst_definitions,
    src_definitions,
  )

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
    df = d["data"]
    key_cols = d["key_cols"]

    # キー重複チェック
    errors += check_data_duplicate(df, key_cols)

    # 型チェック
    model = create_dynamic_model(d["data_name"], d["field_def"])
    errors += check_data_definition(df, model)
  
  return errors

def create_dynamic_model(name, migration_definition):
    
    # print(f'migration_definition: {migration_definition}')

    mname = f'{name}Model'  # XXX_MasterModel
    fields = {}

    for md in migration_definition:
        default_value = ... if md.get('null_ng') else None
        fields[md['name']] = (md['type'], default_value)

    return create_model(
        mname,
        **fields
    )

def check_data_duplicate(df, key_cols):
    
    print(f'key_cols: {key_cols}')

    keys = []
    for _, key in key_cols:
      keys.append(key)

    # キー項目で重複しているデータを取得
    duplicates = df.filter(pl.struct(keys).is_duplicated())
    # エラーオブジェクトに格納して返却
    errors = [
      {
         'data': dup,
         'error': f'key is duplicated: {keys}'
      } for dup in duplicates.to_dicts()
    ]

    return errors

def check_data_definition(df, model):

  errors = []
  with time_log(f"{len(df)}件のチェック処理"):
      rows = df.to_dicts()
      for target in rows:
          try:
              model(**target)
          except ValidationError as e:
              errors.append({
                 "data": target,
                 "error": e.errors()
              })

  return errors

def merge_dfs(datas, final_key_cols, final_cols):

  # カラム名を最終形に統一
  for i, d in enumerate(datas):
    df = d["data"]
    df = df.select([
      pl.col(f["name"]).alias(f["final_name"]) for f in d["field_def"]
    ])
    datas[i]["data"] = df
  
  print(f'datas: {datas}')
  print(f'final_key_cols: {final_key_cols}')
  print(f'final_cols: {final_cols}')

  # 両方のキーをマージし、キーのみのdfを作成
  key_only_df = pl.concat([d["data"][final_key_cols] for d in datas]).unique().sort(by=final_key_cols)
  print(f'key: {key_only_df}')

  # 元データのdfを順番にマージ
  prev_df = key_only_df
  for d in datas:
    with time_log(f"{len(d['data'])}件のマージ処理"):
      # カラム名を最終形に統一
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

def output_excel(df:pl.DataFrame, dst):
  file_path = dst["output_path"]
  definition = dst["definition"]
  cols = dst["cols"]

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
  print(sheets)
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
      if row_num != '' and row_num != '-':
        # 全体が5カラムで、2カラム目の要素が「3番目」だった場合、以下のようにしたい
        # query: [pl.lit(None), pl.lit(None), 3番目のカラム, pl.lit(None), pl.lit(None)]
        query[int(row_num) - 1] = pl.col(cols[idx])
        is_output = True
    if is_output:
      ws = wb.create_sheet(title=sheet_name)
      print(f'query: {query}')
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
