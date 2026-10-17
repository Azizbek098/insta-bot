[10/17/2026 7:04 PM] Azizbek: import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp import YoutubeDL

TOKEN = "8905783431:AAE_anEnvMEXCL3LD0g6699H5BA9mdQiNU4"

bot = telebot.TeleBot(TOKEN)

user_audios = {}
user_artists = {}

@bot.message_handler(commands=['start'])
def start_command(message):
    try:
        bot.reply_to(
            message, 
            f"Assalomu alaykum, {message.from_user.first_name}!\n\n"
            f"Menga Instagram video havolasini yuboring, uni zumda yuklab beraman! 📥"
        )
    except Exception as e:
        print(f"Start error: {e}")

@bot.message_handler(func=lambda message: True)
def download_instagram_media(message):
    url = message.text.strip()
    
    if "instagram.com" not in url:
        bot.reply_to(message, "Iltimos, faqat to'g'ri Instagram video havolasini yuboring!")
        return

    msg = bot.reply_to(message, "⚡️ Tezkor yuklanmoqda, kuting...")
    chat_id = message.chat.id

    video_file = f"video_{chat_id}.mp4"
    audio_file = f"audio_{chat_id}.mp3"

    ydl_opts = {
        'format': 'mp4',
        'outtmpl': video_file,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title') or info.get('uploader') or 'Xonanda / Artist'
            user_artists[chat_id] = title

        extract_cmd = f"ffmpeg -i {video_file} -vn -ab 192k -y {audio_file} > /dev/null 2>&1"
        os.system(extract_cmd)

        if os.path.exists(audio_file):
            user_audios[chat_id] = audio_file

        bot_info = bot.get_me()
        bot_username = bot_info.username

        caption = f"❤️ @{bot_username} orqali yuklab olindi\n🚀 📥"

        markup = InlineKeyboardMarkup()
        btn_save = InlineKeyboardButton("💾 Saqlash", callback_data="save_video")
        btn_music = InlineKeyboardButton("🎵 Qo'shiqni yuklab olish", callback_data="get_music")
        btn_group = InlineKeyboardButton("➕ Guruhga qo'shish", url=f"https://t.me/{bot_username}?startgroup=true")
        
        markup.add(btn_save)
        markup.add(btn_music)
        markup.add(btn_group)

        with open(video_file, 'rb') as video:
            bot.send_video(chat_id, video, caption=caption, reply_markup=markup)

        bot.delete_message(chat_id, msg.message_id)

    except Exception as e:
        bot.edit_message_text("❌ Xatolik yuz berdi. Havola yaroqsiz yoki video yopiq profildan bo'lishi mumkin.", chat_id, msg.message_id)

    finally:
        if os.path.exists(video_file):
            os.remove(video_file)

@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    chat_id = call.message.chat.id

    if call.data == "save_video":
        bot.answer_callback_query(call.id, "Video saqlandi!")

    elif call.data == "get_music":
        audio_file = user_audios.get(chat_id)

        if audio_file and os.path.exists(audio_file):
            bot.answer_callback_query(call.id, "Musiqa yuborilmoqda...")
            
            markup = InlineKeyboardMarkup()
            btn_artist = InlineKeyboardButton("🔍 Artistning boshqa musiqalari", callback_data="get_artist_songs")
            markup.add(btn_artist)

            with open(audio_file, 'rb') as audio:
                bot.send_audio(chat_id, audio, caption="🎵 Videodagi musiqa", reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "Musiqa topilmadi. Qaytadan video yuboring.", show_alert=True)

    elif call.data == "get_artist_songs":
        bot.answer_callback_query(call.id, "Tavsiyalar tayyorlanmoqda...")
        
        artist_name = user_artists.get(chat_id, "Artist")
        if len(artist_name) > 25:
            artist_name = artist_name[:25] + "..."

        markup = InlineKeyboardMarkup(row_width=5)
        buttons = [InlineKeyboardButton(str(i), callback_data=f"hit_{i}") for i in range(1, 11)]
        markup.add(*buttons)
[10/17/2026 7:04 PM] Azizbek: text = (
            f"🔍 {artist_name} - Mashhur taronalari:\n\n"
            f"1. {artist_name} - Hit Trek 1\n"
            f"2. {artist_name} - Hit Trek 2\n"
            f"3. {artist_name} - Mashhur tarona 3\n"
            f"4. {artist_name} - Sevimli tarona 4\n"
            f"5. {artist_name} - Albom treki 5\n"
            f"6. {artist_name} - Remiks 6\n"
            f"7. {artist_name} - Jonli ijro 7\n"
            f"8. {artist_name} - Klip versiya 8\n"
            f"9. {artist_name} - Top tarona 9\n"
            f"10. {artist_name} - Yangi taronasi 10\n\n"
            "Kerakli raqamni bosing:"
        )
        bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup)

    elif call.data.startswith("hit_"):
        song_num = call.data.split("_")[-1]
        bot.answer_callback_query(call.id, f"{song_num}-musiqa yuborilmoqda...")
        
        audio_file = user_audios.get(chat_id)
        if audio_file and os.path.exists(audio_file):
            with open(audio_file, 'rb') as audio:
                bot.send_audio(chat_id, audio, caption=f"🎵 Tanlangan trek (#{song_num})")
        else:
            bot.send_message(chat_id, f"🎵 Tanlangan #{song_num}-taronasi tayyorlandi.")

print("Bot ultra tezlikda ishga tushdi...")
bot.infinity_polling(timeout=10, long_polling_timeout=5)