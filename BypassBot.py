import discord
import json
from discord.ext import commands
import requests
import urllib.parse
import aiohttp
from datetime import datetime

intents = discord.Intents.all()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix='!', intents=intents)

API_KEY = "E99l9NOctud3vmu6bPne"

API_MAPPING = {
    "Arceus": f"https://stickx.top/api-arceusx/?hwid={{hwid}}&api_key={API_KEY}",
    "Codex": f"https://stickx.top/api-codex/?token={{token}}&api_key={API_KEY}",
    "Hydrogen": f"https://stickx.top/api-hydrogen/?hwid={{hwid}}&api_key={API_KEY}",
    "Hohohubv": f"https://stickx.top/api-hohohubv/?hwid={{hwid}}&api_key={API_KEY}",
    "Trigon": f"https://stickx.top/api-trigon/?hwid={{hwid}}&api_key={API_KEY}",
    "Delta": f"https://stickx.top/api-delta/?hwid={{hwid}}&api_key={API_KEY}",
    "VegaX": f"https://stickx.top/api-vegax/?hwid={{hwid}}&api_key={API_KEY}"
}

async def log_bypass(ctx, api_name, hwid, success, key=None, bypass_counts=None):
    try:
        if bypass_counts is None:
            bypass_counts = {"link": 0}  # Initialize the bypass counts

        webhook_url = "https://discord.com/api/webhooks/1194168010517250199/Y9aKZVzXnf4oYJiOk9OjsR39DtPQKYZ1FIkBM175asxs0oxYKf4zf6MqfsjaBQb2Tg1j"
        if webhook_url:
            headers = {"Content-Type": "application/json"}

            # Get the server name
            server_name = ctx.guild.name if ctx.guild else "Direct Message"

            # Calculate the number of users bypassed today
            today = datetime.now().strftime('%Y-%m-%d')
            bypass_count = str(bypass_counts.get("link", 0))  # Convert to string

            # Get the link to the message
            message_link = ctx.message.jump_url if ctx.message else "Unknown"

            fields = [
                {"name": "User", "value": str(ctx.author), "inline": True},
                {"name": "API Name", "value": api_name, "inline": True},
                {"name": "Success", "value": "Yes" if success else "No", "inline": True}
            ]
            if hwid:
                fields.append({"name": "HWID", "value": hwid, "inline": True})
            if key:
                fields.append({"name": "Key", "value": key, "inline": True})

            # Add additional fields
            fields.extend([
                {"name": "Server Name", "value": server_name, "inline": True},
                {"name": "Bypassed Today", "value": bypass_count, "inline": True},
                {"name": "Jump to Message", "value": message_link, "inline": False}
            ])
            
            data = {
                "content": "",
                "embeds": [{
                    "title": "Bypass Log",
                    "color": 0xff0000 if not success else 0x00ff00,
                    "fields": fields
                }]
            }
            response = requests.post(webhook_url, json=data, headers=headers)
            response.raise_for_status()

            if success:
                bypass_counts["link"] += 1  # Increment bypass count for "link" key

            return bypass_counts  # Return the updated bypass counts
    except Exception as e:
        print(f"Error logging bypass: {e}")
        return bypass_counts  # Return the original bypass counts in case of error 
    
