import models.Controller as ControllerModel
import service.dialogue.BotDialogueUtils as BotDialogueUtils
import service.dialogue.BotOutputDialogue as BotOutputDialogue
import service.dialogue.BotInputDialogue as BotInputDialogue


class BotDialogue:
    def __init__(self) -> None:
        return

    def processInputDialogue(self, input: str):
        intent = input.split(" ")[0]
        if intent.lower().strip() == ControllerModel.ControllerIntent.START_BOT.value:
            return ControllerModel.ControllerIntent.START_BOT.value, None, ""
        elif intent.lower().strip() == ControllerModel.ControllerIntent.STATUS.value:
            return ControllerModel.ControllerIntent.STATUS.value, None, ""
        elif intent.lower().strip() == ControllerModel.ControllerIntent.STOP_BOT.value:
            query, err = BotInputDialogue.validateStopBotParamaterText(input)
            return ControllerModel.ControllerIntent.STOP_BOT.value, query, err
        elif intent.lower().strip() == ControllerModel.ControllerIntent.START_ENTRY.value:
            return ControllerModel.ControllerIntent.START_ENTRY.value, None, ""
        elif intent.lower().strip() == ControllerModel.ControllerIntent.STOP_ENTRY.value:
            return ControllerModel.ControllerIntent.STOP_ENTRY.value, None, ""
        elif intent.lower().strip() == ControllerModel.ControllerIntent.ACTIVE_TRADES.value:
            return ControllerModel.ControllerIntent.ACTIVE_TRADES.value, None, ""
        elif intent.lower().strip() == ControllerModel.ControllerIntent.ACCOUNT_STATEMENT.value:
            return ControllerModel.ControllerIntent.ACCOUNT_STATEMENT.value, None, ""
        elif intent.lower().strip() == ControllerModel.ControllerIntent.FORCE_EXIT.value:
            query, err = BotInputDialogue.validateForceExitQueryParamaterText(
                input)
            return ControllerModel.ControllerIntent.FORCE_EXIT.value, query, err

        # Update Config Bot Dialogue
        elif intent.lower().strip() == ControllerModel.ControllerIntent.UPDATE_CONFIG_MAX_ACTIVE_TRADES.value:
            query, err = BotInputDialogue.validateMaxActiveTradeQueryParamaterText(
                input)
            return ControllerModel.ControllerIntent.UPDATE_CONFIG_MAX_ACTIVE_TRADES.value, query, err
        elif intent.lower().strip() == ControllerModel.ControllerIntent.UPDATE_CONFIG_PERCENT_DEPLOYED_CAPITAL.value:
            query, err = BotInputDialogue.validatePercentDeployedCapitalQueryParamaterText(
                input)
            return ControllerModel.ControllerIntent.UPDATE_CONFIG_PERCENT_DEPLOYED_CAPITAL.value, query, err
        elif intent.lower().strip() == ControllerModel.ControllerIntent.UPDATE_CONFIG_STRATEGY.value:
            query, err = BotInputDialogue.validateStrategyQueryParamaterText(
                input)
            return ControllerModel.ControllerIntent.UPDATE_CONFIG_STRATEGY.value, query, err
        elif intent.lower().strip() == ControllerModel.ControllerIntent.UPDATE_WHITELIST_ADD_COIN.value:
            query, err = BotInputDialogue.validateWhitelistQueryParamaterText(
                input)
            return ControllerModel.ControllerIntent.UPDATE_WHITELIST_ADD_COIN .value, query, err
        elif intent.lower().strip() == ControllerModel.ControllerIntent.UPDATE_WHITELIST_REMOVE_COIN.value:
            query, err = BotInputDialogue.validateWhitelistQueryParamaterText(
                input)
            return ControllerModel.ControllerIntent.UPDATE_WHITELIST_REMOVE_COIN.value, query, err
        elif intent.lower().strip() == ControllerModel.ControllerIntent.UPDATE_BLACKLIST_ADD_COIN.value:
            query, err = BotInputDialogue.validateBlacklistQueryParamaterText(
                input)
            return ControllerModel.ControllerIntent.UPDATE_BLACKLIST_ADD_COIN.value, query, err
        elif intent.lower().strip() == ControllerModel.ControllerIntent.UPDATE_BLACKLIST_REMOVE_COIN.value:
            query, err = BotInputDialogue.validateBlacklistQueryParamaterText(
                input)
            return ControllerModel.ControllerIntent.UPDATE_BLACKLIST_REMOVE_COIN.value, query, err

        # BackTesting Bot Dialogue
        elif intent.lower().strip() == ControllerModel.ControllerIntent.BACKTEST.value:
            query, err = BotInputDialogue.validateBackTestQueryParamaterText(
                input)
            return ControllerModel.ControllerIntent.BACKTEST.value, query, err

        return None, None, BotInputDialogue.invalidQueryParamaterText()

    def processOutputDialogue(self, intent: ControllerModel.ControllerIntent, data):
        if intent == ControllerModel.ControllerIntent.START_BOT.value:
            # Get current bot configuration, account statement
            return "Bot Started"
        elif intent == ControllerModel.ControllerIntent.STATUS.value:
            # Get Trading Bot Status
            return BotOutputDialogue.generateBotStatusOutputDialogue(data)
        elif intent == ControllerModel.ControllerIntent.STOP_BOT.value:
            return "Bot Stopped with command - " + data
        elif intent == ControllerModel.ControllerIntent.START_ENTRY.value:
            return "Bot will now enter new trades"
        elif intent == ControllerModel.ControllerIntent.STOP_ENTRY.value:
            return "Bot won't enter new trades"
        elif intent == ControllerModel.ControllerIntent.ACTIVE_TRADES.value:
            # Get Report for all active trades with id
            return BotOutputDialogue.generateActiveTradeOutputDialogue(data)
        elif intent == ControllerModel.ControllerIntent.ACCOUNT_STATEMENT.value:
            # Get current account statement
            return BotOutputDialogue.generateAccountStatementOutputDialogue(data)
        elif intent == ControllerModel.ControllerIntent.FORCE_EXIT.value:
            return "Trade Exit in symbol - " + data

        # Update Config Bot Dialogue
        elif intent == ControllerModel.ControllerIntent.UPDATE_CONFIG_MAX_ACTIVE_TRADES.value:
            return "Max Active Trades Updated to - " + data
        elif intent == ControllerModel.ControllerIntent.UPDATE_CONFIG_PERCENT_DEPLOYED_CAPITAL.value:
            return "Percent Deployed Capital Updated to - " + data
        elif intent == ControllerModel.ControllerIntent.UPDATE_CONFIG_STRATEGY.value:
            return "Strategy Updated to - " + data
        elif intent == ControllerModel.ControllerIntent.UPDATE_WHITELIST_ADD_COIN.value:
            return data + " added to whitelist"
        elif intent == ControllerModel.ControllerIntent.UPDATE_WHITELIST_REMOVE_COIN.value:
            return data + " removed to whitelist"
        elif intent == ControllerModel.ControllerIntent.UPDATE_BLACKLIST_ADD_COIN.value:
            return data + " added to blacklist"
        elif intent == ControllerModel.ControllerIntent.UPDATE_BLACKLIST_REMOVE_COIN.value:
            return data + " removed to blacklist"

        # BackTest Bot Dialogue
        elif intent == ControllerModel.ControllerIntent.BACKTEST.value:
            return BotOutputDialogue.generateBackTestingOutputDialogue(data["context"], data["query"])

        return data
