import decimal
import logging

from botocore.exceptions import ClientError
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
from app.internal.domain.services.s3_service import S3Service
from app.internal.domain.services.user_service import UserService


class BotHandlers:
    def __init__(self):
        self.user_service = UserService()
        self.account_service = AccountService()
        self.card_service = CardService()
        self.transaction_service = TransactionService()
        self.s3_service = S3Service()
        self.logger = logging.getLogger("root")

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
            photo_name = None
            if not user.phone_number:
                raise CustomErrors.PhoneError
            if update.message.photo and update.message.caption:
                caption = update.message.caption.split(" ")
                photo_name = await self.s3_service.upload_image(
                    await (await update.message.photo[-1].get_file()).download_as_bytearray()
                )
                self.logger.debug(f"sending money with photo user: {user.id} photo_name: {photo_name} args: {caption}")
                await self.account_service.send_money(caption[1], caption[2], caption[3], user, photo_name)
                response = "Photo saved, transaction complete"
            else:
                self.logger.debug(f"sending money user: {user.id} args: {context.args}")
                await self.account_service.send_money(
                    context.args[0], context.args[1], context.args[2], user, photo_name
                )
                response = "Done"
        except IntegrityError:
            response = render_to_string("command_send_money.html", context={"error": "integrity"})
            self.logger.warning(
                f"IntegrityError user: {user.id}, caption:{update.message.caption}, args:{context.args}", exc_info=True
            )
        except CustomErrors.InvalidFieldValue:
            response = render_to_string("command_send_money.html", context={"error": "object"})
            self.logger.warning(
                f"InvalidFieldValue user: {user.id}, caption:{update.message.caption}, args:{context.args}",
                exc_info=True,
            )
        except CustomErrors.Sender:
            response = render_to_string("command_send_money.html", context={"error": "sender"})
            self.logger.warning(
                f"Sender user: {user.id}, caption:{update.message.caption}, args:{context.args}", exc_info=True
            )
        except (decimal.InvalidOperation, CustomErrors.AmountMoney):
            response = render_to_string("command_send_money.html", context={"error": "decimal"})
            self.logger.warning(
                f"InvalidOperation user: {user.id}, caption:{update.message.caption}, args:{context.args}",
                exc_info=True,
            )
        except IndexError:
            response = render_to_string("command_send_money.html", context={"error": "object"})
            self.logger.warning(
                f"IndexError user: {user.id}, caption:{update.message.caption}, args:{context.args}", exc_info=True
            )
        except BankAccount.DoesNotExist:
            response = render_to_string("command_send_money.html", context={"error": "account"})
            self.logger.warning(
                f"BankAccount.DoesNotExist user: {user.id}, caption:{update.message.caption}, args:{context.args}",
                exc_info=True,
            )
        except ClientError:
            response = "cant save photo, try again or without him"
            self.logger.warning(f"ClientError user: {user.id}, {photo_name}, {caption}", exc_info=True)
        except TelegramUser.DoesNotExist:
            response = render_to_string("register_error.html")
            self.logger.warning(f"TelegramUser.DoesNotExist {update.message}, args:{context.args}", exc_info=True)
        except CustomErrors.PhoneError:
            response = render_to_string("phone_error.html")
            self.logger.warning(f"PhoneError user: {user.id}", exc_info=True)
        except Exception as e:
            response = "unknown error"
            self.logger.error(f"error: {e.args}\n update: {update}, context.args: {context.args}", exc_info=True)
        await update.message.reply_text(response)

    async def command_account_history_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """/account_history {account_number}"""
        try:
            user = await self.user_service.aget_user_by_id(update.message.from_user.id)
            if not user.phone_number:
                raise CustomErrors.PhoneError
            history_list = await self.transaction_service.account_history(user, context.args[0])
            for history in history_list:
                if history.photo_name:
                    photo_url = await self.s3_service.create_presigned_url(history.photo_name, 3600)
                    await update.message.reply_text(
                        render_to_string(
                            "account_history.html",
                            context={"history": history, "self": context.args[0], "photo_url": photo_url},
                        ),
                    )
                else:
                    await update.message.reply_text(
                        render_to_string(
                            "account_history.html",
                            context={"history": history, "self": context.args[0], "photo_url": "None"},
                        )
                    )
            response = "Done"
        except CustomErrors.PhoneError:
            response = render_to_string("phone_error.html")
        except TelegramUser.DoesNotExist:
            response = render_to_string("register_error.html")
        except IndexError:
            response = "/account_history {u account number}"
        except BankAccount.DoesNotExist:
            response = "account does not exist"
        except ClientError:
            response = "cant get url photo, try again later"
        except CustomErrors.Sender:
            response = "its not u account"
        except CustomErrors.InvalidFieldValue:
            response = "its not a account"
        await update.message.reply_text(response)

    async def command_unseen_receipt_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """/unviewed_history {account_number}"""
        try:
            user = await self.user_service.aget_user_by_id(update.message.from_user.id)
            if not user.phone_number:
                raise CustomErrors.PhoneError
            history_list = await self.transaction_service.unseen_receipts(user)
            for history in history_list:
                await self.transaction_service.amark_is_viewed(history)
                if history.photo_name:
                    await update.message.reply_photo(
                        photo=await self.s3_service.create_presigned_url(history.photo_name, 3600),
                        caption=render_to_string("unseen_receipt.html", context={"history": history}),
                    )
                else:
                    await update.message.reply_text(
                        render_to_string("unseen_receipt.html", context={"history": history})
                    )
            response = "Done"
        except CustomErrors.PhoneError:
            response = render_to_string("phone_error.html")
        except TelegramUser.DoesNotExist:
            response = render_to_string("register_error.html")
        except IndexError:
            response = "/account_history {u account number}"
        except ClientError:
            response = "cant get url photo, try again later"
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
