import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
import json

slovar = {}
with open("questions.json", encoding="utf-8") as file:
    data = json.load(file)


def viktorina(vk, event, user_id):
    if slovar[user_id]['user_state'] == 'waiting answer':
        otvet = event.obj.message['text'].lower()
        if otvet == data["questions"][slovar[user_id]['number_of_question']]['right']:
            slovar[user_id]['right_answer'] += 1
        slovar[user_id]['number_of_question'] += 1
        slovar[user_id]['user_state'] = 'waiting question'
    if slovar[user_id]['number_of_question'] < len(data['questions']):
        quest = data["questions"][slovar[user_id]['number_of_question']]['question']
        keyboard = VkKeyboard(inline=True)
        for ind, value in enumerate(data["questions"][slovar[user_id]['number_of_question']]["answers"]):
            keyboard.add_button(value, color=VkKeyboardColor.PRIMARY)
            if ind < len(data["questions"][slovar[user_id]['number_of_question']]["answers"]) - 1:
                keyboard.add_line()
        vk.messages.send(user_id=user_id,
                         message=quest,
                         random_id=random.randint(0, 2 ** 64),
                         keyboard=keyboard.get_keyboard())
        slovar[user_id]['user_state'] = 'waiting answer'
    else:
        vk.messages.send(user_id=user_id,
                         message=f"Всё! Вопросы кончились! Вы ответили правильно на {slovar[user_id]['right_answer']} вопрос(а) из {len(data['questions'])} возможных:)",
                         random_id=random.randint(0, 2 ** 64))
        slovar[user_id]['user_state'] = None


def main():
    vk_session = vk_api.VkApi(
        token="vk1.a.-93K-Rdj2RfJ_nAcg8FWlTKcRWtuZAHzY5ZMWdxUvgMNR2P47cqZEC9KNMY1SOOSFSBElNVLIAAiE6idhU10m-5ecU0O08Eqgu5iRZq1AqyAQpwU58hAC0BSJ4bJ3eCc-7XCY6PPKBrFkafMgybDICCxVgeMQlfRVaclAy3-1-JzYv1t_WH2dW37yV0xEvej8PEuNNpL94TrgmJgBORMUw")
    longpoll = VkBotLongPoll(vk_session, 226466660)
    vk = vk_session.get_api()
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.obj.message['from_id']
            if user_id not in slovar.keys():
                slovar[user_id] = {}
            if slovar[user_id].get('user_state') is None:
                keyboard = VkKeyboard(one_time=True, inline=False)
                keyboard.add_button('ДА', color=VkKeyboardColor.POSITIVE)
                keyboard.add_button('НЕТ', color=VkKeyboardColor.NEGATIVE)
                vk.messages.send(user_id=user_id,
                                 message="Дратуте! Го сыгранём в викторину! Жми на кнопку!",
                                 random_id=random.randint(0, 2 ** 64),
                                 keyboard=keyboard.get_keyboard())
                slovar[user_id]['user_state'] = 'waiting start game'
            elif slovar[user_id]['user_state'] == 'waiting start game':
                otvet = event.obj.message['text']
                if otvet == 'ДА':
                    slovar[user_id]['number_of_question'] = 0
                    slovar[user_id]['right_answer'] = 0
                    slovar[user_id]['user_state'] = 'waiting question'
                    viktorina(vk, event, user_id)
                elif otvet == 'НЕТ':
                    vk.messages.send(user_id=user_id,
                                     message=":(",
                                     random_id=random.randint(0, 2 ** 64))
                    slovar[user_id]['user_state'] = None
                else:
                    keyboard = VkKeyboard(one_time=True, inline=False)
                    keyboard.add_button('ДА', color=VkKeyboardColor.POSITIVE)
                    keyboard.add_button('НЕТ', color=VkKeyboardColor.NEGATIVE)
                    vk.messages.send(user_id=user_id,
                                     message="Тыкни, пожалуйста, на кнопочку",
                                     random_id=random.randint(0, 2 ** 64),
                                     keyboard=keyboard.get_keyboard())
                    slovar[user_id]['user_state'] = 'waiting start game'
            elif slovar[user_id]['user_state'] == 'waiting question' or slovar[user_id]['user_state'] == 'waiting answer':
                viktorina(vk, event, user_id)


if __name__ == '__main__':
    main()