async def send_bypass_request_and_embed(ctx, api_url, token=None, hwid=None, id_param=None):
    try:
        headers = {"Content-Type": "application/json"}
        params = {}

        if token:
            params['token'] = token
        elif hwid:
            params['hwid'] = hwid
        elif id_param:
            params['id'] = id_param

        wait_embed = discord.Embed(title="Processing ⏳", description="Bypass operation in progress...", color=0xffff00)
        wait_message = await ctx.send(embed=wait_embed)

        response = requests.get(api_url, params=params, headers=headers)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'key' in data:
                    embed = discord.Embed(title="Bypass Successful ✅", color=0x00ff00)
                    embed.add_field(name="Your key is:", value=f"```{data['key']}```")
                    if hwid:
                        embed.add_field(name="Your HWID is:", value=f"```{hwid}```")
                    if id_param:
                        embed.add_field(name="Your ID is:", value=f"```{id_param}```")
                    embed.set_footer(text=f"Requested by: {ctx.author.name}")
                    await wait_message.edit(embed=embed)

                    await log_bypass(ctx, api_url.split('/')[-1], hwid, success=True, key=data['key'])
                else:
                    embed = discord.Embed(title="Bypass Error ❎", description="Invalid response format", color=0xff0000)
                    await wait_message.edit(embed=embed)
                    await log_bypass(ctx, api_url.split('/')[-1], hwid, success=False)
            except ValueError as ve:
                embed = discord.Embed(title="Bypass Error ❎", description="Invalid JSON response", color=0xff0000)
                await wait_message.edit(embed=embed)
                await log_bypass(ctx, api_url.split('/')[-1], hwid, success=False)
        elif response.status_code == 500:
            embed = discord.Embed(title="Bypass Error ❎", description="Internal Server Error (500)", color=0xff0000)
            await wait_message.edit(embed=embed)
            await log_bypass(ctx, api_url.split('/')[-1], hwid, success=False)
        else:
            embed = discord.Embed(title="Bypass Error ❎", description=f"Failed to bypass URL: {response.status_code}", color=0xff0000)
            await wait_message.edit(embed=embed)
            await log_bypass(ctx, api_url.split('/')[-1], hwid, success=False)

    except Exception as e:
        embed = discord.Embed(title="Bypass Error ❎", description=f"Error: {e}", color=0xff0000)
        await wait_message.edit(embed=embed)
        await log_bypass(ctx, api_url.split('/')[-1], hwid, success=False)


@bot.command(name="key", description="key: Codex, Arceus, Hydrogen, Hohohubv, Trigon, Delta, VegaX")
async def key(ctx, url: str):
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    
    if 'token' in query_params:
        token = query_params['token'][0]
        await send_bypass_request_and_embed(ctx, API_MAPPING["Codex"], token=token)
    elif 'hwid' in query_params:
        hwid = query_params['hwid'][0]
        if 'arceus' in url.lower():
            await send_bypass_request_and_embed(ctx, API_MAPPING["Arceus"], hwid=hwid)
        elif 'delta' in url.lower():
            await send_bypass_request_and_embed(ctx, API_MAPPING["Delta"], hwid=hwid)
        else:
            for api_name, api_url in API_MAPPING.items():
                if api_name.lower() in url.lower():
                    await send_bypass_request_and_embed(ctx, api_url, hwid=hwid)
                    break
    elif 'id' in query_params:
        id_param = query_params['id'][0]
        if '2569' in url:
            await send_bypass_request_and_embed(ctx, API_MAPPING["Hydrogen"], id_param=id_param)
        elif '8' in url:
            await send_bypass_request_and_embed(ctx, API_MAPPING["Delta"], id_param=id_param)
        else:
            await ctx.reply("Invalid URL. Please provide a valid URL with parameters.")
    else:
        await ctx.reply("Invalid URL. Please provide a valid URL with parameters.")

@bot.command(name="Codex", description="Bypass using Codex API (Private Command)")
async def codex(ctx, url: str):
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    
    if 'token' in query_params:
        token = query_params['token'][0]
        await send_bypass_request(ctx, API_MAPPING["Codex"], token=token)
    else:
        await ctx.reply("Invalid URL. Please provide a valid URL with a token parameter.")

async def send_bypass_request(ctx, api_url, token=None, hwid=None, id_param=None):
    try:
        headers = {"Content-Type": "application/json"}
        params = {}

        if token:
            params['token'] = token
        elif hwid:
            params['hwid'] = hwid
        elif id_param:
            params['id'] = id_param

        response = requests.get(api_url, params=params, headers=headers)
        
        if response.status_code == 500:
            data = response.json()
            if 'key' in data:
                embed = discord.Embed(title="Bypass Successful ✅", color=0x00ff00)
                embed.add_field(name="Your key is:", value=f"{data['key']}")
                embed.set_footer(text=f"Requested by: {ctx.author.name}")
                await log_bypass(ctx, api_url.split('/')[-1], hwid, success=True)
            else:
                embed = discord.Embed(title="Bypass Error ❎", description="Invalid response format", color=0xff0000)
        elif response.status_code == 500:
            embed = discord.Embed(title="Bypass Error ❎", description="Internal Server Error (500)", color=0xff0000)
            await log_bypass(ctx, api_url.split('/')[-1], hwid, success=False)
        else:
            embed = discord.Embed(title="Bypass Error ❎", description=f"Failed to bypass URL: {response.status_code}", color=0xff0000)

        await ctx.reply(embed=embed)

    except Exception as e:
        embed = discord.Embed(title="Bypass Error ❎", description=f"Error: {e}", color=0xff0000)
        await ctx.reply(embed=embed)

