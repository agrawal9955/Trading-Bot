from dataclasses import dataclass
import enum
import models.Controller as ControllerModels
import models.Config as ConfigModel


class SideType(enum.Enum):
    BUY = "buy"
    SELL = "sell"
    INVALID = "invalid"


class PositionType(enum.Enum):
    LONG = "long"
    SHORT = "short"
    INVALID = "invalid"


class OrderType(enum.Enum):
    LIMIT = "limit"
    MARKET = "market"
    INVALID = "invalid"


@dataclass
class TradeType:
    id: str
    leverage: int
    symbol: str
    timeFame: str
    quantity: float
    entryTime: int
    exitTime: int
    positionType: str
    entryPrice: float
    exitPrice: float
    activeStatus: bool
    tradingFee: float
    ROI: float
    takeProfit: float
    stopLoss: float
    entryValueInBaseCurrency: float
    tradeOutput: str


@dataclass
class AccountDetails:
    startingBalance: float
    closingBalance: float
    # this is the capital left that can be traded, (total-deployed)
    availableBalance: float
    ROI: float


@dataclass
class ContextType:
    activeTrades: dict[str, TradeType]
    totalTradeExecuted: list[TradeType]
    startTime: int
    currentBotStatus: bool
    currentEntryStatus: bool
    controllerActivity: list[ControllerModels.ControllerActivity]
    config: ConfigModel.ConfigData
    accountDetails: AccountDetails
    dummyAccountDetails: AccountDetails
