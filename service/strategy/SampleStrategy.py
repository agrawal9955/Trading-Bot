from time import time
from models.Context import TradeType
import models.ExchangeDataModel as ExchangeDataModel


class StrategyService:
    def __init__(self) -> None:
        self.indicatorData = {}
        return

    # return signal and stoploss value
    def initiatePositionSignal(self, candleData: list[ExchangeDataModel.CandleStickType], marketDepth=None, backTestingEnabled=False) -> ExchangeDataModel.InitiatePositionData:

        currentTime = int(time()*1000000)
        currentCandle = candleData[len(
            candleData) - 1]
        secTillCandleClose = currentCandle.closeTime - currentTime
        if secTillCandleClose < 50 and secTillCandleClose > 35:
            return ExchangeDataModel.InitiatePositionData(True, None, "market", "long", None)
        return ExchangeDataModel.InitiatePositionData(False, None, "market", "long", None)

    def closePositionSignal(self, candleData: list[ExchangeDataModel.CandleStickType], tradeData: TradeType, backTestingEnabled=False) -> ExchangeDataModel.ClosePositionData:
        if tradeData == None:
            return ExchangeDataModel.ClosePositionData(False, None, "market")

        currentTime = int(time()*1000000)
        currentCandle = candleData[len(
            candleData) - 1]
        secTillCandleClose = currentCandle.closeTime - currentTime
        if secTillCandleClose > 10 and secTillCandleClose < 25:
            return ExchangeDataModel.ClosePositionData(True, None, "market")
        return ExchangeDataModel.ClosePositionData(False, None, "market")

    # update indicator data in self.indicatorData Map
    def calculateIndicators(self, candleData: list[ExchangeDataModel.CandleStickType]):
        return

    # timeframe should be configured here
    def getDesiredTimeFrame(self, symbol):
        timeFramePerPair = {
            "ETHUSDT": "1m",
            "SOLUSDT": "1m",
            "BTCUSDT": "1m",
        }

        if symbol in timeFramePerPair.keys():
            return timeFramePerPair[symbol]

        return ""
