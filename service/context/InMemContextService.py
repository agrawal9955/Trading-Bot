import dataclasses
import json
import logging
from time import time
import models.Context as ContextModel
import models.Controller as ControllerModel
import models.Config as ConfigModel
from service.configuration.JsonConfigService import ConfigService


class ContextService:
    def __init__(self, filePath, configService: ConfigService) -> None:
        self.filePath = filePath
        self.configService = configService
        pass

    def generateContext(self) -> ContextModel.ContextType:
        config = self.configService.getConfig()
        return ContextModel.ContextType(
            {},
            [],
            int(time()*1000000),
            False,
            False,
            [],
            config,
            ContextModel.AccountDetails(
                config.startBalance, config.startBalance, config.startBalance, 0.0),
            ContextModel.AccountDetails(
                config.startBalance, config.startBalance, config.startBalance, 0.0),
        )

    def getContext(self) -> ContextModel.ContextType:
        try:
            context = self.__loadContext()
            context.config = self.configService.getConfig()
            return context
        except Exception as e:
            logging.warning(
                "InMemContextService: getContext: Some Error Reading old Context File: Generating New Context\n")
            logging.warning(e)
            context = self.generateContext()
            self.__setContext(context)
            return context

    def __loadContext(self) -> ContextModel.ContextType:
        contextjson = json.load(open(self.filePath))

        context = ContextModel.ContextType(**contextjson)

        context.controllerActivity = []
        for activity in context.controllerActivity:
            context.controllerActivity.append(ControllerModel.ControllerActivity(
                **activity))

        context.config = ConfigModel.ConfigData(
            **contextjson["config"])

        context.accountDetails = ContextModel.AccountDetails(
            **contextjson["accountDetails"])

        context.dummyAccountDetails = ContextModel.AccountDetails(
            **contextjson["dummyAccountDetails"])

        context.activeTrades = {}
        for trade in contextjson["activeTrades"].values():
            context.activeTrades[trade["symbol"]
                                 ] = ContextModel.TradeType(**trade)

        context.totalTradeExecuted = []
        for trade in contextjson["totalTradeExecuted"]:
            context.totalTradeExecuted.append(
                ContextModel.TradeType(**trade))

        context.controllerActivity = []
        for activity in contextjson["controllerActivity"]:
            context.controllerActivity.append(
                ControllerModel.ControllerActivity(**activity))

        return context

    def addActiveTrade(self, context: ContextModel.ContextType, tradeData: ContextModel.TradeType):
        try:
            context.activeTrades[tradeData.symbol] = tradeData
            self.__setContext(context)
            return True, ""
        except Exception as e:
            logging.warning(
                "InMemContextService: addActiveTrade: Some Error In adding active trade\n")
            logging.warning(e)
            return False, str(e)

    def removeActiveTrade(self, context: ContextModel.ContextType, symbol: str):
        try:
            context.activeTrades.pop(symbol)
            self.__setContext(context)
            return True, ""
        except Exception as e:
            logging.warning(
                "InMemContextService: removeActiveTrade: Some Error In removing active trade\n")
            logging.warning(e)
            return False, str(e)

    def addTotalExecutedTrades(self, context: ContextModel.ContextType, tradeData: ContextModel.TradeType):
        try:
            context.totalTradeExecuted.append(tradeData)
            self.__setContext(context)
            return True, ""
        except Exception as e:
            logging.warning(
                "InMemContextService: addTotalExecutedTrades: Some Error In adding total executed trade\n")
            logging.warning(e)
            return False, str(e)

    def updateBotActiveState(self, context: ContextModel.ContextType, state: bool):
        try:
            context.currentBotStatus = state
            self.__setContext(context)
            return True, ""
        except Exception as e:
            logging.warning(
                "InMemContextService: updateBotActiveState: Some Error In updating bot active status\n")
            logging.warning(e)
            return False, str(e)

    def updateTradeEntryState(self, context: ContextModel.ContextType, state: bool):
        try:
            context.currentEntryStatus = state
            self.__setContext(context)
            return True, ""
        except Exception as e:
            logging.warning(
                "InMemContextService: updateTradeEntryState: Some Error In updating trade entry state\n")
            logging.warning(e)
            return False, str(e)

    def updateAccountDetails(self, context: ContextModel.ContextType, accountDetails: ContextModel.AccountDetails):
        try:
            context.accountDetails = accountDetails
            self.__setContext(context)
            return True, ""
        except Exception as e:
            logging.warning(
                "InMemContextService: updateAccountDetails: Some Error In updating account details\n")
            logging.warning(e)
            return False, str(e)

    def updateDummyAccountDetails(self, context: ContextModel.ContextType, accountDetails: ContextModel.AccountDetails):
        try:
            context.dummyAccountDetails = accountDetails
            self.__setContext(context)
            return True, ""
        except Exception as e:
            logging.warning(
                "InMemContextService: updateDummyAccountDetails: Some Error In updating dummy account details\n")
            logging.warning(e)
            return False, str(e)

    def updateDummyAccountDetails(self, context: ContextModel.ContextType, accountDetails: ContextModel.AccountDetails):
        try:
            context.dummyAccountDetails = accountDetails
            self.__setContext(context)
            return True, ""
        except Exception as e:
            logging.warning(
                "InMemContextService: updateDummyAccountDetails: Some Error In updating dummy account details\n")
            logging.warning(e)
            return False, str(e)

    def addControllerActivity(self, context: ContextModel.ContextType, controllerActivity: ControllerModel.ControllerActivity):
        try:
            context.controllerActivity.append(controllerActivity)
            self.__setContext(context)
            return True, ""
        except Exception as e:
            logging.warning(
                "InMemContextService: updateDummyAccountDetails: Some Error In updating dummy account details\n")
            logging.warning(e)
            return False, str(e)

    def __setContext(self, context: ContextModel.ContextType):
        jsonData = dataclasses.asdict(context)
        self.serviceBusy = True
        with open(self.filePath, 'w', encoding='utf-8') as f:
            json.dump(jsonData, f, ensure_ascii=False, indent=4)

        self.serviceBusy = False
        return

    ##############################################
    #
    #       Config Update Functions
    #
    ##############################################

    def updateMaxActiveTradesConfig(self, context: ContextModel.ContextType, data: int):
        try:
            err = self.configService.updateMaxActiveTradesConfig(data)
            if err == None or err == "":
                context.config = self.configService.getConfig()
            else:
                return False, err
            self.__setContext(context)
            return True, ""
        except Exception as e:
            logging.warning(
                "InMemContextService: updateMaxActiveTradesConfig: Some Error In updating Config MaxActiveTrades\n")
            logging.warning(e)
            return False, str(e)

    def updatePercentCapitalDeployedConfig(self, context: ContextModel.ContextType, data: int):
        try:
            err = self.configService.updatePercentCapitalDeployedConfig(data)
            if err == None or err == "":
                context.config = self.configService.getConfig()
            else:
                return False, err
            self.__setContext(context)
            return True, ""
        except Exception as e:
            logging.warning(
                "InMemContextService: updatePercentCapitalDeployedConfig: Some Error In updating Config MaxCapitalDeployed\n")
            logging.warning(e)
            return False, str(e)

    def updateWhitelistConfigAddCoin(self, context: ContextModel.ContextType, data: str):
        try:
            err = self.configService.updateWhitelistConfigAddCoin(data)
            if err == None or err == "":
                context.config = self.configService.getConfig()
            else:
                return False, err
            self.__setContext(context)
            return True, ""
        except Exception as e:
            logging.warning(
                "InMemContextService: updateWhitelistConfigAddCoin: Some Error In updating Config - add symbol to whitelist\n")
            logging.warning(e)
            return False, str(e)

    def updateWhitelistConfigRemoveCoin(self, context: ContextModel.ContextType, data: str):
        try:
            err = self.configService.updateWhitelistConfigRemoveCoin(data)
            if err == None or err == "":
                context.config = self.configService.getConfig()
            else:
                return False, err
            self.__setContext(context)
            return True, ""
        except Exception as e:
            logging.warning(
                "InMemContextService: updateWhitelistConfigRemoveCoin: Some Error In updating Config - remove symbol from whitelist\n")
            logging.warning(e)
            return False, str(e)

    def updateBlacklistConfigAddCoin(self, context: ContextModel.ContextType, data: str):
        try:
            err = self.configService.updateBlacklistConfigAddCoin(data)
            if err == None or err == "":
                context.config = self.configService.getConfig()
            else:
                return False, err
            self.__setContext(context)
            return True, ""
        except Exception as e:
            logging.warning(
                "InMemContextService: updateBlacklistConfigAddCoin: Some Error In updating Config - add symbol to blacklist\n")
            logging.warning(e)
            return False, str(e)

    def updateBlacklistConfigRemoveCoin(self, context: ContextModel.ContextType, data: str):
        try:
            err = self.configService.updateBlacklistConfigRemoveCoin(data)
            if err == None or err == "":
                context.config = self.configService.getConfig()
            else:
                return False, err
            self.__setContext(context)
            return True, ""
        except Exception as e:
            logging.warning(
                "InMemContextService: updateBlacklistConfigRemoveCoin: Some Error In updating Config - remove symbol from blacklist\n")
            logging.warning(e)
            return False, str(e)
