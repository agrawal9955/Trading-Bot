from dataclasses import dataclass
import enum

from models.Context import OrderType, PositionType


class TradeOutputType(enum.Enum):
    WINNER = "winner"
    LOSER = "loser"
    IN_PROGRESS = "in_progress"


@dataclass
class CandleStickType:
    openTime: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    closeTime: int
    quoteAssetVolume: float
    numberOfTrades: int
    takerBuyBaseAssetVolume: float
    takerBuyQuoteAssetVolume: float
    canBeIgnored: float


@dataclass
class OrderParameterData:
    symbol: str
    sideType: str
    orderType: str
    quantity: float
    price: float
    stoploss: float


@dataclass
class OrderFillsData:
    price: float
    quantity: float
    commission: float
    commissionAsset: str
    tradeId: int


@dataclass
class OrderData:
    symbol: str
    orderId: int
    orderListId: int
    clientOrderId: str
    transactTime: int
    price: float
    quantity: float
    status: str
    type: str
    side: str
    fills: list[OrderFillsData]


@dataclass
class InitiatePositionData:
    status: bool
    price: float
    orderType: str
    positionType: str
    stoploss: float


@dataclass
class ClosePositionData:
    status: bool
    price: float
    orderType: str
