## はじめに

皆さん、こんにちは。

私は業務でデータ利活用基盤を取り扱っているため、[dbt](https://www.getdbt.com/)や[Iceberg](https://iceberg.apache.org/)、そして[AWS GenU](https://aws-samples.github.io/generative-ai-use-cases-jp/)に取り組む必要があると考えています。特に AWS Japan Top Engineer として、[GenU](https://aws-samples.github.io/generative-ai-use-cases-jp/)を扱い、その活用を広めることが責務だと感じています。

しかし、私はこれまで CloudFormation を好んで使っており、（逆張り思考も重なって）Cfn テンプレートをシンプルかつ汎用性・拡張性の高い形で作ることに注力してきました。そのため、改めて[GenU の CDK コード](https://github.com/aws-samples/generative-ai-use-cases-jp/tree/main/packages/cdk)を読もうとしても、なかなか理解が進みませんでした。

そこで、CDK を学びながら、その過程を記事としてまとめることにしました。

## (事前準備) GenU の理解

前回までで、以下が完了しました。

- [CDK のセットアップ](https://qiita.com/siruko/items/fd25fdcf89615cb85262)
- [AWS CDK の動作確認](https://qiita.com/siruko/items/73169f986b4173e3d3a5)
- [GenU の理解](https://qiita.com/siruko/items/625801b9e1847b305c1e)

今回はデプロイへ進む前に、 GenU の中身を確認していきたいと思います。

## GenU アーキテクチャについて

2025/3/16 現在、[クイックスタート](https://aws-samples.github.io/generative-ai-use-cases-jp/ABOUT.html)に記載されているアーキテクチャは以下の通りです。

![image.png](https://aws-samples.github.io/generative-ai-use-cases-jp/assets/images/arch.drawio.png)

このアーキテクチャを CDK のソースコードと照らし合わせながら見ていきます。

### デプロイコマンドの確認

まずはデプロイコマンドです。
最初に[`npm ci`](https://docs.npmjs.com/cli/v9/commands/npm-ci) コマンドを実行します。
`npm ci` コマンドについて、npm Docs の説明文を訳すと以下の通りです。

> このコマンドは npm install と似ているが、テストプラットフォーム、継続的インテグレーション、デプロイなどの自動化された環境で使うことを意図している。
> npm install と npm ci の主な違いは以下の通り：
>
> - プロジェクトに既存の package-lock.json か npm-shrinkwrap.json があること。
> - package-lock.json 内の依存関係が package.json 内の依存関係と一致しない場合、 npm ci はパッケージロックを更新する代わりにエラーで終了します。
> - npm ci は、一度にプロジェクト全体をインストールすることしかできません: 個々の依存関係をこのコマンドで追加することはできません。
> - 既に node_modules が存在する場合は、npm ci がインストールを始める前に自動的に削除されます。
> - package.json や package-lock に書き込むことはありません: インストールは基本的に凍結されます。

つまり、package-lock.json のみを利用してクリーンインストールするコマンドになります。
こちらは大人しく実行しておきましょう。

```bash
npm ci
```

次に、以下のデプロイコマンドを実行せよと記載されています。

```
# 通常デプロイ
npm run cdk:deploy

# 高速デプロイ (作成されるリソースを事前確認せずに素早くデプロイ)
npm run cdk:deploy:quick
```

この実行コマンドは前回確認した通り、以下の通りです。

```diff_json:package.json
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
+   "cdk:deploy:quick": "npm -w packages/cdk run cdk deploy -- --all --asset-parallelism --asset-prebuild=false --concurrency 3 --method=direct --require-approval never --force",
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

つまり、以下のコマンドを実行しています。

```
# npm run cdk:deploy
npm -w packages/cdk run cdk deploy -- --all

# npm run cdk:deploy:quick
npm -w packages/cdk run cdk deploy -- --all --asset-parallelism --asset-prebuild=false --concurrency 3 --method=direct --require-approval never --force
```

### デプロイコマンド（2 層目）の確認

上記のデプロイコマンドは packages/cdk を Workspace として`run cdk deploy --all # +オプション`を実行しています。
ここで`--`は最上階の npm コマンドではなく、`run cdk deploy`に`--all`オプションをつけるという記法です。
packages/cdk/package.json の npm-scripts を確認します。

```diff_json:packages/cdk/package.json
{
  "name": "cdk",
  "private": true,
  "scripts": {
    "build": "tsc",
    "watch": "tsc -w",
    "test": "jest",
+   "cdk": "cdk",
    "lint": "eslint . --ext ts --report-unused-disable-directives --max-warnings 0",
    "postinstall": "npm ci --prefix custom-resources"
  },
  "devDependencies": {
    "@types/aws-lambda": "^8.10.137",
    "@types/jest": "^29.5.12",
    "@types/node": "^20.12.5",
    "@typescript-eslint/eslint-plugin": "^7.6.0",
    "@typescript-eslint/parser": "^7.6.0",
    "aws-cdk": "^2.154.1",
    "eslint": "^8.56.0",
    "jest": "^29.7.0",
    "ts-jest": "^29.2.5",
    "ts-node": "^10.9.2",
    "typescript": "~5.4.5"
  },
  "dependencies": {
    "@aws-cdk/aws-cognito-identitypool-alpha": "^2.154.1-alpha.0",
    "@aws-cdk/aws-lambda-python-alpha": "^2.154.1-alpha.0",
    "@aws-sdk/client-bedrock-agent": "^3.755.0",
    "@aws-sdk/client-bedrock-agent-runtime": "^3.755.0",
    "@aws-sdk/client-bedrock-runtime": "^3.755.0",
    "@aws-sdk/client-dynamodb": "^3.755.0",
    "@aws-sdk/client-kendra": "^3.755.0",
    "@aws-sdk/client-s3": "^3.755.0",
    "@aws-sdk/client-sagemaker-runtime": "^3.755.0",
    "@aws-sdk/client-transcribe": "^3.755.0",
    "@aws-sdk/client-transcribe-streaming": "^3.755.0",
    "@aws-sdk/lib-dynamodb": "^3.755.0",
    "@aws-sdk/s3-request-presigner": "^3.755.0",
    "@aws-solutions-constructs/aws-cloudfront-s3": "^2.68.0",
    "aws-cdk-lib": "^2.154.1",
    "aws-jwt-verify": "^4.0.0",
    "constructs": "^10.3.0",
    "deploy-time-build": "^0.3.17",
    "node-html-parser": "^6.1.13",
    "sanitize-html": "^2.13.0",
    "source-map-support": "^0.5.21",
    "upsert-slr": "^1.0.4",
    "zod": "^3.24.1"
  }
}

```

Workspace の package/cdk で`cdk deploy --all`を実行しています。
[`cdk deploy`](https://docs.aws.amazon.com/ja_jp/cdk/v2/guide/ref-cli-cmd-deploy.html)コマンドに以下のオプションをつけて実行しています。

- `--all` BOOLEAN: CDK アプリにすべてのスタックをデプロイします。

ここまでで、クイックスタートのコマンドは、すべての CDK スタックをデプロイするコマンドであることが確認できました。

### GenU に含まれている CDK スタックの確認

次に GenU に含まれている CDK スタックを確認します。
CDK の[`cdk list`](https://docs.aws.amazon.com/ja_jp/cdk/v2/guide/ref-cli-cmd-list.html) コマンドを使います。
`--show-dependencies`オプションをつけて依存関係情報も確認します。

```bash
cd packages/cdk
cdk list --show-dependencies
```

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/217144/fac04ea1-eb79-4ca2-979e-de81ef8a1fad.png)

スタックは`GenerativeAiUseCasesStack`の 1 つのみで、依存関係はないようです。

### GenU の CDK スタックの確認

それでは、CDK ソースコードを読んでいきます。
**なお、この記事に記載のコードは、あくまでもこの記事の執筆時点（2025/3/17）のもの** であることにご留意ください。
まずは [`packages/cdk/cdk.json`](https://github.com/aws-samples/generative-ai-use-cases-jp/blob/main/packages/cdk/cdk.json) を確認します。

```diff_json:packages/cdk/cdk.json
{
  "app": "npx ts-node --prefer-ts-exts bin/generative-ai-use-cases.ts",
  ~~ 省略 ~~
}
```

`bin/generative-ai-use-cases.ts`を実行しています。
次に、 [`packages/cdk/bin/generative-ai-use-cases.ts`](https://github.com/aws-samples/generative-ai-use-cases-jp/blob/main/packages/cdk/bin/generative-ai-use-cases.ts) を確認します。

```diff_typescript:packages/cdk/bin/generative-ai-use-cases.ts
#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { getParams } from '../parameter';
import { createStacks } from '../lib/create-stacks';

const app = new cdk.App();
const params = getParams(app);
createStacks(app, params);
```

createStacks 関数でスタックを作成しているため、[`packages/cdk/lib/create-stacks.ts`](https://github.com/aws-samples/generative-ai-use-cases-jp/blob/main/packages/cdk/lib/create-stacks.ts) を確認します。

```typescript
import * as cdk from 'aws-cdk-lib';
import { IConstruct } from 'constructs';
import { GenerativeAiUseCasesStack } from './generative-ai-use-cases-stack';
import { CloudFrontWafStack } from './cloud-front-waf-stack';
import { DashboardStack } from './dashboard-stack';
import { AgentStack } from './agent-stack';
import { RagKnowledgeBaseStack } from './rag-knowledge-base-stack';
import { GuardrailStack } from './guardrail-stack';
import { StackInput } from './stack-input';

class DeletionPolicySetter implements cdk.IAspect {
  constructor(private readonly policy: cdk.RemovalPolicy) {}

  visit(node: IConstruct): void {
    if (node instanceof cdk.CfnResource) {
      node.applyRemovalPolicy(this.policy);
    }
  }
}

export const createStacks = (app: cdk.App, params: StackInput) => {
  // CloudFront WAF
  // IP アドレス範囲(v4もしくはv6のいずれか)か地理的制限が定義されている場合のみ、CloudFrontWafStack をデプロイする
  // WAF v2 は us-east-1 でのみデプロイ可能なため、Stack を分けている
  const cloudFrontWafStack =
    params.allowedIpV4AddressRanges ||
    params.allowedIpV6AddressRanges ||
    params.allowedCountryCodes ||
    params.hostName
      ? new CloudFrontWafStack(app, `CloudFrontWafStack${params.env}`, {
          env: {
            account: params.account,
            region: 'us-east-1',
          },
          params: params,
          crossRegionReferences: true,
        })
      : null;

  // RAG Knowledge Base
  const ragKnowledgeBaseStack =
    params.ragKnowledgeBaseEnabled && !params.ragKnowledgeBaseId
      ? new RagKnowledgeBaseStack(app, `RagKnowledgeBaseStack${params.env}`, {
          env: {
            account: params.account,
            region: params.modelRegion,
          },
          params: params,
          crossRegionReferences: true,
        })
      : null;

  // Agent
  const agentStack = params.agentEnabled
    ? new AgentStack(app, `WebSearchAgentStack${params.env}`, {
        env: {
          account: params.account,
          region: params.modelRegion,
        },
        params: params,
        crossRegionReferences: true,
      })
    : null;

  // Guardrail
  const guardrail = params.guardrailEnabled
    ? new GuardrailStack(app, `GuardrailStack${params.env}`, {
        env: {
          account: params.account,
          region: params.modelRegion,
        },
        crossRegionReferences: true,
      })
    : null;

  // GenU Stack

  const generativeAiUseCasesStack = new GenerativeAiUseCasesStack(
    app,
    `GenerativeAiUseCasesStack${params.env}`,
    {
      env: {
        account: params.account,
        region: params.region,
      },
      description: params.anonymousUsageTracking
        ? 'Generative AI Use Cases JP (uksb-1tupboc48)'
        : undefined,
      params: params,
      crossRegionReferences: true,
      // RAG Knowledge Base
      knowledgeBaseId: ragKnowledgeBaseStack?.knowledgeBaseId,
      knowledgeBaseDataSourceBucketName:
        ragKnowledgeBaseStack?.dataSourceBucketName,
      // Agent
      agents: agentStack?.agents,
      // Guardrail
      guardrailIdentifier: guardrail?.guardrailIdentifier,
      guardrailVersion: 'DRAFT',
      // WAF
      webAclId: cloudFrontWafStack?.webAclArn,
      // Custom Domain
      cert: cloudFrontWafStack?.cert,
    }
  );

  cdk.Aspects.of(generativeAiUseCasesStack).add(
    new DeletionPolicySetter(cdk.RemovalPolicy.DESTROY)
  );

  const dashboardStack = params.dashboard
    ? new DashboardStack(
        app,
        `GenerativeAiUseCasesDashboardStack${params.env}`,
        {
          env: {
            account: params.account,
            region: params.modelRegion,
          },
          params: params,
          userPool: generativeAiUseCasesStack.userPool,
          userPoolClient: generativeAiUseCasesStack.userPoolClient,
          appRegion: params.region,
          crossRegionReferences: true,
        }
      )
    : null;

  return {
    cloudFrontWafStack,
    ragKnowledgeBaseStack,
    agentStack,
    guardrail,
    generativeAiUseCasesStack,
    dashboardStack,
  };
};
```

GenU の CDK は最大で以下の 6 つの子スタックを作成します。

- `CloudFrontWafStack`
- `RagKnowledgeBaseStack`
- `AgentStack`
- `GuardrailStack`
- `GenerativeAiUseCasesStack`
- `DashboardStack`

デプロイオプションを設定しない場合、デフォルトでは `GenerativeAiUseCasesStack` スタックのみ作成する作りになっています。
そのため、`cdk list` コマンドでは `GenerativeAiUseCasesStack` スタックしか出力されませんでした。

他の 5 つのスタックについては、[前回の記事で少し触れたデプロイオプション](https://qiita.com/siruko/items/625801b9e1847b305c1e#%E3%83%87%E3%83%97%E3%83%AD%E3%82%A4%E3%82%AA%E3%83%97%E3%82%B7%E3%83%A7%E3%83%B3%E3%81%AE%E7%A2%BA%E8%AA%8D)を指定することで作成されます。

それぞれのスタックの作成条件について見ていきましょう。

#### CloudFrontWafStack の作成条件

CloudFrontWafStack は、[AWS WAF による制限を有効化する](https://aws-samples.github.io/generative-ai-use-cases-jp/DEPLOY_OPTION.html#aws-waf-%E3%81%AB%E3%82%88%E3%82%8B%E5%88%B6%E9%99%90%E3%82%92%E6%9C%89%E5%8A%B9%E5%8C%96%E3%81%99%E3%82%8B)か、[カスタムドメインの使用](https://aws-samples.github.io/generative-ai-use-cases-jp/DEPLOY_OPTION.html#%E3%82%AB%E3%82%B9%E3%82%BF%E3%83%A0%E3%83%89%E3%83%A1%E3%82%A4%E3%83%B3%E3%81%AE%E4%BD%BF%E7%94%A8) を行うと作成されます。

パラメータ例として、`packages/cdk/parameter.ts` に以下を設定します。

```typescript: packages/cdk/parameter.ts
  dev: {
    allowedIpV4AddressRanges: ["192.168.0.0/24"],
    allowedIpV6AddressRanges: ["2001:0db8::/32"],
    allowedCountryCodes: ["JP"]
  }
```

```typescript: packages/cdk/parameter.ts
  dev: {
    hostName: 'genai',
    domainName: 'example.com',
    hostedZoneId: 'Z0123456789ABCDEFGHIJ',
  }
```

#### RagKnowledgeBaseStack の作成条件

RagKnowledgeBaseStack は、[RAG チャット (Knowledge Base) ユースケースの有効化](https://aws-samples.github.io/generative-ai-use-cases-jp/DEPLOY_OPTION.html#rag-%E3%83%81%E3%83%A3%E3%83%83%E3%83%88-knowledge-base-%E3%83%A6%E3%83%BC%E3%82%B9%E3%82%B1%E3%83%BC%E3%82%B9%E3%81%AE%E6%9C%89%E5%8A%B9%E5%8C%96) を行うと作成されます。

パラメータ例として、`packages/cdk/parameter.ts` に以下を設定します。

```typescript: packages/cdk/parameter.ts
  dev: {
    ragKnowledgeBaseEnabled: true,
    ragKnowledgeBaseId: 'XXXXXXXXXX',
    ragKnowledgeBaseStandbyReplicas: false,
    ragKnowledgeBaseAdvancedParsing: false,
    ragKnowledgeBaseAdvancedParsingModelId: 'anthropic.claude-3-sonnet-20240229-v1:0',
    embeddingModelId: 'amazon.titan-embed-text-v2:0',
  }
```

#### AgentStack の作成条件

AgentStack は、[Agent チャットユースケースの有効化](https://aws-samples.github.io/generative-ai-use-cases-jp/DEPLOY_OPTION.html#agent-%E3%83%81%E3%83%A3%E3%83%83%E3%83%88%E3%83%A6%E3%83%BC%E3%82%B9%E3%82%B1%E3%83%BC%E3%82%B9%E3%81%AE%E6%9C%89%E5%8A%B9%E5%8C%96) を行うと作成されます。

パラメータ例として、`packages/cdk/parameter.ts` に以下を設定します。

```typescript: packages/cdk/parameter.ts
  dev: {
    agentEnabled: true,
  }
```

#### GuardrailStack の作成条件

GuardrailStack は、[ガードレール](https://aws-samples.github.io/generative-ai-use-cases-jp/DEPLOY_OPTION.html#%E3%82%AC%E3%83%BC%E3%83%89%E3%83%AC%E3%83%BC%E3%83%AB) を適用すると作成されます。

パラメータ例として、`packages/cdk/parameter.ts` に以下を設定します。

```typescript: packages/cdk/parameter.ts
  dev: {
    guardrailEnabled: true,
  }
```

#### GenerativeAiUseCasesStack の作成条件

GenerativeAiUseCasesStack は唯一、無条件で作成されるスタックです。

#### DashboardStack の作成条件

DashboardStack は、[モニタリング用のダッシュボードの有効化](https://aws-samples.github.io/generative-ai-use-cases-jp/DEPLOY_OPTION.html#%E3%83%A2%E3%83%8B%E3%82%BF%E3%83%AA%E3%83%B3%E3%82%B0%E7%94%A8%E3%81%AE%E3%83%80%E3%83%83%E3%82%B7%E3%83%A5%E3%83%9C%E3%83%BC%E3%83%89%E3%81%AE%E6%9C%89%E5%8A%B9%E5%8C%96) を行うと作成されます。

パラメータ例として、`packages/cdk/parameter.ts` に以下を設定します。

```typescript: packages/cdk/parameter.ts
  dev: {
    dashboard: true,
  }
```

次回はこの 6 つのスタックをもう少し深堀りしていきます。
