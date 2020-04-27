#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ЭТО ОЧЕНЬ ПЛОХОЙ КОД ПОЖАЛУЙСТА НЕ ЧИТАЙ ЕГО
"""
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
from telegram import (Poll, ParseMode, KeyboardButton, KeyboardButtonPollType,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove, Game, InlineQueryResultGame, InlineQuery)
from telegram.ext import (Updater, CommandHandler, PollAnswerHandler, PollHandler, MessageHandler,
                          Filters, CallbackQueryHandler)
from telegram.utils.helpers import mention_html
import pandas as pd 
import os
from natsort import natsorted

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

CURRENT = 0
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# data = pd.read_csv("./all_tests/tests.csv", encoding="utf8")


class MessageCounter:
    def __init__(self, bot2):
        
        self.counter = 0
        self.maxQuestions = 0#len(self.data['questions']) -1
        self.update = None
        self.data = None #pd.read_csv("./all_tests/tests.csv", encoding="utf8")

        search_file = sorted(os.listdir("./all_tests"))
        

        self.keyboard = [[InlineKeyboardButton("{}.{} {}".format(i+1, 'Тест по', search_file[i][3:-4]), callback_data='t{}'.format(i))] 
        for i in range(len(sorted(os.listdir("./all_tests"))))]

        self.keyboard.append([InlineKeyboardButton("Назад", callback_data="BACK")])

        self.reply_markup = InlineKeyboardMarkup(self.keyboard)
        self.bot2 = bot2
        self.timerDuration = 1
        self.score = 0
        self.hasStikers = True

    #     self.timer = self.Timer()

    # def Timer(self):
    def score_word(self):
        if self.score == 0:
            return "Ноль тоже результат, покури доки, почитай форумы и возвращайся, успехов!"
        elif self.score > 0 and self.score < 2:
            return "Ты очень старался и даже что-то заработал, но можно лучше :)"
        elif self.score > 1 and self.score < 4:
            return "А вот это уже заявочка! Я уверен что в следующий раз этот тест не устоит под твоим натиском"
        elif self.score > 3 and self.score < 6:
            return "Вот это ты разогнался конечно, моё уважение"
        elif self.score > 5:
            return "Либо это вы составляли тест, либо действительно очень много знаете, снимаю шляпу"


    def custom_quiz(self, update, context):
        """Send a predefined poll"""
        print(self, update, context)
        current = self.counter
        self.update = update

        questions = [item.strip() for item in list(map(str, self.data['options'][current].split("###")))]
        main_question = str(self.data['questions'][current])
        right_id = int(self.data['right'][current])
        self.update.message.reply_text("ВОПРОС №{}".format(current))
        # print(questions, str(data['right'][current]))

        text = ""
        if str(self.data['image'][current]) != 'nan':
            text = str(self.data['image'][current])
            self.update.message.reply_text(text=text, parse_mode=ParseMode.HTML)

        message = update.effective_message.reply_poll(main_question,
                                                    questions, type=Poll.QUIZ, correct_option_id=right_id, is_anonymous=False,)
        # Save some info about the poll the bot_data for later use in receive_quiz_answer
        payload = {message.poll.id: {"chat_id": update.effective_chat.id,
                                    "message_id": message.message_id}}
        context.bot_data.update(payload)
        self.update = update

        # self.set_timer(update, context)

    def select_quiz(self, update, context):

        update.message.reply_text('Выберете тест, который хотите пройти:', reply_markup=self.reply_markup)
        self.update = update
        self.counter = 0
        self.score = 0

    def custom_quiz_handler(self, update, context):
        print("RECIEVE QUIZ CUR", context.user_data)
        print('MESSAGE ==="%s"',  update["poll_answer"]['option_ids'][0])
        if self.counter < self.maxQuestions:
            user_answer = int(update["poll_answer"]['option_ids'][0])
            if self.data['right'][self.counter] == user_answer:
                self.score += 1
                print("=======CORRECT========")
            self.counter += 1
            current = self.counter

            questions = [item.strip() for item in list(map(str, self.data['options'][current].split("###")))]
            main_question = str(self.data['questions'][current])
            right_id = int(self.data['right'][current])

            # print(questions, str(data['right'][current]))
            self.update.message.reply_text("ВОПРОС №{}".format(current))
            text = ""
            if str(self.data['image'][current]) != 'nan':
                text = str(self.data['image'][current])
                self.update.message.reply_text(text=text, parse_mode=ParseMode.HTML)

            message = self.update.effective_message.reply_poll(main_question,
                                                        questions, type=Poll.QUIZ, correct_option_id=right_id, is_anonymous=False)
            # Save some info about the poll the bot_data for later use in receive_quiz_answer
            payload = {message.poll.id: {"chat_id": update.effective_chat.id,
                                        "message_id": message.message_id}}
            context.bot_data.update(payload)
            
            self.update = update

        else:
            user_answer = int(update["poll_answer"]['option_ids'][0])
            if self.data['right'][self.counter] == user_answer:
                print("=======CORRECT========")
            print("again")
            if self.hasStikers:
                self.update.message.reply_text('🎉🎉🎉\nТест окончен, вас счет {}/{} => {}\nНезависимо от результата <a href="https://t.me/addstickers/SuperProger">держи стикеры</a>, спасибо что был с нами\nМожете попробовать другие /quiz\nИли выбрать другой раздел /start'.format(self.score, self.maxQuestions, self.score_word()), parse_mode=ParseMode.HTML) 
            else:
                self.update.message.reply_text('🎉🎉🎉\nТест окончен, вас счет {}/{} => {}\nМожете попробовать другие /quiz\nИли выбрать другой раздел /start'.format(self.score, self.maxQuestions, self.score_word())) 
            self.hasStikers = False
            self.counter = 0
            self.score = 0



    
    def start(self, update, context):
        """Inform user about what this bot can do"""
        
        update.message.reply_text("""Привет! Я твой виртуальный помощник от компании "Гринатом". 👾

