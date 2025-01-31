#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Basic example for a bot that works with polls. Only 3 people are allowed to interact with each
poll/quiz the bot generates. The preview command generates a closed poll/quiz, excatly like the
one the user sends the bot
"""
import logging

from telegram import (Poll, ParseMode, KeyboardButton, KeyboardButtonPollType,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, PollAnswerHandler, PollHandler, MessageHandler,
                          Filters)
from telegram.utils.helpers import mention_html
import pandas as pd 

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

CURRENT = 0
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

data = pd.read_csv("tests.csv", encoding="utf8")

def start(update, context):
    """Inform user about what this bot can do"""
    
    update.message.reply_text('Please select /quiz to get a Quiz')
    context.bot_data.update({'CURRENT': 0})
    print("start", context.bot_data)


def poll(update, context):
    """Sends a predefined poll"""
    print("THIS IS START STATE",context.bot_data)
    current = context.bot_data["CURRENT"]
    answers = ["Хорошо", "Рельно хорошо", "Фантастически", "Отлично"]
    answers = list(map(str, data['options'][current].split(",")))
    main_question = str(data['questions'][current])
    message = context.bot.send_poll(update.effective_user.id, main_question, answers,
                                    is_anonymous=False, allows_multiple_answers=False)
                                    
    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {message.poll.id: {"questions": answers, "message_id": message.message_id,
                                 "chat_id": update.effective_chat.id, "answers": 0}}
    context.bot_data.update(payload)
    print("context updated",context.bot_data)


def receive_poll_answer(update, context):
    """Summarize a users poll vote"""
    print(update, context, "receive_poll_answer")
    answer = update.poll_answer
    poll_id = answer.poll_id
    try:
        questions = context.bot_data[poll_id]["questions"]
    # this means this poll answer update is from an old poll, we can't do our answering then
    except KeyError:
        return
    selected_options = answer.option_ids
    answer_string = ""
    for question_id in selected_options:
        if question_id != selected_options[-1]:
            answer_string += questions[question_id] + " and "
        else:
            answer_string += questions[question_id]
    user_mention = mention_html(update.effective_user.id, update.effective_user.full_name)
    context.bot.send_message(context.bot_data[poll_id]["chat_id"],
                             "{} {}!".format(user_mention, answer_string),
                             parse_mode=ParseMode.HTML)
    context.bot_data[poll_id]["answers"] += 1
    
    cur = context.bot_data["CURRENT"] + 1
    print("CUR qustion", cur)
    all_data = context.bot_data
    all_data["CURRENT"] = cur
    context.bot_data.update(all_data)
    print("udated cur data", context.bot_data["CURRENT"])
    # Close poll after three participants voted
    # if context.bot_data[poll_id]["answers"] == 3:
    #     context.bot.stop_poll(context.bot_data[poll_id]["chat_id"],
    #                           context.bot_data[poll_id]["message_id"])


def quiz(update, context):
    """Send a predefined poll"""
    current = context.bot_data["CURRENT"]

    questions = ["1", "2", "4", "20"]
    questions = [item.strip() for item in list(map(str, data['options'][current].split(",")))]

    main_question = str(data['questions'][current])
    print(questions, str(data['right'][current]))
    right_id = questions.index(str(data['right'][current]))
    message = update.effective_message.reply_poll(main_question,
                                                  questions, type=Poll.QUIZ, correct_option_id=right_id, is_anonymous=False)
    # Save some info about the poll the bot_data for later use in receive_quiz_answer
    payload = {message.poll.id: {"chat_id": update.effective_chat.id,
                                 "message_id": message.message_id}}
    context.bot_data.update(payload)


def receive_quiz_answer(update, context):
    """Close quiz after three participants took it"""
    # cur = context.bot_data["CURRENT"] + 1
    # all_data = context.bot_data
    # all_data["CURRENT"] = cur
    # context.bot_data.update(all_data)
    print("RECIEVE QUIZ CUR")
    # the bot can receive closed poll updates we don't care about
    # if update.poll.is_closed:
    #     return
    # if update.poll.total_voter_count == 1:
    #     try:
    #         quiz_data = context.bot_data[update.poll.id]
    #         cur = context.bot_data["CURRENT"] + 1
    #         all_data = context.bot_data
    #         all_data["CURRENT"] = cur
    #         context.bot_data.update(all_data)
    #         print(cur)
    #     # this means this poll answer update is from an old poll, we can't stop it then
    #     except KeyError:
    #         return
    #     context.bot.stop_poll(quiz_data["chat_id"], quiz_data["message_id"])


def preview(update, context):
    """Ask user to create a poll and display a preview of it"""
    # using this without a type lets the user chooses what he wants (quiz or poll)
    button = [[KeyboardButton("Press me!", request_poll=KeyboardButtonPollType())]]
    message = "Press the button to let the bot generate a preview for your poll"
    # using one_time_keyboard to hide the keyboard
    update.effective_message.reply_text(message,
                                        reply_markup=ReplyKeyboardMarkup(button,
                                                                         one_time_keyboard=True))


def receive_poll(update, context):
    """On receiving polls, reply to it by a closed poll copying the received poll"""
    actual_poll = update.effective_message.poll
    # Only need to set the question and options, since all other parameters don't matter for
    # a closed poll
    update.effective_message.reply_poll(
        question=actual_poll.question,
        options=[o.text for o in actual_poll.options],
        # with is_closed true, the poll/quiz is immediately closed
        is_closed=True,
        reply_markup=ReplyKeyboardRemove()
    )


def help_handler(update, context):
    """Display a help message"""
    update.message.reply_text("Use /quiz, /poll or /preview to test this "
                              "bot.")


class MessageCounter:
    def __init__(self):
        
        self.counter = 0
        self.maxQuestions = len(data['questions']) -1
        self.update = None
    
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

        

def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    BOT = MessageCounter()
    updater = Updater("1181981103:AAGKnUqVXKu7OR5DDfMqXpuxn00uaCeOD-8", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    # dp.add_handler(CommandHandler('poll', poll))
    dp.add_handler(CommandHandler('quiz', BOT.custom_quiz))
    # dp.add_handler(CommandHandler('next-question', BOT.custom_quiz))
    # dp.add_handler(PollHandler(receive_quiz_answer))
    # dp.add_handler(CommandHandler('preview', preview))
    # dp.add_handler(MessageHandler(Filters.poll, receive_poll))
    # dp.add_handler(CommandHandler('help', help_handler))

    # dp.add_handler(PollAnswerHandler(receive_poll_answer))
    dp.add_handler(PollAnswerHandler(BOT.custom_quiz_handler))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()



main()