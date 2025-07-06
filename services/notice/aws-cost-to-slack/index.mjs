import https from 'https';
import {
  CostExplorerClient,
  GetCostAndUsageCommand,
} from '@aws-sdk/client-cost-explorer';

// SlackのWebhook URL（環境変数から取得）
const SLACK_WEBHOOK_URL = process.env.SLACK_WEBHOOK_URL;

const threshold = 0.5; // 費用のしきい値（これを下回ると非表示）

export const handler = async () => {
  const target = new Date();

  // targetの前日までの月額期間を計算
  const period = getPeriod(target);

  // コストを取得
  const cost = await getCost(period);

  // Slack用通知情報を生成
  const body = makeBody(cost);
  console.log(JSON.stringify(body));

  // Slack通知
  await sendToSlack(body);
};

// 期間の取得
const getPeriod = (date) => {
  // 前日を基準日とし、1日からのコストを取得する
  date.setDate(date.getDate() - 1);
  const yyyy = date.getFullYear();
  const mm = `0${date.getMonth() + 1}`.slice(-2);
  const dd = date.getDate();

  return {
    Start: `${yyyy}-${mm}-01`,
    End: `${yyyy}-${mm}-${dd}`,
  };
};

// 金額の取得
const getCost = async (period) => {
  const client = new CostExplorerClient({ region: 'us-east-1' });
  const params = {
    TimePeriod: period,
    Granularity: 'MONTHLY',
    Metrics: ['UnblendedCost'],
    GroupBy: [
      {
        Type: 'DIMENSION',
        Key: 'SERVICE',
      },
    ],
  };

  try {
    const command = new GetCostAndUsageCommand(params);
    const data = await client.send(command);
    const cost = data.ResultsByTime[0];
    // console.log(JSON.stringify(cost));
    return cost;
  } catch (error) {
    console.error('エラー:', error);
  }
};

// 少数第二位で丸める
const round100 = (num) => (Math.round(num * 100) / 100).toFixed(1);

const makeBody = (cost) => {
  // オブジェクト取得
  const { TimePeriod, Groups } = cost;

  // コスト情報の抽出
  const { Start, End } = TimePeriod;
  const periodTxt = `${Start}～${End}`;
  const targetMonth = new Date(Start).getMonth() + 1;

  // サービスごとのコスト
  // コストの降順で並び替える
  Groups.sort(
    (a, b) => b.Metrics.UnblendedCost.Amount - a.Metrics.UnblendedCost.Amount
  );
  const costByServices = Groups.map((service) => {
    const name = service.Keys[0];
    const cost = Number(service.Metrics.UnblendedCost.Amount);

    // 少額は無視する
    const isDisp = threshold < cost;

    return isDisp
      ? {
          type: 'rich_text_section',
          elements: [
            {
              type: 'text',
              text: `${name}: `,
            },
            {
              type: 'text',
              text: `$${round100(cost)}`,
            },
          ],
        }
      : null;
  }).filter((x) => !!x);

  // リスト形式
  const costByServicesList =
    costByServices.length > 0
      ? {
          type: 'rich_text',
          elements: [
            {
              type: 'rich_text_list',
              style: 'bullet',
              indent: 0,
              elements: costByServices,
            },
          ],
        }
      : {
          type: 'section',
          text: {
            type: 'plain_text',
            text: '表示対象なし',
            emoji: true,
          },
        };

  // トータルコスト
  const totalCost = round100(
    Groups.reduce(
      (total, service) => total + Number(service.Metrics.UnblendedCost.Amount),
      0
    )
  );

  // Slackメッセージテンプレートを返却
  return {
    blocks: [
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: `${targetMonth}月の *AWS* 利用料金は *$${totalCost}* です\n※${periodTxt}の料金です`,
        },
      },
      {
        type: 'divider',
      },
      costByServicesList,
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: `($${round100(threshold)}以上のみ抜粋)`,
        },
      },
      {
        type: 'divider',
      },
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: ' ',
        },
        accessory: {
          type: 'button',
          text: {
            type: 'plain_text',
            text: 'AWSマネジメントコンソールにログインする',
            emoji: true,
          },
          value: 'click_to_console',
          url: 'https://0123456789012345.signin.aws.amazon.com/console',
          action_id: 'button-action',
        },
      },
    ],
  };
};

const sendToSlack = async (body) => {
  const payload = JSON.stringify(body);

  return new Promise((resolve, reject) => {
    const req = https.request(
      SLACK_WEBHOOK_URL,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(payload),
        },
      },
      (res) => {
        res.on('data', () => {});
        res.on('end', resolve);
      }
    );

    req.on('error', reject);
    req.write(payload);
    req.end();
  });
};
