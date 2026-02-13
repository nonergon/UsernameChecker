import asyncio
import aiohttp
import aiofiles
from colorama import Fore, Style, init

init(autoreset=True)

PLATFORMS = {
    "github": "https://github.com/{}",
    "gitlab": "https://gitlab.com/{}",
    "bitbucket": "https://bitbucket.org/{}",
    "reddit": "https://www.reddit.com/user/{}",
    "pinterest": "https://www.pinterest.com/{}/",
    "steam": "https://steamcommunity.com/id/{}",
    "medium": "https://medium.com/@{}",
    "keybase": "https://keybase.io/{}",
    "replit": "https://replit.com/@{}",
    "pastebin": "https://pastebin.com/u/{}",
    "roblox": "https://www.roblox.com/user.aspx?username={}",
    "soundcloud": "https://soundcloud.com/{}",
    "npm": "https://www.npmjs.com/~{}",
    "pypi": "https://pypi.org/user/{}",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

SEM = asyncio.Semaphore(80)
RETRIES = 3


async def single_check(session, url):
    try:
        async with SEM:
            async with session.get(url, allow_redirects=True) as r:
                if r.status == 404:
                    return "free"
                if r.status == 200:
                    return "taken"
                return None
    except:
        return None


async def check_platform(session, platform, username):
    url = PLATFORMS[platform].format(username)

    tasks = [single_check(session, url) for _ in range(RETRIES)]
    results = await asyncio.gather(*tasks)

    free_count = results.count("free")
    taken_count = results.count("taken")

    if free_count >= 2:
        return platform, "free"
    if taken_count >= 2:
        return platform, "taken"

    return platform, None


async def process(username, session):
    tasks = [
        check_platform(session, platform, username)
        for platform in PLATFORMS
    ]

    results = await asyncio.gather(*tasks)

    free_list = []
    taken_list = []

    for platform, status in results:
        if status == "free":
            free_list.append(platform)
        elif status == "taken":
            taken_list.append(platform)

    print(f"\n{Fore.WHITE}{username}{Style.RESET_ALL}")

    if free_list:
        print(f"{Fore.LIGHTGREEN_EX}[ FREE  : {', '.join(sorted(free_list))} ]")

    if taken_list:
        print(f"{Fore.LIGHTBLUE_EX}[ TAKEN : {', '.join(sorted(taken_list))} ]")


async def main():
    async with aiofiles.open("users.txt", "r") as f:
        usernames = [line.strip() async for line in f if line.strip()]

    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession(
        headers=HEADERS,
        timeout=timeout
    ) as session:

        await asyncio.gather(*(process(u, session) for u in usernames))


if __name__ == "__main__":
    asyncio.run(main())