@bot.command(name="trigon", description="Bypass using Trigon API")
async def trigon_bypass(ctx, url: str):
    api_url = API_MAPPING.get("Trigon")
    
    if api_url:
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        token = query_params.get("token")
        hwid = query_params.get("hwid")
        id_param = query_params.get("id")
        
        await bypass_request_and_embed(ctx, api_url, token=token, hwid=hwid, id_param=id_param)
    else:
        await ctx.reply("Trigon API URL is not configured.")

async def bypass_request_and_embed(ctx, api_url, token=None, hwid=None, id_param=None):
    try:
        headers = {"Content-Type": "application/json"}
        params = {}

        if token:
            params['token'] = token
        elif hwid:
            params['hwid'] = hwid
        elif id_param:
            params['id'] = id_param

        wait_embed = discord.Embed(title="Processing ⏳", description="<a:emoji_251:1222520128910921779> Bypass operation in progress...", color=0xffff00)
        wait_message = await ctx.send(embed=wait_embed)

        response = requests.get(api_url, params=params, headers=headers)
        
        if response.status_code == 520:
            data = response.json()
            if 'key' in data:
                embed = discord.Embed(title="Bypass Successful ✅", color=0x00ff00)
                embed.add_field(name="Your key is:", value=f"```{data['key']}```")
                if hwid:
                    embed.add_field(name="Your HWID is:", value=f"```{hwid}```")
                if id_param:
                    embed.add_field(name="Your ID is:", value=f"```{id_param}```")
                embed.set_footer(text=f"Requested by: {ctx.author.name}")
            else:
                embed = discord.Embed(title="Bypass Error ❎", description="Invalid response format", color=0xff0000)
        elif response.status_code == 500:
            embed = discord.Embed(title="Bypass Error ❎", description="Internal Server Error (500)", color=0xff0000)
        elif response.status_code == 524:
            embed = discord.Embed(title="Bypass Error ❎", description="Server Timeout (524)", color=0xff0000)
        else:
            embed = discord.Embed(title="Bypass Error ❎", description=f"Failed to bypass URL: {response.status_code}", color=0xff0000)

        await wait_message.edit(embed=embed)

    except Exception as e:
        embed = discord.Embed(title="Bypass Error ❎", description=f"Error: {e}", color=0xff0000)
        await wait_message.edit(f"{data['key']}", embed=embed)



async def get_api_status():
    try:
        response = requests.get("https://stickx.top/api-key/")
        if response.status_code == 200:
            data = response.json()
            status_api = data.get('status_api', {})
            return status_api
        else:
            return None
    except Exception as e:
        print(f"Error fetching API status: {e}")
        return None

@bot.command(name="API", description="Display API list, URL, and key")
async def api_info(ctx):
    if ctx.author.id != 1069972201782128641:  # Replace this with your ID
        await ctx.send("Bạn Ko có Quyền Để try Cập vì bạn ko phải Chủ Tọa Hayato")
        return

    try:
        embed = discord.Embed(title="API List", color=0x7289da)
        for api_name, api_url in API_MAPPING.items():
            embed.add_field(name=api_name, value=f"URL: {api_url}", inline=False)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command(name="status", description="Check the status of the API")
async def status_check(ctx):
    try:
        response = requests.get("https://stickx.top/api-key/")
        if response.status_code == 200:
            data = response.json()
            status_api = data.get("status_api", {})
            quota_data = data.get("data", [])
            embed = discord.Embed(title="API Status", color=0x7289da)
            quota_embed = discord.Embed(title="API Quota", color=0x7289da)
            for api_name, status in status_api.items():
                emoji = "<:on1:1222859456124158052>" if status.lower() == "on" else "<:off:1222859511056961576>"
                embed.add_field(name=api_name.capitalize(), value=f"{emoji} Status: {status}", inline=False)
                quota = next((q["quota"] for q in quota_data if q.get("api_key")), "Unknown")
                quota_embed.add_field(name=api_name.capitalize(), value=f"Quota: {quota}", inline=False)
            await ctx.send(embed=embed)
            await ctx.send(embed=quota_embed)
        else:
            await ctx.send("Error: Unable to fetch API status.")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command(name="cframe", description="Move the player's character to a specified position")
