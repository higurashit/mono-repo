## はじめに

皆さん、こんにちは。

私は業務でデータ利活用基盤を取り扱っているため、[dbt](https://www.getdbt.com/)や[Iceberg](https://iceberg.apache.org/)、そして[AWS GenU](https://aws-samples.github.io/generative-ai-use-cases-jp/)に取り組む必要があると考えています。特に AWS Japan Top Engineer として、[GenU](https://aws-samples.github.io/generative-ai-use-cases-jp/)を扱い、その活用を広めることが責務だと感じています。

しかし、私はこれまで CloudFormation を好んで使っており、（逆張り思考も重なって）Cfn テンプレートをシンプルかつ汎用性・拡張性の高い形で作ることに注力してきました。そのため、改めて[GenU の CDK コード](https://github.com/aws-samples/generative-ai-use-cases-jp/tree/main/packages/cdk)を読もうとしても、なかなか理解が進みませんでした。

そこで、CDK を学びながら、その過程を記事としてまとめることにしました。

## CDK の概要

[AWS Cloud Development Kit（CDK）](https://aws.amazon.com/jp/cdk/)は、CloudFormation 同様、AWS のインフラをプログラムで定義できるツールです。従来の CloudFormation との違いは、CDK は TypeScript や Python などの一般的なプログラミング言語で記述できることです。

プログラミング言語で記述できるため、コードの再利用や構造化がしやすくなり、インフラの管理が CloudFormation よりも効率化されます。
私は、便利である一方で、**リファクタリングの機会が少ないインフラストラクチャにおいて、可読性の低いソースコードが生成された場合の不が大きい**と考えていました。

まあそれは CloudFormation でも同じことが言えますし、CloudFormation で環境依存を取り扱う際の Mapping の煩雑さ、条件分岐の煩雑さが取り除かれるというメリットから、これからはどんどん CDK を使っていこうと思います。

## AWS CDK のセットアップ

AWS CDK を使用するには、まず開発環境をセットアップする必要があります。GenU では Typescript を使用しているようなので、この記事では TypeScript を使用します。

### 前提条件

CDK を利用するために、[このページに記載の環境](https://docs.aws.amazon.com/ja_jp/cdk/v2/guide/prerequisites.html)が必要です。

- AWS アカウント
- AWS CLI
- Node.js（14.15.0 以上。2025/3/10 時点の[最新の LTS 版](https://nodejs.org/en/download/)は v22.14.0 です。）
- npm または yarn（ここでは npm を使います）

事前に AWS CLI をセットアップし、`aws configure` を実行して認証情報を設定しておくことを推奨します。

### CDK のインストール

まず、nodejs, npm が古かったので整えます。
nodejs は [Nodist](https://github.com/nodists/nodist) でインストールしていますが、お好きな方法で LTS 版にしてあげてください。

```bash:node最新化
nodist dist | grep 22.14
nodist + 22.14.0
nodist 22.14.0
node -v # v22.14.0
npm -v # 10.2.3
```

```bat:aws-cli最新化 (コマンドプロンプトで実行)
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
```

```bash
aws --version # aws-cli/2.24.20 Python/3.12.9 Windows/10 exe/AMD64
```

AWS CDK をインストールします。

```bash
npm install -g aws-cdk
cdk --version # 2.1003.0
```

### プロジェクトの作成

新しい TypeScript プロジェクトを作成します。

```bash
mkdir cdk_tutorial && cd cdk_tutorial
cdk init app --language typescript
```

このようなファイルセットが作成されました。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/217144/53268a51-5d33-4922-957b-2c3d41f11445.png)

次に依存パッケージをインストールします。

```bash
npm i
```

### CDK の動作確認

npm コマンドで動作確認をしていきます。

```bash
cat package.json # npm scrpts を確認
npm run test # PASS test/cdk_tutorial.test.ts
npm run cdk synth
```

```yaml
Resources:
  CDKMetadata:
    Type: AWS::CDK::Metadata
    Properties:
      Analytics: v2:deflate64:H4sIAAAAAAAA/zPSM7Qw1DNUTCwv1k1OydbNyUzSCy5JTM7WyctPSdXLKtYvMzLSMzTRM1DMKs7M1C0qzSvJzE3VC4LQAL6qgsE/AAAA
    Metadata:
      aws:cdk:path: CDKTutorialStack/CDKMetadata/Default
    Condition: CDKMetadataAvailable
Conditions:
  CDKMetadataAvailable:
    Fn::Or:
      - Fn::Or:
          - Fn::Equals:
              - Ref: AWS::Region
              - af-south-1
          - Fn::Equals:
              - Ref: AWS::Region
              - ap-east-1
          - Fn::Equals:
              - Ref: AWS::Region
              - ap-northeast-1
          - Fn::Equals:
              - Ref: AWS::Region
              - ap-northeast-2
          - Fn::Equals:
              - Ref: AWS::Region
              - ap-northeast-3
          - Fn::Equals:
              - Ref: AWS::Region
              - ap-south-1
          - Fn::Equals:
              - Ref: AWS::Region
              - ap-south-2
          - Fn::Equals:
              - Ref: AWS::Region
              - ap-southeast-1
          - Fn::Equals:
              - Ref: AWS::Region
              - ap-southeast-2
          - Fn::Equals:
              - Ref: AWS::Region
              - ap-southeast-3
      - Fn::Or:
          - Fn::Equals:
              - Ref: AWS::Region
              - ap-southeast-4
          - Fn::Equals:
              - Ref: AWS::Region
              - ca-central-1
          - Fn::Equals:
              - Ref: AWS::Region
              - ca-west-1
          - Fn::Equals:
              - Ref: AWS::Region
              - cn-north-1
          - Fn::Equals:
              - Ref: AWS::Region
              - cn-northwest-1
          - Fn::Equals:
              - Ref: AWS::Region
              - eu-central-1
          - Fn::Equals:
              - Ref: AWS::Region
              - eu-central-2
          - Fn::Equals:
              - Ref: AWS::Region
              - eu-north-1
          - Fn::Equals:
              - Ref: AWS::Region
              - eu-south-1
          - Fn::Equals:
              - Ref: AWS::Region
              - eu-south-2
      - Fn::Or:
          - Fn::Equals:
              - Ref: AWS::Region
              - eu-west-1
          - Fn::Equals:
              - Ref: AWS::Region
              - eu-west-2
          - Fn::Equals:
              - Ref: AWS::Region
              - eu-west-3
          - Fn::Equals:
              - Ref: AWS::Region
              - il-central-1
          - Fn::Equals:
              - Ref: AWS::Region
              - me-central-1
          - Fn::Equals:
              - Ref: AWS::Region
              - me-south-1
          - Fn::Equals:
              - Ref: AWS::Region
              - sa-east-1
          - Fn::Equals:
              - Ref: AWS::Region
              - us-east-1
          - Fn::Equals:
              - Ref: AWS::Region
              - us-east-2
          - Fn::Equals:
              - Ref: AWS::Region
              - us-west-1
      - Fn::Equals:
          - Ref: AWS::Region
          - us-west-2
Parameters:
  BootstrapVersion:
    Type: AWS::SSM::Parameter::Value<String>
    Default: /cdk-bootstrap/hnb659fds/version
    Description: Version of the CDK Bootstrap resources in this environment, automatically retrieved from SSM Parameter Store.
```

ただし、以下の Notice メッセージが出力されます。

```bash
NOTICES         (What's this? https://github.com/aws/aws-cdk/wiki/CLI-Notices)

32775   (cli): CLI versions and CDK library versions have diverged

        Overview: Starting in CDK 2.179.0, CLI versions will no longer be in
                  lockstep with CDK library versions. CLI versions will now be
                  released as 2.1000.0 and continue with 2.1001.0, etc.

        Affected versions: cli: >=2.0.0 <=2.1005.0

        More information at: https://github.com/aws/aws-cdk/issues/32775
```

どうやら cdk のバージョンが>=2.0.0 <=2.1005.0 に収まっており、ライブラリのバージョンと分岐するという注意が載っているようです。

[この記事](https://aws.amazon.com/jp/blogs/opensource/aws-cdk-is-splitting-construct-library-and-cli/)を見ると、このままで大丈夫そうなので、放置します。
※以下のように[バージョンを揃えて構築する手順](https://github.com/aws/aws-cdk/issues/32775)になっている場合は修正が必要のようです。

```bash
# This no longer works, there will be two different versions
$ CDK_VERSION=2.714.0
$ npm install aws-cdk-lib@$CDK_VERSION
$ npm install aws-cdk@$CDK_VERSION

# Do this instead (install the latest 2.x)
$ npm install aws-cdk@^2
```

ということで、CDK の環境構築が完了しました。
