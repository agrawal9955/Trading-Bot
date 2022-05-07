from dataclasses import asdict, dataclass
import enum
import json
import pandas as pd
from models.Context import PositionType, TradeType
from models.ExchangeDataModel import CandleStickType, ClosePositionData, InitiatePositionData
import service.strategy.ma_fakeout.MA_fakeout_Utils as StrategyUtils

#################################################
#
#       Entry Helper Functions
#
#################################################

# tollrance - This parameter defines deadband percent tollrance around level


def getTradeEntry(backTestignEnabled: bool, candleData: list[CandleStickType]) -> StrategyUtils.TradeEntryConfidenceScoreType:
    priceClose = StrategyUtils.getArray(candleData, "close")

    ma_233 = StrategyUtils.calculateMA(200, priceClose)
    ma_377 = StrategyUtils.calculateMA(377, priceClose)

    percentDiff = (ma_233.get(ma_233.size-1) -
                   ma_377.get(ma_377.size-1)) * 100 / ma_377.get(ma_377.size-1)
    if percentDiff < 0.25:
        return StrategyUtils.TradeEntryConfidenceScoreType.NO_TRADE, "long", 0.0

    currentCandleCloseTime = candleData[len(candleData) - 1].closeTime

    # if currentCandleCloseTime >= 1651118700000:
    #     print("Debug Code")

    marketType = StrategyUtils.getMarketType(priceClose, ma_233, 0.00, 50)
    if marketType == StrategyUtils.MarketType.BULLISH:
        return __getLongTradeEntry(backTestignEnabled, candleData, ma_233)
    elif marketType == StrategyUtils.MarketType.BEARISH:
        return __getShortTradeEntry(backTestignEnabled, candleData, ma_233)
    else:
        return StrategyUtils.TradeEntryConfidenceScoreType.NO_TRADE, "long", 0.0


def __getLongTradeEntry(backTestignEnabled: bool, candleData: list[CandleStickType], ma: pd.Series) -> StrategyUtils.TradeEntryConfidenceScoreType:
    currentCandle = candleData[len(candleData) - 1]

    fakeoutDetection = StrategyUtils.checkFakeout(
        StrategyUtils.AreaBreachApproachType.FROM_TOP, candleData, ma, 2, 1)

    if fakeoutDetection.detected:
        # for back testing use open price otherwise entry rule will generally be violated
        # if not backTestignEnabled:
        #     entryDetection = StrategyUtils.checkEntry(
        #         PositionType.LONG, currentCandle.close, fakeoutDetection.peakPrice, bb_20_2.ma.get(bb_20_2.ma.size-1), 0.5)
        # else:
        #     entryDetection = StrategyUtils.checkEntry(
        #         PositionType.LONG, currentCandle.open, fakeoutDetection.peakPrice, bb_20_2.ma.get(bb_20_2.ma.size-1), 0.5)

        if (
            fakeoutDetection.score == 3.0
        ):
            return StrategyUtils.TradeEntryConfidenceScoreType.VERY_HIGH, PositionType.LONG.value, fakeoutDetection.peakPrice
        elif (
            fakeoutDetection.score == 2.0
        ):
            return StrategyUtils.TradeEntryConfidenceScoreType.HIGH, PositionType.LONG.value, fakeoutDetection.peakPrice
        elif (
            fakeoutDetection.score == 1.0
        ):
            return StrategyUtils.TradeEntryConfidenceScoreType.MID, PositionType.LONG.value, fakeoutDetection.peakPrice
        elif (
            fakeoutDetection.score == 0.0
        ):
            return StrategyUtils.TradeEntryConfidenceScoreType.NO_TRADE, PositionType.LONG.value, 0.0

    else:
        return StrategyUtils.TradeEntryConfidenceScoreType.NO_TRADE, PositionType.LONG.value, 0.0

    return StrategyUtils.TradeEntryConfidenceScoreType.NO_TRADE, PositionType.LONG.value, 0.0


