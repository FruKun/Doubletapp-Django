import decimal

from django.conf import settings
from django.db.utils import IntegrityError
from django.template.loader import render_to_string
from phonenumbers import NumberParseException
from telegram import Update
from telegram.ext import ContextTypes

from app.internal.db.models.bank_data import BankAccount, BankCard
from app.internal.db.models.user_data import TelegramUser
from app.internal.domain.services import CustomErrors
from app.internal.domain.services.account_service import AccountService
from app.internal.domain.services.card_service import CardService
from app.internal.domain.services.history_service import TransactionService
from app.internal.domain.services.user_service import UserService


class BotHandlers:
    def __init__(self):
        self.user_service = UserService()
        self.account_service = AccountService()
        self.card_service = CardService()
        self.transaction_service = TransactionService()

    async def command_start_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """/start"""
        await self.user_service.asave_user(
            update.message.from_user.id, update.message.from_user.username, update.message.from_user.full_name
        )
        await update.message.reply_html(render_to_string("command_start.html"))

    async def command_help_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """/help"""
        await update.message.reply_html(render_to_string("command_help.html", context={}))

    async def command_set_phone_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """/set_phone"""
        await self.user_service.asave_user(
            update.message.from_user.id, update.message.from_user.full_name, update.message.from_user.username
        )
        try:
            await self.user_service.set_phone(
                update.message.from_user.id, context.args[0], update.message.from_user.language_code
            )
            response = "Done"
        except TelegramUser.DoesNotExist:
            response = render_to_string("register_error.html")
        except (NumberParseException, AttributeError, IndexError):
            response = "try again /set_phone +78005553535"
        await update.message.reply_text(response)

    async def message_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """message handler"""
        await update.message.reply_html(render_to_string("command_start.html"))

    async def command_me_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """/me"""
        try:
            user = await self.user_service.aget_user_by_id(update.message.from_user.id)
            if not user.phone_number:
                raise CustomErrors.PhoneError
            response = render_to_string(
                "command_me.html",
                context={"fullname": user.full_name, "username": user.username, "phone": user.phone_number},
            )
        except TelegramUser.DoesNotExist:
            response = render_to_string("register_error.html")
        except CustomErrors.PhoneError:
            response = render_to_string("phone_error.html")
        await update.message.reply_text(response)

    async def command_me_link_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """/give_me_link"""
        user_id = update.message.from_user.id
        try:
            user = await self.user_service.aget_user_by_id(update.message.from_user.id)
            if not user.phone_number:
                raise CustomErrors.PhoneError
            response = f"https://{settings.DOMAIN_URL}/api/get_user?user_id={user_id}"

        except TelegramUser.DoesNotExist:
            response = render_to_string("register_error.html")
        except CustomErrors.PhoneError:
            response = render_to_string("phone_error.html")
        await update.message.reply_text(response)

    async def command_accounts_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """/accounts"""
        try:
            user = await self.user_service.aget_user_by_id(update.message.from_user.id)
            if not user.phone_number:
                raise CustomErrors.PhoneError
            accounts = await self.account_service.aget_accounts_by_user(user)
            response = render_to_string("command_accounts.html", context={"list": accounts})
        except TelegramUser.DoesNotExist:
            response = render_to_string("register_error.html")
        except CustomErrors.PhoneError:
            response = render_to_string("phone_error.html")
        await update.message.reply_text(response)

    async def command_cards_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """/cards"""
        try:
            user = await self.user_service.aget_user_by_id(update.message.from_user.id)
            if not user.phone_number:
                raise CustomErrors.PhoneError
            account = await BankAccount.objects.prefetch_related("user").aget(number=context.args[0])
            if account.user == user:
                cards = await self.card_service.aget_cards_by_account_number(context.args[0])
                response = render_to_string("command_cards.html", context={"list": cards})
            else:
                raise CustomErrors.InvalidFieldValue
        except IndexError:
            response = "try again\nexample: /cards 12345"
        except TelegramUser.DoesNotExist:
            response = render_to_string("register_error.html")
        except BankAccount.DoesNotExist:
            response = "account does not exist"
        except CustomErrors.InvalidFieldValue:
            response = "its not u account"
        except CustomErrors.PhoneError:
            response = render_to_string("phone_error.html")
        await update.message.reply_text(response)

    async def command_favourites_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """/favourites"""
        try:
            user = await self.user_service.aget_user_by_id(update.message.from_user.id)
            favourites = user.list_of_favourites
            response = render_to_string(
                "command_favourites.html",
                context={"list": favourites},
            )
        except TelegramUser.DoesNotExist:
            response = render_to_string("register_error.html")
        await update.message.reply_text(response)

    async def command_add_favorite_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """/add_favorite"""
        try:
            user = await self.user_service.aget_user_by_id(update.message.from_user.id)
            await self.user_service.add_favorite(user, context.args[0])
            response = "done"
        except TelegramUser.DoesNotExist:
            response = render_to_string("favorite_error.html", context={"error": "user"})
        except BankAccount.DoesNotExist:
            response = render_to_string("favorite_error.html", context={"error": "account"})
        except BankCard.DoesNotExist:
            response = render_to_string("favorite_error.html", context={"error": "card"})
        except (CustomErrors.InvalidFieldValue, IndexError):
            response = render_to_string("favorite_error.html", context={"error": "base"})
        await update.message.reply_text(response)

    async def command_del_favorite_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """/del_favorite"""
        try:
            user = await self.user_service.aget_user_by_id(update.message.from_user.id)
            await self.user_service.del_favorite(user, context.args[0])
            response = "done"
        except TelegramUser.DoesNotExist:
            response = render_to_string("favorite_error.html", context={"error": "user"})
        except (CustomErrors.InvalidFieldValue, IndexError, ValueError):
            response = render_to_string("favorite_error.html", context={"error": "del"})
        await update.message.reply_text(response)

    async def command_send_money_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """/send_money {payment_sender} {payee} {amount}"""
        try:
            user = await self.user_service.aget_user_by_id(update.message.from_user.id)
            if not user.phone_number:
                raise CustomErrors.PhoneError
            await self.account_service.send_money(context.args[0], context.args[1], context.args[2], user)
            response = render_to_string("command_send_money.html", context={"error": ""})
        except IntegrityError:
            response = render_to_string("command_send_money.html", context={"error": "integrity"})
        except CustomErrors.InvalidFieldValue:
            response = render_to_string("command_send_money.html", context={"error": "object"})
        except CustomErrors.Sender:
            response = render_to_string("command_send_money.html", context={"error": "sender"})
        except (decimal.InvalidOperation, CustomErrors.AmountMoney):
            response = render_to_string("command_send_money.html", context={"error": "decimal"})
        except IndexError:
            response = render_to_string("command_send_money.html", context={"error": "object"})
        except BankAccount.DoesNotExist:
            response = render_to_string("command_send_money.html", context={"error": "account"})
        except TelegramUser.DoesNotExist:
            response = render_to_string("register_error.html")
        except CustomErrors.PhoneError:
            response = render_to_string("phone_error.html")
        await update.message.reply_text(response)

    async def command_account_history_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """/account_history {account_number}"""
        try:
            user = await self.user_service.aget_user_by_id(update.message.from_user.id)
            if not user.phone_number:
                raise CustomErrors.PhoneError
            history_list = await self.transaction_service.account_history(user, context.args[0])
            response = render_to_string(
                "account_history.html", context={"histories": history_list, "self": context.args[0]}
            )
        except CustomErrors.PhoneError:
            response = render_to_string("phone_error.html")
        except TelegramUser.DoesNotExist:
            response = render_to_string("register_error.html")
        except IndexError:
            response = "/account_history {u account number}"
        except BankAccount.DoesNotExist:
            response = "account does not exist"
        except CustomErrors.Sender:
            response = "its not u account"
        except CustomErrors.InvalidFieldValue:
            response = "its not a account"
        await update.message.reply_text(response)

    async def command_all_users_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """/all_users"""
        try:
            user = await self.user_service.aget_user_by_id(update.message.from_user.id)
            if not user.phone_number:
                raise CustomErrors.PhoneError
            user_list = await self.transaction_service.all_usernames(user)
            response = render_to_string("command_all_users.html", context={"list": user_list})
        except CustomErrors.PhoneError:
            response = render_to_string("phone_error.html")
        except TelegramUser.DoesNotExist:
            response = render_to_string("register_error.html")
        except (IndexError, KeyError):
            response = render_to_string("command_all_users.html")
        except CustomErrors.Sender:
            response = "its not u account"
        except CustomErrors.InvalidFieldValue:
            response = "its not a account"
        await update.message.reply_text(response)
