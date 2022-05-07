import logging
from time import sleep
import models.Controller
from models.ExchangeDataModel import InitiatePositionData, OrderParameterData, ClosePositionData
from service.dialogue.BotDialogue import BotDialogue
import models.Controller as ControllerModel
from service.context.InMemContextService import ContextService
from service.fundManagement.TestFundManagement import AccountManagementService
import tradingbot.TradingBotUtil as TradingBotUtil
import tradingbot.TradingBotUpdateConfigUtils as TradingBotUpdateConfigUtils
import tradingbot.TradingBotBL as TradingBotBL
import models.Context as ContextModel
from service.strategy.SampleStrategy import StrategyService
from os.path import exists
from service.exchangeService.BinanceService import ExchangeService


class TradingBotService:
    def __init__(self,
                 botDialogueService: BotDialogue,
                 contextService: ContextService,
                 accountService: AccountManagementService,
                 exchangeService: ExchangeService,
                 strategyService: StrategyService) -> None:
        self.botDialogue = botDialogueService
        self.contextService = contextService
        self.accountService = accountService
        self.exchangeService = exchangeService
        self.strategyService = strategyService

        self.context = self.contextService.getContext()

    # Process Controller Request
    def updateConfig(self, request: models.Controller.ControllerRequest) -> None:
        try:
            intent, query, err = self.botDialogue.processInputDialogue(
                request.text)

            if err != None and err != "":
                message = "Invalid Input For the Given Command: Detailed Error message mentined below:\n"
                request.setReply(message + err)
                return

            if intent == ControllerModel.ControllerIntent.UPDATE_CONFIG_MAX_ACTIVE_TRADES.value:
                context, data, err = TradingBotUpdateConfigUtils.processIntentUpdateMaxOpenTrade(
                    self.context, query, self.contextService)
            elif intent == ControllerModel.ControllerIntent.UPDATE_CONFIG_PERCENT_DEPLOYED_CAPITAL.value:
                context, data, err = TradingBotUpdateConfigUtils.processIntentUpdatePercentDeployedCapital(
                    self.context, query, self.contextService)
            elif intent == ControllerModel.ControllerIntent.UPDATE_CONFIG_STRATEGY.value:
                context, data, err = TradingBotUpdateConfigUtils.processIntentUpdateStrategy(
                    self.context, query, self.contextService)
            elif intent == ControllerModel.ControllerIntent.UPDATE_WHITELIST_ADD_COIN.value:
                context, data, err = TradingBotUpdateConfigUtils.processIntentUpdateWhitelistAddCoin(
                    self.context, query, self.contextService)
            elif intent == ControllerModel.ControllerIntent.UPDATE_WHITELIST_REMOVE_COIN.value:
                context, data, err = TradingBotUpdateConfigUtils.processIntentUpdateWhitelistRemoveCoin(
                    self.context, query, self.contextService)
            elif intent == ControllerModel.ControllerIntent.UPDATE_BLACKLIST_ADD_COIN.value:
                context,  data, err = TradingBotUpdateConfigUtils.processIntentUpdateBlacklistAddCoin(
                    self.context, query, self.contextService)
            elif intent == ControllerModel.ControllerIntent.UPDATE_BLACKLIST_REMOVE_COIN.value:
                context, data, err = TradingBotUpdateConfigUtils.processIntentUpdateBlacklistRemoveCoin(
                    self.context, query, self.contextService)
            else:
                data, err = "", "Invalid Command"

            if err != None and err != "":
                message = "Some Error Occurred In Processing Dialogue: Detailed Error message mentined below:\n"
                request.setReply(message + err)
                return

            nextDialogue = self.botDialogue.processOutputDialogue(
                intent, data)

            request.setReply(nextDialogue)

            return

        except Exception as e:
            self.disableChatBot()
            logging.warning(
                "TradingBotService: Some Error Occurred while in updateConfig")
            logging.warning(e)
            return

    # Process Controller Request
    def processRequest(self, request: models.Controller.ControllerRequest) -> None:
        try:
            intent, query, err = self.botDialogue.processInputDialogue(
                input=request.text)

            if err != None and err != "":
                message = "Invalid Input For the Given Command: Detailed Error message mentined below:\n"
                request.setReply(message + err)
                return

            if intent == ControllerModel.ControllerIntent.STATUS.value:
                context, data, err = TradingBotUtil.processIntentStatus(
                    context=self.context, contextService=self.contextService)
            elif intent == ControllerModel.ControllerIntent.START_BOT.value:
                context, data, err = TradingBotUtil.processIntentStartBot(
                    context=self.context, contextService=self.contextService)
            elif intent == ControllerModel.ControllerIntent.STOP_BOT.value:
                context, data, err = TradingBotUtil.processIntentStopBot(
                    context=self.context,
                    query=query,
                    contextService=self.contextService,
                    closeAllTradeCallback=self.__closeAllOpenTrades,
                )
            elif intent == ControllerModel.ControllerIntent.START_ENTRY.value:
                context, data, err = TradingBotUtil.processIntentStartEntry(
                    context=self.context, contextService=self.contextService)
            elif intent == ControllerModel.ControllerIntent.STOP_ENTRY.value:
                context, data, err = TradingBotUtil.processIntentStopEntry(
                    context=self.context, contextService=self.contextService)
            elif intent == ControllerModel.ControllerIntent.ACTIVE_TRADES.value:
                context, data, err = TradingBotUtil.processIntentGetActiveTrades(
                    context=self.context, contextService=self.contextService)
            elif intent == ControllerModel.ControllerIntent.ACCOUNT_STATEMENT.value:
                context, data, err = TradingBotUtil.processIntentAccountStatement(
                    context=self.context, contextService=self.contextService)
            elif intent.startswith(ControllerModel.ControllerIntent.FORCE_EXIT.value):
                context, data, err = TradingBotUtil.processIntentForceExit(
                    context=self.context,
                    query=query,
                    contextService=self.contextService,
                    closeTradeCallback=self.__forceCloseTrade,
                    closeAllTradeCallback=self.__closeAllOpenTrades
                )
            else:
                data, err = "", "Invalid Command"

            if err != None and err != "":
                message = "Some Error Occurred In Processing Dialogue: Detailed Error message mentined below:\n"
                request.setReply(message + err)
                return

            nextDialogue = self.botDialogue.processOutputDialogue(
                intent=intent, data=data)

            request.setReply(nextDialogue)

            return
        except Exception as e:
            self.disableChatBot()
            logging.warning(
                "TradingBotService: Some Error Occurred in Process Request")
            logging.warning(e)
            return

    # Run Trading Bot
    def run(self) -> None:
        try:
            while True:
                if self.context.currentBotStatus:
                    self.__trade(self.context)
                    sleep(1)
                else:
                    self.__closeAllOpenTrades(self.context)
                    sleep(1)

        except Exception as e:
            self.disableChatBot()
            logging.warning(
                "TradingBotService: Some Error Occurred while running trading bot")
            logging.warning(e)
            self.run()
            return

    def __trade(self, context: ContextModel.ContextType):

        for coin in context.config.whitelist:
            timeFrame = self.strategyService.getDesiredTimeFrame(coin)
            if timeFrame == "":
                continue

            candleData = self.exchangeService.getRecentData(coin, timeFrame)
            if len(candleData) == 0 and coin in context.activeTrades.keys():
                self.disableChatBot()
                continue
            elif len(candleData) == 0:
                logging.warning("BAD SYMBOL FOUND - " + coin)
                continue

            price = candleData[len(candleData)-1].close

            tradeData = None
            if coin in context.activeTrades.keys():
                tradeData = context.activeTrades[coin]
                tradeData = TradingBotUtil.updateTradeData(
                    context.activeTrades[coin], candleData[len(candleData)-1])

            self.strategyService.calculateIndicators(candleData)
            if tradeData == None:
                tradeSignalData = self.strategyService.initiatePositionSignal(
                    candleData)
                if tradeSignalData.price == None:
                    tradeSignalData.price = price
            else:
                tradeSignalData = self.strategyService.closePositionSignal(
                    candleData, tradeData)
                if tradeSignalData.price == None:
                    tradeSignalData.price = price

            if (
                tradeSignalData.status and
                tradeData == None and
                context.currentEntryStatus and
                len(context.activeTrades) < context.config.maxActiveTrades
            ):
                context = TradingBotBL.enterNewTrade(
                    contextService=self.contextService,
                    accountService=self.accountService,
                    exchangeService=self.exchangeService,
                    context=context,
                    symbol=coin,
                    initiatePositionData=tradeSignalData,
                    timeframe=timeFrame
                )
            elif(
                tradeSignalData.status and
                tradeData != None
            ):
                context = TradingBotBL.closeTrade(
                    contextService=self.contextService,
                    accountService=self.accountService,
                    exchangeService=self.exchangeService,
                    context=context,
                    symbol=coin,
                    closePositionData=tradeSignalData,
                    tradeData=tradeData
                )

        return context

    def __forceCloseTrade(self, symbol: str, context: ContextModel.ContextType):
        activeTrade = context.activeTrades[symbol]
        timeFrame = self.strategyService.getDesiredTimeFrame(
            activeTrade.symbol)
        candleData = self.exchangeService.getRecentData(
            activeTrade.symbol, timeFrame)
        price = candleData[len(candleData)-1].close

        tradeData = TradingBotUtil.updateTradeData(
            context.activeTrades[activeTrade.symbol], candleData[len(candleData)-1])

        closePositionData = ClosePositionData(True, price, "market")

        context = TradingBotBL.closeTrade(
            contextService=self.contextService,
            accountService=self.accountService,
            exchangeService=self.exchangeService,
            context=context,
            symbol=tradeData.symbol,
            closePositionData=closePositionData,
            tradeData=tradeData
        )

        return context

    def __closeAllOpenTrades(self, context: ContextModel.ContextType):
        activeTradeCopy = context.activeTrades.copy()
        for tradeData in activeTradeCopy.values():
            context = self.__forceCloseTrade(tradeData.symbol, context)

        return context

    def disableChatBot(self):
        self.context.currentEntryStatus = False
        self.__closeAllOpenTrades(self.context)
