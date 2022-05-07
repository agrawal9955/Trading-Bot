import dataclasses
import json
import logging
import models.Config as ConfigModel
import service.configuration.ConfigServiceUtils as ConfigServiceUtils


class ConfigService:
    def __init__(self, filename) -> None:
        self.filename = filename
        pass

    def __generateConfig(self) -> ConfigModel.ConfigData:
        return ConfigModel.ConfigData(
            3,
            "USDT",
            100,
            80,
            "ma",
            "telegram",
            "binance",
            True,
            [],
            [],
            0.5,
            1
        )

    def __validateConfig(self, configJson) -> ConfigModel.ConfigData:
        try:
            config = ConfigModel.ConfigData(**configJson)
            if (ConfigServiceUtils.validateExchange(config.exchange) and
                    ConfigServiceUtils.validateMaxActiveTrades(config.maxActiveTrades) and
                    ConfigServiceUtils.validatePercentDeployedCapital(config.percentDeployedCapital) and
                    ConfigServiceUtils.validateStrategy(config.strategy)):
                return config
            return None
        except Exception as e:
            logging.warning(
                "JsonConfigService: __validateConfig: Some Error in Validating Config json")
            logging.warning(e)
            return None

    def getConfig(self) -> ConfigModel.ConfigData:
        try:
            configJson = json.load(open(self.filename))
            config = self.__validateConfig(configJson)
            if config != None:
                return config
            else:
                return self.__generateConfig()
        except Exception as e:
            logging.warning(
                "JsonConfigService: getConfig: Some Error Reading old Config File: Generating New Config\n")
            logging.warning(e)
            config = self.__generateConfig()
            self.__setConfig(config)
            return config

    # currently not supporting change of
    # some parameters because of security reasons:
    #   List of variables blocked for update:
    #     - startBalance
    #     - isTestBot
    #     - settlementCurrency
    #     - controller
    #
    #     for now exchange update is also not supported
    #
    def updateMaxActiveTradesConfig(self, data: int):
        config = self.getConfig()
        if ConfigServiceUtils.validateMaxActiveTrades(data):
            config.maxActiveTrades = data
        else:
            return "Invalid input: Max Active Trades Should be between 0 to 100\n"
        self.__setConfig(config)
        return ""

    def updatePercentCapitalDeployedConfig(self, data: int):
        config = self.getConfig()
        if ConfigServiceUtils.validatePercentDeployedCapital(data):
            config.percentDeployedCapital = data
        else:
            return "Invalid input: Percent Capital Deployed Should be between 0 to 100\n"
        self.__setConfig(config)
        return ""

    def updateWhitelistConfigAddCoin(self, data: int):
        config = self.getConfig()
        config.whitelist.append(data)
        self.__setConfig(config)
        return ""

    def updateWhitelistConfigRemoveCoin(self, data: int):
        config = self.getConfig()
        if data in config.whitelist:
            config.whitelist.remove(data)
        else:
            return "Invalid input: Symbol doesn't exist in whilelist\n"
        self.__setConfig(config)
        return ""

    def updateBlacklistConfigAddCoin(self, data: int):
        config = self.getConfig()
        config.blacklist.append(data)
        self.__setConfig(config)
        return ""

    def updateBlacklistConfigRemoveCoin(self, data: int):
        config = self.getConfig()
        if data in config.blacklist:
            config.blacklist.remove(data)
        else:
            return "Invalid input: Symbol doesn't exist in blacklist\n"
        self.__setConfig(config)
        return ""

    def __setConfig(self, config: ConfigModel.ConfigData):
        jsonData = dataclasses.asdict(config)
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(jsonData, f, ensure_ascii=False, indent=4)

        return
