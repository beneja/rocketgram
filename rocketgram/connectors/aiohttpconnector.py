# Copyright (C) 2015-2019 by Vd.
# This file is part of RocketGram, the modern Telegram bot framework.
# RocketGram is released under the MIT License (see LICENSE).


import asyncio
import logging

import aiohttp

try:
    import ujson as json
except ModuleNotFoundError:
    import json

from .. import types
from .baseconnector import BaseConnector
from ..requests import Request
from ..update import Response
from ..errors import RocketgramNetworkError, RocketgramParseError

logger = logging.getLogger('rocketgram.connectors.aiohttpconnector')


class AioHttpConnector(BaseConnector):
    def __init__(self, loop: asyncio.AbstractEventLoop = None, timeout: int = 35,
                 api_url: str = types.API_URL):
        if not loop:
            loop = asyncio.get_event_loop()
        self._api_url = api_url
        self._session = aiohttp.ClientSession(loop=loop)
        self._timeout = timeout

    async def init(self):
        pass

    async def shutdown(self):
        await self._session.close()

    async def send(self, token: str, request: Request) -> Response:
        try:
            url = self._api_url % token + request.method

            request_data = request.render()

            files = request.files()

            if len(files):
                data = aiohttp.FormData()
                for name, field in request_data.items():
                    if isinstance(field, (dict, list)):
                        data.add_field(name, json.dumps(field), content_type='application/json')
                        continue
                    data.add_field(name, str(field), content_type='text/plain')

                for file in files:
                    data.add_field(file.file_name, file.data, filename=file.file_name, content_type=file.content_type)

                response = await self._session.post(url, data=data, timeout=self._timeout)
            else:
                headers = {'Content-Type': 'application/json'}
                response = await self._session.post(url, data=json.dumps(request_data), headers=headers,
                                                    timeout=self._timeout)

            return Response.parse(json.loads(await response.read()), request)
        except json.decoder.JSONDecodeError as e:
            raise RocketgramParseError(e)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            raise RocketgramNetworkError(e)
