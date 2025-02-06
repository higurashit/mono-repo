import os
from utils import time_log, create_lock_file, delete_lock_file
from reader import read_excel, read_definition, get_srcs_data
from processor import initialize_dfs, check_datas, process_src_dfs, merge_dfs, set_default_values
from writer import output_excel, output_csv
from const import Constructor



class MigrationHandler:
    def __init__(self):
        # 作業フォルダを作成
        self.const = Constructor()
        path = self.const.local_directory_path
        os.makedirs(path, exist_ok=False)
        print(f'create directory: {path}')

    def get_setting(self, sheetname):
        with time_log("[処理全体] 移行定義Excelの読み込みとループ用配列の生成処理"):
            xlsx_list = self.load_definitions()

            setting = read_definition(sheetname, xlsx_list[sheetname])
            return setting

    def load_definitions(self):
        with time_log("[移行定義取得]"):
            return read_excel(
                self.const.bucket_name,
                self.const.definition_object_key,
                self.const.local_definition_file_path
            )

    def run(self, setting):
        with time_log("[処理全体] 移行データの作成処理"):
            dst, srcs = setting
            self.process_data(dst, srcs)

    def process_data(self, dst, srcs):
        file_path = dst["output"]["path"]
        lock_file = f"{self.const.object_path}{file_path}.lock"
        create_lock_file(
            self.const.bucket_name,
            lock_file
        )
        try:
            srcs = self.process_sources(srcs, dst)
            dst["df"] = self.process_result(srcs, dst)
            self.output_result(dst)
        finally:
            delete_lock_file(
                self.const.bucket_name,
                lock_file
            )

    def process_sources(self, srcs, dst):
        with time_log("[元データ-取得]"):
            srcs = get_srcs_data(
                self.const.bucket_name,
                self.const.object_path,
                self.const.local_directory_path,
                srcs
            )

        with time_log("[元データ-初期化]"):
            srcs = initialize_dfs(srcs)

        with time_log("[元データ-チェック]"):
            check_datas(srcs)

        with time_log("[元データ-加工]"):
            return process_src_dfs(srcs, dst)

    def process_result(self, srcs, dst):
        with time_log("[マージ処理全体]"):
            merged_df = merge_dfs(srcs, dst)

        with time_log("[結果データ-初期値設定]"):
            return set_default_values(merged_df, dst)

    def output_result(self, dst):
        with time_log("[結果データ-チェック]"):
            check_datas([dst])

        with time_log("[結果データ-ファイル出力]"):
            if dst["output"]["type"] == "xlsx":
                output_excel(dst)
            elif dst["output"]["type"] == "csv":
                output_csv(dst)
            else:
                raise ValueError(f"出力形式が不明: {dst['output']['type']}")
