# Shopi-py
A simple utility package for building all sorts of shops with [discord.py]('https://github.com/Rapptz/discord.py') API wrapper.

**Note: proper documentation and README will be added soon.**
## Quickstart
### 1. Import the required packages
```python
import discord
from discord.ext import commands
from shopipy import Shop, ShopPage, ShopItem
```
### 2. Create a simple bot client (for more info please refer to [this]('https://discordpy.readthedocs.io/en/latest/quickstart.html'))
```python
client = commands.client(prefix="PREFIX_HERE")

@client.event
async def on_ready():
    print("All shops online!")

client.run("BOT_TOKEN_HERE")
```
### 3. Create the command
```python
@client.command()
async def shop(ctx):
    # define global information for the shop
    shop = Shop(
        title = "Grocery Store",
        currency = "$"
    )

    # define items for the shop
    cereals = [
        ShopItem(
            id = "rice_krispies",
            name = "Rice Krispies",
            description = "Rice Krispies is a light and crispy breakfast cereal made from toasted rice",
            price = 10,
            category_id = "cereal"
        ),
        ShopItem(
            id = "lucky_charms",
            name = "Lucky Charms",
            description = "Lucky Charms is a colorful breakfast cereal featuring frosted oats and marshmallow shapes, each representing a different magical charm",
            price = 20,
            category_id = "cereal"
        ),
    ]

    # define shop page for the items
    cereal_page = ShopPage(
        shop = shop,
        title = "Cereals",
        items = cereals,
        description = "A collection of our finest oats and wheat",
        footer = "The cake is a lie..."
    )

    # send a message containing the shop 
    await ctx.send(embed = cereal_page.embed, view = cereal_page)
```
