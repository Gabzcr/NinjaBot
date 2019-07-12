# NinjaBot

This is a discord bot for the needs of the "Quatrième Etage", a group of French LARP players.

# Fonctionnement du bot

**- Commande join :** permet de rejoindre un salon.
```
!join [nom de la murder]
```
Exemple : `!join professeur layton et l'île de soay`.

Le bot reconnaît les salons même si les accents ne sont pas les bons (ex : `!join hotel du grand nord` ou `!join joyeux nôêl` sont des noms de salon valides).

Le bot peut répondre à plusieurs demandes en une seule fois, dans un même message (l'exemple suivant sera reconnu) :
```
!join L'Affaire Dreyfus, l'Odieuse Vérité
!join Avant l'Aube
!join Bord de Ciel
```
Le bot efface tous les messages contenant une commande `join` ou une réponse à une commande `join` au bout de cinq minutes.

**- Commande leave :** permet de quitter un salon.
Cette commande fonctionne de la même façon que la commande join.
Note : les permissions redeviennent celles du salon par défaut pour l'utilisateur.

**- Commande roll :** permet de lancer un ou plusieurs dés.
```
![r ou roll] [nb de dés (par défaut : 1)][d ou D][valeur des dés]
```
Exemple: `!roll d6` ou `!r 2d20`.

La légende raconte que cette commande serait truffée d'easter eggs...

**- Commande poll (ou sondage):** permet de créer un sondage d'opinion par réactions à un message de sondage.
```
![poll ou sondage] [message contenant les emojis à reporter en réaction]
(ou sur des lignes séparées après la commande:)
[1-9 ou A-Z ou a-Z][. ou - ou ␣][Proposition]
...
```
Exemple : 
```
!poll Choisissez une réponse:
1. La réponse 1.
B- La réponse B.
:emoji_quelconque: La réponse emoji
```

NinjaBot s'occupe alors de préremplir le message avec les réactions appropriées afin que les sondés n'aient pas à chercher eux-même dans la liste des émojis celui qui correspond à leur opinion.

**- Commande help :** cette doc en moins bien faite (et en Anglais).
