import boto3
import os
import sys

s3 = boto3.client('s3', region_name='ap-northeast-1')

def upload_file_to_s3():
    # スクリプトファイルの場所までcd
    cd_pwd()

    # ローカルデータをS3にアップロード
    bucket_name = 'siruko-cloudformation-templetes'
    local_data_path = './data/'
    s3_data_path = 'migration-tool/unittest/'

    local_file_names = ['移行定義FMT.xlsx', '001-01_Bmaster.csv', '001-02_Cmaster.csv']
    for file_name in local_file_names:
        file_path = f"{local_data_path}{file_name}"
        object_path = f"{s3_data_path}{file_name}"
        s3.upload_file(file_path, bucket_name, object_path)
        print(f"File {file_path} uploaded to {bucket_name}/{object_path}.")

def cd_pwd():
    # スクリプトの絶対パスを取得
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    # カレントディレクトリをスクリプトのディレクトリに変更
    os.chdir(script_dir)

if __name__ == '__main__':
    upload_file_to_s3()
