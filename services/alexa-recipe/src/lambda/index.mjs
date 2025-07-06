// alexaRecipeAssistant
// need Layer ask-sdk-core (NOT aws-sdk-core)
import Alexa from 'ask-sdk-core';
import { recipeInference } from './bedrock.mjs';

// デバッグ用ハンドラ
const DebugFallbackHandler = {
  canHandle() {
    // 何でも拾う
    return true;
  },
  handle(handlerInput) {
    // リクエスト内容をJSON文字列化
    const json = JSON.stringify(handlerInput.requestEnvelope, null, 2);
    console.log('DEBUG REQUEST:', json);
    console.log(
      'REQUEST TYPE',
      Alexa.getRequestType(handlerInput.requestEnvelope),
    );
    console.log(
      'INTENT NAME',
      Alexa.getIntentName(handlerInput.requestEnvelope),
    );

    // 初めに戻る
    return LunchSuggestionIntentHandler.handle(handlerInput);
  },
};

// 起動時の挨拶
const LaunchRequestHandler = {
  canHandle(handlerInput) {
    return (
      Alexa.getRequestType(handlerInput.requestEnvelope) === 'LaunchRequest'
    );
  },
  handle(handlerInput) {
    return handlerInput.responseBuilder
      .speak('はーい、レシッピです。昼食、夕食どちらのメニューを考えますか？')
      .reprompt('昼食、夕食どちらのメニューを考えますか？')
      .getResponse();
  },
};

const whichMenu = (handlerInput) => {
  const intent = Alexa.getIntentName(handlerInput.requestEnvelope);
  switch (intent) {
    case 'LunchSuggestionIntent':
      return '昼食';
    case 'DinerSuggestionIntent':
      return '夕食';
    default:
      return '';
  }
};
// 献立候補の返却
const MenuSuggestionIntentHandler = {
  canHandle(handlerInput) {
    return (
      Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest' &&
      ['LunchRecipeSuggestIntent', 'DinerRecipeSuggestIntent'].includes(
        Alexa.getIntentName(handlerInput.requestEnvelope),
      )
    );
  },
  async handle(handlerInput) {
    const menu = whichMenu(handlerInput);
    const ingredients = Alexa.getSlotValue(
      handlerInput.requestEnvelope,
      'ingredients',
    );
    const slot = handlerInput.requestEnvelope.request.intent.slots.ingredients;

    if (slot) {
      const ingredients = slot.value;
      const status = slot.confirmationStatus;

      if (status === 'CONFIRMED') {
        const result = await recipeInference({ ingredients });
        const { status, candidates } = JSON.parse(result);
        console.log({ status, candidates });
        if (status === 'error') {
          return handlerInput.responseBuilder
            .speak(`申し訳ありません。最適な料理が見つかりませんでした。`)
            .withShouldEndSession(true)
            .getResponse();
        }
        const speakText = `
          <speak>
            ${ingredients}ですね。${
          menu && 'これを使った' + menu + 'を考えます。'
        }
            <break time="1s"/>
            ${candidates.join('、')}
            はいかがでしょうか。
          </speak>
        `;
        console.log(speakText);

        return handlerInput.responseBuilder
          .speak(speakText)
          .withShouldEndSession(true)
          .getResponse();
      }
      if (status === 'DENIED') {
        return handlerInput.responseBuilder
          .speak(`では他に使いたい食材はありますか？`)
          .reprompt('他に使いたい食材を教えてください。')
          .getResponse();
      }

      // まだ確認されていない場合
      return handlerInput.responseBuilder
        .addConfirmSlotDirective('ingredients')
        .speak(`${ingredients}を使います。よろしいですか？`)
        .reprompt(`${ingredients}でよろしいですか？`)
        .getResponse();
    }

    return handlerInput.responseBuilder
      .speak(`${menu && menu + 'ですね。'} 使いたい食材はありますか？`)
      .reprompt('どんな食材を使いますか？')
      .getResponse();
  },
};

export const handler = Alexa.SkillBuilders.custom()
  .addRequestHandlers(
    LaunchRequestHandler,
    MenuSuggestionIntentHandler,
    DebugFallbackHandler,
  )
  .lambda();
