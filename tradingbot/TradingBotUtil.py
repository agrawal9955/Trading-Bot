from datetime import datetime

from urllib3 import Retry
from models.Config import ConfigData
import models.Context as ContextModels
import models.Controller as ControllerModel
from models.ControllerQuery import ForceExitCommands, QueryKeys, StopBotCommands
from models.ExchangeDataModel import CandleStickType, OrderData, TradeOutputType
from time import time

from service.configuration.JsonConfigService import ConfigService
from service.context.InMemContextService import ContextService

###################################################
#
#   Process Intent Functions
#
##################################################


def processIntentStatus(context: ContextModels.ContextType, contextService: ContextService):
    controllerActivity = ControllerModel.ControllerActivity(
        int(time()*1000000),
        ControllerModel.ControllerIntent.STATUS.value
    )
    status, err = contextService.addControllerActivity(
        context, controllerActivity)
    return context, context, err


def processIntentStartBot(context: ContextModels.ContextType, contextService: ContextService):
    state, err = contextService.updateBotActiveState(context, True)
    if not state:
        return context, "", err
    controllerActivity = ControllerModel.ControllerActivity(
        int(time()*1000000),
        ControllerModel.ControllerIntent.START_BOT.value
    )
    status, err = contextService.addControllerActivity(
        context, controllerActivity)
    return context, "", err


def processIntentStopBot(context: ContextModels.ContextType, query: ControllerModel.ControllerQuery, contextService: ContextService, closeAllTradeCallback):
    if query.params[QueryKeys.STOP_TYPE.value] == StopBotCommands.SOFT.value:
        state, err = contextService.updateTradeEntryState(context, False)
        if not state:
            return context, "", err
    elif query.params[QueryKeys.STOP_TYPE.value] == StopBotCommands.HARD.value:
        closeAllTradeCallback(context)
        state, err = contextService.updateBotActiveState(context, False)
        state, err = contextService.updateTradeEntryState(context, False)
        if not state:
            return context, "", err
    else:
        return context, "", "Invalid Option provided for /stop_bot, valid inputs are hard or soft"
    controllerActivity = ControllerModel.ControllerActivity(
        int(time()*1000000),
        ControllerModel.ControllerIntent.STOP_BOT.value
    )
    status, err = contextService.addControllerActivity(
        context, controllerActivity)
    return context, query.params[QueryKeys.STOP_TYPE.value], err


def processIntentStartEntry(context: ContextModels.ContextType, contextService: ContextService):
    state, err = contextService.updateTradeEntryState(context, True)
    if not state:
        return context, "", err
    controllerActivity = ControllerModel.ControllerActivity(
        int(time()*1000000),
        ControllerModel.ControllerIntent.START_ENTRY.value
    )
    status, err = contextService.addControllerActivity(
        context, controllerActivity)
    return context, "", err


def processIntentStopEntry(context: ContextModels.ContextType, contextService: ContextService):
    state, err = contextService.updateTradeEntryState(context, False)
    if not state:
        return context, "", err
    controllerActivity = ControllerModel.ControllerActivity(
        int(time()*1000000),
        ControllerModel.ControllerIntent.STOP_ENTRY.value
    )
    status, err = contextService.addControllerActivity(
        context, controllerActivity)
    return context, "", err


def processIntentGetActiveTrades(context: ContextModels.ContextType, contextService: ContextService):
    controllerActivity = ControllerModel.ControllerActivity(
        int(time()*1000000),
        ControllerModel.ControllerIntent.ACTIVE_TRADES.value
    )
    status, err = contextService.addControllerActivity(
        context, controllerActivity)
    return context, context.activeTrades, err


def processIntentAccountStatement(context: ContextModels.ContextType, contextService: ContextService):
    controllerActivity = ControllerModel.ControllerActivity(
        int(time()*1000000),
        ControllerModel.ControllerIntent.ACCOUNT_STATEMENT.value
    )
    status, err = contextService.addControllerActivity(
        context, controllerActivity)
    if context.config.isTestBot:
        return context, context.dummyAccountDetails, err
    else:
        return context, context.accountDetails, err


def processIntentForceExit(context: ContextModels.ContextType, query: ControllerModel.ControllerQuery, contextService: ContextService, closeTradeCallback, closeAllTradeCallback):
    if query.params[QueryKeys.SYMBOL.value] == ForceExitCommands.ALL.value:
        closeAllTradeCallback(context)
    elif query.params[QueryKeys.SYMBOL.value] in context.activeTrades.keys():
        closeTradeCallback(query.params[QueryKeys.SYMBOL.value], context)
    else:
        return context, "", "Invalid Option provided for /force_exit, valid inputs are any active symbol name or all"
    controllerActivity = ControllerModel.ControllerActivity(
        int(time()*1000000),
        ControllerModel.ControllerIntent.FORCE_EXIT.value
    )
    status, err = contextService.addControllerActivity(
        context, controllerActivity)
    return context, query.params[QueryKeys.SYMBOL.value], err


