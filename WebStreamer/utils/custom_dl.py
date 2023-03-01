from math import ceil, log2
from secrets import choice
from typing import List, Union

from pyrogram import Client, raw, utils
from pyrogram.errors import AuthBytesInvalid
from pyrogram.file_id import FileId, FileType, ThumbnailSource
from pyrogram.session import Auth, Session
from pyrogram.types import Message

from WebStreamer.bot import StreamBot
from WebStreamer.logger import LOGGER


async def chunk_size(length) -> int:
    """
    Calculate chunk size based on file length
    """
    return 2 ** max(min(ceil(log2(length / 1024)), 10), 2) * 1024


async def offset_fix(offset, chunksize) -> int:
    """
    Fix offset to be a multiple of chunksize
    """
    offset -= offset % chunksize
    return offset


class TGCustomYield:
    """
    class to get the file from telegram servers
    """

    def __init__(self, main_bot: List[Client] = [StreamBot]):
        """
        A custom method to stream files from telegram. functions: generate_file_properties: returns the properties
        for a media on a specific message contained in FileId class. generate_media_session: returns the media
        session for the DC that contains the media file on the message. yield_file: yield a file from telegram
        servers for streaming.
        """
        # NOTE: This is the default bot, can add a list and iterate over it to switch to different bots, need to add clients to 'bot/__init__.py'
        # choose a different bot from the list each time
        bot_used: Client = choice(main_bot)
        self.main_bot = bot_used
        LOGGER.info(f"Using {bot_used.name} to stream files")

    @staticmethod
    async def generate_file_properties(m: Message):
        """
        generate file properties from a message
        """
        available_media = (
            "audio",
            "document",
            "photo",
            "sticker",
            "animation",
            "video",
            "voice",
            "video_note",
        )

        if isinstance(m, Message):
            error_message = "This message doesn't contain any downloadable media"
            for kind in available_media:
                media = getattr(m, kind, None)

                if media is not None:
                    break
            else:
                raise ValueError(error_message)
        else:
            media = m

        file_id_str = media if isinstance(media, str) else media.file_id
        file_id_obj = FileId.decode(file_id_str)

        # The below lines are added to avoid a break in routes.py
        setattr(file_id_obj, "file_size", getattr(media, "file_size", 0))
        setattr(file_id_obj, "mime_type", getattr(media, "mime_type", ""))
        setattr(file_id_obj, "file_name", getattr(media, "file_name", ""))

        return file_id_obj

    async def generate_media_session(self, c: Client, m: Message):
        """
        generate media session from a message
        """
        data = await self.generate_file_properties(m)

        media_session = c.media_sessions.get(data.dc_id, None)

        if media_session is None:
            if data.dc_id != await c.storage.dc_id():
                media_session = Session(
                    c,
                    data.dc_id,
                    await Auth(
                        c,
                        data.dc_id,
                        await c.storage.test_mode(),
                    ).create(),
                    await c.storage.test_mode(),
                    is_media=True,
                )
                await media_session.start()

                for _ in range(3):
                    exported_auth = await c.invoke(
                        raw.functions.auth.ExportAuthorization(dc_id=data.dc_id),
                    )

                    try:
                        await media_session.invoke(
                            raw.functions.auth.ImportAuthorization(
                                id=exported_auth.id,
                                bytes=exported_auth.bytes,
                            ),
                        )
                    except AuthBytesInvalid:
                        continue
                    else:
                        break
                else:
                    await media_session.stop()
                    raise AuthBytesInvalid
            else:
                media_session = Session(
                    c,
                    data.dc_id,
                    await c.storage.auth_key(),
                    await c.storage.test_mode(),
                    is_media=True,
                )
                await media_session.start()

            c.media_sessions[data.dc_id] = media_session

        return media_session

    @staticmethod
    async def get_location(file_id: FileId):
        """
        get location from file id
        """
        file_type = file_id.file_type

        if file_type == FileType.CHAT_PHOTO:
            if file_id.chat_id > 0:
                peer = raw.types.InputPeerUser(
                    user_id=file_id.chat_id,
                    access_hash=file_id.chat_access_hash,
                )
            elif file_id.chat_access_hash == 0:
                peer = raw.types.InputPeerChat(chat_id=-file_id.chat_id)
            else:
                peer = raw.types.InputPeerChannel(
                    channel_id=utils.get_channel_id(file_id.chat_id),
                    access_hash=file_id.chat_access_hash,
                )

            return raw.types.InputPeerPhotoFileLocation(
                peer=peer,
                photo_id=file_id.media_id,
                big=file_id.thumbnail_source == ThumbnailSource.CHAT_PHOTO_BIG,
            )
        elif file_type == FileType.PHOTO:
            return raw.types.InputPhotoFileLocation(
                id=file_id.media_id,
                access_hash=file_id.access_hash,
                file_reference=file_id.file_reference,
                thumb_size=file_id.thumbnail_size,
            )
        else:
            return raw.types.InputDocumentFileLocation(
                id=file_id.media_id,
                access_hash=file_id.access_hash,
                file_reference=file_id.file_reference,
                thumb_size=file_id.thumbnail_size,
            )

    async def yield_file(
        self,
        media_msg: Message,
        offset: int,
        first_part_cut: int,
        last_part_cut: int,
        part_count: int,
        chunk_size_int: int,
    ) -> Union[str, None]:  # pylint: disable=unsubscriptable-object
        """
        yield a file from telegram servers for streaming
        """
        client = self.main_bot
        data = await self.generate_file_properties(media_msg)
        media_session = await self.generate_media_session(client, media_msg)

        location = await self.get_location(data)

        r = await media_session.invoke(
            raw.functions.upload.GetFile(
                location=location,
                offset=offset,
                limit=chunk_size_int,
            ),
        )

        if isinstance(r, raw.types.upload.File):
            current_part = 1

            while current_part <= part_count:
                chunk = r.bytes
                if not chunk:
                    break
                offset += chunk_size_int
                if part_count == 1:
                    yield chunk[first_part_cut:last_part_cut]
                    break
                if current_part == 1:
                    yield chunk[first_part_cut:]
                if 1 < current_part <= part_count:
                    yield chunk

                r = await media_session.invoke(
                    raw.functions.upload.GetFile(
                        location=location,
                        offset=offset,
                        limit=chunk_size_int,
                    ),
                )

                current_part += 1

    async def download_as_bytesio(self, m: Message):
        """
        download a file as bytesio
        """
        client = self.main_bot
        data = await self.generate_file_properties(m)
        media_session = await self.generate_media_session(client, m)

        location = await self.get_location(data)

        limit = 1024 * 1024
        offset = 0

        r = await media_session.invoke(
            raw.functions.upload.GetFile(location=location, offset=offset, limit=limit),
        )

        if isinstance(r, raw.types.upload.File):
            m_file = []
            # m_file.name = file_name
            while True:
                chunk = r.bytes

                if not chunk:
                    break

                m_file.append(chunk)

                offset += limit

                r = await media_session.invoke(
                    raw.functions.upload.GetFile(
                        location=location,
                        offset=offset,
                        limit=limit,
                    ),
                )

            return m_file
