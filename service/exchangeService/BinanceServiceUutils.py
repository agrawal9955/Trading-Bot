from time import time
from binance import Client as BinanceClient
from models.Context import OrderType, SideType
import models.ExchangeDataModel as ExchangeDataModel
from binance.helpers import round_step_size

currentOrderId = 0
currentTradeId = 100


def getBinanceDate(inputDate):
    date = inputDate.split("-")

    return date[0] + " " + __getBinanceMonth(date[1]) + ", " + date[2]


def __getBinanceMonth(month):
    monthInt = int(month)
    if monthInt == 1:
        return "Jan"
    elif monthInt == 2:
        return "Feb"
    elif monthInt == 3:
        return "Mar"
    elif monthInt == 4:
        return "Apr"
    elif monthInt == 5:
        return "May"
    elif monthInt == 6:
        return "Jun"
    elif monthInt == 7:
        return "Jul"
    elif monthInt == 8:
        return "Aug"
    elif monthInt == 9:
        return "Sep"
    elif monthInt == 10:
        return "Oct"
    elif monthInt == 11:
        return "Nov"
    elif monthInt == 12:
        return "Dec"
    else:
        return ""


def getKlineInterval(interval):
    if interval.lower().strip() == "1m":
        return BinanceClient.KLINE_INTERVAL_1MINUTE
    elif interval.lower().strip() == "3m":
        return BinanceClient.KLINE_INTERVAL_3MINUTE
    elif interval.lower().strip() == "5m":
        return BinanceClient.KLINE_INTERVAL_5MINUTE
    elif interval.lower().strip() == "15m":
        return BinanceClient.KLINE_INTERVAL_15MINUTE
    elif interval.lower().strip() == "30m":
        return BinanceClient.KLINE_INTERVAL_30MINUTE
    elif interval.lower().strip() == "1h":
        return BinanceClient.KLINE_INTERVAL_1HOUR
    elif interval.lower().strip() == "2h":
        return BinanceClient.KLINE_INTERVAL_2HOUR
    elif interval.lower().strip() == "4h":
        return BinanceClient.KLINE_INTERVAL_4HOUR
    elif interval.lower().strip() == "6h":
        return BinanceClient.KLINE_INTERVAL_6HOUR
    elif interval.lower().strip() == "8h":
        return BinanceClient.KLINE_INTERVAL_8HOUR
    elif interval.lower().strip() == "12h":
        return BinanceClient.KLINE_INTERVAL_12HOUR
    elif interval.lower().strip() == "1d":
        return BinanceClient.KLINE_INTERVAL_1DAY
    elif interval.lower().strip() == "3d":
        return BinanceClient.KLINE_INTERVAL_3DAY
    elif interval.lower().strip() == "10d":
        return BinanceClient.KLINE_INTERVAL_1DAY
    elif interval.lower().strip() == "30d":
        return BinanceClient.KLINE_INTERVAL_3DAY
    elif interval.lower().strip() == "1w":
        return BinanceClient.KLINE_INTERVAL_1WEEK
    elif interval.lower().strip() == "1M":
        return BinanceClient.KLINE_INTERVAL_1MONTH
    else:
        return BinanceClient.KLINE_INTERVAL_5MINUTE


def getBinanceOrderType(type, stoploss):
    if type == OrderType.LIMIT.value and stoploss == None:
        return BinanceClient.ORDER_TYPE_LIMIT
    if type == OrderType.LIMIT.value and stoploss != None:
        return BinanceClient.ORDER_TYPE_STOP_LOSS_LIMIT
    elif type == OrderType.MARKET.value and stoploss == None:
        return BinanceClient.ORDER_TYPE_MARKET
    elif type == OrderType.MARKET.value and stoploss != None:
        return BinanceClient.ORDER_TYPE_MARKET
    return


def getBinancePositionType(side):
    if side == SideType.BUY.value:
        return BinanceClient.SIDE_BUY
    elif side == SideType.SELL.value:
        return BinanceClient.SIDE_SELL

    return


def convertKileToCandleStick(inputData) -> list[ExchangeDataModel.CandleStickType]:
    output = []
    for data in inputData:
        candleData = ExchangeDataModel.CandleStickType(
            int(data[0]),
            float(data[1]),
            float(data[2]),
            float(data[3]),
            float(data[4]),
            float(data[5]),
            int(data[6]),
            float(data[7]),
            int(data[8]),
            float(data[9]),
            float(data[10]),
            float(data[11]),
        )

        output.append(candleData)

    return output


def getPrecision(value):
    count = 0
    while value < 1.0:
        value = value * 10
        count = count + 1

    return count


def applyPriceFilter(price, filter):
    if price < float(filter["minPrice"]):
        price = float(filter["minPrice"])
    elif price > float(filter["maxPrice"]):
        price = float(filter["maxPrice"])

    if price % float(filter["tickSize"]) == 0:
        return price
    else:
        return price - price % float(filter["tickSize"])


def applyLotSizeFilter(quantity, filter):
    if quantity < float(filter["minQty"]):
        quantity = float(filter["minQty"])
    elif quantity > float(filter["maxQty"]):
        quantity = float(filter["maxQty"])

    if (quantity - float(filter["minQty"])) % float(filter["stepSize"]) == 0:
        return quantity
    else:
        return quantity - (quantity - float(filter["minQty"])) % float(filter["stepSize"])


def applyMinimumNotionalFilter(price, quantity, filter):
    if price*quantity < float(filter["minNotional"]):
        return False
    return True


def generateTestOrder(orderParameter: ExchangeDataModel.OrderParameterData, currentOrderId, currentTradeId):
    fills = ExchangeDataModel.OrderFillsData(
        orderParameter.price, orderParameter.quantity, orderParameter.quantity/1000, orderParameter.symbol, currentTradeId)
    return ExchangeDataModel.OrderData(
        orderParameter.symbol,
        currentOrderId,
        -1,
        "",
        int(time()*1000000),
        orderParameter.price,
        orderParameter.quantity,
        "FILLED",
        orderParameter.orderType,
        orderParameter.sideType,
        [fills]
    )
