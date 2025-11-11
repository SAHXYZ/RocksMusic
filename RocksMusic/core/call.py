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
# 🔹 yt-dlp Fallback Downloader (Fix for No Audio Source)
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

        # Validate audio using ffprobe
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
# 🔹 Main Class - Call Handler
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
    # Basic Control Methods
    # =======================================================

    async def pause_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.pause_stream(chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.resume_stream(chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_group_call(chat_id)
        except:
            pass

    async def stop_stream_force(self, chat_id: int):
        try:
            if config.STRING1:
                await self.one.leave_group_call(chat_id)
            if config.STRING2:
                await self.two.leave_group_call(chat_id)
            if config.STRING3:
                await self.three.leave_group_call(chat_id)
            if config.STRING4:
                await self.four.leave_group_call(chat_id)
            if config.STRING5:
                await self.five.leave_group_call(chat_id)
        except:
            pass
        await _clear_(chat_id)

    # =======================================================
    # Streaming Logic
    # =======================================================

    async def change_stream(self, client, chat_id):
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

        # =======================================================
        # Fix: Fallback when YouTube downloader fails
        # =======================================================
        if "vid_" in queued:
            mystic = await app.send_message(original_chat_id, _["call_7"])
            try:
                file_path, direct = await YouTube.download(
                    videoid,
                    mystic,
                    videoid=True,
                    video=video,
                )
            except Exception:
                try:
                    file_path = download_audio(f"https://www.youtube.com/watch?v={videoid}")
                    direct = None
                except Exception as e:
                    return await mystic.edit_text(f"❌ Audio download failed: {e}")
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
    # Other Methods
    # =======================================================

    async def ping(self):
        pings = []
        if config.STRING1:
            pings.append(await self.one.ping)
        if config.STRING2:
            pings.append(await self.two.ping)
        if config.STRING3:
            pings.append(await self.three.ping)
        if config.STRING4:
            pings.append(await self.four.ping)
        if config.STRING5:
            pings.append(await self.five.ping)
        return str(round(sum(pings) / len(pings), 3))

    async def start(self):
        LOGGER(__name__).info("Starting PyTgCalls Client...\n")
        if config.STRING1:
            await self.one.start()
        if config.STRING2:
            await self.two.start()
        if config.STRING3:
            await self.three.start()
        if config.STRING4:
            await self.four.start()
        if config.STRING5:
            await self.five.start()

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
