from diagrams import Cluster, Diagram

# AWS resources search for https://diagrams.mingrammer.com/docs/nodes/aws

## samples: Static Web Service
from diagrams.onprem.client import Users
from diagrams.onprem.network import Internet
from diagrams.aws.security import WAF, ACM
from diagrams.aws.network import CF
from diagrams.aws.compute import Lambda
from diagrams.aws.storage import S3
from diagrams.aws.devtools import Codepipeline, Codecommit, Codebuild, Codedeploy

with Diagram('Web Service Name'):
    users = Users('End Users')
    devs = Users('Developers')
    internet = Internet('Internet')

    with Cluster('AWS: in /src/***.yaml'):
        with Cluster('WAF Rules'):
            waf = [WAF('WAF: rules\n同一IPからの連続アクセス遮断'), WAF('WAF: rules\nIP制限（検証環境のみ）')]

        cf = CF('CloudFront\nキャッシュサーバ')

        with Cluster('Lambda@Edge Origin Request'):
            lmd = Lambda('Lambda\nS3 ディレクトリアクセス')

        s3 = S3('S3\n静的コンテンツ置き場')
        acm = ACM('ACM\nSSL証明書')

        with Cluster('CodePipeline: git pushをトリガーにパイプライン処理'):
            codecm = Codecommit('CodeCommit\nGitリポジトリ')
            codebl = Codebuild('CodeBuild\nソースコード取得')
            codedp = Codedeploy('CodeDeploy\nS3に配置')

    users >> internet >> waf >> cf >> lmd >> s3
    devs >> codecm >> codebl >> codedp >> s3
    acm - cf
