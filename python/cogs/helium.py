"""This is a cog for a discord.py bot.
It collects informmation about helium miners...
    ├ stats                 Helium stats
    ├ tokensupply           Returns the circulating token supply
    ├ blockheight           Helium blockheight | ISO8601 timestamp or relative time can be used.
    ├ blockstats            Block Stats
    ├ blocks                Retrieves block descriptions
    ├ blockforheight        Block at Height
    ├ blocktrasheight       Get transactions for a block at a given height
    ├ blockathash           Get block descriptor for the given block hash
    ├ blocktranshash        [WIP] Get transactions for a block at a given block hash
    ├ listaccounts          [WIP] Retrieve the current set of known accounts
    ├ accountaddress        Retrieve a specific account record
    ├ hotspotsaccount       Fetches hotspots owned by a given account address
    ├ validatorsaccount     Fetches validators owned by a given account address
    ├ ouisaccount           Fetches OUIs owned by a given account address
    ├ minerdistance         Fetches distance between 2 helium hotspots by animal name.
    └ minername             Helium hotspot data for name
    --
    tosolana                Helium wallet converted to solana
"""

import re
import random
from geopy.distance import geodesic
from discord.ext import commands
from discord import Embed


class Helium(commands.Cog, name='Helium'):
    def __init__(self, client):
        self.client = client
        self.api_base = 'https://api.helium.io'
        self.bones = 100_000_000
        self.hnt_image = 'https://cdn.discordapp.com/attachments/788621973709127693/999838638827380806/hnt.png'
        self.headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'User-Agent': 'Discord python helium bot bar moo oink'
        }

    def locations(city: str):
        """
        maybe create a db with city -> lat -> lon (or see if i can find existing one).
        """
        city_location = {
            'armidale': 'lat=-30.500557&lon=151.5973595',
            'tamworth': 'lat=-31.0929782&lon=150.9235611',
            'kootingal': 'lat=-31.062917&lon=151.0262554',
            'moonbi': 'lat=-30.9514627&lon=150.975929',
            'quirindi': 'lat=-31.4994214&lon=150.5558575',
        }
        return city_location[city]

    # ----------------------------------------------
    # coingecko simple api cog commands
    # ----------------------------------------------
    @commands.group(
        pass_context=True,
        name='helium',
        aliases=['hm', 'h'],
        hidden=True,
        invoke_without_command=True,
    )
    async def helium(self, ctx):
        "Commands to view current information on helium miners"
        await ctx.send_help('helium')

    ##########
    # helium stats
    @helium.command(name='stats', aliases=['stat', 'st'])
    async def helium_stats(self, ctx):
        """
        Helium stats
        GET https://api.helium.io/v1/stats
        Retrieve basic stats for the blockchain such as total token supply, and average block and
        election times over a number of intervals.
        """
        async with self.client.session.get(
            f'{self.api_base}/v1/stats', headers=self.headers
        ) as response:
            data = (await response.json())['data']
            hotspots = data['counts']['hotspots']
            online = data['counts']['hotspots_online']
            online_percent = (hotspots - online)/((hotspots + online) / 2) * 100

            embed = Embed(color=random.randint(0, 0xFFFFFF))
            embed.set_author(
                name='Helium Stats',
                icon_url=self.hnt_image
            )
            embed.add_field(
                name='Token Supply',
                value=data['token_supply'],
                inline=False
            )
            embed.add_field(
                name='Validators',
                value=data['counts']['validators'],
                inline=True
            )
            embed.add_field(
                name='Transactions',
                value=data['counts']['transactions'],
                inline=True
            )
            embed.add_field(
                name='OUIs',
                value=data['counts']['ouis'],
                inline=True
            )
            embed.add_field(
                name='Hotspots Online',
                value=online,
                inline=True
            )
            embed.add_field(
                name='Data Only',
                value=data['counts']['hotspots_dataonly'],
                inline=True
            )
            embed.add_field(
                name='Hotspots',
                value=hotspots,
                inline=True
            )
            embed.add_field(
                name='Countries',
                value=data['counts']['countries'],
                inline=True
            )
            embed.add_field(
                name='Cities',
                value=data['counts']['cities'],
                inline=True
            )
            embed.add_field(
                name='Challenges',
                value=data['counts']['challenges'],
                inline=True
            )
            embed.add_field(
                name='Blocks',
                value=data['counts']['blocks'],
                inline=True
            )
            embed.add_field(
                name='Challenge Counts',
                value=data['challenge_counts']['last_day'],
                inline=True
            )
            embed.add_field(
                name='Online Percent',
                value=f'{round(online_percent, 2)}%',
                inline=True
            )
            return await ctx.send(embed=embed)

    ##########
    # helium token supply
    @helium.command(name='tokensupply', aliases=['supply', 'ts'])
    async def helium_stats_token_supply(self, ctx):
        """
        Current total helium supply
        GET https://api.helium.io/v1/stats/token_supply
        Returns the circulating token supply in either JSON or raw form.
        """
        async with self.client.session.get(
            f'{self.api_base}/v1/stats/token_supply', headers=self.headers
        ) as response:
            data = (await response.json())['data']

            embed = Embed(color=random.randint(0, 0xFFFFFF))
            embed.set_author(
                name='Helium Stats',
                icon_url=self.hnt_image
            )
            embed.add_field(
                name='Token Supply',
                value=data['token_supply'],
                inline=True
            )
            return await ctx.send(embed=embed)

    ##########
    # helium blocks
    @helium.command(name='blockheight', aliases=['block', 'bh'])
    async def helium_blockheight(self, ctx, max_time: str = None):
        """
        Helium blockheight
        GET https://api.helium.io/v1/blocks/height
        If max_time is specified this returns highest block height that was valid
        (but not equal to) the given time.max_time can be given as an ISO8601 timestamp or
        relative time can be used.
        https://api.helium.io/v1/blocks/height?max_time=2022-07-20T23:05:00Z
        """
        if max_time is None:
            async with self.client.session.get(
                f'{self.api_base}/v1/blocks/height', headers=self.headers
            ) as response:
                data = (await response.json())['data']

                embed = Embed(color=random.randint(0, 0xFFFFFF))
                embed.set_author(
                    name='Blockheight',
                    icon_url=self.hnt_image
                )
                embed.add_field(
                    name='Current Block Height',
                    value=data['height'],
                    inline=True
                )
            return await ctx.send(embed=embed)

        async with self.client.session.get(
            f'{self.api_base}/v1/blocks/height?max_time={max_time}', headers=self.headers
        ) as response:
            data = await response.json()

            embed = Embed(color=random.randint(0, 0xFFFFFF))
            embed.set_author(
                name='Blockheight',
                icon_url=self.hnt_image
            )
            embed.add_field(
                name=f'Block Height @ {re.sub(r"(T|Z)", " ", data["meta"]["max_time"])}',
                value=data['data']['height'],
                inline=False
            )
            return await ctx.send(embed=embed)

    ##########
    # helium block stats
    @helium.command(name='blockstats', aliases=['bs'])
    async def helium_blockstats(self, ctx):
        """
        Block Stats
        GET https://api.helium.io/v1/blocks/stats
        """
        async with self.client.session.get(
            f'{self.api_base}/v1/blocks/stats', headers=self.headers
        ) as response:
            data = (await response.json())['data']

            embed = Embed(color=random.randint(0, 0xFFFFFF))
            embed.set_author(
                name='Helium Blocks Stats',
                icon_url=self.hnt_image
            )
            embed.add_field(
                name='Last Month',
                value=f'stddev: {data["last_month"]["stddev"]}\n'
                      + f'Avg: {data["last_month"]["avg"]}',
                inline=False
            )
            embed.add_field(
                name='Last Week',
                value=f'stddev: {data["last_week"]["stddev"]}\n'
                      + f'Avg: {data["last_week"]["avg"]}',
                inline=False
            )
            embed.add_field(
                name='Last Day',
                value=f'stddev: {data["last_day"]["stddev"]}\n'
                      + f'Avg: {data["last_day"]["avg"]}',
                inline=False
            )
            embed.add_field(
                name='Last hour',
                value=f'stddev: {data["last_hour"]["stddev"]}\n'
                      + f'Avg: {data["last_hour"]["avg"]}',
                inline=False
            )
            return await ctx.send(embed=embed)

    ##########
    # helium blocks
    @helium.command(name='blocks')
    async def helium_blocks(self, ctx):
        """
        Block Descriptions
        GET https://api.helium.io/v1/blocks
        Retrieves block descriptions. Blocks descriptions are paged. A cursor field will be in the
        response when more results are available.
        """
        async with self.client.session.get(
            f'{self.api_base}/v1/blocks', headers=self.headers
        ) as response:
            data = await response.json()
            return await ctx.send(str(data)[:2000])

    ##########
    # helium block for height
    @helium.command(name='blockforheight', aliases=['bfh'])
    async def helium_block_for_height(self, ctx, height: int):
        """
        Block at Height
        GET https://api.helium.io/v1/blocks/:height
        Get block descriptor for block at height
        """
        async with self.client.session.get(
            f'{self.api_base}/v1/blocks/{height}', headers=self.headers
        ) as response:
            data = await response.json()
            return await ctx.send(data)

    ##########
    # helium block at height transaction
    @helium.command(name='blocktrasheight', aliases=['bth'])
    async def helium_block_transaction_height(self, ctx, height: int):
        """
        Block at Height Transactions
        GET https://api.helium.io/v1/blocks/:height/transactions
        Get transactions for a block at a given height. The list of returned transactions is paged.
        A cursor field is present if more results are available.
        """
        async with self.client.session.get(
            f'{self.api_base}/v1/blocks/{height}/transactions', headers=self.headers
        ) as response:
            data = await response.json()
            return await ctx.send(data)

    ##########
    # helium block at hash
    @helium.command(name='blockathash', aliases=['bah'])
    async def helium_block_at_hash(self, ctx, hash: str):
        """
        Block at Hash
        GET https://api.helium.io/v1/blocks/hash/:hash
        Get block descriptor for the given block hash.
        """
        async with self.client.session.get(
            f'{self.api_base}/v1/blocks/hash/{hash}', headers=self.headers
        ) as response:
            data = await response.json()
            return await ctx.send(data)

    ##########
    # helium black transaction at hash
    @helium.command(name='blocktranshash', aliases=['btah'])
    async def helium_block_transaction_at_hash(self, ctx, hash: str):
        """
        Block at Hash Transactions
        GET https://api.helium.io/v1/blocks/hash/:hash/transactions
        Get transactions for a block at a given block hash. The list of returned transactions
        is paged.
        A cursor field is present if more results are available.
        """
        async with self.client.session.get(
            f'{self.api_base}/v1/blocks/hash/{hash}/transactions', headers=self.headers
        ) as response:
            data = await response.json()
            return await ctx.send(data)

    ##########
    # helium accounts
    @helium.command(name='listaccounts', aliases=['la'])
    async def helium_list_accounts(self, ctx, limit: int = 2):
        """
        List Accounts [WIP]
        GET https://api.helium.io/v1/accounts
        Retrieve the current set of known accounts. The result is paged. A cursor field is present
        if more results are available.
        Note: The cursor for accounts is valid for a limited time. If you receive a 400 http
        response code for a cursor based request, you will need to start fetching accounts from
        the beginning of the list.

        GET https://api.helium.io/v1/accounts/rich
        GET https://api.helium.io/v1/accounts/rich?limit=:int
        Returns up to 100 of the accounts sorted by highest token balance.
        """
        async with self.client.session.get(
            f'{self.api_base}/v1/accounts/rich?limit={limit}', headers=self.headers
        ) as response:
            data = await response.json()
            return await ctx.send(data)

    ##########
    # helium account for address
    @helium.command(name='accountaddress', aliases=['aa'])
    async def helium_account_for_address(self, ctx, address: str):
        """
        Account for address
        GET https://api.helium.io/v1/accounts/:address
        Retrieve a specific account record. The account details for a record include additional
        speculative nonces that indicate what the expected nonce for the account is for a specific
        balance. Any transactions affecting the given balance type should use an adjusted
        speculative nonce for that balance type.

        For example, when constructing a payment transaction, get the speculative_nonce field for
        the source account and use speculative_nonce + 1 for the new transaction nonce.Currently
        only the speculative_nonce is supported. It indicates the expected nonce for the account
        """
        async with self.client.session.get(
            f'{self.api_base}/v1/accounts/{address}', headers=self.headers
        ) as response:
            data = await response.json()
            return await ctx.send(data)

    ##########
    # helium hotspots for account
    @helium.command(name='hotspotsaccount', aliases=['hfa'])
    async def helium_hotspots_for_account(self, ctx, address: str):
        """
        Hotspots for Account
        GET https://api.helium.io/v1/accounts/:address/hotspots
        Fetches hotspots owned by a given account address.The list of returned hotspots is paged.
        If a cursor field is present more results are available.

        The filter_modes parameter can be used to filter hotspot by how they were added to the
        blockchain. Supported values are full, dataonly, or light. A comma separated list
        (no whitespace) can be used to filter for multiple modes.

        Note: The cursor for accounts is valid for a limited time. If you receive a 400 http
        response code for a cursor
        based request, you will need to start fetching accounts from the beginning of the list.
        """
        async with self.client.session.get(
            f'{self.api_base}/v1/accounts/{address}/hotspots', headers=self.headers
        ) as response:
            data = (await response.json())['data']
            hotspots = [f"[View in explorer]({gw['name']})" for gw in data]

            paginator = commands.Paginator(
                prefix='```',
                suffix='```',
                linesep='\n',
                max_size=2000
            )
            message = None

            all_fields = [' '.join(word.title() for word in gw['name'].split('-')) for gw in data]

            if len(all_fields) <= 25:
                embed = Embed(
                    color=random.randint(0, 0xFFFFFF),
                    description=f'```Hotspots found for this address.\n{address}```',
                )
                embed.set_author(
                    name=f'{len(hotspots)} Helium Hotspots Found',
                    icon_url=self.hnt_image
                )
                [embed.add_field(
                    name=' '.join(word.title() for word in gw['name'].split('-')),
                    value=f'[View in explorer](https://explorer.helium.com/hotspots/{gw["address"]}/activity)',
                    inline=False
                ) for gw in data]
                embed.set_footer(
                    text='Provided By: https://api.helium.io'
                )
                return await ctx.send(embed=embed)
            else:
                for num, line in enumerate(all_fields):
                    paginator.add_line(f'{num+1:3} | {line}')

                for page in paginator.pages:
                    await ctx.send(page)

                paginator.clear()
                return message

    ##########
    # helium validators for account
    @helium.command(name='validatorsaccount', aliases=['vfa'])
    async def validators_for_account(self, ctx, address: str):
        """
        Validators for Account
        GET https://api.helium.io/v1/accounts/:address/validators
        Fetches validators owned by a given account address. The list of returned validators is
        paged. If a cursor field is present more results are available.
        """
        async with self.client.session.get(
            f'{self.api_base}/v1/accounts/{address}/validators', headers=self.headers
        ) as response:
            data = await response.json()
            return await ctx.send(data)

    ##########
    # helium ouis for account
    @helium.command(name='ouisaccount', aliases=['oui'])
    async def helium_ouis_for_account(self, ctx, address: str):
        """
        OUIs for Account
        GET https://api.helium.io/v1/accounts/:address/ouis
        Fetches OUIs owned by a given account address. The list of returned OUIs is paged.
        If a cursor field is present more results are available.
        """
        async with self.client.session.get(
            f'{self.api_base}/v1/accounts/{address}/ouis', headers=self.headers
        ) as response:
            data = await response.json()
            return await ctx.send(data)

    ##########
    # helium hotspots
    @helium.command(name='minername', aliases=['miner', 'hotspot', 'hs'])
    async def helium_miner_name(self, ctx, *words):
        """
        Helium hotspot by name
        GET https://api.helium.io/v1/hotspots/name/:name
        Fetch the hotspots which map to the given 3-word animal name. The name must be all
        lower-case with dashes between the words, e.g. tall-plum-griffin.
        Because of collisions in the Angry Purple Tiger algorithm, the given name might map to
        more than one hotspot.
        """
        gw_name = '-'.join((word.lower() for word in words[:3]))

        async with self.client.session.get(
            f'{self.api_base}/v1/hotspots/name/{gw_name}', headers=self.headers
        ) as response:
            resp = (await response.json())['data']

            if len(resp) == 0:
                embed = Embed(
                    description=f'Hotspot with name ```{" ".join((word.title() for word in words[:3]))}``` not found.',
                    color=random.randint(0, 0xFFFFFF)
                )
                embed.set_author(
                    name='Helium Hotspot Not Found!',
                    icon_url=self.hnt_image
                )
                return await ctx.send(embed=embed)

            embed = Embed(
                title=f'{" ".join((word.title() for word in words[:3]))}',
                url=f'https://explorer.helium.com/hotspots/{resp[0]["address"]}',
            )
            embed.set_author(
                    name='Helium Hotspot Found!',
                    icon_url=self.hnt_image
                )
            embed.add_field(
                name='Location [lat, Lon]',
                value=f'{round(resp[0]["lat"], 4)}, {round(resp[0]["lng"], 4)}',
                inline=False
            )
            embed.add_field(
                name='Date Added',
                value=resp[0]['timestamp_added'][:10],
                inline=True
            )
            embed.add_field(
                name='Status',
                value=resp[0]['status']['online'].title(),
                inline=True
            )
            embed.add_field(
                name='Hotspot Name',
                value=resp[0]['mode'].title(),
                inline=True
            )
            embed.add_field(
                name='Location Hex',
                value=resp[0]['location_hex'],
                inline=True
            )
            embed.add_field(
                name='Location',
                value=resp[0]['location'],
                inline=True
            )
            embed.add_field(
                name='Mode',
                value=resp[0]['mode'],
                inline=True
            )
            embed.add_field(
                name='Block Added',
                value=resp[0]['block_added'],
                inline=True
            )
            embed.add_field(
                name='Miner Address',
                value=resp[0]['address'],
                inline=False
            )
            embed.set_footer(
                text='Provided By: https://api.helium.io'
            )

            return await ctx.send(embed=embed)

    @helium.command(name='minerdistance', aliases=['minerdis', 'md'])
    async def miner_distance(self, ctx, hotspot_1, hotspot_2):
        """
        Helium get 2 x hotspots by name and return the distance between them in Kilometers
        and miles.
        GET https://api.helium.io/v1/hotspots/name/:name
        """
        async with self.client.session.get(
            f'{self.api_base}/v1/hotspots/name/{hotspot_1}', headers=self.headers
        ) as resp1:
            hs1 = (await resp1.json())['data']

            if len(hs1) == 0:
                embed = Embed(
                    description=f'Hotspot with name ```{hotspot_1}``` not found.',
                    color=random.randint(0, 0xFFFFFF)
                )
                embed.set_author(
                    name='Helium Hotspot Not Found!',
                    icon_url=self.hnt_image
                )
                return await ctx.send(embed=embed)

        async with self.client.session.get(
            f'{self.api_base}/v1/hotspots/name/{hotspot_2}', headers=self.headers
        ) as resp2:
            hs2 = (await resp2.json())['data']

            if len(hs2) == 0:
                embed = Embed(
                    description=f'Hotspot with name ```{hotspot_2}``` not found.',
                    color=random.randint(0, 0xFFFFFF)
                )
                embed.set_author(
                    name='Helium Hotspot Not Found!',
                    icon_url=self.hnt_image
                )
                return await ctx.send(embed=embed)

        kms = round(geodesic((hs1[0]["lat"], hs1[0]["lng"]), (hs2[0]["lat"], hs2[0]["lng"])).km, 2)
        mis = round(geodesic((hs1[0]["lat"], hs1[0]["lng"]), (hs2[0]["lat"], hs2[0]["lng"])).mi, 2)

        embed = Embed(
            color=random.randint(0, 0xFFFFFF),
            description=f'{hotspot_1}\nto...\n{hotspot_2}'
        )
        embed.set_author(
            name='Hotspot Distances Generated',
            icon_url=self.hnt_image
        )
        embed.add_field(
            name='Kilometers',
            value=f'{kms:,} km',
            inline=True
        )
        embed.add_field(
            name='Miles',
            value=f'{mis:,} mi',
            inline=True
        )
        return await ctx.send(embed=embed)


    @helium.command(name='tosolana', aliases=['solanaaddress', 'sa'])
    async def wallet_to_solana(self, ctx, wallet_address):
        """
        Helium tool to convert old public wallet address to solana
        GET https://migration.web.helium.io/helium/:helium_address
        """
        async with self.client.session.get(
            f'https://migration.web.helium.io/helium/{wallet_address}', headers=self.headers
        ) as resp:
            sw = (await resp.json())#['solanaAddress']

            if resp.status != 200:
                embed = Embed(
                    description=f'Helium Wallet ```{wallet_address}``` not found.',
                    color=random.randint(0, 0xFFFFFF)
                )
                embed.set_author(
                    name='Helium Wallet Not Found!',
                    icon_url=self.hnt_image
                )
                return await ctx.send(embed=embed)

            embed = Embed(
                description=f'''
                    Helium Wallet ```{wallet_address}```\n
                    Solana Wallet ```{sw["solanaAddress"]}```
                    ''',
                color=random.randint(0, 0xFFFFFF)
            )
            embed.set_author(
                name='Helium Wallet Found!',
                icon_url=self.hnt_image
            )
            return await ctx.send(embed=embed)

    # ----------------------------------------------
    # Cog Tasks
    # ----------------------------------------------


async def setup(client):
    """This is called when the cog is loaded via load_extension"""
    await client.add_cog(Helium(client))
