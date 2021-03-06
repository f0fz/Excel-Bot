#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

import logging

from functions.init import TYPING_NRIC, ENDSEM, QUESTION, ENDPOST
from functions.init import ADMIN_TXT_START, ADMIN_FB_START, ADMIN_END, NEW_ADMIN, ADMIN_RM_END
from functions import seminar, post_seminar, utils, admin, message

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater("-")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states TYPING_NRIC and RESPONSE
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', seminar.start)],
        states={
            TYPING_NRIC: [MessageHandler(Filters.text,
                                         seminar.get_nric,
                                         pass_user_data=True)],
            ENDSEM: [RegexHandler('^Yes|No$',
                                  seminar.final,
                                  pass_user_data=True)]
        },
        fallbacks=[]
    )

    # Add conversation handler with the states QN1, QN2, QN3
    post_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('postevent', post_seminar.postevent, pass_user_data=True)],
        states={
            QUESTION: [MessageHandler(Filters.text,
                                      post_seminar.question,
                                      pass_user_data=True)],
            ENDPOST: [MessageHandler(Filters.text,
                                     post_seminar.endPost,
                                     pass_user_data=True)]
        },
        fallbacks=[]
    )

    # Add conversation handler with the states ADMIN_START, ADMIN_END
    admin_txt_handler = ConversationHandler(
        entry_points=[CommandHandler('changeText', message.startChangeChat,
                                     pass_user_data=True, pass_args=True)],
        states={
            ADMIN_TXT_START: [MessageHandler(Filters.text,
                                             message.receiveChatToChange,
                                             pass_user_data=True)],
            ADMIN_END: [MessageHandler(Filters.text,
                                       message.updateChatText,
                                       pass_user_data=True)]
        },
        fallbacks=[]
    )

    # Add conversation handler with the states ADMIN_START, ADMIN_END
    admin_fb_handler = ConversationHandler(
        entry_points=[CommandHandler('changeFeedback', message.startChangeFeedback,
                                     pass_user_data=True, pass_args=True)],
        states={
            ADMIN_FB_START: [MessageHandler(Filters.text,
                                            message.receiveFeedbackToChange,
                                            pass_user_data=True)],
            ADMIN_RM_END: [MessageHandler(Filters.text,
                                          message.removeQuestion,
                                          pass_user_data=True)],
            ADMIN_END: [MessageHandler(Filters.text,
                                       message.updateChatText,
                                       pass_user_data=True)]
        },
        fallbacks=[]
    )

    # Add conversation handler with the state NEW_ADMIN_END
    admin_handler = ConversationHandler(
        entry_points=[CommandHandler('newAdmin', admin.startNewAdmin)],
        states={
            NEW_ADMIN: [MessageHandler(Filters.contact,
                                       admin.addNewAdmin)]
        },
        fallbacks=[]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(post_conv_handler)
    dp.add_handler(admin_txt_handler)
    dp.add_handler(admin_fb_handler)
    dp.add_handler(admin_handler)

    dp.add_handler(CommandHandler('help', utils.adminHelp))
    dp.add_handler(CommandHandler('id', utils.chatID))

    dp.add_handler(CommandHandler('aStats', utils.attendanceStats))
    dp.add_handler(CommandHandler('fStats', utils.feedbackStats))

    dp.add_handler(CommandHandler('aFile', utils.sendAttendanceFile))
    dp.add_handler(CommandHandler('fFile', utils.sendFeedbackFile))

    dp.add_handler(CommandHandler('listAdmins', admin.listAllAdmins))
    dp.add_handler(CommandHandler('deleteAll', admin.deleteAllAdmins))
    dp.add_handler(CommandHandler('removeAdmin', admin.removeAdmin, pass_args=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    logger.info("The bot is running.")
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
