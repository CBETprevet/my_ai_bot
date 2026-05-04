import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
import httpx

# --- ТВОИ ДАННЫЕ (ВСТАВЬ В КАВЫЧКИ) ---
TG_TOKEN = "8408846324:AAF8jssX8eaMJz1tpB40kH-PchfLF7vH2Ww"
OPENROUTER_KEY = "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"
# -------------------------------------

bot = Bot(token=TG_TOKEN)
dp = Dispatcher()

async def ask_ai(prompt: str, image_url: str = None):
    url = "https://openrouter.ai"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    
    content = [{"type": "text", "text": prompt}]
    if image_url:
        content.append({"type": "image_url", "image_url": {"url": image_url}})
    
    data = {
        "model": "google/gemini-flash-1.5-free", 
        "messages": [{"role": "user", "content": content}]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data, timeout=60.0)
        result = response.json()
        return result['choices']['message']['content']

@dp.message(F.photo)
async def handle_photo(message: Message):
    file = await bot.get_file(message.photo[-1].file_id)
    file_url = f"https://telegram.org{TG_TOKEN}/{file.file_path}"
    status_msg = await message.reply("Изучаю фото... 🔍")
    try:
        text = await ask_ai(message.caption or "Что на фото?", file_url)
        await status_msg.edit_text(text)
    except:
        await status_msg.edit_text("Не удалось прочитать фото.")

@dp.message(F.text)
async def handle_text(message: Message):
    try:
        text = await ask_ai(message.text)
        await message.answer(text)
    except:
        await message.answer("Ошибка связи с ИИ.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
