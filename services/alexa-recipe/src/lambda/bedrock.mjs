import {
  BedrockRuntimeClient,
  InvokeModelCommand,
} from '@aws-sdk/client-bedrock-runtime';
import {
  FAVORITE_CATEGORIES,
  FAVORITE_FOODS,
  FAVORITE_MATERIALS,
} from './const.mjs';
console.log({ FAVORITE_CATEGORIES, FAVORITE_FOODS, FAVORITE_MATERIALS });

const client = new BedrockRuntimeClient({ region: 'us-east-1' });

export const getBodyParam = function (body, name) {
  if (!body) return '';
  if (!body[name]) return '';
  return body[name];
};

export const error400 = function () {
  console.error('No user prompt provided');
  return {
    statusCode: 400,
    body: JSON.stringify({ message: 'No user prompt provided' }),
    headers: {
      'Access-Control-Allow-Origin': '*', // 全オリジン許可。セキュリティに応じて適宜変更
      'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    },
  };
};

export const recipeInference = async ({ ingredients }) => {
  console.log('Received ingredients:', ingredients);

  const dynamicPrompt = `
    あなたは料理アシスタントです。以下のルールを守り、家庭向け献立を最大5つ提案してください。
    
    # 必ず守るルール
    - 「必ず使用する食材」を、一般的に使用する料理を提案すること
    - 具体的な料理名を提案すること
        - NG: 中華、イタリアン
    - 出力は「出力形式」に沿ったJSONのみとし、他の文は必ず出力しないこと

    # できれば守るルール
    - 日本の家庭で食べる料理にすること
    - 中華、イタリアン、肉、魚、麺、ごはんなど幅広いジャンルを含めること
    - 「ユーザの好み（カテゴリ、料理、食材）」を可能な限り取り入れつつ、それ以外も提案すること
    
    # 必ず使用する食材
    ${ingredients}

    # 出力形式
    {"candidates":["料理1","料理2","料理3","料理4","料理5"]}
    
    # ユーザの好み
    カテゴリ: ${FAVORITE_CATEGORIES.join(', ')}
    料理: ${FAVORITE_FOODS.join(', ')}
    食材: ${FAVORITE_MATERIALS.join(', ')}
    
  `;

  console.log(ingredients);
  console.log(dynamicPrompt);

  const promptPrefix = '\n\nHuman:';
  const promptSuffix = '\n\nAssistant: ';
  const inputPrompt = `${promptPrefix}${dynamicPrompt}${promptSuffix}`;

  console.log(inputPrompt);

  const input = {
    // modelId: "apac.anthropic.claude-3-5-sonnet-20240620-v1:0",
    // modelId: "apac.anthropic.claude-3-5-sonnet-20241022-v2:0",
    modelId: 'anthropic.claude-3-haiku-20240307-v1:0',
    body: JSON.stringify({
      anthropic_version: 'bedrock-2023-05-31',
      max_tokens: 1000,
      messages: [
        {
          role: 'user',
          content: [{ type: 'text', text: inputPrompt }],
        },
      ],
    }),
    accept: 'application/json',
    contentType: 'application/json',
  };

  try {
    const data = await client.send(new InvokeModelCommand(input));
    const jsonString = Buffer.from(data.body).toString('utf8');
    const parsedData = JSON.parse(jsonString);

    // APIレスポンスの構造をログに出力
    console.log('API Response:', parsedData);

    // completionが存在するかをチェック
    if (parsedData.content && parsedData.content.length > 0) {
      const text = parsedData.content[0].text;
      console.log('Generated text:', text);
      return JSON.stringify({
        status: 'success',
        candidates: JSON.parse(text).candidates,
      });
    } else {
      return JSON.stringify({
        status: 'error',
        candidates: null,
      });
    }
  } catch (error) {
    console.error('Error calling model:', error);
    return JSON.stringify({
      status: 'error',
      candidates: null,
    });
  }
};
