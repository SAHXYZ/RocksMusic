import asyncio
import os
import json
import subprocess
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.exceptions import (
    AlreadyJoinedError,
    NoActiveGroupCall,
    TelegramServerError,
)
from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo
from pytgcalls.types.stream import StreamAudioEnded

import config
from RocksMusic import LOGGER, YouTube, app
from RocksMusic.misc import db
from RocksMusic.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from RocksMusic.utils.exceptions import AssistantErr
from RocksMusic.utils.formatters import check_duration, seconds_to_min, speed_converter
from RocksMusic.utils.inline.play import stream_markup
from RocksMusic.utils.stream.autoclear import auto_clean
from RocksMusic.utils.thumbnails import gen_thumb
from strings import get_string


# ============================================================
# 🔹 Fallback yt-dlp Downloader (for failed audio cases)
# ============================================================

def download_audio(source: str) -> str:
    """Force-download playable audio using yt-dlp + ffprobe verification."""
    try:
        os.makedirs("downloads", exist_ok=True)
        output_template = "downloads/%(id)s.%(ext)s"
        command = [
            "yt-dlp",
            "-f", "bestaudio/best",
            "--no-playlist",
            "--no-warnings",
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "-o", output_template,
            source
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        files = sorted(
            [f for f in os.listdir("downloads") if f.endswith(".mp3")],
            key=lambda f: os.path.getmtime(os.path.join("downloads", f))
        )
        if not files:
            raise Exception("No file downloaded by yt-dlp.")
        latest = os.path.join("downloads", files[-1])

        probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type", "-of", "json", latest]
        probe = subprocess.check_output(probe_cmd, text=True)
        data = json.loads(probe)
        if not any(s.get("codec_type") == "audio" for s in data.get("streams", [])):
            raise Exception("Invalid audio file (no audio stream).")

        return latest
    except Exception as e:
        raise RuntimeError(f"Audio download failed: {e}")


autoend = {}
counter = {}


async def _clear_(chat_id):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)


# ============================================================
# 🔹 Main Class - RocksMusic Call Handler
# ============================================================

class Call(PyTgCalls):
    def __init__(self):
        self.userbot1 = Client(
            name="RocksAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
        )
        self.one = PyTgCalls(self.userbot1, cache_duration=100)

        self.userbot2 = Client(
            name="RocksAss2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
        )
        self.two = PyTgCalls(self.userbot2, cache_duration=100)

        self.userbot3 = Client(
            name="RocksAss3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
        )
        self.three = PyTgCalls(self.userbot3, cache_duration=100)

        self.userbot4 = Client(
            name="RocksAss4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
        )
        self.four = PyTgCalls(self.userbot4, cache_duration=100)

        self.userbot5 = Client(
            name="RocksAss5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
        )
        self.five = PyTgCalls(self.userbot5, cache_duration=100)

    # =======================================================
    # 🔹 Join & Stream Control
    # =======================================================

    async def join_call(
        self,
        chat_id: int,
        original_chat_id: int,
        file_path: str,
        video: Union[bool, str] = None,
    ):
        """Handles first join & stream."""
        assistant = await group_assistant(self, chat_id)
        language = await get_lang(chat_id)
        _ = get_string(language)

        stream = (
            AudioVideoPiped(file_path, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo())
            if video
            else AudioPiped(file_path, audio_parameters=HighQualityAudio())
        )

        try:
            await assistant.join_group_call(
                chat_id,
                stream,
                stream_type=StreamType().pulse_stream,
            )
        except NoActiveGroupCall:
            raise AssistantErr(_["call_8"])
        except AlreadyJoinedError:
            raise AssistantErr(_["call_9"])
        except TelegramServerError:
            raise AssistantErr(_["call_10"])

        await add_active_chat(chat_id)
        await music_on(chat_id)
        if video:
            await add_active_video_chat(chat_id)

        LOGGER(__name__).info(f"🎶 Joined VC successfully in chat {chat_id}")

    async def change_stream(self, client, chat_id):
        """Handles next song in queue."""
        check = db.get(chat_id)
        loop = await get_loop(chat_id)
        try:
            if loop == 0:
                popped = check.pop(0)
            else:
                await set_loop(chat_id, loop - 1)
        except Exception:
            await _clear_(chat_id)
            return await client.leave_group_call(chat_id)

        if not check:
            await _clear_(chat_id)
            return await client.leave_group_call(chat_id)

        queued = check[0]["file"]
        streamtype = check[0]["streamtype"]
        videoid = check[0]["vidid"]
        title = (check[0]["title"]).title()
        user = check[0]["by"]
        original_chat_id = check[0]["chat_id"]
        language = await get_lang(chat_id)
        _ = get_string(language)

        video = True if str(streamtype) == "video" else False

        # Fallback downloader
        if "vid_" in queued:
            try:
                file_path, direct = await YouTube.download(videoid, None, videoid=True, video=video)
            except Exception:
                try:
                    file_path = download_audio(f"https://www.youtube.com/watch?v={videoid}")
                except Exception as e:
                    return await app.send_message(original_chat_id, f"❌ Audio download failed: {e}")
        else:
            file_path = queued

        stream = (
            AudioVideoPiped(file_path, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo())
            if video
            else AudioPiped(file_path, audio_parameters=HighQualityAudio())
        )

        try:
            await client.change_stream(chat_id, stream)
        except Exception:
            return await app.send_message(original_chat_id, text=_["call_6"])

        img = await gen_thumb(videoid)
        button = stream_markup(_, chat_id)
        run = await app.send_photo(
            chat_id=original_chat_id,
            photo=img,
            caption=_["stream_1"].format(
                f"https://t.me/{app.username}?start=info_{videoid}",
                title[:23],
                check[0]["dur"],
                user,
            ),
            reply_markup=InlineKeyboardMarkup(button),
        )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "stream"

    # =======================================================
    # 🔹 Start & Ping
    # =======================================================

    async def ping(self):
        pings = []
        for client in [self.one, self.two, self.three, self.four, self.five]:
            try:
                pings.append(await client.ping)
            except:
                pass
        return str(round(sum(pings) / len(pings), 3))

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Client...\n")
        for client in [self.one, self.two, self.three, self.four, self.five]:
            try:
                await client.start()
            except Exception as e:
                LOGGER(__name__).warning(f"Assistant start skipped: {e}")

    async def decorators(self):
        @self.one.on_stream_end()
        @self.two.on_stream_end()
        @self.three.on_stream_end()
        @self.four.on_stream_end()
        @self.five.on_stream_end()
        async def stream_end_handler(client, update: Update):
            if isinstance(update, StreamAudioEnded):
                await self.change_stream(client, update.chat_id)


Rocks = Call()
