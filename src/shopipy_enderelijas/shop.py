"""
Copyright (C) 2024  enderelijas

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.
"""

import dataclasses
import discord
from dataclasses import dataclass
from typing import Any, Coroutine, List, Optional, Callable, Union

class Shop():
    """
    Represents a shop.

    Attributes:
        title (str): The title of the shop.
        currency (str): The currency used in the shop.
        footer (str, optional): The footer text of the shop. Defaults to None.
        description (str, optional): The description of the shop. Defaults to None.
    """

    def __init__(self, title: str, currency: str, footer: str = None, description: str = None):
        self.title = title
        self.description = description
        self.footer = footer
        self.currency = currency

class ShopPage(discord.ui.View):
    """
    Represents a shop page in a Discord bot.

    Args:
        shop (Shop): The shop object associated with the page.
        title (str): The title of the shop page.
        description (str): The description of the shop page.
        items (Union[List['ShopItem'], List['ShopCategory']]): The list of items or categories to display on the shop page.
        footer (str, optional): The footer text for the shop page. Defaults to None.
        on_select (Callable[[discord.Interaction], None], optional): The callback function to be called when an item is selected. Defaults to None.
        timeout (float, optional): The timeout duration for the shop page. Defaults to None.
    """

    def __init__(self, shop: Shop, title: str, description: str, items: Union[List['ShopItem'], List['ShopCategory']], footer: str = None, on_select: Callable[[discord.Interaction], None] = None, timeout: float = None):
        super().__init__(timeout=timeout)
        
        self.shop = shop
        self.title = title
        self.items = items
        self.description = description
        self.footer = footer
        self.embed = self.__create_embed()

        if isinstance(items[0], ShopCategory):
            self.add_item(CategorySelector(self.items))
        else:
            self.add_item(ItemSelector(self.items, on_select))

    def __create_embed(self) -> discord.Embed:
        """
        Creates and returns a discord.Embed object representing the shop page.

        Returns:
            discord.Embed: The embed object representing the shop page.
        """
        embed = discord.Embed(title=f'{self.title} | {self.shop.title}', description=self.description)
        for item in self.items:
            if isinstance(item, ShopCategory):
                embed.add_field(
                    name=f'{item.icon if item.icon else ""} {item.name}',
                    value=item.description if item.description else "",
                    inline=False
                )
            elif isinstance(item, ShopItem):
                embed.add_field(
                    name=f'{item.icon if item.icon else ""} {item.name} | `{item.price:,d}` {self.shop.currency}',
                    value=f'*{item.description}*\n{(len(item.description) + 1) * "-"}\n' + "\n".join(map(lambda x: '> ' + x, item.fields)),
                    inline=False
                )
        embed.set_footer(text=self.footer)
        
        return embed

class BackButton(discord.ui.Button):
    def __init__(self, nav_handler: 'NavigationHandler'):
        super().__init__(label="Back", custom_id="back_button")
        self.nav_handler = nav_handler
    
    async def callback(self, interaction: discord.Interaction):
        page = self.nav_handler.go_back()

        await interaction.response.edit_message(embed=page.embed, view=page)

class NavigationHandler():
    """
    A class that handles navigation between shop pages.

    Attributes:
        to_page (ShopPage): The page to navigate to.
        from_page (ShopPage): The page to navigate from.
    """

    def __init__(self, to_page: ShopPage, from_page: ShopPage):
        self.to_page = to_page
        self.from_page = from_page

    def navigate(self) -> ShopPage:
        """
        Navigates to the specified page.

        Returns:
            ShopPage: The page that was navigated to.
        """
        if not [child for child in self.to_page.children if isinstance(child, BackButton)]:
            self.to_page.add_item(BackButton(self))

        return self.to_page
    
    def go_back(self) -> ShopPage:
        """
        Navigates back to the previous page.

        Returns:
            ShopPage: The page that was navigated back to.
        """
        return self.from_page

class CategorySelector(discord.ui.Select):
    def __init__(self, categories: List['ShopCategory']):
        self.categories = categories
        options = [discord.SelectOption(label=category.name, value=category.id, emoji=category.icon) for category in self.categories]
        super().__init__(placeholder="Select a category", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction) -> None:
        selected_category = [category for category in self.categories if category.id == self.values[0]][0]
        
        if not selected_category:
            raise ValueError(f'No category found with ID:{self.values[0]}')
        
        nav_handler = NavigationHandler(from_page=self.view, to_page=selected_category.navigate_to)
        
        page = nav_handler.navigate()

        await interaction.response.edit_message(embed=page.embed, view=page)
        
class ItemSelector(discord.ui.Select):
    def __init__(self, items: List['ShopItem'], on_select: Callable[[discord.Interaction, 'ShopItem'], None] = None):
        self.items = items
        options = [discord.SelectOption(label=item.name, value=item.id, emoji=item.icon) for item in self.items]
        self.on_select = on_select if on_select is not None else self.on_select_default
        super().__init__(placeholder="Select an item...", min_values=1, max_values=1, options=options)
    
    async def on_select_default(self, interaction: discord.Interaction, item: 'ShopItem'):
        await interaction.response.send_message(f'Succesfully purchased {item.name}')

    async def callback(self, interaction: discord.Interaction) -> None:
        selected_item = [item for item in self.items if item.id == self.values[0]][0]
        
        await self.on_select(interaction=interaction, item=selected_item)
                
@dataclass
class ShopItem:
    """Represents an item in a shop.

    Attributes:
        id (str): The unique identifier of the item.
        name (str): The name of the item.
        description (str): The description of the item.
        price (int): The price of the item.
        category_id (str): The category ID of the item.
        icon (Optional[str], optional): The icon of the item. Defaults to None.
        fields (List[str], optional): The additional fields of the item. Defaults to an empty list.
    """
    id: str
    name: str
    description: str
    price: int
    category_id: str
    icon: Optional[str] = None
    fields: List[str] = dataclasses.field(default_factory=list)

@dataclass
class ShopCategory:
    """
    Represents a category in a shop.

    Attributes:
        id (str): The unique identifier of the category.
        name (str): The name of the category.
        navigate_to (ShopPage): The page to navigate to when the category is selected.
        description (Optional[str]): An optional description of the category.
        icon (Optional[str]): An optional icon for the category.
    """
    id: str
    name: str
    navigate_to: ShopPage
    description: Optional[str] = None
    icon: Optional[str] = None
