import asyncio
import json
import os
import random
import re
import string
import time as _time
import uuid

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    FSInputFile,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    MessageEntity,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils import formatting as fmt
from aiogram.fsm.storage.base import StorageKey
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
import logging

import locales
from database import db

# Короткий алиас для премиум-эмодзи в текстах сообщений
e = locales.e

logging.basicConfig(level=logging.INFO)

CONFIG_FILE = "config.json"
ADMINS_FILE = "admins.json"
PANEL_ADMINS_FILE = "panel_admins.json"
SETTINGS_FILE = "settingsadm.json"
users_data_file = "users_data.json"
deals_file = "deals.json"

# ─── Настройки ─────────────────────────────────────────────────────────────────
NOTIFICATION_CHANNEL_ID = -1003707650124
MANAGER_TON_WALLET  = "UQBqWH8izPM-mpf8deVo-cFSU1iUUOWukgsrPv3geSCQIUw"
MANAGER_CARD        = "2204120122508217"
MANAGER_USDT_WALLET = "TManagerUSDTWalletAddressHere"
MANAGER_BTC_WALLET  = "bc1qManagerBTCAddressHere"
MIN_DEALS_FOR_WITHDRAW = 3

# ─── ID кастомных эмодзи для кнопок ───────────────────────────────────────────
# Используются в icon_custom_emoji_id для InlineKeyboardButton
_BEID = {
    "cross":        "5210952531676504517",
    "check":        "5902002809573740949",
    "bridge":       "5240428351063081133",
    "usdt":         "5814556334829343625",
    "btc":          "5816788957614053645",
    "money_bag":    "5375296873982604963",
    "person":       "6032693626394382504",
    "person2":      "5884366771913233289",
    "down":         "5406745015365943482",
    "star":         "4983746717313664194",
    "diamond":      "5427168083074628963",
    "people":       "6032609071373226027",
    "writing":      "5197269100878907942",
    "back":         "5924683191834121281",
    "cart":         "5312361253610475399",
    "handshake":    "5395732581780040886",
    "edit":         "5395444784611480792",
    "card":         "5445353829304387411",
    "package":      "5778672437122045013",
    "chat":         "5443038326535759644",
    "chart":        "5190806721286657692",
    "megaphone":    "5424818078833715060",
    "flag_ru":      "5449408995691341691",
    "flag_ua":      "5447309366568953338",
    "flag_kz":      "5228718354658769982",
    "flag_by":      "5382219601054544127",
    "link":         "5902449142575141204",
    "timer":        "5386367538735104399",
    "hammer":       "5836997023554870252",
    "crown":        "5217822164362739968",
    "bell":         "5458603043203327669",
    "no":           "5260293700088511294",
    "coin":         "5224257782013769471",
    "tag":          "5888620056551625531",
    "mail":         "5253742260054409879",
    "mailbox":      "5350421256627838238",
    "question":     "5436113877181941026",
    "tv":           "6039391078136681499",
    "pin":          "5397782960512444700",
    "finish":       "5411520005386806155",
    "globe":        "5776233299424843260",
    "star2":        "5924870095925942277",
    "warning":      "5420323339723881652",
    "sparkle":      "5325547803936572038",
    "flag_us":      "5202021044105257611",
    "globe2":       "5447410659077661506",
    "gift":         "6037175527846975726",
    "confetti":     "5193018401810822951",
    "target":       "5310278924616356636",
    "bank":         "5332455502917949981",
    "broken_heart": "5316583309541651465",
    "heart_spark":  "5470080737711502911",
    "heart":        "5406926593698312391",
    "heart_gift":   "5192879906295397710",
    "briefcase":    "5445221832074483553",
    "writing2":     "5470060791883374114",
    "outbox":       "6043874504302661409",
    "inbox":        "6039420807900303010",
    "shield":       "5893365724830765382",
    "flying_money": "5375296873982604963",
    "gear":         "5902432207519093015",
    "lock":         "5296369303661067030",
    "sparkle2":     "5778647930038653243",
    "plane":        "5927118708873892465",
    "gem":          "5891105528356018797",
    # ── Расширенный набор ──────────────────────────────────────────────────────────
    "shield2":      "5902016123972358349",
    "phone":        "5895652322469482989",
    "phone2":       "5895266423952904371",
    "phone3":       "5893100690988863311",
    "check2":       "5895514131896733546",
    "check3":       "5895713431264170680",
    "check4":       "5893431652578758294",
    "cross2":       "5893163582194978381",
    "cross3":       "5893081007153746175",
    "briefcase2":   "5893255507380014983",
    "sleep":        "5774138454896022007",
    "money2":       "5893473283696759404",
    "search":       "5893382531037794941",
    "pin2":         "5895440460322706085",
    "idea":         "5893290369629556374",
    "coin2":        "6039802097916974085",
    "gear2":        "5893161718179173515",
    "stop":         "5904238507555033712",
    "person3":      "5902335789798265487",
    "next":         "5893368370530621889",
    "heart2":       "5893406892092297627",
    "heart3":       "5895213106228891182",
    "eyes":         "5210956306952758910",
    "lightning":    "5456140674028019486",
    "smile":        "5461117441612462242",
    "exclaim":      "5274099962655816924",
    "ban":          "5240241223632954241",
    "think":        "5467538555158943525",
    "trending":     "5244837092042750681",
    "snowflake":    "5449449325434266744",
    "gold":         "5440539497383087970",
    "silver":       "5447203607294265305",
    "bronze":       "5453902265922376865",
    "n0":           "5794375786743995258",
    "n1":           "5794164805065514131",
    "n2":           "5794085322400733645",
    "n3":           "5794280000383358988",
    "n4":           "5794241397217304511",
    "n5":           "5793985348446984682",
    "n6":           "5794324702402976226",
    "n7":           "5793942849745591465",
    "n8":           "5793926687783655907",
    "n9":           "5793979472931723221",
}


