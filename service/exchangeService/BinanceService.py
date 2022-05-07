from decimal import Decimal, Context
from tracemalloc import stop
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from models.Config import ConfigData
from models.Context import OrderType, PositionType
import service.exchangeService.BinanceServiceUutils as ExchangeUtils
import models.ExchangeDataModel as ExchangeDataModel
from binance import Client as BinanceClient


class ExchangeService:
    def __init__(self, apiKey, apiSecret) -> None:
        self.client = Client(apiKey, apiSecret)
        self.currentOrderId = 1
        self.currentTradeId = 100
        return

    #################################
    # Exchange Settings End Points #
    #################################
    def getAllAvailableCoins(self):
        return self.client.get_all_tickers()

    def checkExchangeActive(self):
        status = self.client.get_system_status()
        return status["status"] == 0

    ##############################
    # Get Market Data End Points #
    ##############################
    def getSymbolInfo(self, symbol):
        return self.client.get_symbol_info(symbol)

    def updateSymbolInfo(self, symbol):
        self.symbolInfo = self.getSymbolInfo(symbol)

    def getTradingFees(self, symbol):
        fees = self.client.get_trade_fee(symbol=symbol)
        return fees

    def getMarketDepth(self, symbol):
        return self.client.get_order_book(symbol=symbol)

    def getAveragePrice(self, symbol):
        return self.client.get_avg_price(symbol=symbol)

    def getRecentData(self, symbol, interval) -> list[ExchangeDataModel.CandleStickType]:
        formattedInterval = ExchangeUtils.getKlineInterval(interval)
        klines = self.client.get_klines(
            symbol=symbol, interval=formattedInterval)
        candleData = ExchangeUtils.convertKileToCandleStick(klines)
        return candleData

    def getHistoricalData(self, symbol, interval, start, end) -> list[ExchangeDataModel.CandleStickType]:
        formattedInterval = ExchangeUtils.getKlineInterval(interval)
        start = ExchangeUtils.getBinanceDate(start)
        end = ExchangeUtils.getBinanceDate(end)
        klines = self.client.get_historical_klines(
            symbol, formattedInterval, start, end)
        candleData = ExchangeUtils.convertKileToCandleStick(klines)
        return candleData

    ######################
    # Trading End points #
    ######################

    def placeOrder(self, orderParameter: ExchangeDataModel.OrderParameterData):
        symbolInfo = self.getSymbolInfo(orderParameter.symbol)
        formattedPositionType = ExchangeUtils.getBinancePositionType(
            orderParameter.positionType)
        formattedOrderType = ExchangeUtils.getBinanceOrderType(
            orderParameter.orderType, stoploss)
        status, price, quantity, stoploss = self.validateOrder(
            symbolInfo, price, quantity, stoploss)

        if not status:
            return None

        if stoploss != None:
            order = self.client.create_order(
                symbol=orderParameter.symbol,
                side=formattedPositionType,
                type=formattedOrderType,
                quantity=quantity,
                stopPrice=stoploss)
        else:
            order = self.client.create_order(
                symbol=orderParameter.symbol,
                side=formattedPositionType,
                type=formattedOrderType,
                quantity=quantity)

        return order

    def placeTestOrder(self, orderParameter: ExchangeDataModel.OrderParameterData, isBackTestingEnabled=False):
        if not isBackTestingEnabled:
            symbolInfo = self.getSymbolInfo(orderParameter.symbol)
        else:
            symbolInfo = self.symbolInfo
        formattedPositionType = ExchangeUtils.getBinancePositionType(
            orderParameter.sideType)
        formattedOrderType = ExchangeUtils.getBinanceOrderType(
            orderParameter.orderType, orderParameter.stoploss)
        status, orderParameter.price, orderParameter.quantity, orderParameter.stoploss = self.validateOrder(
            symbolInfo, orderParameter.price, orderParameter.quantity, orderParameter.stoploss)

        if not status:
            return None

        order = self.client.create_test_order(
            symbol=orderParameter.symbol,
            side=formattedPositionType,
            type=formattedOrderType,
            quantity=orderParameter.quantity)

        order = ExchangeUtils.generateTestOrder(
            orderParameter, self.currentOrderId, self.currentTradeId)
        self.currentOrderId = self.currentOrderId + 1
        self.currentTradeId = self.currentTradeId + 1

        return order

    def checkOrderStatus(self):
        return

    def cancelOrder(self):
        return

    def getAllOpenOrders(self):
        return

    #################################
    # Account Management End points #
    #################################
    # General
    def getAccountStatus(self):
        return

    # Assets
    def getAssetbalance(self):
        return

    # Orders
    def getAllTrades(self):
        return

    def getRecentTrades(self, symbol):
        trades = self.client.get_recent_trades(symbol=symbol)
        return trades

    def getAllOrders():
        return

    def getDailyAccountSnapshot(self, walletType):
        info = self.client.get_account_snapshot(type=walletType)
        return info

    #################################
    # Helper End points #
    #################################
    def validateOrder(self, symbolInfo, price, quantity, stoploss):
        for filter in symbolInfo["filters"]:

            if stoploss != None and filter["filterType"] == "PRICE_FILTER":
                stoploss = ExchangeUtils.applyPriceFilter(stoploss, filter)
                precision = ExchangeUtils.getPrecision(
                    float(filter["minPrice"]))
                stoploss = round(stoploss, precision)

            if price != None and filter["filterType"] == "PRICE_FILTER":
                price = ExchangeUtils.applyPriceFilter(price, filter)
                precision = ExchangeUtils.getPrecision(
                    float(filter["minPrice"]))
                price = round(price, precision)

            if quantity != None and filter["filterType"] == "LOT_SIZE":
                quantity = ExchangeUtils.applyLotSizeFilter(quantity, filter)
                precision = ExchangeUtils.getPrecision(
                    float(filter["minQty"]))
                quantity = round(quantity, precision)

        return True, price, quantity, stoploss
