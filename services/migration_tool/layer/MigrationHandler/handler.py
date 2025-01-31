import os
from utils import time_log, check_lock_file, create_lock_file, delete_lock_file
from reader import read_excel, read_definition, get_srcs_data
from processor import initialize_dfs, check_datas, process_src_dfs, merge_dfs, set_default_values
from writer import output_excel, output_csv

class MigrationHandler:
    def __init__(self, file_path="移行定義FMT.xlsx"):
        self.file_path = file_path

    def get_settings(self):
        with time_log("[処理全体] 移行定義Excelの読み込みとループ用配列の生成処理"):
            xlsx_list = self.load_definitions()

            settings = []
            for key, value in xlsx_list.items():
                setting = read_definition(key, value)
                settings.append(setting)
            return settings

    def load_definitions(self):
        with time_log("[移行定義取得]"):
            return read_excel(self.file_path)

    def run(self, setting):
        with time_log("[処理全体] 移行データの作成処理"):
            dst, srcs = setting
            self.process_data(dst, srcs)

    def process_data(self, dst, srcs):
        file_path = dst["output"]["path"]
        lock_file = f"{file_path}.lock"
        check_lock_file(lock_file)
        create_lock_file(lock_file)

        try:
            srcs = self.process_sources(srcs, dst)
            dst["df"] = self.process_result(srcs, dst)
            self.output_result(dst)
        finally:
            delete_lock_file(lock_file)

    def process_sources(self, srcs, dst):
        with time_log("[元データ-取得]"):
            srcs = get_srcs_data(srcs)

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
