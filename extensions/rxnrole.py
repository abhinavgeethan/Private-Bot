import asyncio
import discord
from discord.ext import commands
from utils import send_embed
from main import botName,field

class rxnrole(commands.Cog):
    
    def __init__(self,client):
        self.client=client

    async def del_msg_chain(self,msg_chain):
        for m in msg_chain:
            await m.delete()
        return
        
    async def wait_yn(self,ctx,msg_chain,timeout=10):
        try:
            resp,user= await self.client.wait_for('reaction_add',check=lambda resp,user: user==ctx.author and resp.emoji in ['\u2705','\u274c'] and resp.message.channel==ctx.channel,timeout=timeout)
        except asyncio.TimeoutError:
            await ctx.send("Request Timeout.")
            await self.del_msg_chain(msg_chain)
            return -1
        else:
            return resp

    async def wait_msg(self,ctx,msg_chain,timeout=60):
        try:
            resp=await self.client.wait_for('message',check=lambda resp: resp.author==ctx.author and resp.channel==ctx.channel,timeout=timeout)
        except asyncio.TimeoutError:
            await ctx.send("Request Timeout.")
            await self.del_msg_chain(msg_chain)
            return -1
        else:
            return resp

    async def rr_post(self,ctx,em_channel: discord.TextChannel,em_title: str,em_desc: str,em_fields: list,roles: list,role_emojis):
        rr_msg=await send_embed(em_channel,em_title,em_desc,fields=em_fields,thumbnail_url=ctx.guild.icon_url,footer="DBRRE"+str(em_channel.id)[-5:])
        for i in range(len(roles)):
            await rr_msg.add_reaction(role_emojis[i])
        await ctx.send("Reaction Role post sent successfully.")
        return

    async def get_title(self,ctx,msg_chain,heading="Reaction Roles Setup: 1"):
        msg_s1=await send_embed(ctx.channel, heading,"What is this for?\nYour reply will appear as the title for the final message.",footer='This times out in 1 minute.')
        msg_chain.append(msg_s1)
        
        resp=await self.wait_msg(ctx,msg_chain)
        if resp==-1:
            return -1,-1
        elif len(resp.content)>256:
            msg_e1=await ctx.send("The title cannot be longer than 256 characters. Try again.")
            msg_chain.append(msg_e1)
            resp=await self.wait_msg(ctx,msg_chain)
            if resp==-1:
                return
            elif len(resp.content)>256:
                await ctx.send("The title cannot be longer than 256 characters. Try again later.")
                await self.del_msg_chain(msg_chain)
                return
            else:
                em_title=resp.content
                return em_title,msg_chain
        else:
            em_title=resp.content
            return em_title,msg_chain

    async def get_desc(self,ctx,msg_chain,heading="Reaction Roles Setup: 2"):
        em_default_desc="Use the following guide and click on a reaction below to get your role."
        msg_s2=await send_embed(
            ctx.channel,
            heading,
            f"How would you like to describe the process to your members? \n\n To use the default response respond with `default`.\n Default Response: `{em_default_desc}`",
            footer="This times out in 2 minutes."
            )
        msg_chain.append(msg_s2)
        resp=await self.wait_msg(ctx,msg_chain,120)
        if resp==-1:
            return
        elif len(resp.content)>4096:
            msg_e1=await ctx.send("The description cannot be longer than 4096 characters. Try again.")
            msg_chain.append(msg_e1)
            resp=await self.wait_msg(ctx,msg_chain)
            if resp==-1:
                return -1,-1
            elif len(resp.content)>4096:
                await ctx.send("The description cannot be longer than 4096 characters. Try again later.")
                await self.del_msg_chain(msg_chain)
                return -1,-1
            else:
                if (resp.content).lower()=="default":
                    em_desc=em_default_desc
                    return em_desc,msg_chain
                else:
                    em_desc=resp.content
                    return em_desc,msg_chain
        else:
            if (resp.content).lower()=="default":
                em_desc=em_default_desc
                return em_desc,msg_chain
            else:
                em_desc=resp.content
                return em_desc,msg_chain

    async def get_roles(self,ctx,msg_chain,heading="Reaction Roles Setup: 3"):
        msg_s3=await send_embed(
            ctx.channel,
            heading,
            "Enter the roles you would like to give separated by \na **comma followed by a space** ( `, ` ).\n Example: `Role 1, Role 2`",
            footer="This times out in 1 minute."
            )
        msg_chain.append(msg_s3)
        resp=await self.wait_msg(ctx,msg_chain)
        if resp==-1:
            return -1,-1
        raw_roles=resp.content.split(", ")
        roles=[]
        missing_roles=[]
        for role in raw_roles:
            try:
                roles.append(await commands.RoleConverter().convert(ctx,role))
            except commands.RoleNotFound:
                missing_roles.append(role)
        
        if missing_roles:
            msg_e2=await send_embed(
                ctx.channel,
                "Minor Error",
                "The following roles were not found in the server:\n"+ ("\n".join(role for role in missing_roles)) +"\n\nWould you like me to create these new roles?",
                footer="clear"
                )
            await msg_e2.add_reaction('\u2705')
            await msg_e2.add_reaction('\u274c')
            msg_chain.append(msg_e2)
            resp=await self.wait_msg(ctx,msg_chain)
            if resp==-1:
                return -1,-1
            elif resp.emoji=='\u274c':
                await ctx.send("Okay, please create the roles and try again.")
                await self.del_msg_chain(msg_chain)
                return -1,-1
            else:
                for role in missing_roles:
                    new_role=await ctx.guild.create_role(name=role[1:] if role.startswith("@") else role, reason=f"Role created by {botName} for reaction roles as instructed by {ctx.author.name}")
                    await ctx.send(f"Role: `{role}` created.")
                    roles.append(new_role)
        return roles,msg_chain

    async def get_emojis(self,ctx,msg_chain,heading="Reaction Roles Setup: 4"):
        role_emojis=["\U0001f7e5","\U0001f7e6","\U0001f7e7","\U0001f7e8","\U0001f7e9","\U0001f7ea","\U0001f7eb","\U00002b1b","\U00002b1c"]
        return role_emojis,msg_chain
        #Future
        # msg_s4=await send_embed(ctx.channel,heading,"Would you like to use the default emojis?\n Default emojis: "+" ".join(emoji for emoji in role_emojis),footer="clear")
        # await msg_s4.add_reaction('\u2705')
        # await msg_s4.add_reaction('\u274c')
        # msg_chain.append(msg_s4)
        
        # resp=await self.wait_yn(ctx,msg_chain)
        # if resp==-1:
        #     return -1 -1
        # elif resp.emoji=='\u2705':
        #     return role_emojis,msg_chain
        # else:
        #     msg_s4_1=await send_embed(
        #         ctx.channel,
        #         f"{heading}_1",
        #         "Enter the emojis you would like to use separated by **a space** (` `).\n Example: `\u2705 \u274c`",
        #         footer="This times out in 2 minutes."
        #         )
        #     msg_chain.append(msg_s4_1)
        #     resp=await self.wait_msg(ctx,msg_chain,120)
        #     if resp==-1:
        #         return
        #     raw_emojis=resp.content.split(" ")
        #     for i in range(len(raw_emojis)):
        #         role_emojis[i]=raw_emojis[i]
        #     return role_emojis,msg_chain

    async def get_channel(self,ctx,msg_chain,heading="Reaction Roles Setup: 5"):
        msg_s5=await send_embed(ctx.channel,heading,"Which channel should the post go to? \n",footer="This times out in 1 minute.")
        msg_chain.append(msg_s5)
        resp=await self.wait_msg(ctx,msg_chain)
        if resp==-1:
            return -1,-1
        elif not isinstance(resp.content,discord.TextChannel):
            try:
                em_channel=await commands.TextChannelConverter().convert(ctx,resp.content[1:] if resp.content.startswith("#") else resp.content)
                return em_channel,msg_chain
            except commands.ChannelNotFound:
                await ctx.send(f"Channel: {resp.content} was not found.")
                await self.del_msg_chain(msg_chain)
                return -1,-1
        else:
            em_channel=resp.content
            return em_channel,msg_chain

    @commands.command(help="Sets up reaction roles.")
    async def rrsetup(self,ctx):
        msg=await send_embed(ctx.channel,"Reaction Roles Setup","Would you like to set up reaction roles?",footer="This times out in 10 seconds.")
        await msg.add_reaction('\u2705')
        await msg.add_reaction('\u274c')
        msg_chain=[msg]
        resp=await self.wait_yn(ctx,msg_chain)
        if resp==-1:
            return
        elif resp.emoji=='\u274c':
            await ctx.send("Okay.")
            await msg.delete()
            return
        else:
            em_title,msg_chain=await self.get_title(ctx,msg_chain)
            if em_title==-1 or msg_chain==-1:
                return
            em_desc,msg_chain=await self.get_desc(ctx,msg_chain)
            if em_desc==-1 or msg_chain==-1:
                return
            roles,msg_chain=await self.get_roles(ctx,msg_chain)
            if roles==-1 or msg_chain==-1:
                return
            role_emojis,msg_chain=await self.get_emojis(ctx,msg_chain)
            if role_emojis==-1 or msg_chain==-1:
                return
            em_channel,msg_chain=await self.get_channel(ctx,msg_chain)
            if em_channel==-1 or msg_chain==-1:
                return
            em_fields=[]
            for i in range(len(roles)):
                em_fields.append(field(role_emojis[i]+" - "+roles[i].name,"\u200b",inline=False))
            # print(em_fields)
            # print("".join(x.name for x in em_fields))
        
            msg_s6_1=await send_embed(ctx.channel,"Reaction Roles Setup: 6, Review",f"The following is the reaction role post that will be sent to {em_channel.mention}.",footer="clear")
            msg_s6_2=await send_embed(ctx.channel,em_title,em_desc,fields=em_fields,footer="clear",thumbnail_url=ctx.guild.icon)
            msg_s6_3=await send_embed(ctx.channel,"",description="Click \u2705 below to confirm or \u274c to make any changes.",footer="Cancels automatically in 1 minute.")
            await msg_s6_3.add_reaction('\u2705')
            await msg_s6_3.add_reaction('\u274c')
            msg_chain.append(msg_s6_1)
            msg_chain.append(msg_s6_2)
            msg_chain.append(msg_s6_3)
            
            resp=await self.wait_yn(ctx,msg_chain,60)
            if resp==-1:
                return
            elif resp.emoji=='\u2705':
                await self.rr_post(ctx,em_channel,em_title,em_desc,em_fields,roles,role_emojis)
                return
            else:
                #Edit Screen
                msg_s7=await send_embed(
                    ctx.channel,
                    "Reaction Roles Setup: Edit",
                    "Respond with the number of the field which you would like to edit.\n If you'd like to proceed instead type **0**.",
                    footer="This times out in 30 seconds.",
                    fields=[
                        field("1. Destination Channel",f"{em_channel.mention}",False),
                        field("2. Title","`"+em_title+"`",False),
                        field("3. Description","`"+em_desc+"`",False),
                        field("4. Roles and Emojis", "\n".join(x.name for x in em_fields),False)
                    ]
                    )
                # print("".join(x.value for x in em_fields))
                msg_chain.append(msg_s7)
                resp=await self.wait_msg(ctx,msg_chain,30)
                if resp==-1:
                    return
                elif resp.content=='0':
                    await self.rr_post(ctx,em_channel,em_title,em_desc,em_fields,roles,role_emojis)
                elif resp.content=='1':
                    em_channel,msg_chain=await self.get_channel(ctx,msg_chain,heading="Edit Destination Channel")
                    if em_channel==-1 or msg_chain==-1:
                        return
                elif resp.content=='2':
                    em_title,msg_chain=await self.get_title(ctx,msg_chain,"Edit Title")
                    if em_title==-1 or msg_chain==-1:
                        return
                elif resp.content=='3':
                    em_desc,msg_chain=await self.get_desc(ctx,msg_chain,"Edit Description")
                    if em_desc==-1 or msg_chain==-1:
                        return
                elif resp.content=='4':
                    roles,msg_chain=await self.get_roles(ctx,msg_chain,heading="Re-enter Roles")
                    if roles==-1 or msg_chain==-1:
                        return
                    role_emojis,msg_chain=await self.get_emojis(ctx,msg_chain,"Re-assign Emojis")
                    if role_emojis==-1 or msg_chain==-1:
                        return
                    em_fields=[]
                    for i in range(len(roles)):
                        em_fields.append(field(role_emojis[i]+" - "+roles[i].name,"\u200b",inline=False))
                
                msg_s6_1_1=await send_embed(ctx.channel,"Reaction Roles Setup: 6, Review",f"The following is the reaction role post that will be sent to {em_channel.mention}.")
                msg_s6_2_1=await send_embed(ctx.channel,em_title,em_desc,fields=em_fields,footer="clear",thumbnail_url=ctx.guild.icon_url)
                msg_s6_3_1=await send_embed(ctx.channel,"",description="Click \u2705 below to confirm or \u274c to exit.",footer="Exits automatically in 1 minute.")
                await msg_s6_3_1.add_reaction('\u2705')
                await msg_s6_3_1.add_reaction('\u274c')
                msg_chain.append(msg_s6_1_1)
                msg_chain.append(msg_s6_2_1)
                msg_chain.append(msg_s6_3_1)
                resp=await self.wait_yn(ctx,msg_chain,60)
                if resp==-1:
                    return
                elif resp.emoji=='\u2705':
                    await self.rr_post(ctx,em_channel,em_title,em_desc,em_fields,roles,role_emojis)
                    return
                else:
                    return



def setup(client):
    client.add_cog(rxnrole(client))