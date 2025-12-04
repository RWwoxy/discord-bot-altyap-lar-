import discord
from discord.ext import commands
import asyncio
import random
import json
import os

PREFIX = "!"
TOKEN = "BURAYA_TOKEN"

INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=INTENTS)

# ---------------- KAYIT VERİLERİ ----------------

if not os.path.exists("kayıtlar.json"):
    with open("kayıtlar.json", "w") as f:
        json.dump({}, f)

def kayıt_veri_yükle():
    with open("kayıtlar.json", "r") as f:
        return json.load(f)

def kayıt_veri_kaydet(data):
    with open("kayıtlar.json", "w") as f:
        json.dump(data, f, indent=4)

# ---------------- TERMINAL ----------------

async def terminal():
    await bot.wait_until_ready()
    while True:
        komut = input("Terminal >> ")

        if komut.lower() == "dur":
            print("Bot kapatılıyor...")
            await bot.close()
            break

        elif komut.lower().startswith("yayınla "):
            mesaj = komut[8:]
            for guild in bot.guilds:
                for channel in guild.text_channels:
                    try:
                        await channel.send(mesaj)
                        print(f"Gönderildi: {guild.name} -> {channel.name}")
                        break
                    except:
                        continue

# ---------------- EVENT ----------------

@bot.event
async def on_ready():
    print(f"\nBot aktif: {bot.user}\n")
    bot.loop.create_task(terminal())

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    msg = message.content.lower()
    cevaplar = {
        "merhaba": "Hoş geldin! 😊",
        "selam": "Aleyküm selam!",
        "sa": "Aleyküm selam!",
        "hi": "Hello! 👋"
    }

    if msg in cevaplar:
        await message.channel.send(cevaplar[msg])

    await bot.process_commands(message)

# ---------------- KOMUT LİSTESİ ----------------

@bot.command()
async def komut(ctx):
    embed = discord.Embed(title="🔧 Komutlar", color=discord.Color.blurple())
    embed.add_field(name="Genel Komutlar", value=
                    "!ping\n"
                    "!kartopu @kullanıcı\n"
                    "!fakemesaj #kanal mesaj\n"
                    "!özlüsöz\n"
                    "!kayıt isim yaş\n"
                    "!profil", inline=False)
    embed.add_field(name="Moderasyon (yetkili)", value=
                    "!mute @kullanıcı\n"
                    "!unmute @kullanıcı\n"
                    "!kick @kullanıcı\n"
                    "!ban @kullanıcı\n"
                    "!timeout @kullanıcı süre", inline=False)
    embed.add_field(name="Bot Bilgisi", value="!botbilgi", inline=False)
    await ctx.send(embed=embed)

# ---------------- GENEL KOMUTLAR ----------------

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.command()
async def kartopu(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send("Bir kullanıcı etiketlemelisin!")
    await ctx.send(f"❄️ {ctx.author.mention}, {member.mention}'a kartopu attı!")

@bot.command()
async def fakemesaj(ctx, kanal: discord.TextChannel, *, mesaj):
    try:
        await kanal.send(mesaj)
        await ctx.send("Mesaj gönderildi!")
    except:
        await ctx.send("Gönderilemedi!")

özlü_sözler = [
    "“Başarı, hazırlık ile fırsatın buluştuğu yerdir.”",
    "“Asla pes etme, büyük şeyler zaman alır.”",
    "“Bugün yaptığın şey yarınını belirler.”",
    "“Kendine inan, gerisi gelir.”"
]

@bot.command(name="özlüsöz")
async def ozlu_soz(ctx):
    await ctx.send(random.choice(özlü_sözler))

# ---------------- KAYIT SİSTEMİ ----------------

@bot.command()
async def kayıt(ctx, isim=None, yaş=None):
    if isim is None or yaş is None:
        return await ctx.send("Doğru kullanım: `!kayıt İsim Yaş`")

    data = kayıt_veri_yükle()
    data[str(ctx.author.id)] = {"isim": isim, "yaş": yaş}
    kayıt_veri_kaydet(data)

    await ctx.send(f"✔ {ctx.author.mention} başarıyla kayıt oldun!")

@bot.command()
async def profil(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    data = kayıt_veri_yükle()

    if str(member.id) not in data:
        return await ctx.send("Bu kullanıcı kayıtlı değil!")

    bilgiler = data[str(member.id)]
    embed = discord.Embed(title=f"{member.name} Profil", color=discord.Color.green())
    embed.add_field(name="İsim", value=bilgiler["isim"], inline=False)
    embed.add_field(name="Yaş", value=bilgiler["yaş"], inline=False)
    await ctx.send(embed=embed)

# ---------------- ROL KONTROL ----------------

def rol_kontrol(ctx, member):
    return ctx.guild.me.top_role > member.top_role

# ---------------- MODERASYON ----------------

@bot.command()
@commands.has_permissions(administrator=True)
async def mute(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send("Bir kullanıcı etiketlemelisin!")
    if not rol_kontrol(ctx, member):
        return await ctx.send("Botun rolü düşük.")

    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if mute_role is None:
        mute_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(mute_role, send_messages=False, speak=False)

    await member.add_roles(mute_role)
    await ctx.send(f"{member.mention} susturuldu!")

@bot.command()
@commands.has_permissions(administrator=True)
async def unmute(ctx, member: discord.Member = None):
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if mute_role in member.roles:
        await member.remove_roles(mute_role)
        await ctx.send(f"{member.mention} susturulması kaldırıldı!")

@bot.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member = None, *, sebep="Yok"):
    if member is None:
        return await ctx.send("Bir kullanıcı etiketlemelisin!")
    if not rol_kontrol(ctx, member):
        return await ctx.send("Botun rolü düşük.")
    await member.kick(reason=sebep)
    await ctx.send(f"{member.mention} sunucudan atıldı!")

@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member = None, *, sebep="Yok"):
    if not rol_kontrol(ctx, member):
        return await ctx.send("Botun rolü düşük.")
    await member.ban(reason=sebep)
    await ctx.send(f"{member.mention} banlandı!")

@bot.command()
@commands.has_permissions(administrator=True)
async def timeout(ctx, member: discord.Member = None, süre: int = 10):
    if not rol_kontrol(ctx, member):
        return await ctx.send("Botun rolü düşük.")
    await member.timeout(discord.utils.utcnow() + discord.timedelta(seconds=süre))
    await ctx.send(f"{member.mention} {süre} saniye timeoutlandı!")

# ---------------- BOT BİLGİ ----------------

@bot.command()
async def botbilgi(ctx):
    embed = discord.Embed(
        title="🤖 Bot Bilgisi",
        color=discord.Color.green()
    )
    embed.add_field(name="Sunucu Sayısı", value=len(bot.guilds), inline=False)
    embed.add_field(name="Ücretsiz Botlar", value="https://discord.gg/ves9nWtD6b", inline=False)
    await ctx.send(embed=embed)

bot.run(TOKEN)
