!Sub {{resolve:ssm:${ServiceName}WebSiteBaseDomain:1}}

# [Done] S3 + Cloudfront + Lambda@edge
# Cloudfront + API Gateway + SNS + SQS + Lambda
# Lambda
# Lambda + IAM(access S3)
# CodePipeline
# CodePipeline + S3 + Cloudfront + Lambda@edge
# SNS + SQS
# SNS + SQS + Lambda

https://dev.classmethod.jp/articles/net307-customizing-lambda-edge-sam/

Conditions
https://qiita.com/yasuhiroki/items/8463eed1c78123313a6f

Shell Script
https://qiita.com/zayarwinttun/items/0dae4cb66d8f4bd2a337


開発の仕方
  サービス単位で必要なファイルをコピーして、開発用のGitリポジトリを作成
    アプリT領域（メインのサービス群）
    インフラT領域（DNS、証明書、監視運用など）
    でフォルダを分ける（後でなんか言われたときに分けられるようにする。RSならインフラとセキュリティ両方入れちゃってOK）
  アプリ領域はそれぞれローカルで単体開発 → dev(結合環境) → stg(検証環境) → prod(本番環境)
    Lambda
      ローカルで動作確認（Inputをモックにする＋テスト駆動）
      aws cloudformation packageでリリース（環境を指定）
    静的
      ローカルで動作確認（npmでローカルhttpsサーバ立ち上げ可能）
      S3: aws s3 sync ${SC_DIR}/ s3://${BUCKETNAME}/　でリリース（環境を指定するスクリプトをnpmで作る）
      もしくはCodeCommit
    ビルドS3:
      ローカルで動作確認（create react appなら標準搭載）
      ローカルビルドは怪しいので、CodePipelineでリリース（ブランチによって変える）
      CloudFormationにCodePipelineも含める

・やっておきたいこと
  [Done] AWS-CLIでのCloudformation利用
  [Done] Bsys構成でのGitリポジトリ作成
  データベース選択
    動的に処理して計算する場合、RDBが良さげだけど料金的にDynamoDB
    S3→Athena→DynamoDBをバッチ処理にする？？
  ドメイン設計
    サービス単位でサブドメインを分けるべき
    ・LP
      S3 + static html
    ・派遣依頼
      CF + S3 + webframework
         + API Gateway + SNS + SQS
    ・単金、人数取得API
    ・
