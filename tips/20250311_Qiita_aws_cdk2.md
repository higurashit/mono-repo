## はじめに

皆さん、こんにちは。

私は業務でデータ利活用基盤を取り扱っていること、2024 AWS Japan Top Engineer に選出されたということから、[AWS GenU](https://aws-samples.github.io/generative-ai-use-cases-jp/) およびそれに必要なデータ基盤の探求 ([Snowflake](https://www.snowflake.com/ja/), [dbt](https://www.getdbt.com/), [Iceberg](https://iceberg.apache.org/), etc) に取り組む必要があると考えています。

本投稿では、[GenU のバックエンドである CDK コード](https://github.com/aws-samples/generative-ai-use-cases-jp/tree/main/packages/cdk)を詳細に解説します。
自身そして閲覧して頂いた皆様の GenU への理解が少しでも深まり、生成 AI の民主化につながっていければと考えています。

## 前回までのおさらい

前回までで、以下が完了しました。

- [①AWS CDK のセットアップ](https://qiita.com/siruko/items/fd25fdcf89615cb85262)

今回は CDK の動作確認をしたいと思います。

### CDK の記法（レイヤー）について

CDK には[レイヤー](https://docs.aws.amazon.com/ja_jp/prescriptive-guidance/latest/aws-cdk-layers/introduction.html)という概念があります。

- [L1](https://docs.aws.amazon.com/ja_jp/prescriptive-guidance/latest/aws-cdk-layers/layer-1.html)は CloudFormation 相当の記述です。
- [L2](https://docs.aws.amazon.com/ja_jp/prescriptive-guidance/latest/aws-cdk-layers/layer-2.html)は L1 から CloudFormation 構文の共通的な記載を排除し、よりユーザライクでわかりやすい記述となります。[最も広く使用されているレイヤータイプ](https://docs.aws.amazon.com/cdk/v2/guide/constructs.html#constructs_lib_levels)とのことです。
- [L3](https://docs.aws.amazon.com/ja_jp/prescriptive-guidance/latest/aws-cdk-layers/layer-3.html)は特定のユースケースに即した、複数の AWS リソースを構築する記法と読み取りました。

### 動作確認用 CDK ファイルの定義

以下は L2 での S3 バケット作成の記載例です。
`lib/cdk_tutorial-stack.ts` に、以下のように S3 バケットを定義します。

```typescript: lib/cdk_tutorial-stack.ts
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

export class CdkTutorialStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const accountId = cdk.Stack.of(this).account; // AWSアカウントID

    new s3.Bucket(this, 'MyBucket', {
      bucketName: `my-cdk-app-bucket-${accountId}`,
      versioned: true, // バージョニングを有効化
      removalPolicy: cdk.RemovalPolicy.DESTROY, // スタック削除時にバケットを削除
      autoDeleteObjects: true, // バケット削除時に中身を削除
    });
  }
}
```

### CDK の動作確認

バケットを AWS にデプロイするには、以下のコマンドを実行します。

```bash
cdk synth # or npm run cdk synth
cdk deploy # or npm run cdk deploy
```

`cdk deploy` でエラーが発生しました。

:::note alert
current credentials could not be used to assume 'arn:aws:iam::xxxxxxxxxxxx:role/cdk-hnb659fds-deploy-role-xxxxxxxxxxxx-ap-northeast-1', but are for the right account. Proceeding anyway.
:::

[AWS CDK のブートストラップ](https://docs.aws.amazon.com/ja_jp/cdk/v2/guide/bootstrapping-env.html)ができていなかったようです。

```bash
aws cloudformation list-stacks --query "StackSummaries[?StackName=='CDKToolkit']" # 空
cdk bootstrap aws://[AWSアカウントID]/ap-northeast-1
```

CDKToolkit スタックが作成されました。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/217144/4bfd3e12-6e2a-442c-ab52-51cfe65f6225.png)

再度`cdk deploy` を行ったところ、AWS アカウント ID が取得できていないというエラーが発生しました。
env を明示的に指定します。

```typescript:bin/cdk_tutorial.ts
#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { CdkTutorialStack } from '../lib/cdk_tutorial-stack';

const app = new cdk.App();
new CdkTutorialStack(app, 'CdkTutorialStack', {
  /* If you don't specify 'env', this stack will be environment-agnostic.
   * Account/Region-dependent features and context lookups will not work,
   * but a single synthesized template can be deployed anywhere. */
  /* Uncomment the next line to specialize this stack for the AWS Account
   * and Region that are implied by the current CLI configuration. */
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
  /* Uncomment the next line if you know exactly what Account and Region you
   * want to deploy the stack to. */
  // env: { account: '123456789012', region: 'us-east-1' },
  /* For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html */
});
```

再度`cdk deploy` を行ったところ、エラーが解消しました。
無事に CdkTutorialStack が作成されています。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/217144/067fde07-c73c-4bf6-a0e8-905874fd77ba.png)

```bash
aws s3 ls | grep my-cdk-app-bucket # my-cdk-app-bucket-${accountId}
```

これにて動作確認は終了です。
次回からはいよいよ GenU の解説に入っていきます。

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
