from models.Context import AccountDetails, ContextType, TradeType
from models.ExchangeDataModel import CandleStickType


class AccountManagementService:
    def __init__(self, exchangeService) -> None:
        self
        pass

    def getCapitalForTrade(self, context: ContextType, currencyCost: float):
        accountBalance = context.dummyAccountDetails.availableBalance
        percentCapitalToBeDeployed = context.config.percentDeployedCapital/100
        totalTrades = context.config.maxActiveTrades - \
            len(context.activeTrades)

        capital = (accountBalance*percentCapitalToBeDeployed)/totalTrades

        return capital/currencyCost

    def updateAccountDetailsNewPosition(self, accountData: AccountDetails, tradeData: TradeType):
        accountData.availableBalance = accountData.availableBalance - \
            tradeData.entryValueInBaseCurrency
        return accountData

    def updateAccountDetailsClosePosition(self, accountData: AccountDetails, tradeData: TradeType):
        accountData.availableBalance = accountData.availableBalance + \
            tradeData.exitPrice * tradeData.quantity
        accountData.closingBalance = accountData.availableBalance
        accountData.ROI = (accountData.closingBalance -
                           accountData.startingBalance) * 100.0 / accountData.startingBalance
        return accountData
