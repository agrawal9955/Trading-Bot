from dataclasses import asdict, dataclass
import enum
import json
import pandas as pd
from models.Context import PositionType, TradeType
from models.ExchangeDataModel import CandleStickType, ClosePositionData, InitiatePositionData
import service.strategy.bb_fakeout.BB_fakeout_Utils as StrategyUtils

#################################################
#
#       Entry Helper Functions
#
#################################################

# tollrance - This parameter defines deadband percent tollrance around level


def getTradeEntry(backTestignEnabled: bool, candleData: list[CandleStickType]) -> StrategyUtils.TradeEntryConfidenceScoreType:
    priceClose = StrategyUtils.getArray(candleData, "close")

    ma_89 = StrategyUtils.calculateMA(89, priceClose)
    bb_20_2 = StrategyUtils.calculateBB(20, 2, priceClose)

    currentTime = candleData[len(candleData) - 1].openTime
    marketType = StrategyUtils.getMarketType(priceClose, ma_89, 0.5)
    if marketType == StrategyUtils.MarketType.BULLISH:
        return __getShortTradeEntry(backTestignEnabled, candleData, bb_20_2)
    elif marketType == StrategyUtils.MarketType.BEARISH:
        return __getLongTradeEntry(backTestignEnabled, candleData, bb_20_2)
    else:
        return StrategyUtils.TradeEntryConfidenceScoreType.NO_TRADE, "long"


def __getLongTradeEntry(backTestignEnabled: bool, candleData: list[CandleStickType], bb_20_2: StrategyUtils.BollingerBand) -> StrategyUtils.TradeEntryConfidenceScoreType:
    currentCandle = candleData[len(candleData) - 1]

    fakeoutDetection = StrategyUtils.checkFakeout(
        StrategyUtils.AreaBreachApproachType.FROM_TOP, candleData, bb_20_2.lowerBB, 2, 3)

    if fakeoutDetection.detected:
        saveCandleData(candleData)
        # for back testing use open price otherwise entry rule will generally be violated
        if not backTestignEnabled:
            entryDetection = StrategyUtils.checkEntry(
                PositionType.LONG, currentCandle.close, fakeoutDetection.peakPrice, bb_20_2.ma.get(bb_20_2.ma.size-1), 0.5)
        else:
            entryDetection = StrategyUtils.checkEntry(
                PositionType.LONG, currentCandle.open, fakeoutDetection.peakPrice, bb_20_2.ma.get(bb_20_2.ma.size-1), 0.5)

        if (
            fakeoutDetection.score < 3.0 and
            entryDetection == StrategyUtils.EntryType.LATE
        ):
            return StrategyUtils.TradeEntryConfidenceScoreType.VERY_LOW, PositionType.LONG.value
        elif (
            fakeoutDetection.score < 3.0 and
            entryDetection == StrategyUtils.EntryType.EARLY
        ):
            return StrategyUtils.TradeEntryConfidenceScoreType.LOW, PositionType.LONG.value
        elif (
            fakeoutDetection.score < 3.0 and
            entryDetection == StrategyUtils.EntryType.PERFECT
        ):
            return StrategyUtils.TradeEntryConfidenceScoreType.MID, PositionType.LONG.value
        elif (
            fakeoutDetection.score == 3.0 and
            entryDetection == StrategyUtils.EntryType.LATE
        ):
            return StrategyUtils.TradeEntryConfidenceScoreType.LOW, PositionType.LONG.value
        elif (
            fakeoutDetection.score == 3.0 and
            entryDetection == StrategyUtils.EntryType.EARLY
        ):
            return StrategyUtils.TradeEntryConfidenceScoreType.HIGH, PositionType.LONG.value
        elif (
            fakeoutDetection.score == 3.0 and
            entryDetection == StrategyUtils.EntryType.PERFECT
        ):
            return StrategyUtils.TradeEntryConfidenceScoreType.VERY_HIGH, PositionType.LONG.value

    else:
        return StrategyUtils.TradeEntryConfidenceScoreType.NO_TRADE, PositionType.LONG.value

    return StrategyUtils.TradeEntryConfidenceScoreType.NO_TRADE, PositionType.LONG.value


def __getShortTradeEntry(backTestignEnabled: bool, candleData: list[CandleStickType], bb_20_2: StrategyUtils.BollingerBand) -> StrategyUtils.TradeEntryConfidenceScoreType:
    currentCandle = candleData[len(candleData) - 1]

    fakeoutDetection = StrategyUtils.checkFakeout(
        StrategyUtils.AreaBreachApproachType.FROM_DOWN, candleData, bb_20_2.upperBB, 2, 3)

    if fakeoutDetection.detected:
        saveCandleData(candleData)
        # for back testing use open price otherwise entry rule will generally be violated
        if not backTestignEnabled:
            entryDetection = StrategyUtils.checkEntry(
                PositionType.SHORT, currentCandle.close, fakeoutDetection.peakPrice, bb_20_2.ma.get(bb_20_2.ma.size-1), 0.5)
        else:
            entryDetection = StrategyUtils.checkEntry(
                PositionType.SHORT, currentCandle.open, fakeoutDetection.peakPrice, bb_20_2.ma.get(bb_20_2.ma.size-1), 0.5)

        if (
            fakeoutDetection.score < 3.0 and
            entryDetection == StrategyUtils.EntryType.LATE
        ):
            return StrategyUtils.TradeEntryConfidenceScoreType.VERY_LOW, PositionType.SHORT.value
        elif (
            fakeoutDetection.score < 3.0 and
            entryDetection == StrategyUtils.EntryType.EARLY
        ):
            return StrategyUtils.TradeEntryConfidenceScoreType.LOW, PositionType.SHORT.value
        elif (
            fakeoutDetection.score < 3.0 and
            entryDetection == StrategyUtils.EntryType.PERFECT
        ):
            return StrategyUtils.TradeEntryConfidenceScoreType.MID, PositionType.SHORT.value
        elif (
            fakeoutDetection.score == 3.0 and
            entryDetection == StrategyUtils.EntryType.LATE
        ):
            return StrategyUtils.TradeEntryConfidenceScoreType.LOW, PositionType.SHORT.value
        elif (
            fakeoutDetection.score == 3.0 and
            entryDetection == StrategyUtils.EntryType.EARLY
        ):
            return StrategyUtils.TradeEntryConfidenceScoreType.HIGH, PositionType.SHORT.value
        elif (
            fakeoutDetection.score == 3.0 and
            entryDetection == StrategyUtils.EntryType.PERFECT
        ):
            return StrategyUtils.TradeEntryConfidenceScoreType.VERY_HIGH, PositionType.SHORT.value

    else:
        return StrategyUtils.TradeEntryConfidenceScoreType.NO_TRADE, PositionType.SHORT.value

    return StrategyUtils.TradeEntryConfidenceScoreType.NO_TRADE, PositionType.SHORT.value


#################################################
#
#       Exit Helper Functions
#
#################################################

# tollrance - This parameter defines deadband percent tollrance around level
def getTradeExit(candleData: list[CandleStickType], tradeData: TradeType) -> StrategyUtils.TradeExitConfidenceScoreType:
    if tradeData.ROI < -0.15:
        return StrategyUtils.TradeExitConfidenceScoreType.FULL
    elif tradeData.ROI > 0.3:
        return StrategyUtils.TradeExitConfidenceScoreType.FULL

    return StrategyUtils.TradeExitConfidenceScoreType.NO_EXIT


def saveCandleData(candleData: list[CandleStickType]):
    output = []
    for data in candleData:
        output.append(asdict(data))

    with open("candleData.json", 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

    return
