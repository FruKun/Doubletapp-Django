from ninja_extra import NinjaExtraAPI

from app.internal.presentation.rest.accounts import Accounts
from app.internal.presentation.rest.cards import Cards
from app.internal.presentation.rest.tokens import Tokens
from app.internal.presentation.rest.users import Users

api = NinjaExtraAPI()

api.register_controllers(Tokens)
api.register_controllers(Accounts)
api.register_controllers(Users)
api.register_controllers(Cards)
