# 🚀 CloudFormation Templete!
## 事前準備（ドキュメント）
- gitbashのインストール
- Pythonのインストール
- Graphvizのインストール
- diagramsのインストール

## 事前準備（LambdaをNodeで記述する場合）
- nodeのインストール

## その他
- aws-cliの導入
- https://dev.classmethod.jp/articles/developing-cloudformation-ci-cd-pipeline-with-github-codebuild-codepipeline/

## フォルダ構成
- documents：設計書フォルダ
  - diagramsコマンドでシステム構成図を出力する
- pipline：サービスのCI/CDパイプライン用フォルダ
  - create_pipeline.yaml：CI/CDパイプラインを構築するためのCloudFormationテンプレート
  - buildspec.yaml：CI/CDパイプラインのbuild時に実行するコマンド
- src：ソースフォルダ
  - cfn.yaml：CI/CDパイプライン上でパッケージ対象となるメインテンプレート
  - templetes：cfn.yamlから呼び出されるテンプレート部品フォルダ
  - codes：Lambdaなどのソースファイルを格納するフォルダ（以下が利用可能）
 |  Type  |  Property  |  Zip  |
 | ----   | ----       | ----  |
 |  AWS::Serverless::Function  |  CodeUri  |  true  |
 |  AWS::Serverless::Api | DefinitionUri  |  false  |
 |  AWS::ApiGateway::RestApi | BodyS3Location | false |
 |  AWS::Lambda::Function | Code | true |
 |  AWS::ElasticBeanstalk::ApplicationVersion | SourceBundle | true |
 |  AWS::CloudFormation::Stack | TemplateURL | false |

## 開発の仕方
| #  | 工程 | 手順 | AWSサービスの状態 |
| -  | - | -   | - |
| 1  | 事前準備（初回） | サービスの型を取得しサービス名などを記載 | - |
| 2  | - | AWSコンソールにログイン | - |
| 3  | - | サービス用Gitリポジトリを作成し、以下のブランチを作成<br>・master ※本番<br>　└staging ※検証<br>　　└develop ※結合<br>　　　└release ※リリース用 | +CodeCommit |
| 4  | - | CloudFormationでcreate_pipeline.yamlをdevで実行<br>（以降、developへのpush都度）dev環境へのデプロイが自動実行 | +CodePipeline<br>+CodeBuild<br>+CodeDeploy<br>+yamlに記述したAWSサービス群 |
| 5  | 製造/単体 | 個人用のfeatureブランチを作成 | - |
| 6  | - | AWSサービスのパラメータは、src/templatesフォルダ配下を修正 | - |
| 7  | - | Lambdaなどのコードは、src/codesフォルダ配下を修正 | - |
| 8  | - | 単体テストを実施（できれば自動テスト） | - |
| 9  | - | 単体テストが終わったコードをreleaseブランチにマージ | - |
| 10 | 結合試験 | developブランチにreleaseブランチをマージ | - |
| 11 | - | 結合試験を実施 | - |
| 12 | 受入試験 | CloudFormationでcreate_pipeline.yamlをstgで実行<br>（以降、stagingへのpush都度）stg環境へのデプロイが自動実行 | +CodePipeline<br>+CodeBuild<br>+CodeDeploy<br>+yamlに記述したAWSサービス群 |
| 13 | - | stagingブランチにreleaseブランチをマージ | - |
| 14 | 本番リリース | CloudFormationでcreate_pipeline.yamlをprodで実行<br>（以降、masterへのpush都度）prod環境へのデプロイが自動実行 | +CodePipeline<br>+CodeBuild<br>+CodeDeploy<br>+yamlに記述したAWSサービス群 |
| 15 | - | masterブランチにreleaseブランチをマージ | - |
