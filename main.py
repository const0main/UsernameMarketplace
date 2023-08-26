from aiogram import *
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from config import *
from users_handler import *
from order_handler import *
from buy_handler import *
from time import sleep
from requests import get, post
from json import loads
from crypto import transfer

bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    info = State()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if getUser(message.from_user.id) is None:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton(text='Отправить контакт', request_contact=True))
        await bot.send_message(message.from_user.id, f"📤 Отправьте боту ваш контакт для верификации.", reply_markup=keyboard)
    else:
        buttons = InlineKeyboardMarkup()
        buttons.add(InlineKeyboardButton("💸 Маркет", callback_data='market'))

        await bot.send_message(message.from_user.id, "🉐 Добрый день.\nВ нашем боте вы сможете как продать так и купить @username в Telegram.\n" + 
                            "Наша площадка уникальна тем, что сдесь не получится обмануть и есть система гарантии.", reply_markup=buttons)

hash = ""
order_by = None
@dp.callback_query_handler(lambda call: types.CallbackQuery)
async def query(call: types.CallbackQuery, state: FSMContext):
    user = getUser(call.from_user.id)
    global hash, order_by
    if call.data == 'start':
        buttons = InlineKeyboardMarkup()
        buttons.add(InlineKeyboardButton("💸 Маркет", callback_data='market'))

        await call.bot.edit_message_text(
            text="🉐 Добрый день.\nВ нашем боте вы сможете как продать так и купить @username в Telegram.\n" + 
                            "Наша площадка уникальна тем, что сдесь не получится обмануть и есть система гарантии.",
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=buttons
        )
    elif call.data == 'market':
        buttons = InlineKeyboardMarkup()
        buttons.add(InlineKeyboardButton("👛 Купить", callback_data='buy'))
        buttons.add(InlineKeyboardButton("🪙 Продать", callback_data='sell'))
        buttons.add(InlineKeyboardButton("🔙 Назад", callback_data='start'))

        await call.bot.edit_message_text(
            text="💠 В маркете вы можете: продать, купить юзернеймы людей.",
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=buttons
        )
    elif call.data == 'sell':
        await Form.info.set()
        await call.bot.edit_message_text(
            text="💠 Напиши боту сообщение по следующему примеру информацию о вашем @username для создания обьявления.\n" + 
            "`Тут ваш @username\nТут ваша цена в рублях`",
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            parse_mode='markdown'
        )
    elif call.data == 'buy':
        buttons = InlineKeyboardMarkup()
        for currentOrder in getAllOrders():
            buttons.add(InlineKeyboardButton(f"{currentOrder[1]} {currentOrder[2]}₽ {currentOrder[3]}", callback_data=f'{currentOrder[4]}'))
        buttons.add(InlineKeyboardButton("🔙 Назад", callback_data='market'))
        await call.bot.edit_message_text(
            text="💠 Выберите юзернейм для покупки.",
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=buttons
        )
    elif call.data == 'check_payment':
        get_invoices_url = 'https://testnet-pay.crypt.bot/api/getInvoices'
        headers = {'Crypto-Pay-API-Token': Crypto_API_TESTNET}
        response = get(get_invoices_url, headers=headers)
        jsonResult = loads(response.text)
        status = "Не оплачен"
        for currentDict in jsonResult['result']['items']:
            if currentDict['hash'] == hash:
                if currentDict['status'] == 'paid':
                    status = currentDict['status']
                    break
        if status == 'paid':
            buttons = InlineKeyboardMarkup().add(InlineKeyboardButton("Подтвердить отвязку", callback_data='complete'))
            await call.bot.edit_message_text(
                text=f'💠 Счет был успешно оплачен. Сейчас продавец отвяжет его и вы сможете его поставить себе.',
                chat_id=call.from_user.id,
                message_id=call.message.message_id
            )
            await bot.send_message(getOrder(order_by)['id'], f"💠 Ваш юзернейм {getOrder(order_by)['username']} приобрели, отвяжите его от канала или юзера и нажмите подтвердить после отвязки.", reply_markup=buttons)
            
        else:
            await bot.send_message(call.from_user.id, "⛔️ Платеж не был произведён.")
        await call.answer()
    elif call.data == 'complete':
        await bot.send_message(getOrder(order_by)['id'], "⏳ Ожидаем пока покупатель подтвердит получние, это может занять от нескольких минут до того момента как продавец зайдет в сеть.")
        await call.answer()
        buttons = InlineKeyboardMarkup().add(InlineKeyboardButton("Подтвердить получение", callback_data='complete_o'))
        await bot.send_message(getPurchase(call.from_user.id)[2], "🌟 Продавец отвязал никнейм от своего канала/юзера.\nВы можете ставить его себе а после подтверждать получение.", reply_markup=buttons)
    elif call.data == 'complete_o':
        await bot.send_message(getPurchase(getOrder(order_by)['id'])[2], "🎊 Теперь юзернейм полностью ваш !")
        await call.answer()
        await bot.send_message(getOrder(order_by)['id'], "🔥 Покупатель подтвердил получение. Сейчас вы получить деньги с учетом комиссии...")
        transfer(float(getOrder(order_by)['price']) / 90, getOrder(order_by)['id']) # коммисию сделать
        # stop ship
        removeOrder(order_by)
        removePurchase(call.from_user.id)
    else:
        order_by = call.data
        order = getOrder(call.data)
        sell_id = order['id']
        price = order['price']
        username = order['username']
        buy_id = call.from_user.id
        createBuyOrder(sell_id, buy_id, username, price)
        print(f"Алл покупки: {getAllPurchases()}")
        price = float(order['price']) / 90
        headers = {'Crypto-Pay-API-Token': Crypto_API_TESTNET}
        data = {
            'asset': "USDT",
            'amount': float(price),
            'description': f"Покупка юзернейма",
            'expires_in': 600
        }
        response = post("https://testnet-pay.crypt.bot/api/createInvoice", headers=headers, data=data)
        json_converted = loads(response.text)

        hash = json_converted['result']['hash']

        buttons = InlineKeyboardMarkup()
        buttons.add(InlineKeyboardButton("Перейти к оплате", url=json_converted['result']['pay_url']))
        buttons.add(InlineKeyboardButton("Проверить оплату", callback_data='check_payment'))
        buttons.add(InlineKeyboardButton("🔙 Назад", callback_data='buy'))
        await call.answer()
        await call.bot.edit_message_text(
                text=f"💠 Вы хотите купить юзернейм *{order['username']}* за *{order['price']}₽*\nДля покупки нажмите кнопку *оплатить*.",
                chat_id=call.from_user.id,
                message_id=call.message.message_id,
                reply_markup=buttons,
                parse_mode='markdown'
            )

@dp.message_handler(state=Form.info)
async def processInfo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['info'] = message.text
    array = data['info'].split('\n')
    if len(array) < 2 and array[2] < 150:
        await bot.send_message(message.from_user.id, "💠 Произошла ошибка. Вы используете неправильный формат. Повторите попытку снова.")
    else:
        await bot.send_message(message.from_user.id, "⌛️")
        sleep(3.5)
        addOrder(message.from_user.id, array[0], array[1])
        buttons = InlineKeyboardMarkup().add(InlineKeyboardButton('💠 В меню', callback_data='start'))
        await bot.send_message(message.from_user.id, f"💠 Ваше объявление о продаже юзернейма {array[0]} успешно созданно.", parse_mode='markdown', reply_markup=buttons)
    await state.finish()

@dp.message_handler(content_types=types.ContentType.CONTACT)
async def processContact(message: types.Message):
    phone_number = message.contact.phone_number
    buttons = InlineKeyboardMarkup().add(InlineKeyboardButton("💠 В меню", callback_data="start"))
    await bot.send_message(message.from_user.id, "🔐 Ваш аккаунт успешно верифицирован.", reply_markup=buttons)
    addUser(message.from_user.id, phone_number)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)