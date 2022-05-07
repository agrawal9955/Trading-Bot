import logging
from models.Context import ContextType, TradeType
from models.ExchangeDataModel import ClosePositionData, InitiatePositionData, OrderParameterData
from service.context.InMemContextService import ContextService
from service.exchangeService.BinanceService import ExchangeService
from service.fundManagement.TestFundManagement import AccountManagementService
import tradingbot.TradingBotUtil as TradingBotUtil

# currentTimeMill is used for backtesting, for actual trading we can take system time


def enterNewTrade(contextService: ContextService, accountService: AccountManagementService, exchangeService: ExchangeService, context: ContextType, symbol, initiatePositionData: InitiatePositionData, timeframe: str, currentTimeMill=None, isBackTestingEnabled=False):
    # Initiate a new Position
    order = None
    if context.config.isTestBot:
        capital = accountService.getCapitalForTrade(
            context, initiatePositionData.price)
        orderParameters = OrderParameterData(
            symbol,
            TradingBotUtil.getSideForPositionEntry(
                initiatePositionData.positionType),
            initiatePositionData.orderType,
            capital,
            initiatePositionData.price,
            initiatePositionData.stoploss
        )
        order = exchangeService.placeTestOrder(
            orderParameters, isBackTestingEnabled)
        if currentTimeMill != None:
            order.transactTime = currentTimeMill
        # Generate New Trade Data
        tradeData = TradingBotUtil.generateTradeData(
            context.config, order, timeframe, initiatePositionData.positionType, initiatePositionData.stoploss)
        context.dummyAccountDetails = accountService.updateAccountDetailsNewPosition(
            context.dummyAccountDetails, tradeData)
        contextService.addActiveTrade(context, tradeData)
        contextService.updateDummyAccountDetails(
            context, context.dummyAccountDetails)
        logging.warning("Test Trade Entered in " + symbol +
                        " - Entry Time - " + str(tradeData.entryTime))
    else:
        logging.warning("Trade Entered in " + symbol)
    return context


def closeTrade(contextService: ContextService, accountService: AccountManagementService, exchangeService: ExchangeService, context: ContextType, symbol, closePositionData: ClosePositionData, tradeData: TradeType, currentTimeMill=None, isBackTestingEnabled=False):
    # Close a Position
    order = None
    if context.config.isTestBot:
        orderParameters = OrderParameterData(
            symbol,
            TradingBotUtil.getSideForPositionExit(tradeData.positionType),
            closePositionData.orderType,
            tradeData.quantity,
            closePositionData.price,
            None
        )
        order = exchangeService.placeTestOrder(
            orderParameters, isBackTestingEnabled)
        if currentTimeMill != None:
            order.transactTime = currentTimeMill
        # Update trade data and move to total executed trades
        tradeData = TradingBotUtil.updateCloseTradeData(
            context.activeTrades[symbol], order)
        context.dummyAccountDetails = accountService.updateAccountDetailsClosePosition(
            context.dummyAccountDetails, tradeData)
        contextService.removeActiveTrade(context, symbol)
        contextService.addTotalExecutedTrades(context, tradeData)
        contextService.updateDummyAccountDetails(
            context, context.dummyAccountDetails)
        logging.warning("Test Trade Exit in " + symbol +
                        " - Exit Time - " + str(tradeData.exitTime))
    else:
        logging.warning("Trade Exit in " + symbol)
    return context
