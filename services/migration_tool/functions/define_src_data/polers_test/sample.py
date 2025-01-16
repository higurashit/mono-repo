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
  key_col = ['ID_1', 'ID_2']
  data_col = ['name', 'age', 'birth', 'other']
  moto1 = pl.DataFrame({
    'ID_1': [1, 2, 3],
    'ID_2': [11, 22, 33],
    'name': ['A', 'B', 'C'],
    'age': [10, 20, 30],
    'birth': ['1986/12/17', None, '2025/1/17'],
  })
  moto2 = pl.DataFrame({
    'ID_1': [1, 3, 5],
    'ID_2': [11, 23, 55],
    'name': ['AAA', 'CCC', 'EEE'],
  })

  # 両方のキーをマージ
  key = pl.concat([moto1[key_col], moto2[key_col]]).unique().sort(by=key_col)
  print(f'key: {key}')

  # データをマージ
  ret = key
  print(f'start: {ret}')
  ret = ret.join(moto1, on=key_col, how='left')
  print(f'key join moto1: {ret}')
  ret = ret.join(moto2, on=key_col, how='left')
  print(f'moto1 join moto2: {ret}')

  ret = ret.select([
    pl.lit(None).alias('dummy'),
    pl.col('ID_1'),
    pl.col('ID_2'),
    pl.col('name').fill_null(''),
    pl.col('age').fill_null(0),
    pl.col('birth').fill_null(''),
    pl.lit(None).alias('dummy2'),
  ])
  print(f'select: {ret}')

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