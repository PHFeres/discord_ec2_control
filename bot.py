import discord, boto3, config, sys
from loguru import logger


intents = discord.Intents.all()
intents.messages = True  # Enable message related intents

client = discord.Client(intents=intents)

ec2 = boto3.resource("ec2")

my_instances = config.my_instances


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------------")


@client.event
async def on_message(message):
    if (
        message.author.name == "ec2_control" or 
        message.channel.id != config.my_channel     # only monitors one channel
    ):
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

    instances = {key: ec2.Instance(value) for (key, value) in my_instances.items()}
    instance = instances.get(machine)

    if instance is None:
        return await message.channel.send(
            f"Invalid machine identifier. "
            f"Valid identifiers are {my_instances.keys()}"
        )

    logger.info(f"Valid message received: {message}")

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
        response = getInstanceState(instance=instance)
        if response:
            await message.channel.send("AWS Instance state is: " + response)
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


def configure_loggers(id_file: str):

    # Remove the default handler from the root logger
    logger.remove()

    log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS zz}</green> | <level>{level: <8}</level> | <yellow>Line {line: >4} ({file}):</yellow> <b>{message}</b>"
    logger.add(
        f"debug_file_{id_file}.log",
        level="DEBUG",
        format=log_format,
        colorize=False,
        backtrace=True,
        diagnose=True,
        rotation="1 days",  # Rotate logs every 1 days,
    )
    logger.add(
        f"info_log_{id_file}.log",
        level="INFO",
        format=log_format,
        colorize=False,
        backtrace=True,
        diagnose=True,
        rotation="1 days",
    )

    # no debug logs in terminal
    logger.add(sys.stderr, level="INFO")


if __name__ == "__main__":
    client.run(config.discord_key)
