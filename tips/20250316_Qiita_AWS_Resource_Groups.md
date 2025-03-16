## はじめに

皆さんは AWS リソースにタグをつけていますでしょうか？
タグをつけることで管理がしやすくなるため、複数のワークロードや機能を同一の AWS アカウントにデプロイする際は、タグをつけているのではないでしょうか。

この記事では、**「"Project: X"というタグがついたリソースを抽出して、今！」** と言われた時の手順を紹介します。

## AWS Resource Groups について

[AWS Resource Groups](https://docs.aws.amazon.com/ja_jp/ARG/latest/userguide/resource-groups.html) はタグを管理するサービスです。
タグでのリソース抽出や、タグの一括付与などを行えます。

## 事前準備

東京リージョンと大阪リージョンにテスト用の Lambda 関数を作成します。
タグには `Project: X` を付与します。

(東京リージョン: ap-northeast-1)
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/217144/f0e68d7d-187a-4f0c-87b4-2ecf502ed607.png)

(大阪リージョン: ap-northeast-3)
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/217144/e2bd8df1-5338-418e-9b4c-2e10fa877372.png)

## AWS Resource Groups でのタグ抽出

AWS Resource Groups のページを開きます。
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/217144/ba8aafb1-5160-4f7c-b2b3-b6f7031304be.png)

ここで、**リソースグループの作成** か **タグエディタ** を選びます。

- **リソースグループの作成** : 検索条件をリソースグループとして保存可能。同じ条件で何度も確認する場合に有用。ただし**同一リージョンのみ検索可能** 。
- **タグエディタ** : 検索条件を保存できないが、**クロスリージョンでも検索可能** 。

### リソースグループの作成

リソースグループの作成 > タグベース で条件を入れていきます。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/217144/fa48b52a-92d4-4128-82c8-3335e1b58f8d.png)

「グループリソースをプレビュー」リンクを押すと、指定したタグのついたリソースが表示されます。ただし、同一リージョンのリソースのみ表示されます。

(東京リージョンでの実行例)
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/217144/06326c1d-700a-484b-af23-85565f34c50a.png)

このままグループ名を入力して登録すると、次回以降は検索条件を設定せずにリソースを確認できます。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/217144/1f34d125-7557-48fc-be63-a357e44a7af9.png)

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/217144/68cab3a2-b76a-4665-8285-5036ea067407.png)

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/217144/bd0cd8de-1062-4e5d-a50f-e687282c750b.png)

### タグエディタ

次に、タグエディタでクロスリージョンの検索をします。

タグエディタ > All regions > All supported resourece types を選びます。
タグに `Project: X` を指定して、**リソースを検索** リンクを押します。
すると、「リソースの検索結果」欄に先ほど作成した、東京リージョンと大阪リージョンの関数が表示されます。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/217144/b71ddaff-25eb-452f-a132-998ae1d7dd96.png)

また、表示されたリソースのチェックボックスにチェックを入れ、**選択したリソースのタグを管理する** リンクを押します。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/217144/710b85cc-d517-4ae2-bd44-aa0a2f872fff.png)

次の画面では、`Project: X` の値を一律変更したり、新しいタグを一律で付与することができます。

![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/217144/b94f552f-f28e-4d91-a537-43931b58c7ad.png)

(Lambda 関数)
![image.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/217144/1d083894-c499-4fd5-b439-8e44f46888a8.png)

以上です。
