import logging
import json
import os
import sys
from urllib.parse import urlsplit

from aiohttp import ClientSession
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

with open('config/config.json', 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

with open('config/templates.json', 'r', encoding='utf-8') as templates_file:
    templates = json.load(templates_file)

logging.basicConfig(level=config['loggingLevel'])

# python-socks принимает только открытый HTTP и SOCKS.
# https:// — это TLS до самого прокси, его умеет только штатный proxy aiohttp.
_PLAIN_PROXY_SCHEMES = {'http', 'socks4', 'socks4a', 'socks5', 'socks5h'}


class HttpsProxySession(AiohttpSession):
    def __init__(self, proxy: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._https_proxy = proxy

    async def create_session(self) -> ClientSession:
        session = await super().create_session()
        if getattr(session, '_https_proxy_wrapped', False):
            return session

        original_request = session._request

        async def _request(*args, **kwargs):
            kwargs.setdefault('proxy', self._https_proxy)
            return await original_request(*args, **kwargs)

        session._request = _request
        session._https_proxy_wrapped = True
        return session


def build_session(proxy: str | None) -> AiohttpSession:
    if not proxy:
        return AiohttpSession()

    scheme = urlsplit(proxy).scheme.lower()
    if scheme in _PLAIN_PROXY_SCHEMES:
        return AiohttpSession(proxy=proxy)
    if scheme == 'https':
        if sys.version_info < (3, 11):
            version = sys.version.split()[0]
            raise RuntimeError(
                f'HTTPS proxy needs Python 3.11 or newer (this process is {version})'
            )
        return HttpsProxySession(proxy)
    raise ValueError(f'Unsupported proxy scheme: {scheme}')


proxy = config.get('proxy') or os.environ.get('HTTPS_PROXY')
session = build_session(proxy)

bot = Bot(token=config['token'], session=session)
dp = Dispatcher()

bot_id = bot.id


async def main() -> None:
    await dp.start_polling(bot)
