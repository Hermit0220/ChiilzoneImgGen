import headers
import io
from datetime import datetime
import aiohttp
import base64
from io import BytesIO
#disnake related
import disnake
from disnake.ext import commands
##g4f related
from g4f.client import Client
import g4f
from g4f.Provider import Llama, ReplicateImage
# other related
from gtts import gTTS
from pytube import YouTube
from rembg import remove
from PIL import Image
import nest_asyncio
#import easyocr
time = datetime.now()
activity = disnake.Activity(
    name="!help / Currently working",
    type=disnake.ActivityType.playing,
)
bot = commands.Bot(command_prefix='!', intents=disnake.Intents.all(), help_command=None,activity=activity)
g4f.debug.logging = True
nest_asyncio.apply()
client = Client(
    text_provider=Llama,
    image_provider=ReplicateImage
)
headers.cleaner() # enable this optionally   
@bot.event
async def on_ready(): # [+] "bot_name is ready!" message
    ready_to_work = str(time)+": "+f" Bot {bot.user} is ready to work!"
    logs_on_ready = ['\n'+
    "[INFO] "+ready_to_work]
    with open('logs/logsDS.txt', 'a') as f:
        f.write('\n'.join(logs_on_ready))
    print(logs_on_ready.pop(0))
@bot.command()
async def help(ctx): # !help message
    await ctx.reply(embed=headers.help_msg())
    headers.logger("!help", ctx.author, ctx," ")
@bot.slash_command(description="Will show you credits like used libs and author of this bot")
async def credits(inter): # /credits message
    await inter.response.send_message(embed=headers.credits_msg())
    headers.logger("!credits", inter.author, inter, " ")
@bot.slash_command(description="Receive random cat image")
async def randomcat(inter):
    try:
        await inter.response.send_message(embed=headers.req_claim())
        async with aiohttp.ClientSession() as session:
            async with session.get('https://cataas.com/cat') as resp:
                    data = io.BytesIO(await resp.read())
                    await inter.edit_original_response(embed=headers.req_done(" ").set_image(file=disnake.File(data,"cool_image.png")))
                    headers.logger("!randomcat", inter.author, "inter", "data")
    except Exception as randomcat_error:
        await inter.edit_original_response(embed = headers.req_failed(randomcat_error))
@bot.slash_command(description="Receive random cat gif")
async def randomcatgif(inter):
    try:
        await inter.response.send_message(embed=headers.req_claim())
        async with aiohttp.ClientSession() as session:
            async with session.get('https://cataas.com/cat/gif') as resp:
                    data = io.BytesIO(await resp.read())
                    await inter.edit_original_response(embed=headers.req_done(" ").set_image(file=disnake.File(data,"cool_gif.gif")))
                    headers.logger("!randomcatgif", inter.author, "inter", "data")
    except Exception as randomcat_error:
        await inter.edit_original_response(embed = headers.req_failed(randomcat_error))
@bot.slash_command(description="ChatGPT will write whatever you ask!")
async def chatgpt(inter, *, your_prompt: str):
    try:
        await inter.response.send_message(embed=headers.req_claim())
        resp_msg = client.chat.completions.create(model=g4f.models.llama3_70b_instruct, provider=Llama,messages=[{"role": "user","content": your_prompt,}])
        await inter.edit_original_response(embed=headers.req_done(resp_msg.choices[0].message.content))
        headers.logger("!chatgpt", inter.author, your_prompt, resp_msg.choices[0].message.content)
    except Exception as chatgpt_error:
        await inter.edit_original_response(embed = headers.req_failed(error=chatgpt_error))
        headers.logger("!chatgpt", inter.author, your_prompt, chatgpt_error)
@bot.slash_command(description="SD-XL can draw you a picture from the text prompt")
async def sdxl(inter, *, your_prompt: str): 
    try:
        await inter.response.send_message(embed=headers.req_claim())
        resp_image = client.images.generate(model="stability-ai/sdxl", prompt=your_prompt)
        image_url = resp_image.data[0].url # get the url of image
        image_bytes = BytesIO(base64.b64decode(await headers.async_encode_base64(image_url)))
        await inter.edit_original_response(embed=headers.req_done(" ").set_image(file=disnake.File(image_bytes,"result.png")))
        headers.logger("!sdxl", inter.author, your_prompt, image_url)
    except Exception as genimage_error:
        await inter.edit_original_response(embed = headers.req_failed(error=genimage_error))
        headers.logger("!sdxl", inter.author, your_prompt, genimage_error)
async def ytmp3(inter, *, youtube_link: str):
    try:
        await inter.response.send_message(embed=headers.req_claim())
        yt = YouTube(youtube_link)
        filename = "files/ytmp3/converted"+".mp3"
        yt.streams.filter(only_audio=True).first().download(filename=filename)
        await inter.edit_original_response(embed=headers.req_done("Видео загружено!\nНачинаю процесс конвертации..."))
        with open(filename,"rb") as fp:
            await inter.edit_original_response(embed= headers.req_done("Успешно сконвертировано!"), file=disnake.File(fp,yt.title+".mp3"))
            headers.logger("!ytmp3", inter.author, youtube_link, filename)
    except Exception as error:
        await inter.edit_original_response(embed=headers.req_failed(error))
        headers.logger("!ytmp3", inter.author, inter, error)
@bot.slash_command(description="Google text to speach will convert your message to speach!")
async def gtts(inter, language: str,*, message: str):
    try:
        textGTTS = message
        tts = gTTS(text=textGTTS, lang=language)
        out_file = "files/gtts/gtts.mp3"
        tts.save(out_file)
        with open(out_file, "rb") as fp:
            await inter.response.send_message(embed=headers.req_done("Успешно!"),file=disnake.File(fp,message+".mp3"))
            headers.logger("!gtts", inter.author, language+" "+message, out_file)
    except Exception as error:
        await inter.response.send_message(headers.req_failed(error))
        headers.logger("!gtts", inter.author, message, error)
@bot.command(description="Remove backround from any photos")
async def rembg(ctx):
    try:
        for attachment in ctx.message.attachments:
            await ctx.reply(embed=headers.req_claim())
            await attachment.save('files/rembg/'+attachment.filename)
            input_path = f"files/rembg/{attachment.filename}"
            output_path = f"files/rembg/{attachment.filename}_rembg.png"
            img = Image.open(input_path)
            output = remove(img)
            output.save(output_path)
        await ctx.reply(embed = headers.req_done(" ").set_image(file=disnake.File(output_path)))
        headers.logger("!rembg", ctx.author, attachment.filename, output_path)
    except Exception as error:
        await ctx.message.reply(embed=headers.req_failed(error))
        headers.logger("!rembg", ctx.author, attachment.filename, error)
bot.run(headers.get_bot_token())
""" OCR function
@bot.command(description="OCR allows you to grab text from images!")
async def imgtotxt(ctx):
    try:
        for attachment in ctx.message.attachments:
            await ctx.reply(embed=headers.req_claim())
            input_path = f"files/imgtotxt/{attachment.filename}"
            await attachment.save(input_path)
            reader = easyocr.Reader(['en', "ru"])
            result = reader.readtext(input_path, detail = 0)
            await ctx.reply(embed=headers.req_done(result))
            headers.logger("!imgtotxt", ctx.author, attachment.filename, result)
    except Exception as error:
            await ctx.reply(headers.req_failed(error))
            headers.logger("!imgtotxt", ctx.author, attachment.filename, error)
"""
