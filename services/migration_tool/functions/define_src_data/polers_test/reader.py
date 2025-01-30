import polars as pl
from decimal import Decimal
from datetime import datetime

def read_excel(file_path: str):
    xlsx_list = pl.read_excel(file_path, sheet_id=0, has_header=False)
    xlsx_list.pop('一覧', None)  # 一覧シートを削除
    return xlsx_list

def read_definition(data_name, xlsx):
    config = {
      "data_name": data_name,
      "row": {
        "sys_name": 2,
        "mst_name": 3,
        "file_path": 4,
        "outfile_type": 4,
        "data": 8 # 9行目以降がデータ行
      },
      "column": {
        "outfile_type": 2, # 2列目が出力ファイル名のパターン
        "dst": 19 # 19列目までが最終形の定義
      }, 
      "columns_per_src": 7,
    }  # 設定を辞書として定義

    # ヘッダー部分を除いた定義部分を取得
    data_rows = xlsx[config["row"]["data"]:]
    # 出力定義と入力定義（複数）を取得
    dst_definition = get_dst_definition(config, xlsx, data_rows)
    src_definitions = get_src_definitions(config, xlsx, dst_definition)

    return dst_definition, src_definitions

def get_dst_definition(config, xlsx, data_rows):

    # 最終形の定義の取得
    final_definition = data_rows.select([
      data_rows[f'column_{i+1}'] for i in range(config["column"]["dst"])
    ])
    final_definition.columns = [
      xlsx[f'column_{i+1}'][config["row"]["data"]-1] for i in range(config["column"]["dst"])
    ]

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
    
    # 出力ファイルの形式
    output_type_col = f'column_{config["column"]["outfile_type"]}'
    output_type_row = config["row"]["outfile_type"]
    # print(f'col: {output_type_col}, row: {output_type_row}')
    output_type = xlsx[output_type_col][output_type_row]
    output_path = f'{config["data_name"]}.{output_type}'
    # print(f'type: {output_type}, path: {output_path}')

    return {
      "data_name": config["data_name"],
      "definition": final_definition,
      "key_cols": final_key_cols,
      "field_def": field_def,
      "output": {
        "type": output_type,
        "path": output_path,
      }
    }

def get_src_definitions(config, xlsx, dst_definitions):

    # 元データの件数を算出
    src_cols_num = (len(xlsx.columns) - (config["column"]["dst"] + 1))
    src_data_num, x = divmod(src_cols_num, config["columns_per_src"])
    # 列数が不正の場合
    if x != 0:
      print(f"元データの列数が不正です。")
      print(f"xlsx.columns: {len(xlsx.columns)}, src_cols_num: {src_cols_num}, src_data_num: {src_data_num}, x: {x}")

    # データ行を取り出し
    data_rows = xlsx[config["row"]["data"]:]
    # 元データの定義とデータを取得
    src_definitions = []
    for i in range(src_data_num):
      # 元データの開始列、終了列を算出
      start = config["column"]["dst"] + 1 + i * config['columns_per_src']
      end = start + config['columns_per_src']
      # print(f'start_col_num: {start_col_num}, end_col_num: {end_col_num}')
      # 名称生成
      sys_name = xlsx[f'column_{start + 1}'][config["row"]["sys_name"]]
      mst_name = xlsx[f'column_{start + 1}'][config["row"]["mst_name"]]
      data_name = f'{sys_name}_{mst_name}'
      # print(f'data_name: {data_name}')
      # 定義取得
      definition = data_rows.select([
        data_rows[f'column_{i+1}'] for i in range(start, end)
      ])
      definition.columns = [xlsx[f'column_{i+1}'][config["row"]["data"]-1] for i in range(start, end)]
      
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
      # 元データを取得
      file_path = xlsx[f'column_{start + 1}'][config["row"]["file_path"]]
      
      # データ取得
      src_definition = {
        "data_name": data_name,
        "definition": definition,
        "key_cols": key_cols,
        "field_def": field_def,
        "input": {
          "path": file_path,
        }
      }

      src_definitions.append(src_definition)
    
    return src_definitions

def get_srcs_data(srcs):
  for src in srcs:
    file_path = src["input"]["path"]

    # 0埋め数字の0が取れてしまうため、すべてUtf8にキャスト
    schema_overrides = {f["name"]: pl.Utf8 for f in src["field_def"]}
    src_df = pl.read_csv(file_path, schema_overrides=schema_overrides)
    # null行を削除（is_null行を ~ で反転）
    src_df = src_df.filter(~pl.all_horizontal(src_df.select(pl.all().is_null())))
    src["df"] = src_df  

  return srcs

def add_field_definition(field, definition):

  # print(f'field: {field}, definition: {definition}')
  defi = get_def_dict(definition)
  # print(f'defi: {defi}')
  
  # 物理名
  if defi.get("物理名") and defi.get("物理名") != '-':
    field["physical_name"] = defi["物理名"]
  # 型, 桁数
  if defi["型"] == 'varchar':
    field["type"] = str
    field["typestr"] = 'str'
    if defi["桁数"] != '' and defi["桁数"] != '-':
      field["max_length"] = int(defi["桁数"])
  elif defi["型"] == 'timestamp':
    field["type"] = datetime
    field["typestr"] = 'datetime'
  elif defi["型"] == 'numeric':
    field["type"] = int
    field["typestr"] = 'int'
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
        field["typestr"] = 'Decimal'
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