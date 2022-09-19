import discord
from discord.ext import commands, tasks
import json
import fissures
import time
import datetime
import os
bot = commands.Bot(command_prefix='>')
time_now_disc = lambda: datetime.datetime.now() + datetime.timedelta(hours=4)
with open("missions.txt") as mr:
        with open("nodes.txt") as nr:
            missions_dict = json.load(mr)
            nodes_dict = json.load(nr)

tier_dict = {"VoidT1":"Lith", "VoidT2":"Meso", "VoidT3":"Neo", "VoidT4":"Axi", "VoidT5":"Requiem"}
with open("settings.txt") as sr:
    a = sr.readlines()
    token = a[0]
    #channel_id = a[1]

new_token = "MTAyMTE3NDU1MTAzMzQzNDEyMw.GP__9J"
channel_id = 1005561745416392784

@bot.event
async def on_ready():
    print("Fissure bot ready")
    world_state_data = fissures.Fissures().json
    sp_fissures = [x for x in world_state_data["ActiveMissions"] if "Hard" in list(x.keys()) and x["Hard"] == True] #this is automatically sorted by oldest to newest
    with open("mem.txt", "w") as m:
        m.write(json.dumps(sp_fissures))
    new_fissure.start()

@bot.command()
async def spfissures(ctx):
    world_state_data = fissures.Fissures().json
    sp_fissures = [x for x in world_state_data["ActiveMissions"] if "Hard" in list(x.keys()) and x["Hard"] == True] #this is automatically sorted by oldest to newest
    desc = ""
    for fissure in sp_fissures:
        time_left = int(int(fissure["Expiry"]["$date"]["$numberLong"])/1000 - time.time())
        hours = time_left // 3600 
        minutes = time_left // 60
        seconds = time_left % 60 #seconds as in x hours x minutes x seconds format
        time_left_string = ""
        if hours != 0:
            time_left_string = f"{str(hours)}h {str(minutes-60)}m"
        else:
            time_left_string = f"{str(minutes)}m {str(seconds)}s"
        node = nodes_dict[fissure["Node"]]
        mission_type = missions_dict[fissure["MissionType"]]
        tier = tier_dict[fissure["Modifier"]]
        desc += f"**{tier} {mission_type}** on {node} - {str(time_left_string)} Left\n"
    embed = discord.Embed(title="Fissures", description=desc)
    embed.set_footer(text="Bot made by Bioax")
    await ctx.channel.send(embed=embed)
    
@tasks.loop(seconds=15)
async def new_fissure():
    def find_diff_element_new(orig, new):
        diff = []
        for x in new:
            if x not in orig:
                diff.append(x)
        return diff                
    fissure_data = fissures.Fissures().json
    sp_fissures = [x for x in fissure_data["ActiveMissions"] if "Hard" in list(x.keys()) and x["Hard"] == True] #this is automatically sorted by oldest to newest
    with open("mem.txt") as r:
        mem = json.load(r)
    if sp_fissures != mem and len(sp_fissures) >= len(mem):
        new_fissure = find_diff_element_new(mem, sp_fissures)
        try:
            #part 1
            for fissure in new_fissure:
                time_left = int(int(fissure["Expiry"]["$date"]["$numberLong"])/1000 - time.time())
                hours = time_left // 3600 
                minutes = time_left // 60
                seconds = time_left % 60 #seconds as in x hours x minutes x seconds format
                time_left_string = ""
                if hours != 0:
                    time_left_string = f"{str(hours)}h {str(minutes-60)}m"
                else:
                    time_left_string = f"{str(minutes)}m {str(seconds)}s"
                node = nodes_dict[fissure["Node"]]
                mission_type = missions_dict[fissure["MissionType"]]
                tier = tier_dict[fissure["Modifier"]]
                desc = f"**{tier} {mission_type}** on {node} - {str(time_left_string)} Left"
                embed = discord.Embed(title="New Fissure", description=desc)
                embed.set_footer(text="Bot made by Bioax")
                channel = bot.get_channel(channel_id)
                await channel.send(embed=embed)
            with open("mem.txt", "w") as w: 
                print("updated memory")
                w.write(json.dumps(sp_fissures)) #updates the memory
            
            #part 2
            desc = ""
            for fissure in sp_fissures:
                time_left = int(int(fissure["Expiry"]["$date"]["$numberLong"])/1000 - time.time())
                hours = time_left // 3600 
                minutes = time_left // 60
                seconds = time_left % 60 #seconds as in x hours x minutes x seconds format
                time_left_string = ""
                if hours != 0:
                    time_left_string = f"{str(hours)}h {str(minutes-60)}m"
                else:
                    time_left_string = f"{str(minutes)}m {str(seconds)}s"
                node = nodes_dict[fissure["Node"]]
                mission_type = missions_dict[fissure["MissionType"]]
                tier = tier_dict[fissure["Modifier"]]
                desc += f"**{tier} {mission_type}** on {node} - {str(time_left_string)} Left\n"
            embedTwo = discord.Embed(title="Fissures", description=desc)
            embedTwo.set_footer(text="Bot made by Bioax")
            await channel.send(embed=embedTwo)
        except:
            print("ok")
    elif sp_fissures != mem and len(sp_fissures) < len(mem):
        with open("mem.txt", "w") as w: 
            print("updated memory")
            w.write(json.dumps(sp_fissures)) #updates the memory
    else:
        print("checked")


if __name__ == "__main__":
    bot.run(new_token + ".HYKTTLl8uHMsic-Yw-tERliNiNCMf9NDFRAohc")