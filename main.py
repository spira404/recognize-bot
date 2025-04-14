from aiogram import Dispatcher, types, Bot, F
from aiogram.filters import Command

from io import BytesIO
import aiohttp
import asyncio
import time
import logging

from os import getenv
from dotenv import load_dotenv

from voice import ogg_to_text

load_dotenv()

TOKEN = getenv("BOT_TOKEN")
bot = Bot(TOKEN)
dp = Dispatcher()

logging.basicConfig(filename=".main.log",
        level=logging.WARNING, 
        filemode="a",
        format="%(asctime)s %(levelname)s %(module)s - %(funcName)s \n%(message)s\n|\n|\n|", 
        datefmt="%d/%m/%Y %I:%M:%S %p"
        )

def shrinktxt(txt: str):
    result = []
    while len(txt) > 4090:
        result.append(txt[:4091])
        txt = txt[4091:]
    result.append(txt)
    return result

async def get_audio_bytes(bot: Bot, file_id: str) -> bytes:
    try:
        file_info = await bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as response:
                if response.status == 200:

                    return BytesIO(await response.read())
    except Exception as e:
        logging.warning(e)

@dp.message(Command("start"))
async def greet(mes: types.Message):
    await bot.send_message(mes.from_user.id,
        f"""\
Отправь гс - получи расшифровку
""",
        parse_mode="HTML") 

@dp.message(lambda message: message.audio is not None)
async def handle_audio(mes: types.Message, bot: Bot):
    try:
        audio = mes.audio
        audio_bytes = await get_audio_bytes(bot, audio.file_id)
        transcribation = ogg_to_text(audio_bytes)
        if len(transcribation) > 4090:
            transcribation = shrinktxt(transcribation)

            for txt in transcribation:
                await bot.send_message(mes.from_user.id, txt)
        else:
            await mes.answer(transcribation)
    except Exception as e:
        logging.warning(e)

@dp.message(lambda message: message.voice is not None)
async def handle_voice(mes: types.Message, bot: Bot):
    try:
        voice = mes.voice
        voice_bytes = await get_audio_bytes(bot, voice.file_id)
        transcribation = ogg_to_text(voice_bytes)
        if len(transcribation) > 4090:
            transcribation = shrinktxt(transcribation)
            for txt in transcribation:
                await bot.send_message(mes.from_user.id, txt)
        else:
            await mes.answer(transcribation)
        
    except Exception as e:
        logging.warning(e)

async def main():
    await dp.start_polling(
        bot, 
        skip_updates=True,
        handle_signals=False)

if __name__ == "__main__":
    asyncio.run(main())

