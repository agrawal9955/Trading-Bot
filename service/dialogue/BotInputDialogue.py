
import logging
from models.Controller import ControllerQuery
from models.ControllerQuery import BackTestQuery, ForceExitCommands, QueryKeys, StopBotCommands


def invalidQueryParamaterText():
    return "Invalid Query Parameter Provided"


def validateStopBotParamaterText(input: str):
    output = ControllerQuery({})
    data = input.split(" ")
    if len(data) != 2:
        return output, invalidQueryParamaterText()
    if data[1].lower().strip() == StopBotCommands.HARD.value:
        output.params[QueryKeys.STOP_TYPE.value] = StopBotCommands.HARD.value
    elif data[1].lower().strip() == StopBotCommands.SOFT.value:
        output.params[QueryKeys.STOP_TYPE.value] = StopBotCommands.SOFT.value
    else:
        output.params[QueryKeys.STOP_TYPE.value] = StopBotCommands.INVALID.value

    return output, None


def validateForceExitQueryParamaterText(input: str):
    output = ControllerQuery({})
    data = input.split(" ")
    if len(data) != 2:
        return output, invalidQueryParamaterText()
    if data[1].lower().strip() == ForceExitCommands.ALL.value:
        output.params[QueryKeys.SYMBOL.value] = ForceExitCommands.ALL.value
    else:
        output.params[QueryKeys.SYMBOL.value] = data[1]

    return output, None


def validateMaxActiveTradeQueryParamaterText(input: str):
    output = ControllerQuery({})
    data = input.split(" ")
    if len(data) != 2:
        return output, invalidQueryParamaterText()

    intData = int(data[1])
    if intData != None:
        output.params[QueryKeys.MAX_OPEN_TRADE.value] = intData
    else:
        return output, invalidQueryParamaterText()

    return output, None


def validatePercentDeployedCapitalQueryParamaterText(input: str):
    output = ControllerQuery({})
    data = input.split(" ")
    if len(data) != 2:
        return output, invalidQueryParamaterText()

    intData = int(data[1])
    if intData != None:
        output.params[QueryKeys.PERCENT_CAPITAL_DEPLOYED.value] = intData
    else:
        return output, invalidQueryParamaterText()

    return output, None


def validateStrategyQueryParamaterText(input: str):
    return


def validateWhitelistQueryParamaterText(input: str):
    output = ControllerQuery({})
    data = input.split(" ")
    if len(data) != 2:
        return output, invalidQueryParamaterText()

    output.params[QueryKeys.SYMBOL.value] = data[1]

    return output, None


def validateBlacklistQueryParamaterText(input: str):
    output = ControllerQuery({})
    data = input.split(" ")
    if len(data) != 2:
        return output, invalidQueryParamaterText()

    output.params[QueryKeys.SYMBOL.value] = data[1]

    return output, None


# query - symbol, startDate, endDate, strategy, timeframe, leverage, plannedRR, orderType, positionType
def validateBackTestQueryParamaterText(input: str) -> BackTestQuery:
    try:
        rawQuery = input.split(" ")
        symbol = rawQuery[1]
        startDate = rawQuery[2]
        endDate = rawQuery[3]
        strategy = rawQuery[4]
        timeframe = rawQuery[5]
        leverage = int(rawQuery[6])
        plannedRR = float(rawQuery[7])
        orderType = rawQuery[8]
        positionType = rawQuery[9]

        if (
            symbol != None and
            startDate != None and
            endDate != None and
            strategy != None and
            timeframe != None and
            leverage != None and
            plannedRR != None and
            orderType != None and
            positionType != None
        ):
            return BackTestQuery(
                symbol,
                startDate,
                endDate,
                strategy,
                timeframe,
                leverage,
                plannedRR,
                orderType,
                positionType
            ), None
    except Exception as e:
        logging.warning(e)
        return None, "Invalid Inputs provided"
