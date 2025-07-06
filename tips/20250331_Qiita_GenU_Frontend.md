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
- [GenU のデプロイオプション詳細解説](https://qiita.com/siruko/items/49c43862007603f3f70c)

### GenU のフロントエンド

GenU のフロントエンドは Vite + React で記述されています。フロントエンドのソースコードは CDK の中で S3 に配置され、CloudFront のオリジンとして構築されます。
利用者は CloudFront ディストリビューションの URL でアクセスできる他、CloudFront + Route 53 + ACM にて独自ドメインでアクセスできます。

Web アプリケーションの実体は [packages/web](https://github.com/aws-samples/generative-ai-use-cases-jp/tree/56583580fbc767c70ca451a09cc98ce7c299b998/packages/web) 配下に格納されています。

```
web
├─public
│  └─images
├─src
│  ├─@types
│  ├─assets
│  ├─components
│  │  ├─useCaseBuilder
│  │  └─Writer
│  │      ├─extensions
│  │      ├─generative
│  │      ├─lib
│  │      ├─selectors
│  │      └─ui
│  ├─hooks
│  │  └─useCaseBuilder
│  ├─pages
│  │  └─useCaseBuilder
│  ├─prompts
│  │  └─diagrams
│  └─utils
└─tests
    └─use-case-builder
```

**なお、この記事に記載のコードは、あくまでもこの記事の執筆時点（2025/3/31）のもの** であることにご留意ください。

### GenU フロントエンドのビルド

GenU フロントエンドのビルドは、CDK で定義します。
[この記事](https://qiita.com/siruko/items/1063daa2efe0b374a3fc#generativeaiusecasesstack--web-%E3%83%AA%E3%82%BD%E3%83%BC%E3%82%B9)で説明した通り、実行ディレクトリは packages/cdk/で、npm run web:build コマンドを実行します。

```diff_typescript:packages/cdk/lib/construct/web.ts
    const build = new NodejsBuild(this, 'BuildWeb', {
      /* 省略 */
      destinationBucket: s3BucketInterface,
      distribution: cloudFrontWebDistribution,
      outputSourceDirectory: './packages/web/dist',
+     buildCommands: ['npm ci', 'npm run web:build'],
      /* 省略 */
    });
```

web:build コマンドは VITE_APP_VERSION=${npm_package_version} npm -w packages/web run build -- を実行するため、要は packages/web/package.json の build を実行します。

以下が package.json のソースコードです。

```diff_json:packages/web/package.json
{
  "name": "web",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
+   "build": "tsc && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview",
    "test": "vitest run"
  },
  "dependencies": {
    // 省略
  },
  "devDependencies": {
    // 省略
  }
}
```

`tsc && vite build` を実行しています。

さらに、vite build コマンドの実行結果を web.ts の `outputSourceDirectory: './packages/web/dist'` で指定する通り `packages/web/dist` に出力します。

また、web.ts の中で destinationBucket として [CloudFrontToS3](https://docs.aws.amazon.com/solutions/latest/constructs/aws-cloudfront-s3.html) が自動作成する S3 バケットを指定することで、S3 にアップロードされます。

最後に、web.ts の中で distribution として [CloudFrontToS3](https://docs.aws.amazon.com/solutions/latest/constructs/aws-cloudfront-s3.html) が自動作成する CloudFront ディストリビューションを指定することで、CloudFront + S3 でホストされます。

### GenU フロントエンドのルーティング

GenU フロントエンドのルーティングを解説します。
GenU フロントエンドは SPA で構成されており、[web/src/main.tsx](https://github.com/aws-samples/generative-ai-use-cases-jp/blob/56583580fbc767c70ca451a09cc98ce7c299b998/packages/web/src/main.tsx) にルーティング情報が書かれています。

- GenU ユースケースページ ([web/src/App.tsx](https://github.com/aws-samples/generative-ai-use-cases-jp/blob/56583580fbc767c70ca451a09cc98ce7c299b998/packages/web/src/App.tsx))
  - パス: React コンポーネント
  - `/`: LandingPage ※デフォルトページ
  - `/setting`: Setting
  - `/chat`: ChatPage
  - `/chat/:chatId`: ChatPage
  - `/share/:shareId`: SharedChatPage
  - `/generate`: GenerateTextPage
  - `/summarize`: SummarizePage
  - `/writer`: WriterPage
  - `/translate`: TranslatePage
  - `/web-content`: WebContent
  - `/image`: GenerateImagePage
  - `/video`: GenerateVideoPage
  - `/diagram`: GenerateDiagramPage
  - `/optimize`: OptimizePromptPage
  - `/transcribe`: TranscribePage
  - `/flow-chat`: FlowChatPage
  - `/videoAnalyzer`: VideoAnalyzerPage
  - `/rag`: RagPage
  - `/rag-knowledge-base`: RagKnowledgeBasePage
  - `/agent`: AgentChatPage
  - `/agent/:agentName`: RagPage
  - `/rag`: AgentChatPage
- GenU ユースケースビルダーページ ([web/src/UseCaseBuilderRoot.tsx](https://github.com/aws-samples/generative-ai-use-cases-jp/blob/56583580fbc767c70ca451a09cc98ce7c299b998/packages/web/src/UseCaseBuilderRoot.tsx))
  - パス: React コンポーネント
  - `/use-case-builder`: UseCaseBuilderSamplesPage
  - `/use-case-builder/my-use-case`: UseCaseBuilderMyUseCasePage
  - `/use-case-builder/new`: UseCaseBuilderEditPage
  - `/use-case-builder/edit/:useCaseId`: UseCaseBuilderEditPage
  - `/use-case-builder/execute/:useCaseId`: UseCaseBuilderExecutePage
  - `/use-case-builder/setting`: Setting
- 上記以外
  - NotFound

これらの URL で遷移できない場合は、該当のユースケースがデプロイされていない可能性があるため、[デプロイオプション](https://qiita.com/siruko/items/49c43862007603f3f70c#%E3%83%A6%E3%83%BC%E3%82%B9%E3%82%B1%E3%83%BC%E3%82%B9%E8%A1%A8%E7%A4%BA%E5%88%B6%E5%BE%A1%E3%81%AE%E3%83%87%E3%83%97%E3%83%AD%E3%82%A4%E3%82%AA%E3%83%97%E3%82%B7%E3%83%A7%E3%83%B3%E4%BE%8B)を再度確認してみてください。

今回は以上です。
次回はページごとの詳細仕様を解説していきます。

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

## (参考) GenU のデプロイオプション詳細解説投稿一覧

- [GenU のデプロイオプション詳細解説](https://qiita.com/siruko/items/49c43862007603f3f70c)
