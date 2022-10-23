import discord
from discord.ext import commands, tasks
import json
from fissures import *
import time
import datetime
import os
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='>', intents=intents)
time_now_disc = lambda: datetime.datetime.now() + datetime.timedelta(hours=4)
with open("missions.txt") as mr:
        with open("nodes.txt") as nr:
            missions_dict = json.load(mr)
            nodes_dict = json.load(nr)

tier_dict = {"VoidT1":"Lith", "VoidT2":"Meso", "VoidT3":"Neo", "VoidT4":"Axi", "VoidT5":"Requiem"}
token = os.getenv("DISCORD_TOKEN")

@bot.event
async def on_ready():
    print("Fissure bot ready")
    world_state_data = Fissures().json
    sp_fissures = [x for x in world_state_data["ActiveMissions"] if "Hard" in list(x.keys()) and x["Hard"] == True] #this is automatically sorted by oldest to newest
    with open("mem.txt", "w") as m:
        m.write(json.dumps(sp_fissures))
    new_fissure.start()

@bot.command()
async def price(ctx, *, item):
    i = MarketItem(item)
    if i.valid == True:
        embed = discord.Embed(title=f"{item.title()}", description=f"**Platinum:** {str(i.plat)} \n**Volume:** {str(i.volume)}", 
        timestamp=time_now_disc(), color=discord.Color.green())
        embed.set_footer(text="Prices are pulled from warframe.market")
        await ctx.channel.send(embed=embed)
    else:
        embed = discord.Embed(title="Error", description="Item not found", timestamp=time_now_disc(), color=discord.Colour.red())
        await ctx.channel.send(embed=embed)
        
@bot.command()
async def drops(ctx, *, item):
    i = ItemDrop(item)
    if not i.item_found:
        await ctx.channel.send("Item not found")
        return
    embed = discord.Embed(title=f"Drop locations related to: *{item}*", timestamp=time_now_disc())
    for x in i.item_drops:
        embed.add_field(name=x["item"], value=f"Place: {x['place']} \n Chance: {str(x['chance'])}% ({x['rarity']})", inline=(False if len(i.item_drops) <= 6 else True))
    await ctx.channel.send(embed=embed)

@bot.command()
async def spfissures(ctx):
    world_state_data = Fissures().json
    sp_fissures = [x for x in world_state_data["ActiveMissions"] if "Hard" in list(x.keys()) and x["Hard"] == True] #this is automatically sorted by oldest to newest
    desc = ""
    for fissure in sp_fissures:
        expiry = int(int(fissure["Expiry"]["$date"]["$numberLong"])/1000)
        node = nodes_dict[fissure["Node"]]
        mission_type = missions_dict[fissure["MissionType"]]
        tier = tier_dict[fissure["Modifier"]]
        desc += f"**{tier} {mission_type}** on {node} - Ends <t:{str(expiry)}:R>\n"
    embed = discord.Embed(title="Fissures", description=desc)
    embed.set_footer(text="Bot made by Bioax")
    await ctx.channel.send(embed=embed)

@tasks.loop(seconds=15)
async def new_fissure():
    channel_id = int(os.getenv("CHANNEL_ID"))
    disruption_role_id = int(os.getenv("DISRUPTION_ID"))
    survival_role_id = int(os.getenv("SURVIVAL_ID"))
    def find_diff_element_new(orig, new):
        diff = [x for x in new if x not in orig]
        return diff                
    fissure_data = Fissures().json
    sp_fissures = [x for x in fissure_data["ActiveMissions"] if "Hard" in list(x.keys()) and x["Hard"] == True] #this is automatically sorted by oldest to newest
    with open("mem.txt") as r:
        mem = json.load(r)
    if sp_fissures != mem and len(sp_fissures) >= len(mem):
        new_fissure = find_diff_element_new(mem, sp_fissures)
        channel = bot.get_channel(channel_id)
        try:
            #part 1
            for fissure in new_fissure:
                expiry = int(int(fissure["Expiry"]["$date"]["$numberLong"])/1000)
                node = nodes_dict[fissure["Node"]]
                mission_type = missions_dict[fissure["MissionType"]]
                tier = tier_dict[fissure["Modifier"]]
                desc = f"**{tier} {mission_type}** on {node} - Ends <t:{str(expiry)}:R>"
                if mission_type == "Survival":
                    survival_ping = await channel.send(f"<@&{str(survival_role_id)}>")
                    await survival_ping.delete()
                    desc += f"\n<@&{str(survival_role_id)}>"
                elif mission_type == "Disruption":
                    disruption_ping = await channel.send(f"<@&{str(disruption_role_id)}>")
                    await disruption_ping.delete()
                    desc += f"\n<@&{str(disruption_role_id)}>"
                embed = discord.Embed(title="New Fissure", description=desc)
                embed.set_footer(text="Bot made by Bioax")
                await channel.send(embed=embed)
            with open("mem.txt", "w") as w: 
                print("updated memory")
                w.write(json.dumps(sp_fissures)) #updates the memory
            
            #part 2 message that lists everything
            desc = ""
            for fissure in sp_fissures:
                expiry = int(int(fissure["Expiry"]["$date"]["$numberLong"])/1000)
                node = nodes_dict[fissure["Node"]]
                mission_type = missions_dict[fissure["MissionType"]]
                tier = tier_dict[fissure["Modifier"]]
                desc += f"**{tier} {mission_type}** on {node} - Ends <t:{str(expiry)}:R>\n"
            embedTwo = discord.Embed(title="Current Fissures", description=desc)
            embedTwo.set_footer(text="Bot made by Bioax")
            await channel.send(embed=embedTwo)
        except Exception as e:
            print(e)
    elif sp_fissures != mem and len(sp_fissures) < len(mem):
        with open("mem.txt", "w") as w: 
            print("updated memory")
            w.write(json.dumps(sp_fissures)) #updates the memory
    else:
        print("checked")


if __name__ == "__main__":
    bot.run("MTAwNTk4MDEzMjQyNDU2MDY1MA.GfMgSh.pLCzYa4tw-SNteY_p0Exs0u7B_oVu-A2y5GgVo")