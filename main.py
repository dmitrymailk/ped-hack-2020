#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Basic example for a bot that works with polls. Only 3 people are allowed to interact with each
poll/quiz the bot generates. The preview command generates a closed poll/quiz, excatly like the
one the user sends the bot
"""
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
from telegram import (Poll, ParseMode, KeyboardButton, KeyboardButtonPollType,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, PollAnswerHandler, PollHandler, MessageHandler,
                          Filters)
from telegram.utils.helpers import mention_html
import pandas as pd 
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

CURRENT = 0
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

data = pd.read_csv("./all_tests/tests.csv", encoding="utf8")


class MessageCounter:
    def __init__(self):
        
        self.counter = 0
        self.maxQuestions = len(data['questions']) -1
        self.update = None
        self.data = pd.read_csv("./all_tests/tests.csv", encoding="utf8")

        self.keyboard = [[InlineKeyboardButton("{}.{}".format(i+1, 'Тест'), callback_data='t{}'.format(i))] 
        for i in range(len(os.listdir("./all_tests")))]

        self.keyboard.append([InlineKeyboardButton("Завершить", callback_data="BACK")])

        self.reply_markup = InlineKeyboardMarkup(self.keyboard)
    
    def custom_quiz(self, update, context):
        """Send a predefined poll"""
        print(self, update, context)
        current = self.counter
        self.update = update

        questions = [item.strip() for item in list(map(str, data['options'][current].split("###")))]
        main_question = str(data['questions'][current])
        right_id = int(data['right'][current])
        self.update.message.reply_text("ВОПРОС №{}".format(current))
        # print(questions, str(data['right'][current]))

        text = ""
        if str(data['image'][current]) != 'nan':
            text = str(data['image'][current])
            self.update.message.reply_text(text=text, parse_mode=ParseMode.HTML)

        message = update.effective_message.reply_poll(main_question,
                                                    questions, type=Poll.QUIZ, correct_option_id=right_id, is_anonymous=False,)
        # Save some info about the poll the bot_data for later use in receive_quiz_answer
        payload = {message.poll.id: {"chat_id": update.effective_chat.id,
                                    "message_id": message.message_id}}
        context.bot_data.update(payload)
        self.update = update

    def custom_quiz_handler(self, update, context):
        print("RECIEVE QUIZ CUR")
        if self.counter < self.maxQuestions:
            self.counter += 1
            current = self.counter

            questions = [item.strip() for item in list(map(str, data['options'][current].split("###")))]
            main_question = str(data['questions'][current])
            right_id = int(data['right'][current])

            # print(questions, str(data['right'][current]))
            self.update.message.reply_text("ВОПРОС №{}".format(current))
            text = ""
            if str(data['image'][current]) != 'nan':
                text = str(data['image'][current])
                self.update.message.reply_text(text=text, parse_mode=ParseMode.HTML)

            message = self.update.effective_message.reply_poll(main_question,
                                                        questions, type=Poll.QUIZ, correct_option_id=right_id, is_anonymous=False)
            # Save some info about the poll the bot_data for later use in receive_quiz_answer
            payload = {message.poll.id: {"chat_id": update.effective_chat.id,
                                        "message_id": message.message_id}}
            context.bot_data.update(payload)
            self.update = update

        else:
            print("again")
            self.update.message.reply_text('Quiz is end. You can try again /start') 
            self.counter = 0
    
    def start(self, update, context):
        """Inform user about what this bot can do"""
        
        update.message.reply_text('Выберете /quiz для того чтобы пройти тест\nВыберете /interview для того чтобы пройти интервью')
        context.bot_data.update({'CURRENT': 0})
        update.message.reply_text('Выберете тест, который хотите пройти:', reply_markup=self.reply_markup)
        print("start", context.bot_data)
    
    def button2(self, update, context):
        query = update.callback_query

        # CallbackQueries need to be answered, even if no notification to the user is needed
        # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
        # query.answer()
        print(query.data)


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
    
        if query.data == "DONE":
            context.bot.send_message(chat_id=update.effective_chat.id, text=self.facts_to_str())
            self.update.message.reply_text("Держи файл с твоими ответами:")
            self.df.to_csv('interview.csv', index = False, header=True, encoding='utf-8-sig')
            context.bot.send_document(chat_id=update.effective_chat.id, document=open('interview.csv', 'rb'))
        
        else:
        
            self.current = query.data

            query.edit_message_text(text="{} : {}".format(int(query.data)+1, self.questionList[int(query.data)]))
    
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

def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    BOT = MessageCounter()
    BOT2 = ConversationBot()
    updater = Updater("1181981103:AAGKnUqVXKu7OR5DDfMqXpuxn00uaCeOD-8", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', BOT.start))
    dp.add_handler(CommandHandler('quiz', BOT.custom_quiz))
    dp.add_handler(CommandHandler('interview', BOT2.interview))
    dp.add_handler(PollAnswerHandler(BOT.custom_quiz_handler))
   
    updater.dispatcher.add_handler(CallbackQueryHandler(BOT2.button))
    echo_handler = MessageHandler(Filters.text, BOT2.echo)
    updater.dispatcher.add_handler(echo_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()



main()