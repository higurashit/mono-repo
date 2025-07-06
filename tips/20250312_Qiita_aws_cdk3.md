## はじめに

皆さん、こんにちは。

私は業務でデータ利活用基盤を取り扱っていること、2024 AWS Japan Top Engineer に選出されたということから、[AWS GenU](https://aws-samples.github.io/generative-ai-use-cases-jp/) およびそれに必要なデータ基盤の探求 ([Snowflake](https://www.snowflake.com/ja/), [dbt](https://www.getdbt.com/), [Iceberg](https://iceberg.apache.org/), etc) に取り組む必要があると考えています。

本投稿では、[GenU のバックエンドである CDK コード](https://github.com/aws-samples/generative-ai-use-cases-jp/tree/main/packages/cdk)を詳細に解説します。
自身そして閲覧して頂いた皆様の GenU への理解が少しでも深まり、生成 AI の民主化につながっていければと考えています。

## 前回までのおさらい

前回までで、以下が完了しました。

- [①AWS CDK のセットアップ](https://qiita.com/siruko/items/fd25fdcf89615cb85262)
- [②AWS CDK の動作確認](https://qiita.com/siruko/items/73169f986b4173e3d3a5)

今回は GenU の概要を解説したいと思います。

## GenU 活用パターン集

まずは[ドキュメント](https://aws-samples.github.io/generative-ai-use-cases-jp/ABOUT.html)を読んでいきます。
GenU では、以下の機能やオプションが活用パターンごとに紹介されています。

- 生成 AI のユースケースを体験したい
- RAG がしたい
- 独自に作成した AI エージェントや Bedrock Flows などを **社内で利用したい**
- 独自のユースケースを **作成したい**

後述しますが、RAG は料金がかかるため、後ほどじっくりと検討したいと思います。後ろの 2 つは試験的というよりかは実務的なユースケースのようです。
ということで、まずは **「生成 AI のユースケースを体験したい」** から始めていきます。

## GenU の料金について

GenU は OSS のため、GenU 自体の利用には料金はかかりません。  
しかし、GenU を利用すると、バックエンドで動作する AWS リソースの料金が発生します。

[料金試算のページ](https://aws-samples.github.io/generative-ai-use-cases-jp/ABOUT.html#%E6%96%99%E9%87%91%E8%A9%A6%E7%AE%97)を確認すると、以下のようになっています。

### [シンプル版（RAG なし）](https://aws.amazon.com/jp/cdp/ai-chatbot/): 約 $40/月

すべて従量課金制で、そのうち $33 は Bedrock の Claude 3 Sonnet の出力トークンになります。
**つまり、頻繁に利用しなければほとんど料金がかからない！** といえます。
やはりマネージドサービス（サーバレス）は素晴らしいですね。

### [RAG（Amazon Kendra）あり](https://aws.amazon.com/jp/cdp/ai-chatapp/): 約 $940/月

Amazon Kendra が時間課金制であり、1 ヶ月（730 時間）フル稼働すると **$821** となります。  
これは全体コストの **87%** を占めており、かなり高額です。  
Amazon Kendra の料金は高いため、試しに使うにはハードルが高いですね。

### [RAG（Knowledge Base）あり](https://aws.amazon.com/jp/cdp/genai-chat-app/): 約 $285/月

Knowledge Base 用ベクトルデータストアとしての OpenSearch Serverless 残すとが **$175** です。
「サーバレス」と名がついているものの、意外と高めの料金設定ですね。  
Aurora Serverless なら、もう少し安くなるかもしれません。

### 料金の総論

RAG のコストは高額で、それ以外の構成はおおよそ $100 以内に収まっています。  
RAG は企業の競争優位性を高める要素であり、同時にデータベースのコストが高いことを反映した価格設定になっているように思えます。

## GenU のデプロイ

### GitHub からの clone

いよいよデプロイです。ここで CDK を使います。
まず、clone します。

```bash
cd /path/to/workdir
git clone https://github.com/aws-samples/generative-ai-use-cases-jp
```

### モデルの有効化

以下の注意書きにある通り、**cdk.json に記載されているモデルを有効化** する必要があります。

:::note warn
/packages/cdk/cdk.json に記載されている modelRegion リージョンの modelIds (テキスト生成) 及び imageGenerationModelIds (画像生成) を有効化してください。([Amazon Bedrock の Model access 画面: us-east-1](https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess))
:::

```diff_json: packages/cdk/cdk.json
{
  "app": "npx ts-node --prefer-ts-exts bin/generative-ai-use-cases.ts",
  "watch": {
    "include": [
      "**"
    ],
    "exclude": [
      "README.md",
      "cdk*.json",
      "**/*.d.ts",
      "**/*.js",
      "tsconfig.json",
      "package*.json",
      "yarn.lock",
      "node_modules",
      "test"
    ]
  },
  "context": {
    "env": "",
    "ragEnabled": false,
    "kendraIndexArn": null,
    "kendraDataSourceBucketName": null,
    "kendraIndexScheduleEnabled": false,
    "kendraIndexScheduleCreateCron": null,
    "kendraIndexScheduleDeleteCron": null,
    "ragKnowledgeBaseEnabled": false,
    "ragKnowledgeBaseId": null,
    "ragKnowledgeBaseStandbyReplicas": false,
    "ragKnowledgeBaseAdvancedParsing": false,
    "ragKnowledgeBaseAdvancedParsingModelId": "anthropic.claude-3-sonnet-20240229-v1:0",
    "embeddingModelId": "amazon.titan-embed-text-v2:0",
    "rerankingModelId": null,
    "queryDecompositionEnabled": false,
    "selfSignUpEnabled": true,
    "allowedSignUpEmailDomains": null,
    "samlAuthEnabled": false,
    "samlCognitoDomainName": "",
    "samlCognitoFederatedIdentityProviderName": "",
    "hiddenUseCases": {},
+   "modelRegion": "us-east-1",
+   "modelIds": [
+     "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
+     "us.anthropic.claude-3-5-haiku-20241022-v1:0",
+     "us.amazon.nova-pro-v1:0",
+     "us.amazon.nova-lite-v1:0",
+     "us.amazon.nova-micro-v1:0"
+   ],
    "imageGenerationModelIds": [
      "amazon.nova-canvas-v1:0"
    ],
    "endpointNames": [],
    "agentEnabled": false,
    "searchAgentEnabled": false,
    "searchApiKey": "",
    "agents": [],
    "inlineAgents": false,
    "flows": [],
    "allowedIpV4AddressRanges": null,
    "allowedIpV6AddressRanges": null,
    "allowedCountryCodes": null,
    "hostName": null,
    "domainName": null,
    "hostedZoneId": null,
    "dashboard": false,
    "anonymousUsageTracking": true,
    "guardrailEnabled": false,
    "crossAccountBedrockRoleArn": "",
    "useCaseBuilderEnabled": true,
    "@aws-cdk/aws-lambda:recognizeLayerVersion": true,
    "@aws-cdk/core:checkSecretUsage": true,
    "@aws-cdk/core:target-partitions": [
      "aws",
      "aws-cn"
    ],
    "@aws-cdk-containers/ecs-service-extensions:enableDefaultLogDriver": true,
    "@aws-cdk/aws-ec2:uniqueImdsv2TemplateName": true,
    "@aws-cdk/aws-ecs:arnFormatIncludesClusterName": true,
    "@aws-cdk/aws-iam:minimizePolicies": true,
    "@aws-cdk/core:validateSnapshotRemovalPolicy": true,
    "@aws-cdk/aws-codepipeline:crossAccountKeyAliasStackSafeResourceName": true,
    "@aws-cdk/aws-s3:createDefaultLoggingPolicy": true,
    "@aws-cdk/aws-sns-subscriptions:restrictSqsDescryption": true,
    "@aws-cdk/aws-apigateway:disableCloudWatchRole": true,
    "@aws-cdk/core:enablePartitionLiterals": true,
    "@aws-cdk/aws-events:eventsTargetQueueSameAccount": true,
    "@aws-cdk/aws-iam:standardizedServicePrincipals": true,
    "@aws-cdk/aws-ecs:disableExplicitDeploymentControllerForCircuitBreaker": true,
    "@aws-cdk/aws-iam:importedRoleStackSafeDefaultPolicyName": true,
    "@aws-cdk/aws-s3:serverAccessLogsUseBucketPolicy": true,
    "@aws-cdk/aws-route53-patters:useCertificate": true,
    "@aws-cdk/customresources:installLatestAwsSdkDefault": false,
    "@aws-cdk/aws-rds:databaseProxyUniqueResourceName": true,
    "@aws-cdk/aws-codedeploy:removeAlarmsFromDeploymentGroup": true,
    "@aws-cdk/aws-apigateway:authorizerChangeDeploymentLogicalId": true,
    "@aws-cdk/aws-ec2:launchTemplateDefaultUserData": true,
    "@aws-cdk/aws-secretsmanager:useAttachedSecretResourcePolicyForSecretTargetAttachments": true,
    "@aws-cdk/aws-redshift:columnId": true,
    "@aws-cdk/aws-stepfunctions-tasks:enableEmrServicePolicyV2": true,
    "@aws-cdk/aws-ec2:restrictDefaultSecurityGroup": true,
    "@aws-cdk/aws-apigateway:requestValidatorUniqueId": true,
    "@aws-cdk/aws-kms:aliasNameRef": true,
    "@aws-cdk/aws-autoscaling:generateLaunchTemplateInsteadOfLaunchConfig": true,
    "@aws-cdk/core:includePrefixInUniqueNameGeneration": true,
    "@aws-cdk/aws-opensearchservice:enableOpensearchMultiAzWithStandby": true
  }
}
```

### デプロイオプション

続いて[デプロイオプション](https://aws-samples.github.io/generative-ai-use-cases-jp/ja/DEPLOY_OPTION.html)を解説します。

デプロイオプションは GenU の構築オプション設定であり、機能の有効化／無効化や、既存の生成 AI 基盤モデルを利用する場合にモデル ID を指定することができます。

環境依存でない場合は `packages/cdk/cdk.json` にパラメータを設定し、環境依存の場合は `packages/cdk/parameter.ts` の envs に記載されている環境ごとにパラメータを設定します。
例えば、`ragEnabled: true` を追記すると Amazon Kandra が作成されます。

デプロイオプションでは、この他にも[Agent チャットユースケースを有効化](https://aws-samples.github.io/generative-ai-use-cases-jp/ja/DEPLOY_OPTION.html#agent-%E3%83%81%E3%83%A3%E3%83%83%E3%83%88%E3%83%A6%E3%83%BC%E3%82%B9%E3%82%B1%E3%83%BC%E3%82%B9%E3%81%AE%E6%9C%89%E5%8A%B9%E5%8C%96) するオプションである`agentEnabled: true`などの説明が記載されています。
構築後に色々試すことにします。

```diff_typescript:packages/cdk/parameter.ts
import * as cdk from 'aws-cdk-lib';
import { StackInput, stackInputSchema } from './lib/stack-input';

// CDK Context からパラメータを取得する場合
const getContext = (app: cdk.App): StackInput => {
  const params = stackInputSchema.parse(app.node.getAllContext());
  return params;
};

// パラメータを直接定義する場合
const envs: Record<string, Partial<StackInput>> = {
  // 必要に応じて以下をカスタマイズ
  // paramter.ts で無名環境を定義したい場合は以下をアンコメントすると cdk.json の内容が無視され、parameter.ts がより優先されます。
  // '': {
  //   // 無名環境のパラメータ
  //   // デフォルト設定を上書きしたいものは以下に追記
  // },
+ dev: {
+   // 開発環境のパラメータ
+ },
  staging: {
    // ステージング環境のパラメータ
  },
  prod: {
    // 本番環境のパラメータ
  },
  // 他環境も必要に応じてカスタマイズ
};

// 後方互換性のため、CDK Context > parameter.ts の順でパラメータを取得する
export const getParams = (app: cdk.App): StackInput => {
  // デフォルトでは CDK Context からパラメータを取得する
  let params = getContext(app);

  // env が envs で定義したものにマッチ場合は、envs のパラメータを context よりも優先して使用する
  if (envs[params.env]) {
    params = stackInputSchema.parse({
      ...envs[params.env],
      env: params.env,
    });
  }

  return params;
};
```

### デプロイの実行

ここまで確認したら、手順に従ってデプロイします。
デプロイにはおよそ 20 分かかるそうです。

```bash
npm run cdk:deploy
```

実際に実行されるコマンドは以下の通りです。

```bash
npm -w packages/cdk run cdk deploy -- --all
```

```diff_json: package.json
{
  "name": "generative-ai-use-cases-jp",
  "private": true,
  "version": "3.0.0",
  "scripts": {
    "lint": "run-s root:lint web:lint cdk:lint",
    "test": "run-s web:test",
    "root:lint": "npx prettier --write .",
    "web:devw": "source ./setup-env.sh ${npm_config_env} && VITE_APP_VERSION=${npm_package_version} npm -w packages/web run dev",
    "web:devww": "powershell ./web_devw_win.ps1",
    "web:dev": "VITE_APP_VERSION=${npm_package_version} npm -w packages/web run dev",
    "web:build": "VITE_APP_VERSION=${npm_package_version} npm -w packages/web run build --",
    "web:build:analyze": "VITE_APP_VERSION=${npm_package_version} npm -w packages/web run build -- --mode analyze",
    "web:lint": "npm -w packages/web run lint",
    "web:test": "npm -w packages/web run test",
+   "cdk:deploy": "npm -w packages/cdk run cdk deploy -- --all",
    "cdk:deploy:quick": "npm -w packages/cdk run cdk deploy -- --all --asset-parallelism --asset-prebuild=false --concurrency 3 --method=direct --require-approval never --force",
    "cdk:deploy:quick:hotswap": "npm -w packages/cdk run cdk deploy -- --all --asset-parallelism --asset-prebuild=false --concurrency 3 --method=direct --require-approval never --force --hotswap",
    "cdk:destroy": "npm -w packages/cdk run cdk destroy --",
    "cdk:lint": "npm -w packages/cdk run lint",
    "cdk:test": "npm -w packages/cdk run test",
    "cdk:test:update-snapshot": "npm -w packages/cdk run test -- --update-snapshot",
    "extension:ci": "cd browser-extension && npm ci",
    "extension:dev": "cd browser-extension && npm run dev",
    "extension:devw": "source ./setup-env.sh && cd browser-extension && npm run dev",
    "extension:build": "cd browser-extension && npm run build",
    "extension:buildw": "source ./setup-env.sh && cd browser-extension && npm run build",
    "extension:lint": "npx prettier --write browser-extension/. && cd browser-extension && npm run lint",
    "docs:dev": "mkdocs serve",
    "docs:build": "mkdocs build",
    "docs:gh-deploy": "mkdocs gh-deploy --"
  },
  "devDependencies": {
    "npm-run-all": "^4.1.5",
    "prettier": "^3.2.5"
  },
  "workspaces": [
    "packages/*"
  ]
}
```

次回は、GenU の CDK スタックの解説をしていきます。

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
