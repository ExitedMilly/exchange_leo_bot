from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types.input_file import FSInputFile
from aiogram.filters import Command
from datetime import datetime, timedelta
import math

from states import ExchangeState
from keyboards import main_kb, confirm_kb
from config import Config

last_request_time = {}
router = Router()


@router.message(Command('start', 'menu'))
async def start_cmd(message: Message):
    photo = FSInputFile("data/images/welcome.jpg")

    await message.answer_photo(
        photo=photo,
        caption='Привет! Я бот-обменник, помогающий быстро и выгодно обменять рубли на юани | by lèo\n\n'
                '💰 Минимальная сумма обмена: от 1000¥\n'
                '⏱️ Время работы: 24/7\n\n'
                '<a href="https://t.me/depositchinabyleo">Наши отзывы</a>',
        reply_markup=main_kb(),
        parse_mode='HTML'
    )


@router.message(F.text == 'Связь с менеджером')
async def contact_manager(message: Message):
    await message.answer(
        text='Ссылка для связи с менеджером:\nt.me/managerbyleo',
        disable_web_page_preview=True  # Отключаем превью ссылки
    )


@router.message(F.text.lower() == 'актуальный курс')
async def current_rate(message: Message):
    await message.answer(f'Текущий курс: \n {Config.CURRENT_RATE} ₽ за 1 ¥')


@router.message(F.text.lower() == 'часто задаваемые вопросы')
async def faq(message: Message):
    faq_text = (
        "<b>Часто задаваемые вопросы (FAQ)</b>\n\n"

        "<b>1. Какой у вас курс обмена рублей на юани?</b>\n"
        "Актуальный курс обмена доступен по кнопке Актуальный курс. "
        "Он может меняться в зависимости от рыночной ситуации.\n\n"

        "<b>2. Какая минимальная/максимальная сумма обмена?</b>\n"
        "Минимальная сумма обмена составляет 1000¥. Максимальная сумма обмена не ограничена. "
        "Более подробную информацию о лимитах можно получить у менеджера.\n\n"

        "<b>3. Как происходит обмен?</b>\n"
        "Для начала обмена нажмите кнопку Поменять валюту и следуйте инструкциям. "
        "Вам нужно будет указать сумму в рублях, которую хотите обменять, "
        "и реквизиты для получения юаней.\n\n"

        "<b>4. Какие способы оплаты вы принимаете?</b>\n"
        "Мы принимаем оплату с банковских карт, электронных кошельков и т.д. "
        "Список доступных способов оплаты и реквизиты вы получите после начала обмена.\n\n"

        "<b>5. Сколько времени занимает обмен?</b>\n"
        "Обмен обычно занимает от 15 минут~. В редких случаях возможны задержки. "
        "Если ваш обмен задерживается, пожалуйста, свяжитесь с поддержкой.\n\n"

        "<b>6. Безопасен ли обмен через вашего бота?</b>\n"
        "Да, безопасность ваших данных и средств – наш приоритет.\n\n"

        "<b>7. Могу ли я отменить обмен?</b>\n"
        "Отмена обмена возможна до момента подтверждения оплаты."
    )

    await message.answer(
        text=faq_text,
        parse_mode='HTML'
    )


@router.message(F.text == 'Поменять валюту')
async def exchange_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    now = datetime.now()

    # Проверка временного ограничения
    if user_id in last_request_time:
        last_time = last_request_time[user_id]
        if now - last_time < timedelta(minutes=1):
            wait_seconds = 60 - (now - last_time).seconds
            await message.answer(
                f"⏳ Вы недавно уже отправляли заявку, подождите еще {wait_seconds} секунд",
                reply_markup=main_kb()
            )
            return

    await message.answer(
        text='<b>Введите количество рублей</b>, которые хотите поменять:',
        parse_mode='HTML'
    )
    await state.set_state(ExchangeState.WAITING_AMOUNT)


@router.message(ExchangeState.WAITING_AMOUNT, F.text.regexp(r'^\d+$'))
async def process_amount(message: Message, state: FSMContext):
    amount = int(message.text)
    rate = float(Config.CURRENT_RATE)
    yuan = math.floor((amount / rate) * 100) / 100  # Округление вниз до 2 знаков

    await state.update_data(amount=amount, yuan=yuan)

    await message.answer(
        text=f'Вы получите {yuan:.2f}¥\n\nОтправить заявку?',
        reply_markup=confirm_kb()
    )
    await state.set_state(ExchangeState.CONFIRMATION)


@router.message(ExchangeState.WAITING_AMOUNT)
async def wrong_amount(message: Message):
    await message.answer('❌ Введите целое число рублей (только цифры)!')


@router.message(ExchangeState.CONFIRMATION, F.text == 'Нет')
async def cancel_exchange(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Отмена операции', reply_markup=main_kb())


@router.message(ExchangeState.CONFIRMATION, F.text == 'Да')
async def confirm_exchange(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    data = await state.get_data()
    await state.clear()

    # Обновляем время последней заявки
    last_request_time[user_id] = datetime.now()

    current_time = datetime.now().strftime('%H:%M:%S %d.%m.%Y')

    admin_text = (
        f'🔄 Новая заявка на обмен!\n\n'
        f'⏰ Время: {current_time}\n'
        f'👤 Пользователь: @{message.from_user.username}\n'
        f'📎 Профиль: tg://user?id={message.from_user.id}\n'
        f'💸 Сумма: {data["amount"]} ₽\n'
        f'💵 К выдаче: {data["yuan"]}¥'
    )

    await bot.send_message(
        chat_id=Config.ADMIN,
        text=admin_text
    )

    await message.answer(
        text='✅ Заявка отправлена! С вами свяжутся в ближайшее время.',
        reply_markup=main_kb()
    )
