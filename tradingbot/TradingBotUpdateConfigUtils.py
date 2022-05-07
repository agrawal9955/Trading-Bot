from datetime import datetime
import models.Context as ContextModels
import models.Controller as ControllerModel
from models.ControllerQuery import QueryKeys
from time import time

from service.context.InMemContextService import ContextService


def processIntentUpdateMaxOpenTrade(context: ContextModels.ContextType, query: ControllerModel.ControllerQuery, contextService: ContextService):
    if query.params[QueryKeys.MAX_OPEN_TRADE.value] < len(context.activeTrades):
        return context, "", "ERROR: Cannot set Max Open Trades:\nMax open trades should not be less then current active trades"

    status, err = contextService.updateMaxActiveTradesConfig(
        context, query.params[QueryKeys.MAX_OPEN_TRADE.value])
    if not status:
        return context, "", "ERROR: Some Error in Saving config to DB:\n" + err
    controllerActivity = ControllerModel.ControllerActivity(
        int(time()*1000000),
        ControllerModel.ControllerIntent.UPDATE_CONFIG_MAX_ACTIVE_TRADES.value
    )
    status, err = contextService.addControllerActivity(
        context, controllerActivity)
    return context, str(query.params[QueryKeys.MAX_OPEN_TRADE.value]), err


def processIntentUpdatePercentDeployedCapital(context: ContextModels.ContextType, query: ControllerModel.ControllerQuery, contextService: ContextService):
    status, err = contextService.updatePercentCapitalDeployedConfig(
        context, query.params[QueryKeys.PERCENT_CAPITAL_DEPLOYED.value])
    if not status:
        return context, "", "ERROR: Some Error in Saving config to DB:\n" + err
    controllerActivity = ControllerModel.ControllerActivity(
        int(time()*1000000),
        ControllerModel.ControllerIntent.UPDATE_CONFIG_PERCENT_DEPLOYED_CAPITAL.value
    )
    status, err = contextService.addControllerActivity(
        context, controllerActivity)
    return context, str(query.params[QueryKeys.PERCENT_CAPITAL_DEPLOYED.value]), err


def processIntentUpdateStrategy(context: ContextModels.ContextType, query: ControllerModel.ControllerQuery, contextService: ContextService):
    controllerActivity = ControllerModel.ControllerActivity(
        int(time()*1000000),
        ControllerModel.ControllerIntent.UPDATE_CONFIG_STRATEGY.value
    )
    status, err = contextService.addControllerActivity(
        context, controllerActivity)
    return context, "", err


def processIntentUpdateWhitelistAddCoin(context: ContextModels.ContextType, query: ControllerModel.ControllerQuery, contextService: ContextService):
    status, err = contextService.updateWhitelistConfigAddCoin(
        context, query.params[QueryKeys.SYMBOL.value])
    if not status:
        return context, "", "ERROR: Some Error in Saving config to DB:\n" + err
    controllerActivity = ControllerModel.ControllerActivity(
        int(time()*1000000),
        ControllerModel.ControllerIntent.UPDATE_WHITELIST_ADD_COIN.value
    )
    status, err = contextService.addControllerActivity(
        context, controllerActivity)
    return context, str(query.params[QueryKeys.SYMBOL.value]), err


def processIntentUpdateWhitelistRemoveCoin(context: ContextModels.ContextType, query: ControllerModel.ControllerQuery, contextService: ContextService):
    status, err = contextService.updateWhitelistConfigRemoveCoin(
        context, query.params[QueryKeys.SYMBOL.value])
    if not status:
        return context, "", "ERROR: Some Error in Saving config to DB:\n" + err
    controllerActivity = ControllerModel.ControllerActivity(
        int(time()*1000000),
        ControllerModel.ControllerIntent.UPDATE_WHITELIST_REMOVE_COIN.value
    )
    status, err = contextService.addControllerActivity(
        context, controllerActivity)
    return context, str(query.params[QueryKeys.SYMBOL.value]), err


def processIntentUpdateBlacklistAddCoin(context: ContextModels.ContextType, query: ControllerModel.ControllerQuery, contextService: ContextService):
    status, err = contextService.updateBlacklistConfigAddCoin(
        context, query.params[QueryKeys.SYMBOL.value])
    if not status:
        return context, "", "ERROR: Some Error in Saving config to DB:\n" + err
    controllerActivity = ControllerModel.ControllerActivity(
        int(time()*1000000),
        ControllerModel.ControllerIntent.UPDATE_BLACKLIST_ADD_COIN.value
    )
    status, err = contextService.addControllerActivity(
        context, controllerActivity)
    return context, str(query.params[QueryKeys.SYMBOL.value]), err


def processIntentUpdateBlacklistRemoveCoin(context: ContextModels.ContextType, query: ControllerModel.ControllerQuery, contextService: ContextService):
    status, err = contextService.updateBlacklistConfigRemoveCoin(
        context, query.params[QueryKeys.SYMBOL.value])
    if not status:
        return context, "", "ERROR: Some Error in Saving config to DB:\n" + err
    controllerActivity = ControllerModel.ControllerActivity(
        int(time()*1000000),
        ControllerModel.ControllerIntent.UPDATE_BLACKLIST_REMOVE_COIN.value
    )
    status, err = contextService.addControllerActivity(
        context, controllerActivity)
    return context, str(query.params[QueryKeys.SYMBOL.value]), err
