import logging
from os import stat
from typing import Dict
import models.Controller
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
from tradingbot.TradingBotBackTesting import TradingBotBackTestingService
from tradingbot.TradingBotService import TradingBotService
from service.authentication.AuthenticationService import AuthenticationService

############################
# Compulsory Methods
#
#   init, runBot
#
#
#
############################


class Controller:
    def __init__(self, token, authenticationService: AuthenticationService, tradingBotService: TradingBotService, tradingBacktestingService: TradingBotBackTestingService) -> None:
        self.authenticationService = authenticationService
        self.tradingBotService = tradingBotService
        self.tradingBacktestingService = tradingBacktestingService
        self.controller = Updater(token, use_context=True)
        self.controllerState = models.Controller.AUTHENTICATION

    def runBot(self):

        # Get the dispatcher to register handlers
        dispatcher = self.controller.dispatcher

        # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler(
                'start', self.__startTelegramBotHandler)],
            states={
                models.Controller.AUTHENTICATION: [
                    MessageHandler(
                        Filters.regex(
                            ''), self.__authenticate
                    )
                ],
                models.Controller.ENQUIRY: [
                    MessageHandler(
                        Filters.regex("^/help"), self.__helpTelegramBotEnquiry
                    ),
                    MessageHandler(
                        Filters.regex(
                            "^(?!/help.*$).*"), self.__processTradingBotEnquiry
                    )
                ],
                models.Controller.CONFIG: [
                    MessageHandler(
                        Filters.regex("^/help"), self.__helpTelegramBotConfig
                    ),
                    MessageHandler(
                        Filters.regex(
                            "^(?!/help.*$).*"), self.__updateTradingBotConfig
                    )
                ],
                models.Controller.BACKTESTING: [
                    MessageHandler(
                        Filters.regex(
                            "^/help"), self.__helpTelegramBotBackTesting
                    ),
                    MessageHandler(
                        Filters.regex(
                            "^(?!/help.*$).*"), self.__updateTradingBotBackTesting
                    )
                ],
            },
            fallbacks=[MessageHandler(Filters.regex(
                ''), self.__fallbackHandler)],
        )

        dispatcher.add_handler(conv_handler)

        # Start the Bot
        self.controller.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self.controller.idle()

        logging.warning("Controller Initialized")

        return

    def __startTelegramBotHandler(self, update: Update, context: CallbackContext):
        update.message.reply_text("Hello sir.\n"
                                  "Welcome to the Crypto Trading Bot.\n"
                                  "First You need to authenticate yourself with the token.")

        return models.Controller.AUTHENTICATION

    def __fallbackHandler(self, update: Update, context: CallbackContext):
        if self.controllerState == models.Controller.AUTHENTICATION:
            update.message.reply_text("Hello sir.\n"
                                      "Welcome to the Crypto Trading Bot.\n"
                                      "First You need to authenticate yourself with the token.")
        elif self.controllerState == models.Controller.ENQUIRY:
            self.__helpTelegramBotEnquiry(update, context)
        elif self.controllerState == models.Controller.CONFIG:
            self.__helpTelegramBotConfig(update, context)

    def __helpTelegramBotEnquiry(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            "/status: No Parameter - Status of trading bot.\n"
            "/start_bot: No Parameter - Starts the trader.\n"
            "/stop_bot: hard|soft - Stops the trader.\n"
            "/start_entry: No Parameter - Start entering new trades.\n"
            "/stop_entry: No Parameter - Stop entering new trades.\n"
            "/active_trades: No Parameter - Lists all or specific open trades.\n"
            "/force_exit: <symbol>|al1 : Instantly exits the given trade (ignoring minimum_roi ).\n"
            "/report: timeframe - get report for the given time frame\n Allowed timeframe - 1d, 1w, 1m, 1y\n"
            "/account_statement: No Parameter - Get current account statement\n"
            "/update_config: No Parameter - move to update config state\n"
            "/back_testing: No Parameter - move to back testing bot state.\n")

        return models.Controller.ENQUIRY

    def __helpTelegramBotBackTesting(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            "/backtest symbol, startDate, endDate, strategy, timeframe, leverage, plannedRR, orderType, positionType\n"
            "/tradingbot:No Parameter -  move to trading bot state.\n"
            "/update_config:No Parameter -  move to update config state\n")

        return models.Controller.BACKTESTING

    def __helpTelegramBotConfig(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            "/max_active_trade: number (1 to 100) - update max active trades bot can hold.\n"
            "/percent_deployed_capital: number (1 to 100) - update percent of the capital that can be deployed.\n"
            "/strategy: number (Currently Not Used) - update strategy for the trading bot.\n"
            "/whitelist_add_coin: symbol - add coin to whitelist for the trading bot.\n"
            "/whitelist_remove_coin: symbol - remove coin to whitelist for the trading bot.\n"
            "/blacklist_add_coin: symbol - add coin to blacklist for the trading bot.\n"
            "/blacklist_remove_coin: symbol - remove coin to blacklist for the trading bot.\n"
            "/tradingbot: No Parameter - move to trading bot state.\n"
            "/back_testing: No Parameter - move to back testing bot state.\n")

        return models.Controller.CONFIG

    def __authenticate(self, update: Update, context: CallbackContext) -> int:
        request = models.Controller.ControllerRequest(
            update.message.text, update.message.reply_text)

        status = self.authenticationService.authenticate(request)
        if status:
            self.controllerState = models.Controller.ENQUIRY
            return models.Controller.ENQUIRY
        else:
            return models.Controller.AUTHENTICATION

    def __processTradingBotEnquiry(self, update: Update, context: CallbackContext) -> int:
        if update == None or update.message == None:
            update.message.reply_text(
                "Please specify Some command\nRefer /help for commands")
            return models.Controller.ENQUIRY
        elif update.message.text.lower().strip() == "/update_config":
            update.message.reply_text(
                "Moving to Configurations\nRefer /help for commands")
            self.controllerState = models.Controller.CONFIG
            self.tradingBotService.disableChatBot()
            return models.Controller.CONFIG
        elif update.message.text.lower().strip() == "/back_testing":
            update.message.reply_text(
                "Moving to Back Testing\nRefer /help for commands")
            self.controllerState = models.Controller.BACKTESTING
            self.tradingBotService.disableChatBot()
            return models.Controller.BACKTESTING

        request = models.Controller.ControllerRequest(
            update.message.text, update.message.reply_text)

        self.tradingBotService.processRequest(request)

        return models.Controller.ENQUIRY

    def __updateTradingBotConfig(self, update: Update, context: CallbackContext) -> int:
        if update == None or update.message == None:
            update.message.reply_text(
                "Please specify Some command\nRefer /help for commands")
            return models.Controller.CONFIG
        elif update.message.text.lower().strip() == "/tradingbot":
            update.message.reply_text(
                "Moving to Trading Bot\nRefer /help for commands")
            self.controllerState = models.Controller.ENQUIRY
            return models.Controller.ENQUIRY
        elif update.message.text.lower().strip() == "/back_testing":
            update.message.reply_text(
                "Moving to Back Testing\nRefer /help for commands")
            self.controllerState = models.Controller.BACKTESTING
            return models.Controller.BACKTESTING

        request = models.Controller.ControllerRequest(
            update.message.text, update.message.reply_text)

        self.tradingBotService.updateConfig(request)

        return models.Controller.CONFIG

    def __updateTradingBotBackTesting(self, update: Update, context: CallbackContext) -> int:
        if update == None or update.message == None:
            update.message.reply_text(
                "Please specify Some command\nRefer /help for commands")
            return models.Controller.BACKTESTING
        elif update.message.text.lower().strip() == "/tradingbot":
            update.message.reply_text(
                "Moving to Trading Bot\nRefer /help for commands")
            self.controllerState = models.Controller.ENQUIRY
            return models.Controller.ENQUIRY
        elif update.message.text.lower().strip() == "/update_config":
            update.message.reply_text(
                "Moving to Configurations\nRefer /help for commands")
            self.controllerState = models.Controller.CONFIG
            return models.Controller.CONFIG

        request = models.Controller.ControllerRequest(
            update.message.text, update.message.reply_text)

        self.tradingBacktestingService.processRequest(request)

        return models.Controller.BACKTESTING
