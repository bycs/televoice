import logging
import os

from aiogram import Bot, Dispatcher, executor, types
from pydub import AudioSegment
import speech_recognition as sr

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv("TG_API_TOKEN"))
dp = Dispatcher(bot)


async def voice_to_text(message: types.Message) -> str:
    """
    Расшифровка голосового сообщения
    """
    await bot.download_file_by_id(
        file_id=message.voice.file_id, destination=f"temp/{message.voice.file_id}.ogg"
    )
    voice = AudioSegment.from_ogg(file=f"temp/{message.voice.file_id}.ogg")
    os.remove(os.path.join("temp", f"{message.voice.file_id}.ogg"))
    voice.export(out_f=f"temp/{message.voice.file_id}.wav", format="wav")
    r = sr.Recognizer()
    with sr.AudioFile(f"temp/{message.voice.file_id}.wav") as source:
        audio = r.record(source)
    os.remove(os.path.join("temp", f"{message.voice.file_id}.wav"))
    text_output = r.recognize_google(audio_data=audio, language="ru-RU")
    return text_output


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    """
    Отправка сообщения присиспользования команд `/start` или `/help`
    """
    await message.reply(
        "Привет!\n"
        "Я могу расшифровать голосовые сообщения и передать их содержание в виде текста."
    )


@dp.message_handler(content_types="voice")
async def voice_input(message: types.Message):
    """
    Ответ на голосовое сообщение рашифровкой этого сообщения
    """
    try:
        text_output = await voice_to_text(message)
    except Exception or sr.UnknownValueError:
        await message.reply("Ошибка!\nЧто-то пошло не так...")
    else:
        await message.reply(
            f"Расшифровка сообщения от {message.from_user.full_name}:\n\n"
            f"{text_output}"
        )


if __name__ == "__main__":
    executor.start_polling(dp)
