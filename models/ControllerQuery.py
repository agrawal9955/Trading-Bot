from dataclasses import dataclass
import enum


class StopBotCommands(enum.Enum):
    HARD = "hard"
    SOFT = "soft"
    INVALID = "invalid"


class ForceExitCommands(enum.Enum):
    ALL = "all"
    INVALID = "invalid"


class QueryKeys(enum.Enum):
    STOP_TYPE = "stop_type"
    MAX_OPEN_TRADE = "max_open_trade"
    PERCENT_CAPITAL_DEPLOYED = "percent_capital_deployed"
    SYMBOL = "symbol"


@dataclass
class BackTestQuery:
    symbol: str
    startDate: str
    endDate: str
    strategy: str
    timeframe: str
    leverage: int
    plannedRR: float
    orderType: str
    positionType: str
