from service.context.InMemContextService import ContextService
from service.dialogue.BotDialogue import BotDialogue
from service.exchangeService.BinanceService import ExchangeService
from service.fundManagement.TestFundManagement import AccountManagementService
# from service.strategy.SampleStrategy import StrategyService
# from service.strategy.bb_fakeout.BB_fakeout import StrategyService
from service.strategy.ma_fakeout.MA_fakeout import StrategyService
from service.authentication.AuthenticationService import AuthenticationService
from controller.TelegramController import Controller
from tradingbot.TradingBotBackTesting import TradingBotBackTestingService
from tradingbot.TradingBotService import TradingBotService
from service.configuration.JsonConfigService import ConfigService


class ServiceFactory:
    def __init__(self, accessToken, telegramToken, exchangeApiKey, exchangeApiSecret) -> None:
        self.configService = ConfigService("config.json")
        self.telegramToken = telegramToken
        self.exchangeApiKey = exchangeApiKey
        self.exchangeApiSecret = exchangeApiSecret
        self.accessToken = accessToken
        pass

    def getServices(self):
        authenticationService = AuthenticationService(self.accessToken)
        accountService = AccountManagementService(None)
        contextService = ContextService(
            "context.json",
            configService=self.configService
        )
        strategyService = StrategyService()
        botDialogueService = BotDialogue()
        exchangeService = ExchangeService(
            self.exchangeApiKey,
            self.exchangeApiSecret
        )
        tradingBotService = TradingBotService(
            botDialogueService=botDialogueService,
            contextService=contextService,
            accountService=accountService,
            exchangeService=exchangeService,
            strategyService=strategyService
        )
        tradingBackTestingService = TradingBotBackTestingService(
            botDialogueService=botDialogueService,
            configService=self.configService,
            accountService=accountService,
            exchangeService=exchangeService,
            strategyService=strategyService
        )
        controllerService = Controller(
            token=self.telegramToken,
            tradingBotService=tradingBotService,
            tradingBacktestingService=tradingBackTestingService,
            authenticationService=authenticationService
        )
        return controllerService, tradingBotService
