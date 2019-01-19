from os import getenv
from re import match
from discord.ext import commands
from aiohttp import ClientSession


bot = commands.Bot(command_prefix='$')


session = ClientSession(loop=bot.loop)
url = f"https://api.heroku.com/apps/{getenv('APP_NAME')}/builds"
headers = {
    'Accept': 'application/vnd.heroku+json; version=3',
    'Content-Type': 'application/json',
    'Authorization': f"Bearer {getenv('HEROKU_TOKEN')}"
}


def get_payload(version):
    m = match(r'(v?[\d.-]+)', str(version))
    if m is None:
        raise commands.BadArgument('Invalid Version')
    version = m.group(0)
    if not version.startswith('v'):
        version = 'v' + version

    return {
        'source_blob': {
            'url': 'https://github.com/kyb3r/modmail/'
                   f'archive/{version}.tar.gz'
        }
    }


@bot.command()
@commands.has_permissions(administrator=True)
async def checkout(ctx, *, version: str):
    async with session.post(url=url, headers=headers,
                            json=get_payload(version)) as resp:

        async with session.get(
                url=(await resp.json()).get('output_stream_url')
        ) as resp2:
            while True:
                chunk, b = await resp2.content.readchunk()
                if b:
                    break
                await ctx.send(chunk.decode())


bot.run(getenv('BOT_TOKEN'))
