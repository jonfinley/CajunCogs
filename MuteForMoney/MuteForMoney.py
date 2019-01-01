import discord
from redbot.core import commands, checks, Config


class MuteForMoney(commands.Cog):
    """Voice channel mutes for virtual currency"""
    def __init__(self):
        super().__init__()
        self.config = Config.get_conf(self, identifier=8008135)
        self.task = None
        default_guild = {
            "users": {},
            "moneyPerMin": 0,
            "currency": "USD"
        }
        self.config.register_guild(**default_guild)

    @commands.group()
    @commands.guild_only()
    @checks.admin_or_permissions(manage_roles=True)
    async def mfm(self, ctx: commands.Context):
        """Main Commands"""
        pass

    @commands.guild_only()
    @checks.admin_or_permissions(manage_roles=True)
    @mfm.command()
    async def start(self, ctx):
        """Start event"""
        if not self.task:
            self.task = ctx.bot.loop.create_task('placeholder')
            await ctx.send("Event started!")
        else:
            await ctx.send('Event already running')

    @commands.guild_only()
    @checks.admin_or_permissions(manage_roles=True)
    @mfm.command()
    async def stop(self, ctx):
        """Stop event"""
        if self.task:
            self.task.cancel()
            self.task = None
            await ctx.send("Event Ended!")
        else:
            await ctx.send("Event not currently running")

    @commands.guild_only()
    @checks.admin_or_permissions(manage_roles=True)
    @mfm.command()
    async def reset(self, ctx):
        """Reset all balances"""
        async with self.config.guild(ctx.guild).users() as users:
            for user, stats in users.items():
                stats["balance"] = 0
            await ctx.send("All balances reset to 0")

    @commands.command()
    @commands.guild_only()
    async def balance(self, ctx, member: discord.Member):
        """Get balance for member"""
        async with self.config.guild(ctx.guild).users() as users:
            if users.get(member.id):
                currency = await self.config.guild(ctx.guild).currency()
                money_per_min = await self.config.guild(ctx.guild).moneyPerMin()
                balance = users[member.id]['balance']
                pre = f"{member.name} has a {balance} {currency} balance\n"
                minutes_left = abs(balance / money_per_min)
                if balance >= 0:
                    statement = pre + f"They are safe for {minutes_left} minutes"
                else:
                    statement = pre + f"You can continue enjoying their sweet silence for {minutes_left} minutes"
                await ctx.send(statement)
            else:
                await ctx.send(f"{member.name} has not participated in the event")

    # Backend Functions
    async def create_user(self, ctx, member: discord.Member):
        user = {
            "balance": 0
        }
        async with self.config.guild(ctx.guild).users() as users:
            users[member.id] = user

