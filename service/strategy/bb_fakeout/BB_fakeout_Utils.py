from dataclasses import dataclass
import enum
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
    BREAKOUT = "breakout"
    FAKEOUT = "fakeout"
    NO_BREACH = "no_breach"


@dataclass
class FakeoutDetectionResponse:
    detected: bool
    positionFromCurrentCandle: int
    fakeoutStartTime: int
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
def getMarketType(price: pd.Series, level: pd.Series, tollrance: float) -> MarketType:
    # Check of market if above MA
    aboveCount = 0
    belowCount = 0
    size = 4
    for index in range(len(price)-1, len(price)-1-size, -1):
        diffFromLevel = price.get(index) - level.get(index)
        percentDifference = diffFromLevel * 100.0/level.get(index)
        if percentDifference > tollrance:
            aboveCount = aboveCount + 1
        elif percentDifference < -tollrance:
            belowCount = belowCount + 1

    if aboveCount == size:
        return MarketType.BULLISH
    elif belowCount == size:
        return MarketType.BEARISH
    else:
        return MarketType.SIDEWAYS


# maxOffset - This parameter defines that how back from current candle to consider fakeout
# maxFakeoutWidth - This parameter defines that for how many candles fakeout can exist
def checkFakeout(approachType: AreaBreachApproachType, candleData: list[CandleStickType], level: pd.Series, maxOffset: int, maxFakeoutWidth: int) -> FakeoutDetectionResponse:
    breakoutCount = 0
    fakeoutCount = 0
    fakeoutStartIndex = 0
    fakeoutStartTime = 0

    if approachType == AreaBreachApproachType.FROM_DOWN:
        extremePrice = 0.0
    elif approachType == AreaBreachApproachType.FROM_TOP:
        extremePrice = 1000000.0
    else:
        extremePrice = 0.0

    # First check current candle status
    currentCandle = candleData[len(candleData) - 1]
    currentCandleAreaBreachType = __getAreaBreachType(
        approachType, currentCandle, level.get(level.size - 1))
    if currentCandleAreaBreachType != AreaBreachType.NO_BREACH:
        return FakeoutDetectionResponse(False, 0, 0, 0, 0.0, 0.0)

    # Exclude Current Candle Data
    for index in range(len(candleData)-maxOffset-maxFakeoutWidth-1, len(candleData)-1):
        candleAreaBreachType = __getAreaBreachType(
            approachType, candleData[index], level.get(index))
        if candleAreaBreachType == AreaBreachType.BREAKOUT:
            breakoutCount = breakoutCount + 1
            fakeoutStartTime = candleData[index].openTime
            fakeoutStartIndex = index
        elif candleAreaBreachType == AreaBreachType.FAKEOUT:
            fakeoutCount = fakeoutCount + 1
            fakeoutStartTime = candleData[index].openTime
            fakeoutStartIndex = index

        if candleAreaBreachType == AreaBreachType.FAKEOUT or candleAreaBreachType == AreaBreachType.BREAKOUT:
            if approachType == AreaBreachApproachType.FROM_DOWN and extremePrice < candleData[index].high:
                extremePrice = candleData[index].high
            elif approachType == AreaBreachApproachType.FROM_DOWN and extremePrice > candleData[index].low:
                extremePrice = candleData[index].low

    if breakoutCount > maxFakeoutWidth:
        return FakeoutDetectionResponse(False, 0, 0, 0, 0.0, 0.0)
    elif breakoutCount == 0 and fakeoutCount == 0:
        return FakeoutDetectionResponse(False, 0, 0, 0, 0.0, 0.0)
    elif breakoutCount < maxFakeoutWidth:
        return FakeoutDetectionResponse(True, len(candleData)-1-fakeoutStartIndex, fakeoutStartTime, breakoutCount, extremePrice, 1.0)
    elif fakeoutCount < maxFakeoutWidth:
        return FakeoutDetectionResponse(True, len(candleData)-1-fakeoutStartIndex, fakeoutStartTime, breakoutCount, extremePrice, 2.0)
    elif fakeoutCount >= maxFakeoutWidth:
        return FakeoutDetectionResponse(True, len(candleData)-1-fakeoutStartIndex, fakeoutStartTime, breakoutCount, extremePrice, 3.0)

    return FakeoutDetectionResponse(False, 0, 0, 0, 0.0, 0.0)


def __getAreaBreachType(approachType: AreaBreachApproachType, candleData: CandleStickType, level: float) -> AreaBreachType:
    if approachType == AreaBreachApproachType.FROM_DOWN:
        if candleData.close > level:
            return AreaBreachType.BREAKOUT
        elif candleData.high > level:
            return AreaBreachType.FAKEOUT
        else:
            return AreaBreachType.NO_BREACH
    elif approachType == AreaBreachApproachType.FROM_TOP:
        if candleData.close < level:
            return AreaBreachType.BREAKOUT
        elif candleData.low < level:
            return AreaBreachType.FAKEOUT
        else:
            return AreaBreachType.NO_BREACH
    return AreaBreachType.NO_BREACH

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
        return CandleType.GREEN
    else:
        return CandleType.RED
