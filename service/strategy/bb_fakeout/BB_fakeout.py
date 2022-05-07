from time import time
from models.Context import TradeType
import models.ExchangeDataModel as ExchangeDataModel
import pandas as pd
import service.strategy.bb_fakeout.BB_fakeout_Utils as StrategyUtils
import service.strategy.bb_fakeout.BB_fakeout_BL as StrategyBL


class StrategyService:
    def __init__(self) -> None:
        self.indicatorData = {}
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

    # update indicator data in self.indicatorData Map
    def calculateIndicators(self, candleData: list[ExchangeDataModel.CandleStickType]):
        return

    # return signal and stoploss value
    def initiatePositionSignal(self, candleData: list[ExchangeDataModel.CandleStickType], marketDepth=None, backTestingEnabled=False) -> ExchangeDataModel.InitiatePositionData:
        initiateSignal, positionType = StrategyBL.getTradeEntry(
            backTestingEnabled, candleData)

        if initiateSignal != StrategyUtils.TradeEntryConfidenceScoreType.NO_TRADE:
            if not backTestingEnabled:
                return ExchangeDataModel.InitiatePositionData(True, candleData[len(candleData) - 1].close, "market", positionType, None)
            else:
                return ExchangeDataModel.InitiatePositionData(True, candleData[len(candleData) - 1].open, "market", positionType, None)
        return ExchangeDataModel.InitiatePositionData(False, None, "market", "long", None)

    def closePositionSignal(self, candleData: list[ExchangeDataModel.CandleStickType], tradeData: TradeType, backTestingEnabled=False) -> ExchangeDataModel.ClosePositionData:
        if tradeData == None:
            return ExchangeDataModel.ClosePositionData(False, None, "market")

        exitSignal = StrategyBL.getTradeExit(candleData, tradeData)

        if exitSignal != StrategyUtils.TradeExitConfidenceScoreType.NO_EXIT:
            if not backTestingEnabled:
                return ExchangeDataModel.ClosePositionData(True, candleData[len(candleData) - 1].close, "market")
            else:
                return ExchangeDataModel.ClosePositionData(True, candleData[len(candleData) - 1].open, "market")
        return ExchangeDataModel.ClosePositionData(False, None, "market")
