import random
import re

def easter_eggs(content):
    res = None
    if ":Ninja:" in content:
        res = "Rejoins-moi, camarade <:Ninja:541390402104852485> !"
    elif content.lower() == "easter egg":
        res = "il n'y a aucun easter egg ici :innocent:."
    elif content.lower() == "uranie puffin" or content.lower() == "uranie":
        res = "je ne me permettrais pas de lancer Mlle Puffin !"
    elif content.lower() == "dreyfus":
        res = "la question ne sera pas posée !"
    elif content.lower() == "crocell":
        file = open("crocell_jokes.txt", "r")
        l = file.read().split("\n\n")
        index = random.randint(0,len(l) - 1)
        res = l[index]
        file.close()
    elif "!r" in content or "!roll" in content:
        res = "(i) la première règle de la récursion est (i)."
    elif content == "666":
        res = "vous avez obtenu un **666**."
    elif content == "42":
        res = "vous avez obtenu **la Réponse**."
    else:
        c2 = re.split("d|D", content)
        try:
            if c2[0] == '':
                nb_of_dices = 1
            else:
                nb_of_dices = int(c2[0])
            value_of_dices = int(c2[1])
        except:
            return(None)
        if nb_of_dices != 1:
            return(None)
        if value_of_dices == 666:
            res = "vous avez obtenu un **666**."
        elif value_of_dices == 42:
            res = "vous avez obtenu **la Réponse**."
    return(res)
