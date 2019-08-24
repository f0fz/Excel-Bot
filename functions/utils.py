#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from functions.init import PERSON, rList, adminID, ADMIN_START, ADMIN_END
from functions import excel
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

admin_reply_keyboard = [['1', '2', '3', '4'], ['5', '6', '7', '8']]
admin_markup = ReplyKeyboardMarkup(admin_reply_keyboard, one_time_keyboard=True)
remove = ReplyKeyboardRemove(remove_keyboard=True)

#######################


def validate_nric(nric):
    if len(nric) == 5:
        if nric[:4].isdigit() and nric[4].isalpha():
            return True
    return False


def adminHelp(bot, update):
    helpText = '''AVAILABLE COMMANDS:
    
Attendance stats - /aStats
Gives you the total and currently registered number of participants.

Feedback stats - /fStats
Gives you the current number of feedback responses.

Attendance file - /aFile
Sends you the most updated Excel file for attendance.

Feedback file - /fFile
Sends you the most updated Excel file for feedback.
'''
    if update.message.chat_id in adminID:
        update.message.reply_text(helpText)
    else:
        update.message.reply_text("You are not recognised!")


def attendanceStats(bot, update):
    if update.message.chat_id in adminID:
        count = 0
        total = 0
        for each in PERSON:
            total += 1
            if each['GRP1_REG'] == 'P':
                count += 1
        update.message.reply_text("Good day, admin.\nTotal: {}, Present: {}".format(total, count))
        logger.info("Admin initiates stats report.\nTotal: {}, Present: {}".format(total, count))
    else:
        update.message.reply_text("You are not recognised!")


def feedbackStats(bot, update):
    if update.message.chat_id in adminID:
        update.message.reply_text("Good day, admin.\nTotal replies: {}".format(rList.llen('Feedback')))
        logger.info("Admin initiates stats report.\nTotal replies: {}".format(rList.llen('Feedback')))
    else:
        update.message.reply_text("You are not recognised!")


def chatID(bot, update):
    update.message.reply_text(update.message.chat_id)


def sendAttendanceFile(bot, update):
    if update.message.chat_id in adminID:
        update.message.reply_text("Good day, admin")
        logger.info("Admin requests latest attendance")
        excel.createFile_sem()
        bot.send_document(update.message.chat_id, document=open('Attendance.xlsx', 'rb'))
    else:
        update.message.reply_text("You are not recognised!")


def sendFeedbackFile(bot, update):
    if update.message.chat_id in adminID:
        update.message.reply_text("Good day, admin")
        logger.info("Admin requests latest feedback")
        excel.createFile_fb()
        bot.send_document(update.message.chat_id, document=open('Feedback.xlsx', 'rb'))
    else:
        update.message.reply_text("You are not recognised!")


def getChatText(promptID):
    chatText = rList.get(promptID).decode('utf-8')
    return chatText


def startChangeChat(bot, update, user_data, args):
    updateMessage = "Good day, admin. You have requested to change the chat text. "\
                    "Which one of the 8 text prompts do you want to change?\n\n"\
                    "1. Start of attendance taking\n2. Wrong NRIC message\n3. End of attendance taking\n"\
                    "4. Start of feedback\n5-7. Questions 1-3\n8. End of feedback"

    if update.message.chat_id in adminID:
        logger.info("Admin requests to change chat text")
        if not args:  # if arguments have not been passed, send update message and go to ADMIN_START
            update.message.reply_text(updateMessage, markup=admin_markup)
            return ADMIN_START
        else:
            # if arguments have been passed, pass arguments into receiveChatToChange
            return receiveChatToChange(bot, update, user_data, args[0])  # go straight to ADMIN_END or back to ADMIN_START
    else:
        update.message.reply_text("You are not recognised!")
        return ConversationHandler.END


def receiveChatToChange(bot, update, user_data, admin_state='0'):
    if admin_state not in ['1', '2', '3', '4', '5', '6', '7', '8']:
        update.message.reply_text("Invalid number. Please try again.")
        return ADMIN_START  # go from start again to re-enter number

    admin_state = "TEXT" + admin_state  # in rList, the key is TEXT1 for the 'Start of attendance taking' text
    user_data["ADMIN_STATE"] = admin_state

    update.message.reply_text("The following is the current message:", reply_markup=remove)
    update.message.reply_text(getChatText(admin_state), parse_mode='Markdown')

    if admin_state == "TEXT3":  # only text 3 needs the below for inserting the group number
        update.message.reply_text("Note: type *** where the group/seat number will go in the new message.")
    update.message.reply_text("Please type in your new message:")

    return ADMIN_END


def updateChatText(bot, update, user_data):
    chatToChange = user_data["ADMIN_STATE"]
    newText = update.message.text
    rList.mset({chatToChange: newText})
    update.message.reply_text("The update is complete.")

    return ConversationHandler.END


def addNewAdmin(bot, update):
    user = update.message.from_user
    update.message.reply_text(user.id)



