## はじめに

皆さん、こんにちは。

私は業務でデータ利活用基盤を取り扱っていること、2024 AWS Japan Top Engineer に選出されたということから、[AWS GenU](https://aws-samples.github.io/generative-ai-use-cases-jp/) およびそれに必要なデータ基盤の探求 ([Snowflake](https://www.snowflake.com/ja/), [dbt](https://www.getdbt.com/), [Iceberg](https://iceberg.apache.org/), etc) に取り組む必要があると考えています。

本投稿では、[GenU のバックエンドである CDK コード](https://github.com/aws-samples/generative-ai-use-cases-jp/tree/main/packages/cdk)を詳細に解説します。
自身そして閲覧して頂いた皆様の GenU への理解が少しでも深まり、生成 AI の民主化につながっていければと考えています。

## GenU とは

GenU は生成 AI を安全に業務活用するための、ビジネスユースケース集です。
バックエンドは AWS で、フロントエンドは Vite + React で動作します。

2025/3/10 時点の GenU のバックエンドについては、14 回に分けて解説していますので、詳しく知りたい方はお読みいただけると嬉しいです。

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

### GenU のデプロイオプション

GenU の[デプロイオプション](https://aws-samples.github.io/generative-ai-use-cases-jp/ja/DEPLOY_OPTION.html)を解説します。

デプロイオプションは GenU の構築オプション設定であり、機能の有効化／無効化や、既存の生成 AI 基盤モデルを利用する場合にモデル ID を指定することができます。

`packages/cdk/cdk.json` および `packages/cdk/parameter.ts` でデプロイオプションを指定することができます。

両方に値が設定されている場合、parameter.ts が優先されます。
公式では、複数環境の設定を定義できるため、新規に構築する場合は parameter.ts での指定を推奨する、としています。

#### デプロイオプションの例 ①

```json:cdk.jsonの例①
{
  "app": "npx ts-node --prefer-ts-exts bin/generative-ai-use-cases.ts",
  "watch": {
    "include": [
      ~~ 略 ~~
    ],
    "exclude": [
      ~~ 略 ~~
    ]
  },
  "context": {
    "env": "",
    "ragEnabled": false
    ~~ 略 ~~
  }
}
```

上記例では、`cdk.json` の `env` は指定されておらず、`ragEnabled` オプションは `false` となっています。
この場合、`parameter.ts` の設定は無視され、すべて `cdk.json` の `context` の値を使用してデプロイされます。

#### デプロイオプションの例 ②

```json:cdk.jsonの例②
{
  "app": "npx ts-node --prefer-ts-exts bin/generative-ai-use-cases.ts",
  "watch": {
    "include": [
      ~~ 略 ~~
    ],
    "exclude": [
      ~~ 略 ~~
    ]
  },
  "context": {
    "env": "prod",
    "ragEnabled": false
    ~~ 略 ~~
  }
}
```

この例では、`cdk.json` の `env` は `prod` を指定しており、`ragEnabled` オプションは `false` となっています。

加えて、`parameter.ts` が以下の設定だった場合を考えます。

```typescript:parameter.tsの例
const envs: Record<string, Partial<StackInput>> = {
  dev: {
    ragEnabled: false,
    ~~ 略 ~~
  },
  staging: {
    ragEnabled: false,
    ~~ 略 ~~
  },
  prod: {
    ragEnabled: true,
    ~~ 略 ~~
  },
};
```

この場合、`parameter.ts` の値が優先されるため、最終的な `ragEnabled` は `true` としてデプロイされます。

#### デプロイオプションで設定できる値

デプロイオプションで設定できる値は、[cdk.json](https://github.com/aws-samples/generative-ai-use-cases-jp/blob/56583580fbc767c70ca451a09cc98ce7c299b998/packages/cdk/cdk.json) や [stack-input.ts](https://github.com/aws-samples/generative-ai-use-cases-jp/blob/56583580fbc767c70ca451a09cc98ce7c299b998/packages/cdk/lib/stack-input.ts) が参考になります。
**なお、この記事に記載のコードやデプロイオプションは、あくまでもこの記事の執筆時点（2025/3/30）のもの** であることにご留意ください。

### 各デプロイオプションの解説

#### 共通のデプロイオプション例

```json: cdk.json
{
  "context": {
    "env": "dev"
}
```

```typescript: parameter.ts
// 東京リージョンを優先しつつ、別リージョンの最新のモデルも使いたい場合
const envs: Record<string, Partial<StackInput>> = {
  dev: {
    modelRegion: 'ap-northeast-1',
    modelIds: [
      {modelId: 'us.anthropic.claude-3-7-sonnet-20250219-v1:0', region: 'us-east-1'},
      'apac.anthropic.claude-3-5-sonnet-20241022-v2:0',
      'anthropic.claude-3-5-sonnet-20240620-v1:0',
      {modelId: 'us.anthropic.claude-3-5-haiku-20241022-v1:0', region: 'us-east-1'},
      'apac.amazon.nova-pro-v1:0',
      'apac.amazon.nova-lite-v1:0',
      'apac.amazon.nova-micro-v1:0',
      {modelId: 'us.deepseek.r1-v1:0', region: 'us-east-1'},
      {modelId: 'us.meta.llama3-3-70b-instruct-v1:0', region: 'us-east-1'},
      {modelId: 'us.meta.llama3-2-90b-instruct-v1:0', region: 'us-east-1'},
    ],
    imageGenerationModelIds: [
      'amazon.nova-canvas-v1:0',
      {modelId: 'stability.sd3-5-large-v1:0', region: 'us-west-2'},
      {modelId: 'stability.stable-image-core-v1:1', region: 'us-west-2'},
      {modelId: 'stability.stable-image-ultra-v1:1', region: 'us-west-2'},
    ],
    videoGenerationModelIds: [
      'amazon.nova-reel-v1:0',
      {modelId: 'luma.ray-v2:0', region: 'us-west-2'},
    ],
    endpointNames: [
      "jumpstart-dft-hf-llm-rinna-3-6b-instruction-ppo-bf16",
      "jumpstart-dft-bilingual-rinna-4b-instruction-ppo-bf16"
    ],
    crossAccountBedrockRoleArn: 'arn:aws:iam::[アカウントID]:role/[ロール名]',
  },
};
```

#### 共通のデプロイオプション

`env`
cdk.json のみ設定可能。構築する環境を指定する。デフォルトは空文字。

- **例**: "prod"

`modelRegion`
使用する生成 AI 基盤モデルのリージョンを指定する。デフォルトは us-east-1。

`modelIds`
テキスト生成に使用する生成 AI 基盤モデルの ID を指定する。デフォルトは以下の配列。

- "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
- "us.anthropic.claude-3-5-haiku-20241022-v1:0"
- "us.amazon.nova-pro-v1:0"
- "us.amazon.nova-lite-v1:0"
- "us.amazon.nova-micro-v1:0"
  別リージョンのモデルを使用したい場合は、**{modelId: '[モデル名]', region: '[リージョンコード]'}** で指定する。

`imageGenerationModelIds`
画像生成に使用する生成 AI 基盤モデルの ID を指定する。デフォルトは以下の配列。

- "amazon.nova-canvas-v1:0"
  別リージョンのモデルを使用したい場合は、**{modelId: '[モデル名]', region: '[リージョンコード]'}** で指定する。

`videoGenerationModelIds`
動画生成に使用する生成 AI 基盤モデルの ID を指定する。デフォルトは以下の配列。

- "amazon.nova-reel-v1:0"
  別リージョンのモデルを使用したい場合は、**{modelId: '[モデル名]', region: '[リージョンコード]'}** で指定する。

`endpointNames`
デプロイ済の SageMaker エンドポイントを使用する場合、エンドポイント名のリストを指定する。デフォルトは空配列。

`crossAccountBedrockRoleArn`
異なる AWS アカウントの Becrock を呼び出す際に指定する。デフォルトは空。
一度 GenU を作成した後に設定を追加する必要がある。

#### ユースケース表示制御のデプロイオプション例

```typescript: parameter.ts
// 特定のユースケースを非表示にする
const envs: Record<string, Partial<StackInput>> = {
  dev: {
    hiddenUseCases: {
      generate: true, // 文章生成を非表示
      summarize: true, // 要約を非表示
      writer: true, // 執筆を非表示
      translate: true, // 翻訳を非表示
      webContent: true, // Web コンテンツ抽出を非表示
      image: true, // 画像生成を非表示
      video: true, // 動画生成を非表示
      videoAnalyzer: true, // 映像分析を非表示
      diagram: true, // ダイアグラム生成を非表示
    }
  },
};
```

```typescript: parameter.ts
// RAG (Kendra), RAG (ナレッジベース), Agent, ガードレール, ユースケースビルダーを有効化する
// 画像生成ユースケース、動画生成ユースケースを無効化する
const envs: Record<string, Partial<StackInput>> = {
  dev: {
    ragEnabled: true,
    ragKnowledgeBaseEnabled: true,
    agentEnabled: true,
    guardrailEnabled: true,
    useCaseBuilderEnabled: true,
    imageGenerationModelIds: [],
    videoGenerationModelIds: [],
  },
};
```

#### ユースケース表示制御のデプロイオプション

`hiddenUseCases`
子要素で指定したユースケース (GenU の機能) を非表示にする。デフォルトはすべて false。
以下の値が設定可能。

- generate: 文章生成
- summarize: 要約
- writer: 執筆
- translate: 翻訳
- webContent: Web コンテンツ抽出
- image: 画像生成
- video: 動画生成
- videoAnalyzer: 映像分析
- diagram: ダイアグラム生成

`ragEnabled`
Amazon Kendra を使用した RAG を構築する場合は true を指定する。RAG を構築する場合、比較的高額になるため注意。デフォルトは false。

`ragKnowledgeBaseEnabled`
ナレッジベースを使用した RAG を構築する場合は true を指定する。デフォルトは false。

`agentEnabled`
Agent チャットユースケースのスタックを作成するかを指定する。デフォルトは false。

`guardrailEnabled`
ガードレール (生成 AI の入出力に含まれる機密情報のフィルタリング機能) スタックを作成するかを指定する。デフォルトは false。

`useCaseBuilderEnabled`
ユースケースビルダースタックを作成するかを指定する。デフォルトは false。

`imageGenerationModelIds`
画像生成に使用する生成 AI 基盤モデルの ID を指定する。デフォルトは以下の配列。

- "amazon.nova-canvas-v1:0"
  別リージョンのモデルを使用したい場合は、**{modelId: '[モデル名]', region: '[リージョンコード]'}** で指定する。

1 つ以上指定する場合、画像生成ユースケースが有効化される。

`videoGenerationModelIds`
動画生成に使用する生成 AI 基盤モデルの ID を指定する。デフォルトは以下の配列。

- "amazon.nova-reel-v1:0"
  別リージョンのモデルを使用したい場合は、**{modelId: '[モデル名]', region: '[リージョンコード]'}** で指定する。

1 つ以上指定する場合、動画生成ユースケースが有効化される。

#### ログイン関連設定のデプロイオプション例

```typescript: parameter.ts
// amazon.com, amazon.jp のメールドメインに限り、ユーザ自身のサインアップを許可する場合
const envs: Record<string, Partial<StackInput>> = {
  dev: {
    selfSignUpEnabled: true,
    allowedSignUpEmailDomains: ["amazon.com", "amazon.jp"],
  },
};
```

```typescript: parameter.ts
// SAML認証を行う場合
const envs: Record<string, Partial<StackInput>> = {
  dev: {
    selfSignUpEnabled: false, // false が必須
    allowedSignUpEmailDomains: null,
    samlAuthEnabled: true,
    samlCognitoDomainName: "your-preferred-name.auth.ap-northeast-1.amazoncognito.com",
    samlCognitoFederatedIdentityProviderName: "EntraID",
  },
};
```

#### ログイン関連設定のデプロイオプション例

`selfSignUpEnabled`
Cognito ログインアカウントをユーザ自身が作成できるか (サインアップできるか) を指定する。デフォルトは true。

`allowedSignUpEmailDomains`
サインアップ時に、特定のドメインのメールアドレスのみ許可する場合に指定する。デフォルトは null。
@をつけずに、配列形式で指定する。

`samlAuthEnabled`
Cognito ログインに Active Directory などの IdP が提供する SAML 認証機能を使用する場合に指定する。デフォルトは false。

`samlCognitoDomainName`
SAML 認証時に Cognito の App integration で設定する Cognito ドメイン名を指定する。デフォルトは null。

`samlCognitoFederatedIdentityProviderName`
SAML 認証時に Cognito の Sign-in experience で設定する IdP 名を指定する。デフォルトは null。

#### WAF 関連のデプロイオプション例

```typescript: parameter.ts
const envs: Record<string, Partial<StackInput>> = {
  dev: {
    allowedIpV4AddressRanges: ["192.168.0.0/24"],
    allowedIpV6AddressRanges: ["2001:0db8::/32"],
    allowedCountryCodes: ["JP"],
  },
};
```

#### WAF 制限関連のデプロイオプション

`allowedIpV4AddressRanges`
Web アプリへのアクセスを IPv4 アドレスで制限したい場合に設定する。デフォルトは null。

`allowedIpV6AddressRanges`
Web アプリへのアクセスを IPv4 アドレスで制限したい場合に設定する。デフォルトは null。

`allowedCountryCodes`
Web アプリへのアクセスをアクセス元の国で制限したい場合に設定する。デフォルトは null。

#### カスタムドメイン関連のデプロイオプション例

```typescript: parameter.ts
const envs: Record<string, Partial<StackInput>> = {
  dev: {
    hostName: 'genai',
    domainName: 'example.com',
    hostedZoneId: 'XXXXXXXXXXXXXXXXXXXX',
  },
};
```

#### カスタムドメイン関連のデプロイオプション

`hostName`
Web サイトの URL としてカスタムドメインを使用する場合に Web サイトのホスト名を設定する。デフォルトは null。
以下の domainName と hostedZoneId が事前に作成されていれば、hostName で指定した A レコードが自動で作成される。

`domainName`
Web サイトの URL としてカスタムドメインを使用する場合に、事前作成した Route 53 パブリックホストゾーンのドメイン名を設定する。デフォルトは null。

`hostedZoneId`
Web サイトの URL としてカスタムドメインを使用する場合に、事前作成した Route 53 パブリックホストゾーンのゾーン ID を設定する。デフォルトは null。

#### モニタリング関連のデプロイオプション例

```typescript: parameter.ts
const envs: Record<string, Partial<StackInput>> = {
  dev: {
    dashboard: true,
  },
};
```

#### モニタリング関連のデプロイオプション

`dashboard`
モニタリング用の Amazon CloudWatch ダッシュボードを作成する場合に指定する。デフォルトは false。

#### RAG (ナレッジベース) 関連のデプロイオプション例

```typescript: parameter.ts
const envs: Record<string, Partial<StackInput>> = {
  dev: {
    ragKnowledgeBaseEnabled: true,
    ragKnowledgeBaseId: 'XXXXXXXXXX',
    ragKnowledgeBaseStandbyReplicas: false,
    embeddingModelId: 'amazon.titan-embed-text-v2:0',
    ragKnowledgeBaseAdvancedParsing: true,
    ragKnowledgeBaseAdvancedParsingModelId: 'anthropic.claude-3-sonnet-20240229-v1:0',
    rerankingModelId: 'amazon.rerank-v1:0',
    queryDecompositionEnabled: true,
    ragKnowledgeBaseBinaryVector: false,
  },
};
```

#### RAG (ナレッジベース) 構築関連のデプロイオプション

`ragKnowledgeBaseEnabled`
ナレッジベースを使用した RAG を構築する場合は true を指定する。デフォルトは false。

`ragKnowledgeBaseId`
既存の ナレッジベースを利用する場合に、ナレッジベース ID を指定する。デフォルトは null。
null の場合、OpenSearch Serverless のナレッジベースが作成される。

`ragKnowledgeBaseStandbyReplicas`
false の場合、OpenSearch Serverless をシングル AZ で動作させる。true の場合、マルチ AZ で動作させる。デフォルトは false。
コストと可用性を鑑みて設定する。

`embeddingModelId`
非構造化データのベクトル化に用いる Embedding モデルを指定する。デフォルトは amazon.titan-embed-text-v2:0。
以下のいずれかが指定できる。

- "amazon.titan-embed-text-v1"
- "amazon.titan-embed-text-v2:0"
- "cohere.embed-multilingual-v3"
- "cohere.embed-english-v3"

#### RAG (ナレッジベース) 精度向上、コスト削減関連のデプロイオプション

`ragKnowledgeBaseAdvancedParsing`
RAG の精度向上のために、非構造化データ内の表やグラフから情報を分析したり抽出したりする [Advanced Parsing](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-chunking.html#kb-advanced-parsing) を利用するかを指定する。デフォルトは false。

`ragKnowledgeBaseAdvancedParsingModelId`
Advanced Parsing を行う際に利用するモデル ID を指定する。デフォルトは anthropic.claude-3-sonnet-20240229-v1:0。
以下のいずれかが指定できる。

- "anthropic.claude-3-sonnet-20240229-v1:0"
- "anthropic.claude-3-haiku-20240307-v1:0"

`rerankingModelId`
RAG の精度向上のための Re-ranking 用モデルを指定する。デフォルトは null。
以下のいずれかが指定できる。

- "amazon.rerank-v1:0"
- "cohere.rerank-v3-5:0"

`queryDecompositionEnabled`
RAG の精度向上のためのクエリ分解 (Query Decomposition) を利用するかを指定する。デフォルトは false。

`ragKnowledgeBaseBinaryVector`
コスト最適化のための [Binary Vector Embedding](https://aws.amazon.com/jp/blogs/machine-learning/build-cost-effective-rag-applications-with-binary-embeddings-in-amazon-titan-text-embeddings-v2-amazon-opensearch-serverless-and-amazon-bedrock-knowledge-bases/) 機能を利用するかを指定する。デフォルトは false。

#### Agent チャット関連のデプロイオプション例

```typescript: parameter.ts
const envs: Record<string, Partial<StackInput>> = {
  dev: {
    agentEnabled: true,
    searchAgentEnabled: true,
    searchApiKey: 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    agents: [
      {
        displayName: 'MyCustomAgent',
        agentId: 'XXXXXXXXX',
        aliasId: 'YYYYYYYY',
      },
    ],
    inlineAgents: true,
  },
};
```

#### Agent チャット関連のデプロイオプション

`agentEnabled`
Agent チャットユースケースのスタックを作成するかを指定する。デフォルトは false。

`searchAgentEnabled`
検索 Agent を使用するかを指定する。デフォルトは false。
使用する場合、Agent チャットユースケース内で外部 API を叩きにいくため、セキュリティポリシー等の確認が必要。

`searchApiKey`
検索エンジンの API キーを指定する。デフォルトは空文字。
デフォルトでは、検索エンジンは [Brave Search API](https://brave.com/search/api/) の Data for AI を使用する。

`agents`
自作のカスタム Bedrock Agent を使用する場合、Agent の情報を設定する。デフォルトは空配列。

`inlineAgents`
インライン Agent モードを使用する場合に設定する。デフォルトは false。
インライン Agent モードを使用すると、Agent チャットユースケースは表示されずに、他のユースケースで Agent を使用できるようになる。

#### ガードレール関連のデプロイオプション例

```typescript: parameter.ts
const envs: Record<string, Partial<StackInput>> = {
  dev: {
    guardrailEnabled: true,
  },
};
```

#### ガードレール関連のデプロイオプション

`guardrailEnabled`
ガードレール (生成 AI の入出力に含まれる機密情報のフィルタリング機能) スタックを作成するかを指定する。デフォルトは false。

#### Flow チャット関連のデプロイオプション例

```typescript: parameter.ts
const envs: Record<string, Partial<StackInput>> = {
  dev: {
    flows: [
      {
        flowId: "XXXXXXXXXX",
        aliasId: "YYYYYYYYYY",
        flowName: "WhatIsItFlow",
        description: "任意のキーワードをウェブ検索して、説明を返すフローです。文字を入力してください",
      },
      {
        flowId: "ZZZZZZZZZZ",
        aliasId: "OOOOOOOOOO",
        flowName: "RecipeFlow",
        description: "与えられたJSONをもとに、レシピを作成します。\n{\"dish\": \"カレーライス\", \"people\": 3} のように入力してください。",
      },
      {
        flowId: "PPPPPPPPPP",
        aliasId: "QQQQQQQQQQQ",
        flowName: "TravelPlanFlow",
        description: "与えられた配列をもとに、旅行計画を作成します。\n[{\"place\": \"東京\", \"day\": 3}, {\"place\": \"大阪\", \"day\": 2}] のように入力してください。",
      }
    ]
  },
};
```

#### Flow チャット関連のデプロイオプション

`flows`
自作のカスタム Bedrock Flow を使用する場合、Flow の情報を設定する。デフォルトは空配列。

#### RAG (Amazon Kendra) のデプロイオプション例

```typescript: parameter.ts
// 新規に Kendra インデックスを作成
const envs: Record<string, Partial<StackInput>> = {
  dev: {
    ragEnabled: true,
    kendraIndexLanguage: 'jp',
    kendraIndexArn: null,
    kendraDataSourceBucketName: null,
    kendraIndexScheduleEnabled: true,
    kendraIndexScheduleCreateCron: { "minute": "0", "hour": "23", "month": "\*", "weekDay": "SUN-THU" },
    kendraIndexScheduleDeleteCron: { "minute": "0", "hour": "11", "month": "\*", "weekDay": "MON-FRI" }
  },
};
```

```typescript: parameter.ts
// 既存の Kendra インデックスを利用
const envs: Record<string, Partial<StackInput>> = {
  dev: {
    ragEnabled: true,
    kendraIndexLanguage: 'jp',
    kendraIndexArn: 'arn:aws:kendra:ap-northeast-1:111122223333:index/0123456789abcdef',
    kendraDataSourceBucketName: 'kendra-datasource-111122223333',
    kendraIndexScheduleEnabled: false,
    kendraIndexScheduleCreateCron: null,
    kendraIndexScheduleDeleteCron: null
  },
};
```

#### RAG (Amazon Kendra) 構築関連のデプロイオプション

`ragEnabled`
Amazon Kendra を使用した RAG を構築する場合は true を指定する。RAG を構築する場合、比較的高額になるため注意。デフォルトは false。

`kendraIndexLanguage`
Amazon Kendra の使用言語を指定する。デフォルトは日本語の ja。

`kendraIndexArn`
既存の Amazon Kendra インデックスを利用する場合に、インデックスの ARN を指定する。デフォルトは null。

`kendraDataSourceBucketName`
既存の Amazon Kendra インデックスを利用する場合かつ、S3 データソースを利用している場合は、バケット名を指定する。デフォルトは null。

#### RAG (Amazon Kendra) コスト削減関連のデプロイオプション

`kendraIndexScheduleEnabled`
Amazon Kendra インデックスの料金を抑えるために、スケジュール作成/削除停止を行う場合は true を指定する。デフォルトは false。

- **注意事項**: 既存の Amazon Kendra インデックスに対しては機能しないため注意。つまり `kendraIndexArn` は null であることが必要。

`kendraIndexScheduleCreateCron`
Amazon Kendra インデックスのスケジュール作成/削除を行う場合、作成スケジュールを cron 式で指定する。デフォルトは null。

`kendraIndexScheduleDeleteCron`
Amazon Kendra インデックスのスケジュール作成/削除を行う場合、削除スケジュールを cron 式で指定する。デフォルトは null。

#### ユースケースビルダー関連のデプロイオプション例

```typescript: parameter.ts
const envs: Record<string, Partial<StackInput>> = {
  dev: {
    useCaseBuilderEnabled: true,
  },
};
```

#### ユースケースビルダー関連のデプロイオプション

`useCaseBuilderEnabled`
ユースケースビルダースタックを作成するかを指定する。デフォルトは false。

#### その他

`anonymousUsageTracking`
直訳で「匿名の使用状況追跡」だがその機能は見当たらない。デフォルト値は true。
現状、GenerativeAiUseCasesStack の description 設定のみに使用されている。

```diff_typescript: create-stack.ts
  // GenU Stack
  const generativeAiUseCasesStack = new GenerativeAiUseCasesStack(
    app,
    `GenerativeAiUseCasesStack${params.env}`,
    {
      env: {
        account: params.account,
        region: params.region,
      },
*     description: params.anonymousUsageTracking
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
      // Video Generation
      videoBucketRegionMap,
      // Guardrail
      guardrailIdentifier: guardrail?.guardrailIdentifier,
      guardrailVersion: 'DRAFT',
      // WAF
      webAclId: cloudFrontWafStack?.webAclArn,
      // Custom Domain
      cert: cloudFrontWafStack?.cert,
    }
  );
```

#### AWS CDK オプション

その他の AWS CDK オプションは以下の通りです。

`@aws-cdk/aws-lambda:recognizeLayerVersion`
デフォルト値は true。

`@aws-cdk/core:checkSecretUsage`
デフォルト値は true。

`@aws-cdk/core:target-partitions`: 以下の配列

- "aws"
- "aws-cn"

`@aws-cdk-containers/ecs-service-extensions:enableDefaultLogDriver`
デフォルト値は true。

`@aws-cdk/aws-ec2:uniqueImdsv2TemplateName`
デフォルト値は true。

`@aws-cdk/aws-ecs:arnFormatIncludesClusterName`
デフォルト値は true。

`@aws-cdk/aws-iam:minimizePolicies`
デフォルト値は true。

`@aws-cdk/core:validateSnapshotRemovalPolicy`
デフォルト値は true。

`@aws-cdk/aws-codepipeline:crossAccountKeyAliasStackSafeResourceName`
デフォルト値は true。

`@aws-cdk/aws-s3:createDefaultLoggingPolicy`
デフォルト値は true。

`@aws-cdk/aws-sns-subscriptions:restrictSqsDescryption`
デフォルト値は true。

`@aws-cdk/aws-apigateway:disableCloudWatchRole`
デフォルト値は true。

`@aws-cdk/core:enablePartitionLiterals`
デフォルト値は true。

`@aws-cdk/aws-events:eventsTargetQueueSameAccount`
デフォルト値は true。

`@aws-cdk/aws-iam:standardizedServicePrincipals`
デフォルト値は true。

`@aws-cdk/aws-ecs:disableExplicitDeploymentControllerForCircuitBreaker`
デフォルト値は true。

`@aws-cdk/aws-iam:importedRoleStackSafeDefaultPolicyName`
デフォルト値は true。

`@aws-cdk/aws-s3:serverAccessLogsUseBucketPolicy`
デフォルト値は true。

`@aws-cdk/aws-route53-patters:useCertificate`
デフォルト値は true。

`@aws-cdk/customresources:installLatestAwsSdkDefault`: false,
デフォルト値は false。

`@aws-cdk/aws-rds:databaseProxyUniqueResourceName`
デフォルト値は true。

`@aws-cdk/aws-codedeploy:removeAlarmsFromDeploymentGroup`
デフォルト値は true。

`@aws-cdk/aws-apigateway:authorizerChangeDeploymentLogicalId`
デフォルト値は true。

`@aws-cdk/aws-ec2:launchTemplateDefaultUserData`
デフォルト値は true。

`@aws-cdk/aws-secretsmanager:useAttachedSecretResourcePolicyForSecretTargetAttachments`
デフォルト値は true。

`@aws-cdk/aws-redshift:columnId`
デフォルト値は true。

`@aws-cdk/aws-stepfunctions-tasks:enableEmrServicePolicyV2`
デフォルト値は true。

`@aws-cdk/aws-ec2:restrictDefaultSecurityGroup`
デフォルト値は true。

`@aws-cdk/aws-apigateway:requestValidatorUniqueId`
デフォルト値は true。

`@aws-cdk/aws-kms:aliasNameRef`
デフォルト値は true。

`@aws-cdk/aws-autoscaling:generateLaunchTemplateInsteadOfLaunchConfig`
デフォルト値は true。

`@aws-cdk/core:includePrefixInUniqueNameGeneration`
デフォルト値は true。

`@aws-cdk/aws-opensearchservice:enableOpensearchMultiAzWithStandby`
デフォルト値は true。

### デプロイオプションの設定例

以下がデプロイオプションの設定例です。

#### とにかく早く始める

デフォルトで構築します。
CloudFront にホストされた Web アプリが起動し、テキスト生成や画像生成を行うことができます。
個人でとりあえず使ってみる程度のオプションです。

```json: cdk.json
{
  "context": {
    "env": "dev"
}
```

```typescript: parameter.ts
const envs: Record<string, Partial<StackInput>> = {
  dev: {
  },
};
```

- WAF: なし
- RAG (ナレッジベース) チャット: なし
- Agent チャット: なし
- ガードレール (機密情報フィルタ): なし
- GenU: **あり**
  - Cognito ユーザプール, ID プール: **あり**
  - DynamoDB テーブル: **あり**
  - API GW (Lambda 関数): **あり**
  - CloudFront にホストされた Web アプリケーション: **あり**
  - RAG (Amazon Kendra) チャット: なし
  - ユースケースビルダー: **あり**
  - 翻訳, 文字起こし: **あり**
- モニタリングダッシュボード: なし

#### RAG 以外を有効化し、セキュリティも高める

コストを抑えつつ、セキュリティや Agent 機能などを開放します。
企業内で試しに利用する程度のオプションです。

```json: cdk.json
{
  "context": {
    "env": "dev"
}
```

```typescript: parameter.ts
const envs: Record<string, Partial<StackInput>> = {
  dev: {
    // WAF
    allowedIpV4AddressRanges: ["[企業のGIP CIDR]"],
    // Agent チャット
    agentEnabled: true,
    // ガードレール
    guardrailEnabled: true,
    // モニタリングダッシュボード
    dashboard: true,
  },
};
```

- WAF: **あり**
- RAG (ナレッジベース) チャット: なし
- Agent チャット: **あり** ※ただし Web 検索エージェントは利用しない
- ガードレール (機密情報フィルタ): **あり**
- GenU: **あり**
  - Cognito ユーザプール, ID プール: **あり**
  - DynamoDB テーブル: **あり**
  - API GW (Lambda 関数): **あり**
  - CloudFront にホストされた Web アプリケーション: **あり**
  - RAG (Amazon Kendra) チャット: なし
  - ユースケースビルダー: **あり**
  - 翻訳, 文字起こし: **あり**
- モニタリングダッシュボード: **あり**

#### 可能な限り全機能を開放し、新規作成する

商用利用など競争優位性を確保するために RAG を有効化する際のオプションです。

```json: cdk.json
{
  "context": {
    "env": "dev"
}
```

```typescript: parameter.ts
const envs: Record<string, Partial<StackInput>> = {
  dev: {
    // WAF
    allowedIpV4AddressRanges: ["[企業のGIP CIDR]"],
    allowedCountryCodes: ["JP"],
    // RAG (ナレッジベース) チャット
    ragKnowledgeBaseEnabled: true,
    ragKnowledgeBaseStandbyReplicas: true,
    embeddingModelId: 'amazon.titan-embed-text-v2:0',
    ragKnowledgeBaseAdvancedParsing: true,
    ragKnowledgeBaseAdvancedParsingModelId: 'anthropic.claude-3-sonnet-20240229-v1:0',
    rerankingModelId: 'amazon.rerank-v1:0',
    queryDecompositionEnabled: true,
    ragKnowledgeBaseBinaryVector: true,
    // Agent チャット
    agentEnabled: true,
    searchAgentEnabled: true,
    searchApiKey: 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    agents: [
      {
        displayName: 'MyCustomAgent',
        agentId: 'XXXXXXXXX',
        aliasId: 'YYYYYYYY',
      },
    ],
    inlineAgents: true,
    // ガードレール
    guardrailEnabled: true,
    // GenU Cognito
    selfSignUpEnabled: true,
    allowedSignUpEmailDomains: ["hogehoge.co.jp"],
    // GenU Web アプリケーション
    hostName: 'genai',
    domainName: 'hogehoge.co.jp',
    hostedZoneId: 'XXXXXXXXXXXXXXXXXXXX',
    // GenU RAG (Kendra)
    ragEnabled: true,
    kendraIndexLanguage: 'jp',
    kendraIndexScheduleEnabled: true,
    kendraIndexScheduleCreateCron: { "minute": "0", "hour": "23", "month": "\*", "weekDay": "SUN-THU" },
    kendraIndexScheduleDeleteCron: { "minute": "0", "hour": "11", "month": "\*", "weekDay": "MON-FRI" }
    // モニタリングダッシュボード
    dashboard: true,
  },
};
```

- WAF: **あり**
  - IPv4 でのアクセス制限
  - 日本国内のみアクセス可能
- RAG (ナレッジベース) チャット: **あり**
  - 新規にナレッジベースを作成
  - OpenSearch Serverless をマルチ AZ で動作させる
  - Advanced Parsing を有効化
  - Re-ranking を有効化
  - クエリ分解 (Query Decomposition) を有効化
  - Binary Vector Embedding を有効化
- Agent チャット: **あり**
  - Web 検索エージェントも有効化
  - 独自エージェントを追加
  - インライン Agent モードで各ユースケースで Agent を利用可能に
- ガードレール (機密情報フィルタ): **あり**
- GenU: **あり**
  - Cognito ユーザプール, ID プール: **あり**
    - 企業ドメイン hogehoge.co.jp のメールアドレスであればユーザ自身でサインアップが可能
  - DynamoDB テーブル: **あり**
  - API GW (Lambda 関数): **あり**
  - CloudFront にホストされた Web アプリケーション: **あり**
    - 独自ドメイン genai.hogehoge.co.jp でアクセス可能
  - RAG (Amazon Kendra) チャット: **あり**
    - Kendra インデックスを新規作成
    - データソースを新規作成
    - Kendra インデックスのスケジュール作成/削除を有効化
      - 月曜日～金曜日の 08:00(JST)に Kendra インデックスの作成およびデータソースの同期
      - 月曜日～金曜日の 20:00(JST)に Kendra インデックスの削除
        ※約 64%のコスト削減
  - ユースケースビルダー: **あり**
  - 翻訳, 文字起こし: **あり**
- モニタリングダッシュボード: **あり**

以上で GenU のデプロイオプションの解説は完了です。

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

## (参考) GenU のバックエンド (CDK) 詳細解説投稿一覧

- [GenU のデプロイオプション詳細解説](https://qiita.com/siruko/items/49c43862007603f3f70c)
