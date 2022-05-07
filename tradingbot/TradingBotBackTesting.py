import logging
from time import time
import models.Controller
from models.ControllerQuery import BackTestQuery
from models.ExchangeDataModel import CandleStickType, ClosePositionData, InitiatePositionData, OrderParameterData
from service.dialogue.BotDialogue import BotDialogue
import models.Controller as ControllerModel
from service.context.InMemContextService import ContextService
from service.fundManagement.TestFundManagement import AccountManagementService
import tradingbot.TradingBotUtil as TradingBotUtil
import tradingbot.TradingBotBL as TradingBotBL
import models.Context as ContextModel
from service.configuration.JsonConfigService import ConfigService
from service.strategy.SampleStrategy import StrategyService
from service.exchangeService.BinanceService import ExchangeService


class TradingBotBackTestingService:
    def __init__(self,
                 botDialogueService: BotDialogue,
                 configService: ConfigService,
                 accountService: AccountManagementService,
                 exchangeService: ExchangeService,
                 strategyService: StrategyService) -> None:
        self.botDialogue = botDialogueService
        self.configService = configService
        self.accountService = accountService
        self.exchangeService = exchangeService
        self.strategyService = strategyService
        return

    # Process Controller Request
    def processRequest(self, request: models.Controller.ControllerRequest) -> None:
        intent, query, err = self.botDialogue.processInputDialogue(
            input=request.text)

        if err != None and err != "":
            message = "Invalid Input For the Given Command: Detailed Error message mentined below:\n"
            request.setReply(message + err)
            return

        data = None
        if intent == ControllerModel.ControllerIntent.BACKTEST.value:
            request.setReply(
                "Backtesting started.\nPlease wait it may take a while.")
            context = self.run(query)
            context, data, err = TradingBotUtil.processIntentBacktest(
                context, query, self.contextService)
            data = {"context": context, "query": query}
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

    # Run Trading Backtesting Bot
    def run(self, backTestQuery: BackTestQuery) -> ContextModel.ContextType:
        try:
            logging.warning("TradingBotBackTesting: Testing started")
            self.contextService = ContextService(
                "./backTestingReport/" +
                self.__generateContextFileName(backTestQuery.symbol),
                self.configService
            )
            context = self.contextService.generateContext()
            context.config.isTestBot = True
            context.currentBotStatus = True
            context.currentEntryStatus = True
            candleData = self.exchangeService.getHistoricalData(
                backTestQuery.symbol,
                backTestQuery.timeframe,
                backTestQuery.startDate,
                backTestQuery.endDate
            )
            self.exchangeService.updateSymbolInfo(backTestQuery.symbol)
            startIndex = 0
            endIndex = 500
            while endIndex <= len(candleData):
                self.__trade(
                    backTestQuery.symbol, context, candleData[startIndex:endIndex], backTestQuery.timeframe)
                startIndex = startIndex + 1
                endIndex = endIndex + 1

            self.__closeAllOpenTrades(
                context, candleData[startIndex-1:endIndex-1])

            logging.warning("TradingBotBackTesting: Testing Finished")

            return context
        except Exception as e:
            logging.warning("TradingBotBackTesting: some Exception occurred")
            logging.warning(e)
            return

    def __trade(self, symbol, context: ContextModel.ContextType, candleData: list[CandleStickType], timeFrame: str) -> ContextModel.ContextType:

        tradeData = None
        if symbol in context.activeTrades.keys():
            tradeData = context.activeTrades[symbol]
            tradeData = TradingBotUtil.updateTradeData(
                context.activeTrades[symbol], candleData[len(candleData)-1], True)

        self.strategyService.calculateIndicators(candleData)
        if tradeData == None:
            tradeSignalData = self.strategyService.initiatePositionSignal(
                candleData=candleData, backTestingEnabled=True)
        else:
            tradeSignalData = self.strategyService.closePositionSignal(
                candleData=candleData, tradeData=tradeData, backTestingEnabled=True)
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
                symbol=symbol,
                initiatePositionData=tradeSignalData,
                timeframe=timeFrame,
                currentTimeMill=candleData[len(candleData)-1].openTime*1000,
                isBackTestingEnabled=True,
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
                symbol=symbol,
                closePositionData=tradeSignalData,
                tradeData=tradeData,
                currentTimeMill=candleData[len(candleData)-1].openTime*1000,
                isBackTestingEnabled=True,
            )

        return context

    def __forceCloseTrade(self, symbol: str, context: ContextModel.ContextType, candleData: list[CandleStickType]):
        activeTrade = context.activeTrades[symbol]

        # using open because entry will generally be at starting
        price = candleData[len(candleData)-1].open

        tradeData = TradingBotUtil.updateTradeData(
            context.activeTrades[activeTrade.symbol], candleData[len(candleData)-1], True)

        closePositionData = ClosePositionData(True, price, "market")

        context = TradingBotBL.closeTrade(
            self.contextService,
            self.accountService,
            self.exchangeService,
            context,
            activeTrade.symbol,
            closePositionData,
            tradeData,
            currentTimeMill=candleData[len(candleData)-1].openTime*1000,
            isBackTestingEnabled=True,
        )

        return context

    def __closeAllOpenTrades(self, context: ContextModel.ContextType, candleData: list[CandleStickType]):
        activeTradeCopy = context.activeTrades.copy()
        for tradeData in activeTradeCopy.values():
            context = self.__forceCloseTrade(
                tradeData.symbol, context, candleData)

        return context

    def __generateContextFileName(self, symbol: str):
        return "context_" + symbol + "_" + str(int(time()*1000000)) + "_.json"