def processIntentBacktest(context: ContextModels.ContextType, query, contextService: ContextService):
    controllerActivity = ControllerModel.ControllerActivity(
        int(time()*1000000),
        ControllerModel.ControllerIntent.BACKTEST.value
    )
    status, err = contextService.addControllerActivity(
        context, controllerActivity)
    return context, "", err


###################################################
#
#   Trade Data Functions
#
##################################################
def generateTradeData(config: ConfigData, orderData: OrderData, timeframe: str, positionType: str, stopPrice=-1.0) -> ContextModels.TradeType:
    avgPrice = 0
    quantity = 0
    comission = 0
    for fill in orderData.fills:
        avgPrice = avgPrice + float(fill.price) * fill.quantity
        quantity = quantity + fill.quantity
        comission = comission + float(fill.price) * fill.commission

    avgPrice = avgPrice / quantity

    return ContextModels.TradeType(
        str(orderData.orderId),
        config.leverage,
        orderData.symbol,
        timeframe,
        orderData.quantity,
        orderData.transactTime,
        -1,
        positionType,
        avgPrice,
        -1,
        True,
        comission,
        0,
        -1,
        stopPrice,
        avgPrice*quantity + comission,
        TradeOutputType.IN_PROGRESS.value,
    )


def updateTradeData(tradeData: ContextModels.TradeType, candleData: CandleStickType, backTestingEnabled=False) -> ContextModels.TradeType:
    if not backTestingEnabled:
        if tradeData.positionType == ContextModels.PositionType.LONG.value:
            tradeData.ROI = (candleData.close - tradeData.entryPrice) * 100.0 * tradeData.leverage / \
                tradeData.entryPrice
        else:
            tradeData.ROI = (tradeData.entryPrice - candleData.close) * 100.0 * tradeData.leverage / \
                tradeData.entryPrice
    else:
        if tradeData.positionType == ContextModels.PositionType.LONG.value:
            tradeData.ROI = (candleData.open - tradeData.entryPrice) * 100.0 * tradeData.leverage / \
                tradeData.entryPrice
        else:
            tradeData.ROI = (tradeData.entryPrice - candleData.open) * 100.0 * tradeData.leverage / \
                tradeData.entryPrice
    return tradeData

# Order to be added


def updateCloseTradeData(tradeData: ContextModels.TradeType, orderData: OrderData) -> ContextModels.TradeType:
    avgPrice = 0
    quantity = 0
    comission = 0
    for fill in orderData.fills:
        avgPrice = avgPrice + float(fill.price) * fill.quantity
        quantity = quantity + fill.quantity
        comission = comission + float(fill.price) * fill.commission

    avgPrice = avgPrice / quantity
    if tradeData.positionType == ContextModels.PositionType.LONG.value:
        tradeData.ROI = (avgPrice - tradeData.entryPrice) * 100.0 * tradeData.leverage / \
            tradeData.entryPrice
    else:
        tradeData.ROI = (tradeData.entryPrice - avgPrice) * 100.0 * tradeData.leverage / \
            tradeData.entryPrice
    tradeData.exitPrice = avgPrice
    tradeData.exitTime = orderData.transactTime
    tradeData.activeStatus = False
    tradeData.tradingFee = tradeData.tradingFee + comission

    if tradeData.ROI > 0.0:
        tradeData.tradeOutput = TradeOutputType.WINNER.value
    else:
        tradeData.tradeOutput = TradeOutputType.LOSER.value

    return tradeData


###################################################
#
#   Utility Functions
#
##################################################
def getSideForPositionEntry(position: ContextModels.PositionType) -> ContextModels.SideType:
    if position == ContextModels.PositionType.LONG.value:
        return ContextModels.SideType.BUY.value
    elif position == ContextModels.PositionType.SHORT.value:
        return ContextModels.SideType.SELL.value
    else:
        return ContextModels.SideType.INVALID.value


def getSideForPositionExit(position: ContextModels.PositionType) -> ContextModels.SideType:
    if position == ContextModels.PositionType.LONG.value:
        return ContextModels.SideType.SELL.value
    elif position == ContextModels.PositionType.SHORT.value:
        return ContextModels.SideType.BUY.value
    else:
        return ContextModels.SideType.INVALID.value