def mkbtn(text: str, emoji_key: str = None, **kwargs) -> InlineKeyboardButton:
    """Создать InlineKeyboardButton с кастомным эмодзи (icon_custom_emoji_id)."""
    eid = _BEID.get(emoji_key) if emoji_key else None
    if eid:
        return InlineKeyboardButton(text=text, icon_custom_emoji_id=eid, **kwargs)
    return InlineKeyboardButton(text=text, **kwargs)


# ─── Загрузка / сохранение ─────────────────────────────────────────────────────
def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_admins():
    if os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_admins(admins):
    with open(ADMINS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(admins), f)

def load_panel_admins() -> set:
    """Панельные админы (доступ к /admin). Хардкодные владельцы всегда включены."""
    if os.path.exists(PANEL_ADMINS_FILE):
        with open(PANEL_ADMINS_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_panel_admins(panel_admins: set):
    with open(PANEL_ADMINS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(panel_admins), f)

def load_users_data():
    if os.path.exists(users_data_file):
        with open(users_data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users_data(data):
    pass  # данные хранятся в db.users, сохранение — через db.upsert_user

def load_deals():
    return {}  # данные загружаются из SQLite в db.init()

def save_deals(d):
    pass  # данные хранятся в db.deals, сохранение — через db.schedule_save_deal

_DEFAULT_SETTINGS = {
    "service_name":          "Astral Safe",
    "manager_username":      "AstralTradeSupport",
    "manager_ton_wallet":    "UQBqWH8izPM-mpf8deVo-cFSU1iUUOWukgsrPv3geSCQIUw",
    "manager_card":          "2204120122508217",
    "manager_usdt_wallet":   "TManagerUSDTWalletAddressHere",
    "manager_btc_wallet":    "bc1qManagerBTCAddressHere",
    "notification_channel":  str(NOTIFICATION_CHANNEL_ID),
    "gift_recipient":        "AstralTradeSupport",
    "min_deals_withdraw":    3,
    "log_channel":           "",
    "log_topic_id":          "",
    "admins_list":           [],
}

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in _DEFAULT_SETTINGS.items():
            data.setdefault(k, v)
        return data
    s = dict(_DEFAULT_SETTINGS)
    save_settings(s)
    return s

def save_settings(s: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=4)


# ─── Баннеры ───────────────────────────────────────────────────────────────────
ALLOWED_BANNER_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".mp4"}

# Все слоты баннеров: ключ → (описание, список допустимых имён файлов по расширениям)
BANNER_SLOTS = {
    "menu_ru":    ("Главное меню (RU)",     ["menu_ru.png", "menu_ru.jpg", "menu_ru.gif", "menu_ru.mp4"]),
    "menu_en":    ("Главное меню (EN)",     ["menu_en.png", "menu_en.jpg", "menu_en.gif", "menu_en.mp4"]),
    "menu":       ("Главное меню (резерв)", ["menu.png",    "menu.jpg",    "menu.gif",    "menu.mp4"]),
    "deal_ru":    ("Экран сделки (RU)",     ["deal_ru.png",  "deal_ru.jpg",  "deal_ru.gif",  "deal_ru.mp4"]),
    "deal_en":    ("Экран сделки (EN)",     ["deal_en.png",  "deal_en.jpg",  "deal_en.gif",  "deal_en.mp4"]),
    "balance_ru":    ("Баланс (RU)",           ["balance_ru.png","balance_ru.jpg","balance_ru.gif","balance_ru.mp4"]),
    "balance_en":    ("Баланс (EN)",           ["balance_en.png","balance_en.jpg","balance_en.gif","balance_en.mp4"]),
    "rekvizity_ru":  ("Реквизиты (RU)",        ["rekvizity_ru.png","rekvizity_ru.jpg","rekvizity_ru.gif","rekvizity_ru.mp4"]),
    "rekvizity_en":  ("Реквизиты (EN)",        ["rekvizity_en.png","rekvizity_en.jpg","rekvizity_en.gif","rekvizity_en.mp4"]),
    "rekvizity":     ("Реквизиты (резерв)",    ["rekvizity.png","rekvizity.jpg","rekvizity.gif","rekvizity.mp4"]),
}

def get_banner_path(slot_key: str):
    """Вернуть путь к текущему файлу баннера для слота (или None)."""
    if slot_key not in BANNER_SLOTS:
        return None
    _, names = BANNER_SLOTS[slot_key]
    for name in names:
        path = os.path.join(os.getcwd(), name)
        if os.path.exists(path):
            return path
    return None

def get_banner_status(slot_key: str) -> str:
    path = get_banner_path(slot_key)
    if path:
        fname = os.path.basename(path)
        size_kb = os.path.getsize(path) // 1024
        return f"✅ {fname} ({size_kb} КБ)"
    return "❌ не установлен"

def save_banner_file(slot_key: str, file_bytes: bytes, ext: str) -> str:
    """Сохранить байты файла как баннер. Возвращает итоговый путь."""
    if slot_key not in BANNER_SLOTS:
        raise ValueError(f"Unknown slot: {slot_key}")
    _, names = BANNER_SLOTS[slot_key]
    # Выбираем имя с нужным расширением
    target_name = None
    for name in names:
        if name.endswith(ext):
            target_name = name
            break
    if target_name is None:
        target_name = os.path.splitext(names[0])[0] + ext
    # Удаляем старые файлы этого слота
    for name in names:
        old = os.path.join(os.getcwd(), name)
        if os.path.exists(old):
            os.remove(old)
    target_path = os.path.join(os.getcwd(), target_name)
    with open(target_path, "wb") as f:
        f.write(file_bytes)
    return target_path


config = load_config()
BOT_TOKEN = config["BOT_TOKEN"]
ADMIN_GROUP_ID = config.get("ADMIN_GROUP_ID")

if config.get("NOTIFICATION_CHANNEL_ID") is not None:
    NOTIFICATION_CHANNEL_ID = config["NOTIFICATION_CHANNEL_ID"]
if config.get("MANAGER_USDT_WALLET"):
    MANAGER_USDT_WALLET = config["MANAGER_USDT_WALLET"]
if config.get("MANAGER_BTC_WALLET"):
    MANAGER_BTC_WALLET = config["MANAGER_BTC_WALLET"]

admins = load_admins()
users_data: dict = {}  # алиас — будет привязан к db.users после db.init()
deals: dict = {}       # алиас — будет привязан к db.deals после db.init()
adm_settings = load_settings()
panel_admins = load_panel_admins()  # Панельные админы (доступ к /admin)

# Дедупликация update_id — защита от Telegram-ретрансмитов при плохом соединении
_seen_update_ids: set[int] = set()

# Применяем настройки из settingsadm.json
if adm_settings.get("manager_ton_wallet"):
    MANAGER_TON_WALLET = adm_settings["manager_ton_wallet"]
if adm_settings.get("manager_card"):
    MANAGER_CARD = adm_settings["manager_card"]
if adm_settings.get("manager_usdt_wallet"):
    MANAGER_USDT_WALLET = adm_settings["manager_usdt_wallet"]
if adm_settings.get("manager_btc_wallet"):
    MANAGER_BTC_WALLET = adm_settings["manager_btc_wallet"]
if adm_settings.get("notification_channel"):
    try:
        NOTIFICATION_CHANNEL_ID = int(adm_settings["notification_channel"])
    except ValueError:
        pass
if adm_settings.get("min_deals_withdraw") is not None:
    MIN_DEALS_FOR_WITHDRAW = int(adm_settings["min_deals_withdraw"])

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ─── Автоудаление команд пользователя ──────────────────────────────────────────
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

class DeleteCommandMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        msg = getattr(event, "message", None) or event if isinstance(event, types.Message) else None
        if msg and isinstance(msg, types.Message) and msg.text and msg.text.startswith("/"):
            try:
                await msg.delete()
            except Exception:
                pass
        return await handler(event, data)

dp.message.middleware(DeleteCommandMiddleware())


# ─── Дедупликация сообщений (защита от Telegram-ретрансмитов) ──────────────────
class DeduplicateMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        msg = event if isinstance(event, types.Message) else None
        if msg and msg.message_id:
            key = (msg.chat.id, msg.message_id)
            if key in _seen_update_ids:
                return  # дубль — игнорируем
            _seen_update_ids.add(key)
            if len(_seen_update_ids) > 10000:
                # чистим старые чтобы не росло бесконечно
                _seen_update_ids.clear()
        return await handler(event, data)

dp.message.middleware(DeduplicateMiddleware())


# ─── Локализация ───────────────────────────────────────────────────────────────
def get_text(key: str, user_id: int, **kwargs) -> str:
    lang = users_data.get(str(user_id), {}).get("lang", "ru")
    # Автоматически добавляем currency_emoji если передана currency
    if "currency" in kwargs and "currency_emoji" not in kwargs:
        kwargs["currency_emoji"] = _currency_emoji(str(kwargs["currency"]))
    # Автоматически подставляем настройки сервиса
    kwargs.setdefault("service_name", adm_settings.get("service_name", "Astral Safe"))
    kwargs.setdefault("manager_username", adm_settings.get("manager_username", "AstralTradeSupport"))
    return locales.get_html_text(key, lang, **kwargs)

def get_alert(key: str, user_id: int = None, lang: str = None, **kwargs) -> str:
    """Текст для show_alert — без tg-emoji тегов (Telegram их не рендерит во всплывашках)."""
    import re
    if lang is None:
        lang = users_data.get(str(user_id), {}).get("lang", "ru") if user_id else "ru"
    if "currency" in kwargs and "currency_emoji" not in kwargs:
        kwargs["currency_emoji"] = _currency_emoji(str(kwargs["currency"]))
    kwargs.setdefault("service_name", adm_settings.get("service_name", "Astral Safe"))
    kwargs.setdefault("manager_username", adm_settings.get("manager_username", "AstralTradeSupport"))
    text = locales.get_html_text(key, lang, **kwargs)
    # Убираем <tg-emoji ...>fallback</tg-emoji> — оставляем только fallback
    text = re.sub(r'<tg-emoji[^>]*>(.*?)</tg-emoji>', r'\1', text)
    return text


# ─── Состояния ─────────────────────────────────────────────────────────────────
class CreateDealStates(StatesGroup):
    choose_role           = State()
    choose_payment_method = State()
    choose_crypto         = State()
    choose_currency       = State()
    enter_amount          = State()
    enter_description     = State()

class DealStates(StatesGroup):
    connected_as_seller           = State()
    payment_confirmed_as_seller   = State()
    connected_as_buyer            = State()
    payment_confirmed_as_buyer    = State()
    item_delivered_to_manager     = State()
    buyer_confirmed_receipt       = State()
    completed                     = State()

class EditCredentialsState(StatesGroup):
    waiting_for_ton_wallet    = State()
    waiting_for_card_number   = State()
    waiting_for_stars_username = State()
    waiting_for_usdt_wallet   = State()
    waiting_for_btc_wallet    = State()

class AdsState(StatesGroup):
    waiting_for_ads_message = State()

class WithdrawState(StatesGroup):
    choose_currency = State()
    enter_amount    = State()
    confirm         = State()

class FeedbackState(StatesGroup):
    waiting_for_feedback = State()

class MyDealsState(StatesGroup):
    search = State()

class AdminStates(StatesGroup):
    # Рассылка
    waiting_for_broadcast_message = State()
    # Поиск пользователя
    waiting_for_user_search       = State()
    # Редактирование пользователя
    edit_user_balance_currency    = State()
    edit_user_balance_amount      = State()
    edit_user_deals_count         = State()
    # Сообщение конкретному пользователю
    send_message_to_user          = State()
    # Настройки
    settings_service_name         = State()
    settings_manager_username     = State()
    settings_ton_wallet           = State()
    settings_card                 = State()
    settings_usdt_wallet          = State()
    settings_btc_wallet           = State()
    settings_channel              = State()
    settings_gift_recipient       = State()
    settings_min_deals            = State()
    settings_log_channel          = State()
    settings_log_topic_id         = State()
    settings_add_admin            = State()
    settings_add_panel_admin      = State()
    deals_search                  = State()
    # Баннеры
    settings_upload_banner        = State()

class GoyStates(StatesGroup):
    choose_currency = State()
    enter_amount    = State()


# ─── Вспомогательные функции ───────────────────────────────────────────────────
def _currency_emoji(currency: str) -> str:
    """Возвращает tg-emoji HTML для указанной валюты."""
    from locales import _E as LE
    m = {
        "STARS": '<tg-emoji emoji-id="5924870095925942277">⭐️</tg-emoji>',
        "TON":   '<tg-emoji emoji-id="6039802097916974085">🪙</tg-emoji>',
        "BTC":   '<tg-emoji emoji-id="5816788957614053645">🪙</tg-emoji>',
        "USDT":  "<tg-emoji emoji-id=\"5814556334829343625\">🪙</tg-emoji>",
        "RUB":   LE["flag_ru"],
        "UAH":   LE["flag_ua"],
        "KZT":   LE["flag_kz"],
        "BYN":   LE["flag_by"],
    }
    return m.get(currency, LE.get("coin2", "🪙"))


def _status_emoji(status: str) -> str:
    m = {
        "waiting_for_buyer":          "⏳",
        "waiting_for_seller":         "⏳",
        "waiting_for_payment":        "💳",
        "payment_confirmed_by_admin": "✅",
        "item_delivered_to_manager":  "📦",
        "waiting_for_feedback":       "💬",
        "completed":                  "✅",
        "cancelled":                  "❌",
      
