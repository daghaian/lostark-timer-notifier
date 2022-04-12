from discord_webhook import DiscordWebhook, DiscordEmbed

WEBHOOK_URL = "https://discord.com/api/webhooks/564165764098031617/Jvf-E67KWisFute-lABqSBMY3L2PGmF8xBbSeo0vMWBrlYH-Rv32K1PhFsKQKrordzLW"


class DiscordNotification:
    def __init__(self):
        self._webhook = DiscordWebhook(url=WEBHOOK_URL)

    def notify(self, event, minutes, seconds):
        embed = DiscordEmbed(
            title='New Event', color='03b2f8')
        embed.set_timestamp()
        embed.set_thumbnail(url="{}{}".format(
            "https://lostarkcodex.com/icons/", event.event_icon))

        embed.set_author(name='Lost Ark Event Bot',
                         icon_url='https://cdn2.steamgriddb.com/file/sgdb-cdn/icon_thumb/d77314b5c23c087d9b5ed587e88800d2.png')
        embed.add_embed_field(name='Name', value=event.event_name)
        embed.add_embed_field(name='Item Level', value=event.event_ilevel)
        embed.add_embed_field(
            name='Time Till Start', value="{} minute(s) and {} second(s)".format(minutes, seconds))

        self._webhook.add_embed(embed)
        return self._webhook.execute()