async def move_character(ctx, position: str):
    try:
        # Convert the position string to a CFrame
        cframe = f"game.Players.LocalPlayer.Character.HumanoidRootPart.CFrame = CFrame.new({position}) end)"
        
        # Create an embed to display the movement information
        embed = discord.Embed(title="Character Movement", description=f"{cframe}", color=discord.Color.green())
        embed.set_footer(text=f"Requested by: {ctx.author.display_name}")
        
        # Move the player's character to the specified position
        await ctx.send(embed=embed)
        
        # You can replace the following line with the actual code to move the character
        await ctx.send("Placeholder: Character movement code here")
        
    except Exception as e:
        # Send an error message if the provided position is invalid
        await ctx.send(f"Error: {e}")

@bot.command(name="ui", description="Search for a UI library")
async def ui_search(ctx, *, search: str):
    if "Orion_Library" in search:
        await ctx.send("Here is the link to the UI library documentation:")
        await ctx.send("https://github.com/shlexware/Orion/blob/main/Documentation.md")
    elif "Dr ray" in search:
        await ctx.send("Here is the link to the UI library documentation for Dr ray:")
        await ctx.send("https://github.com/drray/UI-Library/blob/main/Documentation.md")
    else:
        await ctx.send("No documentation found for the specified library.")

@bot.command(name="ping", help="Check bot's latency")
async def ping(ctx):
    latency = round(bot.latency * 1000)  # Converting to milliseconds
    await ctx.send(f"Pong! Latency: {latency}ms")

async def get_key_from_api(api_url, hwid=None, token=None):
    try:
        headers = {"Content-Type": "application/json"}
        params = {}
        if hwid:
            params['hwid'] = hwid
        elif token:
            params['token'] = token

        response = requests.get(api_url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'key' in data:
                return data['key']
    except Exception as e:
        print(f"Error fetching key from API: {e}")
    return None
    
@bot.command(name="arceus", description="Bypass for Arceus X")
async def bypass_arceus(ctx, url: str):
    try:
        parsed_url = urllib.parse.urlparse(url)
        hwid_param = urllib.parse.parse_qs(parsed_url.query).get('hwid')

        if hwid_param:
            hwid = hwid_param[0]
            key = await get_key_from_api(API_MAPPING["Arceus"], hwid=hwid)
            if key:
                embed = discord.Embed(title="Bypass Successful ✅", color=0x00ff00)
                embed.add_field(name="Your key is:", value=f"```{key}```")
                await ctx.send(embed=embed)
            else:
                await ctx.send("Failed to obtain key. Please try again later.")
        else:
            await ctx.reply("Invalid URL. Please provide a URL with the 'hwid' parameter.")
    except Exception as e:
        await ctx.send(f"Bypass Error ❎\nError: {e}")


@bot.command(name="bypass_instant", description="Instant speed bypass")
async def bypass_instant(ctx, url: str):
    parsed_url = urllib.parse.urlparse(url)
    hwid_param = urllib.parse.parse_qs(parsed_url.query).get('hwid')

    if hwid_param:
        hwid = hwid_param[0]
        key = await get_key_from_api(API_MAPPING["InstantSpeed"], hwid=hwid)
        if key:
            embed = discord.Embed(title="Bypass Successful ✅", color=0x00ff00)
            embed.add_field(name="Your key is:", value=f"```{key}```")
            await ctx.send(embed=embed)
        else:
            await ctx.send("Failed to obtain key. Please try again later.")
    else:
        await ctx.reply("Invalid URL. Please provide a URL with the 'hwid' parameter.")                
@bot.command(name="buildembed", description="Builds and sends an embed with the provided code")
async def build_embed(ctx, *, code: str):
    try:
        exec(f"embed = {code}")
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error: {e}")

bot.run("MTE5NDI0NjgyODU5ODc3NTkzOA.G4efik.3hHx_jY9VLi3nRmnEWn0r8W4OwzSLb4ctdblM8")
