from os import access
import models.Controller


class AuthenticationService:
    def __init__(self, accessToken) -> None:
        self.accessToken = accessToken
        return

    def authenticate(self, request: models.Controller.ControllerRequest) -> bool:
        if request.text == self.accessToken:
            request.setReply("Authenticated\n"
                             "Use /help for all command list")
            return True
        else:
            request.setReply("Authentication Failed")
            return False
