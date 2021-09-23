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

**- Commande roll :** permet de lancer un ou plusieurs dés, et d'effectuer des opérations basiques sur les résultats.
```
![r ou roll] (max/min) ([nb de dés (par défaut : 1)])[d ou D][valeur des dés](+ ou - valeur à ajouter/soustraire)
```

Exemple: `!roll d6`,  `!r max 2d20`, `!r d12 + 4` ou encore `!roll 3d10 - 2 min`
Note : la valeur à ajouter/soustraire est appliquée à tous les dés en cas de lancers multiples.

La légende raconte que cette commande serait truffée d'easter eggs... 


**- Commande poll (ou sondage):** permet de créer un sondage par emojis réactions, en plaçant automatiquement les emojis concernés par le sondage en réaction au message.
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

NinjaBot s'occupe alors de mettre les réactions appropriées afin que les sondés n'aient pas à chercher eux-même dans la liste des émojis celui qui correspond à leur opinion.

**-Commande check :** permet de lancer à intervalles réguliers des contrôles de sécurité émotionelle automatisés. Le bot demande l'état émotionnel des joueurs (":ok_hand: :grey_question: ") et prépare les trois émoji réponse en réaction (:thumbsup: :pinching_hand: :thumbsdown: ). En cas de réponse moyenne ou négative, ou d'absence de réponse s'il un rôle à surveiller est spécifié, le bot le notifie au MJ en MP.
```
!check [intervalle entre 2 checks en minutes]m ([durée totale en heures]h) (@rôle_à_surveiller)
```
Exemple : `!check @Bot 25m 1h` ou `!check 5m`.
Pour arrêter les contrôles automatiques, utilisez la commande `!stop` (sans argument).

**- Commande help :** cette doc en moins bien faite (et en Anglais).

**- Divers :** 
 --> NinjaBot efface tous les emojis Ninja au bout de 5 à 15 secondes, effaçant au passage les messages qui le contiennent.
--> NinjaBot réagit par :hatched_chick: à un message de la forme `Bonjour Mada[a+]me`
--> NinjaBot répond avec une emoji Ninja quand il est tagué (y compris par un `@everyone`)
