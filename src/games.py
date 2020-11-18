# Módulo de joguinhos (espero que) inofensivos.

import discord
from random import randint


def eight_ball():
    replies = {
        1: "As I see it, yes.",
        2: "Ask again later.",
        3: "Better not tell you now.",
        4: "Cannot predict now.",
        5: "Concentrate and ask again.",
        6: "Don't count on it.",
        7: "It is certain.",
        8: "It is decidedly so.",
        9: "Most likely.",
        10: "My reply is no.",
        11: "My sources say no.",
        12: "Outlook not so good.",
        13: "Outlook good.",
        14: "Reply hazy, try again.",
        15: "Signs point to yes.",
        16: "Very doubtful.",
        17: "Without a doubt.",
        18: "Yes.",
        19: "Yes - definitely.",
        20: "You may rely on it."
    }
    return replies[randint(1, 20)]
