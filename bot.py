import discord, boto3, config

intents = discord.Intents.all()
intents.messages = True  # Enable message related intents

client = discord.Client(intents=intents)

ec2 = boto3.resource("ec2")

ec2_ids = config.instance_ids

instance_others = ec2.Instance(ec2_ids[0])
instance_osmo = ec2.Instance(ec2_ids[1])


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------------")


@client.event
async def on_message(message):
    if message.author.name == "ec2_control":
        # message from the robot itself, do nothing
        return
    
    my_message = message.content.lower()

    message_split = my_message.split()

    if len(message_split) != 2:
        return await message.channel.send(
            "Invalid command. "
            "Format must be <machine identifier> <desired operation>"
        )

    machine, command = message_split

    if machine == "others":
        instance = instance_others
    elif machine == "osmo":
        instance = instance_osmo
    else:
        instance = None
        return await message.channel.send(
            "Invalid machine identifier. " "Valid identifiers are 'others' and 'osmo'"
        )

    if command == "stop":
        if turnOffInstance(instance=instance):
            await message.channel.send("AWS Instance stopping")
        else:
            await message.channel.send("Error stopping AWS Instance")
    elif command == "start":
        if turnOnInstance(instance=instance):
            await message.channel.send("AWS Instance starting")
        else:
            await message.channel.send("Error starting AWS Instance")
    elif command == "state":
        if getInstanceState(instance=instance):
            await message.channel.send("AWS Instance state is: " + getInstanceState())
    elif command == "reboot":
        if rebootInstance(instance=instance):
            await message.channel.send("AWS Instance rebooting")
        else:
            await message.channel.send("Error rebooting AWS Instance")
    elif command == "test":
        await message.channel.send("I'm alive, don't worry")

    else:
        await message.channel.send(
            "Invalid command. "
            "Valid commands are 'stop', 'start', 'state', 'reboot', 'test'"
        )


def turnOffInstance(instance):
    try:
        instance.stop()
        return True
    except:
        return False


def turnOnInstance(instance):
    try:
        instance.start()
        return True
    except:
        return False


def getInstanceState(instance):
    return instance.state["Name"]


def rebootInstance(instance):
    try:
        instance.reboot()
        return True
    except:
        return False


if __name__ == "__main__":
    client.run(config.discord_key)
