from dataclasses import dataclass
import enum


class SupportedExchange(enum.Enum):
    BINANCE = "binance"


class SupportedStrategy(enum.Enum):
    SAMPLE_STRATEGY = "sample_strategy"
    MA_WITH_DEFINED_RR = "ma_with_defined_rr"


class SupportedController(enum.Enum):
    TELEGRAM = "telegram"
    BASH = "bash"


# class SupportedEController(enum.Enum):
#     TELEGRAM = "telegram"
#     BASH = "bash"


@dataclass
class ConfigData:
    maxActiveTrades: int
    settlementCurrency: str
    startBalance: int
    percentDeployedCapital: int
    strategy: str
    controller: str
    exchange: str
    isTestBot: bool
    whitelist: list[str]
    blacklist: list[str]
    riskToReward: float
    leverage: int