Ты уже крутой профессионал 😎 или хочешь узнать свои зоны роста 🚀?

С моей помощью ты можешь проверить свои силы в тестах по программированию и английскому языку, нажав /quiz 🔥

А если ты уже достаточно уверен_а в себе, можешь сразу пройти /interview в нашу компанию, оставив свои контактные данные для связи. 🧳

Устал_а от культа продуктивности и хочется просто отдохнуть? Жми /game и собирай алмазы между тестами 💎

Кстати! По итогам их успешного прохождения тебя ждёт сюрприз 🎁, и также не забывай добавлять меня в IT-шные беседы для групповых викторин 🤓 """)
        context.bot_data.update({'CURRENT': 0})
        self.update = update
        self.counter = 0
        self.hasStikers = True
        self.score = 0
        print("start", context.bot_data)
    
    def button2(self, update, context):
        query = update.callback_query.data
        print('HELLO FROM GAME"%s"', query)
        # CallbackQueries need to be answered, even if no notification to the user is needed
        # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
        # query.answer()

        # if update.callback_query.game_short_name != 'super_game':
        #     context.bot.answerCallbackQuery(update.callback_query.id, "Sorry, '" + update.callback_query.game_short_name + "' is not available.")
        # else:
        #     # queries[query.id] = query
        #     gameurl = "https://ugly-game.firebaseapp.com?id="+update.callback_query.id
        #     context.bot.answerCallbackQuery(
        #         callback_query_id=update.callback_query.id,
        #         url=gameurl
        #     )
        if update.callback_query.game_short_name == 'super_game':
            gameurl = "https://ugly-game.firebaseapp.com?id="+update.callback_query.id
            context.bot.answerCallbackQuery(
                callback_query_id=update.callback_query.id,
                url=gameurl
            )
        else:
            if query == "BACK":
                print('BACK')
            elif query[:1] == "t":
                pos = int(query[1:])
                print("POS ", pos, sorted(os.listdir("./all_tests")))
                search_file = sorted(os.listdir("./all_tests"))[pos]
                self.data = pd.read_csv("./all_tests/"+ search_file, encoding="utf8")
                print("DATA", self.data)
                self.maxQuestions = len(self.data['questions']) -1
                self.custom_quiz(self.update, context)
            else:
                self.bot2.button(update, context)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

class ConversationBot:
    def __init__(self):
        self.current = 0
        self.update = None
        self.questionList = self.load_questions('questions.csv')
        self.keyboard = [[InlineKeyboardButton("{}.{}".format(i+1, self.questionList[i]), callback_data=i)] 
        for i in range(len(self.questionList))]

        self.keyboard.append([InlineKeyboardButton("Завершить", callback_data="DONE")])

        self.reply_markup = InlineKeyboardMarkup(self.keyboard)
        self.user_data = {}
        self.isStart = False
        self.maxQuestions = len(self.questionList)-1
        self.df = pd.read_csv('questions.csv',)

        self.df['answer'] = "" 

    def load_questions(self, file_name):
        df = pd.read_csv(file_name)
        list_of_questions = [str(item) for item in df['question']]
        return list_of_questions


    def interview(self, update, context):
    
        update.message.reply_text('Пожалуйста ответьте на каждый из пунктов:', reply_markup=self.reply_markup)
        self.update = update
        self.user_data = {}
        self.isStart = True
    
    def help(self, update, context):
        update.message.reply_text("Use /start to test this bot.")
    
    def button(self, update, context):
        query = update.callback_query

        # CallbackQueries need to be answered, even if no notification to the user is needed
        # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
        # query.answer()
        print(query.data)
        if query.data[:1] != "t":
            if query.data == "DONE":
                context.bot.send_message(chat_id=update.effective_chat.id, text=self.facts_to_str())
                self.update.message.reply_text("Держи файл с твоими ответами:")
                self.df.to_csv('interview.csv', index = False, header=True, encoding='utf-8-sig')
                context.bot.send_document(chat_id=update.effective_chat.id, document=open('interview.csv', 'rb'))
                self.update.message.reply_text("Также ты можешь пройти тесты /quiz или сыграть в игру /game")
            
            else:
            
                self.current = query.data

                query.edit_message_text(text="{} : {}".format(int(query.data)+1, self.questionList[int(query.data)]))
        else:
            print("TEST ACTIVATED")
    
    def facts_to_str(self):
        facts = list()

        for key in self.user_data.keys():
            facts.append('{}.{} - {}'.format(int(key[9:])+1, self.questionList[int(key[9:])], self.user_data[key]))
        facts.reverse()
        return "\n".join(facts).join(['\n', '\n'])

    def echo(self, update, context):
        if self.isStart:
            text = update.message.text

            self.user_data['question_'+str(self.current)] = text.encode('utf8')
            self.df['answer'][self.current] = text.encode('utf8')
            context.bot.send_message(chat_id=update.effective_chat.id, text=self.facts_to_str())
            self.update.message.reply_text('Пожалуйста ответьте на каждый из пунктов:', reply_markup=self.reply_markup)     

       
  
def game(update, context):
    print("GAME", update, context, context.bot.send_game)
    context.bot.send_game(update.effective_chat.id, "super_game")

def hand_game_answer(update, context, qwe, asd, zxc):
    print("hand_game_answer")

def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
  
    BOT2 = ConversationBot()
    BOT = MessageCounter(BOT2)
    updater = Updater("1181981103:AAGKnUqVXKu7OR5DDfMqXpuxn00uaCeOD-8", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', BOT.start))
    dp.add_handler(CommandHandler('quiz', BOT.select_quiz))
    dp.add_handler(CommandHandler('interview', BOT2.interview))
    dp.add_handler(PollAnswerHandler(BOT.custom_quiz_handler))
    updater.dispatcher.add_error_handler(error)
    updater.dispatcher.add_handler(CallbackQueryHandler(BOT.button2))
    

    # dp.add_handler(CallbackQueryHandler(game_query_hand, "game"))
    dp.add_handler(CommandHandler('game', game))
    # dp.add_handler(InlineQuery(hand_game_answer))

    updater.dispatcher.add_handler(CallbackQueryHandler(BOT2.button))
    echo_handler = MessageHandler(Filters.text, BOT2.echo)
    updater.dispatcher.add_handler(echo_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()



main()