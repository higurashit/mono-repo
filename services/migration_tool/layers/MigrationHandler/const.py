import os
import uuid

class Constructor:
    def __init__(self):
        # クラス変数を定義
        self.bucket_name = os.environ.get("BUCKET_NAME")
        self.object_path = os.environ.get("OBJECT_PATH")
        self.definition_object_name = '移行定義FMT.xlsx'
        self.definition_object_key = f'{self.object_path}{self.definition_object_name}'
        # 現在時刻を基にtmpディレクトリのパスを定義
        self.local_directory_root = os.environ.get("LOCAL_DIRECTORY_ROOT")
        self.local_directory_path = fr"{self.local_directory_root}/folder_{str(uuid.uuid4())}/"
        self.local_definition_file_path = f"{self.local_directory_path}{self.definition_object_name}"
