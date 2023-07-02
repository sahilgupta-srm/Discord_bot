import discord
from discord.ext import commands
from collections import defaultdict
import tracemalloc
import asyncio
import random
import heapq


tracemalloc.start()


intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content=True

bot = commands.Bot(command_prefix=['#'], intents=intents)

uri='https://sahilgupta-srm.github.io/'

DEFAULT_XP = 0
DEFAULT_LVL = 0
DEFAULT_WARN=0
DEFAULT_LIST=''
XP_MULTIPLIER = 1
temp=None
id=[778838412089884692]



users = defaultdict(lambda: {"xp": DEFAULT_XP, "level": DEFAULT_LVL,"multiplier":XP_MULTIPLIER,"warn": DEFAULT_WARN ,"reason":DEFAULT_LIST})
tuple_words=()

def xp_for_level(level):
    return 100+(50*level)


@bot.event
async def on_message(message):
    
    if message.author.bot:
        return
    ctx=await bot.get_context(message)
    for word in tuple_words:
        if(word in message.content.lower()):
            await message.channel.send(f"{message.author.mention} , you have a balcklisted word in your message.")
            await message.delete()
            await warn(ctx,message.author,f"Bad word ({word})")
            return
    if bot.user in message.mentions and len(message.content) == len(bot.user.mention):
        await ctx.send("Hi! My prefix is #")
    
    user_id = message.author.id
    users[user_id]["xp"] =users[user_id]["xp"]+10*users[user_id]['multiplier']
    old_level = users[user_id]["level"]
    new_level = old_level
    while users[user_id]["xp"] >= xp_for_level(new_level):
        new_level += 1
    if new_level != old_level:
        users[user_id]["level"] = new_level
        users[user_id]['xp']=0
        await message.channel.send(f"{message.author.name} has leveled up to level {new_level}!")
        if(users[user_id]["level"]%10==0 and users[user_id]["level"] not in temp):
            temp.append(users[user_id]["level"])
            id.append(users[user_id][user_id])
            await ctx.send(f'You are eligible to use roll command as you reached {users[user_id]["level"]} first')
    await bot.process_commands(message)

@bot.command()
@commands.check(lambda ctx:ctx.author.guild_permissions.administrator)
async def blacklist(ctx, name):
    try:
        #name=(name)
        global tuple_words
        tuple_words=tuple_words+(name ,)
        await ctx.send(f"Added {name} to blacklisted words")
    except:
        await ctx.send("Please printt")
 
    

@bot.command()
@commands.check(lambda ctx:ctx.author.guild_permissions.administrator)
async def warn(ctx,member:discord.Member,*args):
        reason=' '.join(args)
        if(reason==' '):
            try:
                await ctx.send("State the reson for warn")
                msg=await bot.wait_for('message',check=lambda user:user.author.id==member.id,timeout=30)
                reason=msg.content
            except asyncio.TimeoutError:
                await ctx.send("Timed out. Please try again.")
                return
        id=member.id
        users[id]["warn"]=users[id]["warn"]+1
        a=users[id]["warn"]
        await ctx.send(f"{member.name} has been successfully warned , the user currently has {a} active.")
        warn=users[id]["warn"]
        users[id]["reason"]+=f"{warn}.{reason}\n"
        try:
            await member.send(f"You've been warned in{member.guild.name}.Reason: {reason}")
        except:
            return    
   

@bot.command()
@commands.check(lambda ctx:ctx.author.guild_permissions.administrator)
async def warnings(ctx,member:discord.Member=None):
    if member is None:
        member=ctx.author
    if(users[member.id]["warn"]==0):
        await ctx.send("No active warns")
        return
    else:
         b = users[member.id]["reason"]
         await ctx.send(b)
        
@bot.command()
@commands.check(lambda ctx: ctx.author.guild_permissions.administrator)
async def remove_warn(ctx,number:int,member:discord.Member=None):
    if member is None:
        member=ctx.author
    id=member.id
    line=users[id]["reason"].split('\n')
    for i in range(len(line)):
        line[i]=line[i][2:]
    if 1<=number<=len(line):
        line.pop(number-1)
    enumerated_parts = [(i, part) for i, part in enumerate(line, start=1)]
    users[id]["reason"]=''
    for index, part in enumerated_parts:
        users[id]["reason"]+=(f"{index}.{part}\n")
    k=len(users[id]["reason"])
    users[id]["reason"]=users[id]["reason"][:k-4]
    a=users[id]["reason"]
    await ctx.send(f"Successfully removed warning {number}. Remaining warnings are\n{a}")
    return

