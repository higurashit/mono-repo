import os
from utils import time_log, waiting_lock, create_lock_file, delete_lock_file, debug_print
from reader import read_excel, read_definition
from processor import initialize_dfs, check_dfs, process_src_dfs, merge_dfs, set_default_values
from writer import output_excel, output_csv

class MigrationHandler:
    def __init__(self):
        self.file_path = "移行定義FMT.xlsx"

    def run(self):
        with time_log("[処理全体] 移行データの作成処理"):
            xlsx_list = self.load_definitions()

            for key, value in xlsx_list.items():
                self.process_data(key, value)

    def load_definitions(self):
        with time_log("[移行定義情報] ファイル読み込み処理"):
            return read_excel(self.file_path)

    def process_data(self, key, xlsx_data):
        dst, srcs = read_definition(key, xlsx_data)

        file_path = dst["output"]["path"]
        lock_file = f"{file_path}.lock"
        waiting_lock(lock_file)
        create_lock_file(lock_file)

        try:
            srcs = self.process_sources(srcs, dst)
            dst["df"] = self.process_result(srcs, dst)
            self.output_result(dst)
        finally:
            delete_lock_file(lock_file)

    def process_sources(self, srcs, dst):
        with time_log("[元データ] 初期化処理"):
            srcs = initialize_dfs(srcs)

        with time_log("[元データ] チェック処理"):
            check_dfs(srcs)

        with time_log("[元データ] 加工処理"):
            return process_src_dfs(srcs, dst)

    def process_result(self, srcs, dst):
        with time_log("[データ] マージ処理"):
            merged_df = merge_dfs(srcs, dst)

        with time_log("[結果データ] 初期値設定処理"):
            return set_default_values(merged_df, dst)

    def output_result(self, dst):
        with time_log("[結果データ] チェック処理"):
            check_dfs([dst])

        with time_log("[結果データ] ファイル出力処理"):
            if dst["output"]["type"] == "xlsx":
                output_excel(dst)
            elif dst["output"]["type"] == "csv":
                output_csv(dst)
            else:
                raise ValueError(f"出力形式が不明: {dst['output']['type']}")
