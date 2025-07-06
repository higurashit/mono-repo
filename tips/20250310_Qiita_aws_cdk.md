## はじめに

皆さん、こんにちは。

私は業務でデータ利活用基盤を取り扱っていること、2024 AWS Japan Top Engineer に選出されたということから、[AWS GenU](https://aws-samples.github.io/generative-ai-use-cases-jp/) およびそれに必要なデータ基盤の探求 ([Snowflake](https://www.snowflake.com/ja/), [dbt](https://www.getdbt.com/), [Iceberg](https://iceberg.apache.org/), etc) に取り組む必要があると考えています。

本投稿では、[GenU のバックエンドである CDK コード](https://github.com/aws-samples/generative-ai-use-cases-jp/tree/main/packages/cdk)を詳細に解説します。
自身そして閲覧して頂いた皆様の GenU への理解が少しでも深まり、生成 AI の民主化につながっていければと考えています。

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
次回は CDK の動作確認を行いたいと思います。

## (参考) GenU のバックエンド (CDK) 詳細解説投稿一覧

- [①AWS CDK のセットアップ](https://qiita.com/siruko/items/fd25fdcf89615cb85262)
- [②AWS CDK の動作確認](https://qiita.com/siruko/items/73169f986b4173e3d3a5)
- [③GenU の概要](https://qiita.com/siruko/items/625801b9e1847b305c1e)
- [④GenU CDK スタックの概要](https://qiita.com/siruko/items/8570ed43f7162ea4b907)
- [⑤CloudFrontWafStack スタックの解説](https://qiita.com/siruko/items/30439576ee7c63165d21)
- [⑥RagKnowledgeBaseStack スタックの解説](https://qiita.com/siruko/items/1223c9d22e73168a8809)
- [⑦WebSearchAgentStack スタックの解説](https://qiita.com/siruko/items/aef0a9599df60d47eb1e)
- [⑧GuardrailStack スタックの解説](https://qiita.com/siruko/items/d16e9fe27df4673d7554)
- [⑨GenerativeAiUseCasesStack > Auth スタックの解説](https://qiita.com/siruko/items/0c14040a1af132f42382)
- [⑩GenerativeAiUseCasesStack > Database, Api スタックの解説](https://qiita.com/siruko/items/5f249f11847f3829c18a)
- [⑪GenerativeAiUseCasesStack > CommonWebAcl, Web, Rag スタックの解説](https://qiita.com/siruko/items/1063daa2efe0b374a3fc)
- [⑫GenerativeAiUseCasesStack > RagKnowledgeBase, UseCaseBuilder, Transcribe スタックの解説](https://qiita.com/siruko/items/73d6006004caf8648594)
- [⑬DashBoard スタックの解説](https://qiita.com/siruko/items/73a75c7d0146d12ecbc3)
- [⑭GenU の Outputs の解説](https://qiita.com/siruko/items/afc14128a5b1a15ab69c)