@bot.command()
async def roll(ctx):
    if(ctx.author.id not in id):
        await ctx.send("You are not eligible to use this command")
        return
    a=random.randint(5,10)
    id.remove(ctx.author.id)
    await ctx.send(f"You won {a} tickets{ctx.author.mention}. Ping:<@778838412089884692>")



@bot.command()
async def stats(ctx, member: discord.Member=None):
    
    if member is None:
        member = ctx.author
    embed = discord.Embed(title=f"{member.name}'s stats", description="", color=discord.Color.blue())
    
    user_id = member.id
    xp = users[user_id]["xp"]
    level = users[user_id]["level"]
    multiplier=users[user_id]["multiplier"]
    embed.add_field(name=f"{member.name} is level {level} with {int(xp)} XP.\nMultiplier is :{multiplier}",value='',inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def top(ctx):
    guild=ctx.guild
    sorted_users = heapq.nlargest(10, users.items(), key=lambda x: (x[1]["level"], x[1]["xp"]))
    embed = discord.Embed(title=f"Top Users for {guild.name}", description="Top members of the server", color=discord.Color.red())
    
    for i, (user_id, data) in enumerate(sorted_users):
       
        member = await bot.fetch_user(int(user_id))
        if (users[user_id]["xp"]==0 and users[user_id]["level"]==0):
            continue
        embed.add_field(name='',value=f"{i+1}. {member.mention}  {data['level']} level ",inline=False)
    await ctx.send(embed=embed)

@bot.command()
@commands.check(lambda ctx:ctx.author.guild_permissions.administrator)
async def set_multiplier(ctx, multiplier: float ,user: discord.Member=None ):
    try:
        if user is None:
            user=ctx.author
        users[user.id]["multiplier"]=multiplier
        await ctx.send(f"XP multiplier set to {multiplier} for user {user.name}.")
    except KeyError:
        await ctx.send("Wrongly used")


@bot.command()
@commands.check(lambda ctx:ctx.author.guild_permissions.administrator)
async def reset_levels(ctx):
    for user_id,i in users.items():
            i["xp"]=DEFAULT_XP
            i["level"]=DEFAULT_LVL
            i["multiplier"]=XP_MULTIPLIER
    await ctx.send("All levels have been reset")

@bot.command()
@commands.check(lambda ctx:ctx.author.guild_permissions.administrator)
async def reset_level(ctx,member:discord.Member):
    user_id=member.id
    users[user_id]['level']=DEFAULT_LVL
    users[user_id]['xp']=DEFAULT_XP
    users[user_id]['multiplier']=XP_MULTIPLIER
    await ctx.send(f"{member.name} level has been set to 0")

@bot.command()
@commands.check(lambda ctx:ctx.author.guild_permissions.administrator)
async def set_level(ctx , level: int , member:discord.Member=None):
            if member is None:
                member=ctx.author
            user_id=member.id
            users[user_id]['level']=level
            
            await ctx.send(f"{member.name} level has been set to {level}")

@bot.command()
@commands.check(lambda ctx:ctx.author.guild_permissions.administrator)
async def prefix(ctx,a:str):
    if(a in bot.command_prefix):
        await ctx.send("Already exists")
    bot.command_prefix.append(a)
    await ctx.send(f"Successfully added bot's prefix to {a}")

@bot.command()
@commands.check(lambda ctx:ctx.author.guild_permissions.administrator)
async def remove_prefix(ctx,a:str):
    if(a=='#'):
        await ctx.send("Cannot remove # prefix")
        return
    if a not in bot.command_prefix:
        await ctx.send("That prefix does not exist")
        return
    bot.command_prefix.remove(a)
    await ctx.send(f"Successfully removed {a} prefix")

bot.run('')
