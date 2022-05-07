from dataclasses import dataclass
import enum
from numpy import size
import pandas as pd
from models.Context import PositionType, TradeType
from models.ExchangeDataModel import CandleStickType


@dataclass
class BollingerBand:
    ma: pd.Series
    lowerBB: pd.Series
    upperBB: pd.Series


class MarketType(enum.Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    SIDEWAYS = "sideways"


class TradeEntryConfidenceScoreType(enum.Enum):
    VERY_HIGH = "very_high"
    HIGH = "high"
    MID = "mid"
    LOW = "low"
    VERY_LOW = "very_low"
    NO_TRADE = "no_trade"


class TradeExitConfidenceScoreType(enum.Enum):
    WENT_SIDEWAYS = "very_high"
    FULL = "high"
    PARTIAL = "mid"
    NO_EXIT = "no_trade"


class EntryType(enum.Enum):
    EARLY = "early"
    LATE = "late"
    PERFECT = "perfect"
    NO_ENTRY = "no_entry"


class AreaBreachApproachType(enum.Enum):
    FROM_DOWN = "from_down"
    FROM_TOP = "from_top"


class CandleType(enum.Enum):
    RED = "red"
    GREEN = "green"


class AreaBreachType(enum.Enum):
    COMPLETELY_ABOVE = "completely_above"
    FAKEOUT_FROM_ABOVE = "fakeout_from_above"
    IN_BETWEEN = "in_between"
    FAKEOUT_FROM_BELOW = "fakeout_from_below"
    COMPLETELY_BELOW = "completely_below"


@dataclass
class FakeoutDetectionResponse:
    detected: bool
    positionFromCurrentCandle: int
    fakeoutStartCandleData: CandleStickType
    durationInCandles: int
    peakPrice: float
    score: float


def getArray(candleData: list[CandleStickType], type) -> pd.Series:
    output = []
    for data in candleData:
        if type == "close":
            output.append(data.close)
        elif type == "open":
            output.append(data.open)
        elif type == "high":
            output.append(data.high)
        elif type == "low":
            output.append(data.low)
        else:
            output.append(0)
    return pd.Series(output)

#################################################
#
#       Indicator Helper Functions
#
#################################################


def calculateMA(length, price: pd.Series):
    return price.rolling(length).mean()


def calculateBB(maLength, stdDev, price: pd.Series) -> BollingerBand:
    bb_20_2 = BollingerBand(
        [-1.0]*price.size,
        [-1.0]*price.size,
        [-1.0]*price.size
    )

    std = price.rolling(maLength).std()
    bb_20_2.ma = calculateMA(maLength, price)
    bb_20_2.lowerBB = bb_20_2.ma - std * stdDev
    bb_20_2.upperBB = bb_20_2.ma + std * stdDev

    return bb_20_2


#################################################
#
#       Entry Helper Functions
#
#################################################

# tollrance - This parameter defines deadband percent tollrance around level
def getMarketType(price: pd.Series, level: pd.Series, tollrance: float, maxOffset: int) -> MarketType:
    # Check of market if above MA
    aboveCount = 0
    belowCount = 0
    for index in range(len(price)-1, len(price)-1-maxOffset, -1):
        currentPrice = price.get(index)
        currentLevel = level.get(index)
        diffFromLevel = price.get(index) - level.get(index)
        percentDifference = diffFromLevel * 100.0/level.get(index)
        if percentDifference > tollrance:
            aboveCount = aboveCount + 1
        elif percentDifference < -tollrance:
            belowCount = belowCount + 1

    if float(aboveCount) > float(maxOffset)/2.0:
        return MarketType.BULLISH
    elif float(belowCount) > float(maxOffset)/2.0:
        return MarketType.BEARISH
    else:
        return MarketType.SIDEWAYS

    # if aboveCount == maxOffset:
    #     return MarketType.BULLISH
    # elif belowCount == maxOffset:
    #     return MarketType.BEARISH
    # else:
    #     return MarketType.SIDEWAYS


# maxOffset - This parameter defines that how back from current candle to consider fakeout
# maxFakeoutWidth - This parameter defines that for how many candles fakeout can exist
def checkFakeout(approachType: AreaBreachApproachType, candleData: list[CandleStickType], level: pd.Series, maxOffset: int, maxFakeoutWidth: int) -> FakeoutDetectionResponse:
    breakoutCount = 0
    fakeoutCount = 0
    fakeoutStartIndex = 0
    fakeoutStartCandleData = None

    if approachType == AreaBreachApproachType.FROM_DOWN:
        extremePrice = 0.0
    elif approachType == AreaBreachApproachType.FROM_TOP:
        extremePrice = 100000000.0
    else:
        extremePrice = 0.0

    # First check current candle status
    currentCandle = candleData[len(candleData) - 1]
    currentCandleType = getCandleType(currentCandle)
    currentCandleAreaBreachType = __getAreaBreachType(
        currentCandle, level.get(level.size - 1))

    if (
            approachType == AreaBreachApproachType.FROM_DOWN and
            (
                currentCandleAreaBreachType == AreaBreachType.COMPLETELY_ABOVE or
                currentCandleAreaBreachType == AreaBreachType.FAKEOUT_FROM_ABOVE
            )
    ):
        return FakeoutDetectionResponse(False, 0, None, 0, 0.0, 0.0)
    elif (
            approachType == AreaBreachApproachType.FROM_TOP and
            (
                currentCandleAreaBreachType == AreaBreachType.COMPLETELY_BELOW or
                currentCandleAreaBreachType == AreaBreachType.FAKEOUT_FROM_BELOW
            )
    ):
        return FakeoutDetectionResponse(False, 0, None, 0, 0.0, 0.0)
    elif (
        approachType == AreaBreachApproachType.FROM_DOWN and
        currentCandleType == CandleType.GREEN and
        currentCandleAreaBreachType == AreaBreachType.IN_BETWEEN
    ):
        return FakeoutDetectionResponse(False, 0, None, 0, 0.0, 0.0)
    elif (
        approachType == AreaBreachApproachType.FROM_TOP and
        currentCandleType == CandleType.RED and
        currentCandleAreaBreachType == AreaBreachType.IN_BETWEEN
    ):
        return FakeoutDetectionResponse(False, 0, None, 0, 0.0, 0.0)

    # check if move already done
    diffFromLevel = currentCandle.low - level.get(level.size-1)
    percentDiff = diffFromLevel*100/level.get(level.size-1)
    if percentDiff > 0.1 or percentDiff < -0.1:
        return FakeoutDetectionResponse(False, 0, None, 0, 0.0, 0.0)

    # Exclude Current Candle Data
    for index in range(len(candleData)-maxOffset-maxFakeoutWidth-1, len(candleData)-1):
        candleAreaBreachType = __getAreaBreachType(
            candleData[index], level.get(index))
        candleType = getCandleType(candleData[index])

        if approachType == AreaBreachApproachType.FROM_DOWN:
            if candleAreaBreachType == AreaBreachType.FAKEOUT_FROM_BELOW:
                fakeoutCount = fakeoutCount + 1
                fakeoutStartIndex = index
                fakeoutStartCandleData = candleData[index]
            elif candleAreaBreachType == AreaBreachType.COMPLETELY_ABOVE:
                breakoutCount = breakoutCount + 1
                fakeoutStartCandleData = candleData[index]
            elif candleType == CandleType.RED and candleAreaBreachType == AreaBreachType.IN_BETWEEN:
                fakeoutCount = fakeoutCount + 1
                fakeoutStartIndex = index
                fakeoutStartCandleData = candleData[index]
            elif candleType == CandleType.GREEN and candleAreaBreachType == AreaBreachType.IN_BETWEEN:
                breakoutCount = breakoutCount + 1
                fakeoutStartCandleData = candleData[index]
        elif approachType == AreaBreachApproachType.FROM_TOP:
            if candleAreaBreachType == AreaBreachType.FAKEOUT_FROM_ABOVE:
                fakeoutCount = fakeoutCount + 1
                fakeoutStartIndex = index
                fakeoutStartCandleData = candleData[index]
            elif candleAreaBreachType == AreaBreachType.COMPLETELY_BELOW:
                breakoutCount = breakoutCount + 1
                fakeoutStartCandleData = candleData[index]
            elif candleType == CandleType.GREEN and candleAreaBreachType == AreaBreachType.IN_BETWEEN:
                fakeoutCount = fakeoutCount + 1
                fakeoutStartIndex = index
                fakeoutStartCandleData = candleData[index]
            elif candleType == CandleType.RED and candleAreaBreachType == AreaBreachType.IN_BETWEEN:
                breakoutCount = breakoutCount + 1
                fakeoutStartCandleData = candleData[index]

        if approachType == AreaBreachApproachType.FROM_DOWN:
            if candleAreaBreachType == AreaBreachType.COMPLETELY_ABOVE or candleAreaBreachType == AreaBreachType.FAKEOUT_FROM_BELOW or candleAreaBreachType == AreaBreachType.IN_BETWEEN or candleAreaBreachType == AreaBreachType.FAKEOUT_FROM_ABOVE:
                if extremePrice < candleData[index].high:
                    extremePrice = candleData[index].high
        elif approachType == AreaBreachApproachType.FROM_TOP:
            if candleAreaBreachType == AreaBreachType.COMPLETELY_BELOW or candleAreaBreachType == AreaBreachType.FAKEOUT_FROM_ABOVE or candleAreaBreachType == AreaBreachType.IN_BETWEEN or candleAreaBreachType == AreaBreachType.FAKEOUT_FROM_BELOW:
                if extremePrice > candleData[index].low:
                    extremePrice = candleData[index].low

    # check if there was a breakout
    prevMarketType = getMarketType(
        getArray(candleData[0:len(candleData) -
                 maxOffset - maxFakeoutWidth], "close"),
        level,
        0.0,
        maxOffset + maxFakeoutWidth
    )
    if approachType == AreaBreachApproachType.FROM_DOWN and prevMarketType != MarketType.BEARISH:
        return FakeoutDetectionResponse(False, 0, None, 0, 0.0, 0.0)
    elif approachType == AreaBreachApproachType.FROM_TOP and prevMarketType != MarketType.BULLISH:
        return FakeoutDetectionResponse(False, 0, None, 0, 0.0, 0.0)

    if breakoutCount + fakeoutCount > maxFakeoutWidth:
        return FakeoutDetectionResponse(False, 0, None, 0, 0.0, 0.0)
    elif breakoutCount == 0 and fakeoutCount == 0:
        return FakeoutDetectionResponse(False, 0, None, 0, 0.0, 0.0)
    elif breakoutCount < maxFakeoutWidth:
        return FakeoutDetectionResponse(True, len(candleData)-1-fakeoutStartIndex, fakeoutStartCandleData, breakoutCount + fakeoutCount, extremePrice, 1.0)
    elif fakeoutCount < maxFakeoutWidth:
        return FakeoutDetectionResponse(True, len(candleData)-1-fakeoutStartIndex, fakeoutStartCandleData, breakoutCount + fakeoutCount, extremePrice, 2.0)
    elif fakeoutCount >= maxFakeoutWidth:
        return FakeoutDetectionResponse(True, len(candleData)-1-fakeoutStartIndex, fakeoutStartCandleData, breakoutCount + fakeoutCount, extremePrice, 3.0)

    return FakeoutDetectionResponse(False, 0, None, 0, 0.0, 0.0)


def __getAreaBreachType(candleData: CandleStickType, level: float) -> AreaBreachType:
    candleType = getCandleType(candleData)
    if candleType == CandleType.GREEN:
        if candleData.low > level:
            return AreaBreachType.COMPLETELY_ABOVE
        elif candleData.open > level:
            return AreaBreachType.FAKEOUT_FROM_ABOVE
        elif candleData.high < level:
            return AreaBreachType.COMPLETELY_BELOW
        elif candleData.close < level:
            return AreaBreachType.FAKEOUT_FROM_BELOW
        else:
            return AreaBreachType.IN_BETWEEN
    else:
        if candleData.low > level:
            return AreaBreachType.COMPLETELY_ABOVE
        elif candleData.close > level:
            return AreaBreachType.FAKEOUT_FROM_ABOVE
        elif candleData.high < level:
            return AreaBreachType.COMPLETELY_BELOW
        elif candleData.open < level:
            return AreaBreachType.FAKEOUT_FROM_BELOW
        else:
            return AreaBreachType.IN_BETWEEN

    # maxOffset - This parameter defines that how back from current candle to consider fakeout
    # tollrance - This parameter defines that for how many candles fakeout can exist


def checkEntry(positionType: PositionType, price: float, stoploss: float, target: float, rr: float) -> EntryType:
    if positionType == PositionType.LONG:
        if price >= target:
            tempRR = 100.0
        else:
            tempRR = (price - stoploss)/(target - price)
    elif positionType == PositionType.SHORT:
        if price <= target:
            tempRR = 100.0
        else:
            tempRR = (stoploss - price)/(price - target)
    else:
        tempRR = 100.0

    if tempRR < rr/2.0:
        return EntryType.EARLY
    elif tempRR < rr and tempRR > rr/2.0:
        return EntryType.PERFECT
    elif tempRR > rr and tempRR < rr/0.75:
        return EntryType.LATE
    else:
        return EntryType.NO_ENTRY


#################################################
#
#       Exit Helper Functions
#
#################################################

def checkRoi(price: pd.Series, tradeData: TradeType, maxRoi: float, minRoi: float):
    return


def checkWeakness(candleData: list[CandleStickType]):
    return


def checkTimeLasped(candleData: list[CandleStickType], tradeData: TradeType):
    return


#################################################
#
#       General Helper Functions
#
#################################################
def getCandleType(candleData: CandleStickType) -> CandleType:
    if candleData.open > candleData.close:
        return CandleType.RED
    else:
        return CandleType.GREEN