def __getShortTradeEntry(backTestignEnabled: bool, candleData: list[CandleStickType], ma: pd.Series) -> StrategyUtils.TradeEntryConfidenceScoreType:
    currentCandle = candleData[len(candleData) - 1]

    fakeoutDetection = StrategyUtils.checkFakeout(
        StrategyUtils.AreaBreachApproachType.FROM_DOWN, candleData, ma, 2, 1)

    if fakeoutDetection.detected:
        # for back testing use open price otherwise entry rule will generally be violated
        # if not backTestignEnabled:
        #     entryDetection = StrategyUtils.checkEntry(
        #         PositionType.SHORT, currentCandle.close, fakeoutDetection.peakPrice, bb_20_2.ma.get(bb_20_2.ma.size-1), 0.5)
        # else:
        #     entryDetection = StrategyUtils.checkEntry(
        #         PositionType.SHORT, currentCandle.open, fakeoutDetection.peakPrice, bb_20_2.ma.get(bb_20_2.ma.size-1), 0.5)

        if (
            fakeoutDetection.score == 3.0
        ):
            return StrategyUtils.TradeEntryConfidenceScoreType.VERY_HIGH, PositionType.SHORT.value, fakeoutDetection.peakPrice
        elif (
            fakeoutDetection.score == 2.0
        ):
            return StrategyUtils.TradeEntryConfidenceScoreType.HIGH, PositionType.SHORT.value, fakeoutDetection.peakPrice
        elif (
            fakeoutDetection.score == 1.0
        ):
            return StrategyUtils.TradeEntryConfidenceScoreType.MID, PositionType.SHORT.value, fakeoutDetection.peakPrice
        elif (
            fakeoutDetection.score == 0.0
        ):
            return StrategyUtils.TradeEntryConfidenceScoreType.NO_TRADE, PositionType.SHORT.value, 0.0

    else:
        return StrategyUtils.TradeEntryConfidenceScoreType.NO_TRADE, PositionType.SHORT.value, 0.0

    return StrategyUtils.TradeEntryConfidenceScoreType.NO_TRADE, PositionType.SHORT.value, 0.0


#################################################
#
#       Exit Helper Functions
#
#################################################

# tollrance - This parameter defines deadband percent tollrance around level
def getTradeExit(candleData: list[CandleStickType], tradeData: TradeType) -> StrategyUtils.TradeExitConfidenceScoreType:
    currentCandle = candleData[len(candleData) - 1]
    percentStoploss = 0.1
    percentProfit = 15.0
    priceClose = StrategyUtils.getArray(candleData, "close")

    ma_233 = StrategyUtils.calculateMA(200, priceClose)
    ma_377 = StrategyUtils.calculateMA(377, priceClose)

    percentDiff = (ma_233.get(ma_233.size-1) -
                   ma_377.get(ma_377.size-1)) * 100 / ma_377.get(ma_377.size-1)

    if percentDiff > 0.5:
        percentStoploss = 0.25

    if percentDiff > 0.5:
        percentProfit = 10.0

    if tradeData.positionType == PositionType.LONG.value:
        if (currentCandle.close - tradeData.stopLoss) * 100.0 / currentCandle.close < -percentStoploss:
            return StrategyUtils.TradeExitConfidenceScoreType.FULL
    elif tradeData.positionType == PositionType.SHORT.value:
        if (tradeData.stopLoss - currentCandle.close) * 100.0 / currentCandle.close < -percentStoploss:
            return StrategyUtils.TradeExitConfidenceScoreType.FULL

    if tradeData.ROI > percentProfit:
        return StrategyUtils.TradeExitConfidenceScoreType.FULL

    return StrategyUtils.TradeExitConfidenceScoreType.NO_EXIT


def saveCandleData(candleData: list[CandleStickType]):
    output = []
    for data in candleData:
        output.append(asdict(data))

    with open("candleData.json", 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

    return
