# sam local invokeを実行するまでの手順

## step of test in local (only first)
- `git clone https://github.com/pyenv-win/pyenv-win.git "$HOME/.pyenv"`
- `pyenv install 3.12.8`
- `pyenv global 3.12.8`
- PowerShellで以下を実行（もしくは環境変数に追加）
  - [System.Environment]::SetEnvironmentVariable('PYENV',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")
  - [System.Environment]::SetEnvironmentVariable('PYENV_HOME',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")
- VSCODEの拡張機能「python」をインストール
- [SAM-CLI](https://docs.aws.amazon.com/ja_jp/serverless-application-model/latest/developerguide/install-sam-cli.html)をインストール
- `cd mono-repo/services/migration_tool/`
- `python -m venv venv`
- VSCodeコマンドの「Python: Select InterPreter」からvenv環境を選択
- 新しいターミナルを開く（sourceコマンドでactivateされることを確認）
- `cd mono-repo/services/migration_tool/`
- `pip install -r layer/MigrationHandler/requirements.txt`
- `pip install boto3`
- boto3実行用にAWSコンソールからアクセスキー、シークレットキーを発行
- `aws configure`
- アクセスキー、シークレットキー、リージョンを入力

## step of test in local (only first of day)
- VSCodeコマンドの「Python: Select InterPreter」からvenv環境を選択
- 新しいターミナルを開く（sourceコマンドでactivateされることを確認）
- `cd mono-repo/services/migration_tool/iac`

## step of test in local (by modify)
- `sam build`
- `sam local invoke MGF1LambdaFunction --parameter-overrides "Env=local"`
- `sam local invoke MGF2LambdaFunction --parameter-overrides "Env=local" --event ../tests/unit/event/event_f2_ok_001.json`

## 問題点
遅い