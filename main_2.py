#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Basic example for a bot that uses inline keyboards.
"""
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
from telegram.ext import MessageHandler, Filters
import pandas as pd 

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    keyboard = [[InlineKeyboardButton("1.Где вы учились, проходили стажировку, работали?", callback_data='1')],
                [InlineKeyboardButton("2.Какой ваш основной метод саморазвития: лекции, курсы, профессиональная литература?", callback_data='2')],

                [InlineKeyboardButton("3.Какими языками программирования вы владеете? Например, Java, Kotlin, Python и др.", callback_data='3')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Пожалуйста ответьте на каждый из пунктов:', reply_markup=reply_markup)




def button(update, context):
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    query.edit_message_text(text="Selected option: {}".format(query.data))
    


def help(update, context):
    update.message.reply_text("Use /start to test this bot.")


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


    def start(self, update, context):
    
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
            self.df.to_csv('some.csv', index = False, header=True, encoding='utf-8-sig')
            context.bot.send_document(chat_id=update.effective_chat.id, document=open('some.csv', 'rb'))
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
    updater = Updater("1181981103:AAGKnUqVXKu7OR5DDfMqXpuxn00uaCeOD-8", use_context=True)
    BOT = ConversationBot()

    updater.dispatcher.add_handler(CommandHandler('start', BOT.start))
    updater.dispatcher.add_handler(CallbackQueryHandler(BOT.button))
    updater.dispatcher.add_handler(CommandHandler('help', BOT.help))
    updater.dispatcher.add_error_handler(error)

    echo_handler = MessageHandler(Filters.text, BOT.echo)
    updater.dispatcher.add_handler(echo_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()



main()
