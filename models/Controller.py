import enum
from typing import Callable
from dataclasses import dataclass
import typing


AUTHENTICATION, ENQUIRY, CONFIG, BACKTESTING = range(4)


class ControllerIntent(enum.Enum):
    START_BOT = "/start_bot"
    STOP_BOT = "/stop_bot"
    START_ENTRY = "/start_entry"
    STOP_ENTRY = "/stop_entry"
    ACTIVE_TRADES = "/active_trades"
    FORCE_EXIT = "/force_exit"
    PERFORMANCE = "/performance"
    REPORT = "/report"
    ACCOUNT_STATEMENT = "/account_statement"
    STATUS = "/status"

    UPDATE_CONFIG_MAX_ACTIVE_TRADES = "/max_active_trade"
    UPDATE_CONFIG_PERCENT_DEPLOYED_CAPITAL = "/percent_deployed_capital"
    UPDATE_CONFIG_STRATEGY = "/strategy"
    UPDATE_WHITELIST_ADD_COIN = "/whitelist_add_coin"
    UPDATE_WHITELIST_REMOVE_COIN = "/whitelist_remove_coin"
    UPDATE_BLACKLIST_ADD_COIN = "/blacklist_add_coin"
    UPDATE_BLACKLIST_REMOVE_COIN = "/blacklist_remove_coin"

    # query - symbol, startDate, endDate, strategy, timeframe, leverage, plannedRR, orderType, positionType
    BACKTEST = "/backtest"


@dataclass
class ControllerQuery:
    params: map


@dataclass
class ControllerRequest:
    text: str
    setReply: Callable[[str], None]


@dataclass
class ControllerActivity:
    lastAccessedTime: int
    lastExecutedCd: str
