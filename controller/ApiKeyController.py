
class ApiKeyController:
    def __init__(self) -> None:
        pass

    def getBotApiToken(self) -> str:
        val = input("Enter your Trading Bot Token: ")
        return val

    def getTelegramApiToken(self) -> str:
        val = input("Enter your Telegram Token: ")
        return val

    def getBinanceApiKey(self) -> str:
        val = input("Enter your Binance Api Key: ")
        return val

    def getBinanceApiSecret(self) -> str:
        val = input("Enter your Binance Api Secret: ")
        return val
