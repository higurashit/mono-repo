## はじめに

皆さん、こんにちは。

私は業務でデータ利活用基盤を取り扱っているため、[dbt](https://www.getdbt.com/)や[Iceberg](https://iceberg.apache.org/)、そして[AWS GenU](https://aws-samples.github.io/generative-ai-use-cases-jp/)に取り組む必要があると考えています。特に AWS Japan Top Engineer として、[GenU](https://aws-samples.github.io/generative-ai-use-cases-jp/)を扱い、その活用を広めることが責務だと感じています。

しかし、私はこれまで CloudFormation を好んで使っており、（逆張り思考も重なって）Cfn テンプレートをシンプルかつ汎用性・拡張性の高い形で作ることに注力してきました。そのため、改めて[GenU の CDK コード](https://github.com/aws-samples/generative-ai-use-cases-jp/tree/main/packages/cdk)を読もうとしても、なかなか理解が進みませんでした。

そこで、CDK を学びながら、その過程を記事としてまとめることにしました。

## Cdk の概要

[AWS Cloud Development Kit（CDK）](https://aws.amazon.com/jp/cdk/)は、CloudFormation 同様、AWS のインフラをプログラムで定義できるツールです。従来の CloudFormation との違いは、CDK は TypeScript や Python などの一般的なプログラミング言語で記述できることです。

プログラミング言語で記述できるため、コードの再利用や構造化がしやすくなり、インフラの管理が CloudFormation よりも効率化されます。
私は、便利である一方で、**リファクタリングの機会が少ないインフラストラクチャにおいて、可読性の低いソースコードが生成された場合の不が大きい**と考えていました。

まあそれは CloudFormation でも同じことが言えますし、CloudFormation で環境依存を取り扱う際の Mapping の煩雑さ、条件分岐の煩雑さが取り除かれるというメリットから、これからはどんどん Cdk を使っていこうと思います。

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

CDK が正しく動作するか確認するために、以下のコマンドを実行し、CloudFormation のテンプレートが正しく生成されることを確認します。

```bash
cdk synth
```

問題なく実行されると、生成された CloudFormation のテンプレートが出力されます。

これで AWS CDK のセットアップが完了しました。次は、実際に AWS リソースを定義し、デプロイする方法を解説します。
