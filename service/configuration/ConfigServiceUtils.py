import models.Config as ConfigModel


def validateMaxActiveTrades(data: int):
    if data == None:
        return False
    if data > 0 and data <= 100:
        return True
    return False


def validatePercentDeployedCapital(data: int):
    if data == None:
        return False
    if data > 0 and data <= 100:
        return True
    return False


def validateStrategy(data: ConfigModel.SupportedStrategy):
    if data == None:
        return False
    if data == ConfigModel.SupportedStrategy.MA_WITH_DEFINED_RR.value:
        return True
    elif data == ConfigModel.SupportedStrategy.SAMPLE_STRATEGY.value:
        return True
    return False


def validateExchange(data: ConfigModel.SupportedExchange):
    if data == None:
        return False
    if data == ConfigModel.SupportedExchange.BINANCE.value:
        return True
    return False
