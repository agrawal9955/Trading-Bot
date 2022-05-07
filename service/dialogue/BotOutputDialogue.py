
###################################
#
#   BackTesting Report:
#       # Starting Parameters
#       - Symbol -
#       - Start Date -
#       - End Date -
#       - Timeframe -
#       - Leverage -
#       - Strategy -
#       - Planned RR -
#       - Order Type -
#       - position Type -
#
#       # Report
#       - Total Trades -
#       - Total Win Trades -
#       - Win Ratio -
#       - Average Win ROI -
#       - Average Loss ROI -
#
#       # Account Statement
#       - Starting Balance -
#       - Closing Balance -
#       - ROI -
#
###################################


from typing import Dict
from models.Context import AccountDetails, ContextType, TradeType
from models.ControllerQuery import BackTestQuery
from models.ExchangeDataModel import TradeOutputType


def generateBackTestingOutputDialogue(context: ContextType, query: BackTestQuery) -> str:
    output = "BackTesting Report:\n"

    # Starting Parameters
    output = output + "\t# Starting Parameters\n"
    output = output + "\t- Symbol - " + str(query.symbol) + "\n"
    output = output + "\t- Start Date - " + str(query.startDate) + "\n"
    output = output + "\t- End Date - " + str(query.endDate) + "\n"
    output = output + "\t- Timeframe - " + str(query.timeframe) + "\n"
    output = output + "\t- Leverage - " + str(query.leverage) + "\n"
    output = output + "\t- Strategy - " + str(query.strategy) + "\n"
    output = output + "\t- Planned RR - " + str(query.plannedRR) + "\n"
    output = output + "\t- Order Type - " + str(query.orderType) + "\n"
    output = output + "\t- Position Type - " + str(query.positionType) + "\n"
    output = output + "\n"

    # Report
    output = output + "\t# Report\n"
    output = output + "\t- Total Trades - " + \
        str(len(context.totalTradeExecuted)) + "\n"
    output = output + "\t- Total Win Trades - " + \
        __getWinTrades(context) + "\n"
    output = output + "\t- Win Ratio - " + \
        __getWinRatio(context) + "\n"
    output = output + "\t- Average Win ROI - " + \
        __getAvgWinROI(context) + "\n"
    output = output + "\t- Average Loss ROI - " + \
        __getAvgLossROI(context) + "\n"
    output = output + "\n"

    # Account Statement
    output = output + "\t# Account Statement\n"
    output = output + "\t- Starting Balance - " + \
        str(context.dummyAccountDetails.startingBalance) + "\n"
    output = output + "\t- Closing Balance - " + \
        str(context.dummyAccountDetails.closingBalance) + "\n"
    output = output + "\t- ROI - " + \
        str(context.dummyAccountDetails.ROI) + "\n"

    return output


def __getWinTrades(context: ContextType) -> str:
    if len(context.totalTradeExecuted) == 0:
        return "0"
    winTrades = 0
    for trade in context.totalTradeExecuted:
        if trade.tradeOutput == TradeOutputType.WINNER.value:
            winTrades = winTrades + 1
    return str(winTrades)


def __getWinRatio(context: ContextType) -> str:
    if len(context.totalTradeExecuted) == 0:
        return "0"
    winTrades = 0
    for trade in context.totalTradeExecuted:
        if trade.tradeOutput == TradeOutputType.WINNER.value:
            winTrades = winTrades + 1

    if len(context.totalTradeExecuted) == 0:
        return "0"
    return str(winTrades/len(context.totalTradeExecuted))


def __getAvgWinROI(context: ContextType) -> str:
    if len(context.totalTradeExecuted) == 0:
        return "0"
    winTrades = 0.0
    totalRatio = 0.0
    for trade in context.totalTradeExecuted:
        if trade.tradeOutput == TradeOutputType.WINNER.value:
            totalRatio = totalRatio + trade.ROI
            winTrades = winTrades + 1
    if winTrades == 0.0:
        return("0")
    return str(totalRatio/winTrades)


def __getAvgLossROI(context: ContextType) -> str:
    if len(context.totalTradeExecuted) == 0:
        return "0"
    lossTrades = 0.0
    totalRatio = 0.0
    for trade in context.totalTradeExecuted:
        if trade.tradeOutput == TradeOutputType.LOSER.value:
            totalRatio = totalRatio + trade.ROI
            lossTrades = lossTrades + 1
    if lossTrades == 0.0:
        return("0")
    return str(totalRatio/lossTrades)


###################################
#
#   Active Trade Report:
#       # Starting Parameters
#           long|short trade in symbol -
#               Entry -
#               Capital Deployed -
#               ROI -
#
###################################
def generateActiveTradeOutputDialogue(activeTrades: Dict[str, TradeType]) -> str:
    if len(activeTrades) == 0:
        return "No active trades found"
    output = "Active Trade Report:\n"

    for tradeData in activeTrades.values():
        output = output + "\t" + tradeData.positionType + \
            " trade in symbol - " + tradeData.symbol + "\n"
        output = output + "\t\t" + "Entry - " + \
            str(tradeData.entryPrice) + "\n"
        output = output + "\t\t" + "Capital Deployed - " + \
            str(tradeData.entryPrice*tradeData.quantity +
                tradeData.tradingFee) + "\n"
        output = output + "\t\t" + "ROI - " + \
            str(tradeData.ROI) + "\n\n"

    return output


###################################
#
#   Account Statement Report:
#       Starting Balance -
#       Closing Balance -
#       ROI -
#
###################################
def generateAccountStatementOutputDialogue(accountStatement: AccountDetails) -> str:
    output = "Account Statement Report:\n"

    output = output + "\t\t" + "Starting Balance - " + \
        str(accountStatement.startingBalance) + "\n"
    output = output + "\t\t" + "Closing Balance - " + \
        str(accountStatement.closingBalance) + "\n"
    output = output + "\t\t" + "ROI - " + \
        str(accountStatement.ROI)

    return output


###################################
#
#   Trading Bot Status:
#       Bot Active Status -
#       New Trade Entry -
#       Is Test Bot -
#       Max Open Trades -
#       Percent Capital Deployed -
#       Leverage -
#       Whitelist -
#       Blacklist -
#
###################################
def generateBotStatusOutputDialogue(context: ContextType) -> str:
    output = "Trading Bot Status:\n"

    output = output + "\t\t" + "Bot Active Status - " + \
        str(context.currentBotStatus) + "\n"
    output = output + "\t\t" + "New Trade Entry - " + \
        str(context.currentEntryStatus) + "\n"
    output = output + "\t\t" + "Is Test Bot - " + \
        str(context.config.isTestBot) + "\n"
    output = output + "\t\t" + "Max Open Trades - " + \
        str(context.config.maxActiveTrades) + "\n"
    output = output + "\t\t" + "Percent Capital Deployed - " + \
        str(context.config.percentDeployedCapital) + "\n"
    output = output + "\t\t" + "Leverage - " + \
        str(context.config.leverage) + "\n"

    output = output + "\t\t" + "Whitelist - "
    for symbol in context.config.whitelist:
        output = output + str(symbol) + "\t"
    output = output + "\n"

    output = output + "\t\t" + "Blacklist - "
    for symbol in context.config.blacklist:
        output = output + str(symbol) + "\t"
    output = output + "\n"

    return output
