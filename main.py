import logging
from controller.ApiKeyController import ApiKeyController
from service.ServiceFactory import ServiceFactory

apiKeyController = ApiKeyController()

# Gather all token from deployment
botApiToken = apiKeyController.getBotApiToken()
telegramToken = apiKeyController.getTelegramApiToken()
binanceApiKey = apiKeyController.getBinanceApiKey()
binanceApiSecret = apiKeyController.getBinanceApiSecret()


serviceFactory = ServiceFactory(
    accessToken=botApiToken,
    telegramToken=telegramToken,
    exchangeApiKey=binanceApiKey,
    exchangeApiSecret=binanceApiSecret)


# get all services
controllerService, tradingBotService = serviceFactory.getServices()

if controllerService == None or tradingBotService == None:
    logging.warning("invalid config")
else:
    controllerService.runBot()
    tradingBotService.run()
