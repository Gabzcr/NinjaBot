const Discord = require('discord.js');
const bot = new Discord.Client();
var auth = require('./auth.json');

bot.on('ready', () => {
 console.log(`Logged in as ${bot.user.tag}!`);
 });

bot.on('message', msg => {
 if (msg.content.includes(':Ninja:')) {
   msg.delete(5000).catch(console.error);
 }
 if (msg.content.startsWith('!join')) {
   chan_text = msg.content.substring(6,msg.content.length);
   chan_text = chan_text.toLowerCase().replace(/ |'/g, '-');
   chan_text = chan_text.replace()
   chan = msg.guild.channels.find(val => val.name === chan_text);
   if (chan !== null) {
     chan.overwritePermissions(msg.member, {
       SEND_MESSAGES : true,
       VIEW_CHANNEL : true
     })
    .catch(console.error);
    msg.reply('vous avez désormais accès au channel ' + chan_text);
   }
   else {
     msg.reply('je ne connais pas ce channel.');
   }

 }
 });

bot.on('messageUpdate', (msg, new_msg) => {
  if (new_msg.content.includes(':Ninja:')) {
    new_msg.delete(5000).catch(console.error);
  }
})

bot.on('messageReactionAdd', (reaction, user) => {
  if(reaction.emoji.name === "Ninja") {
    setTimeout(function()
    {
      reaction.remove(user).catch(console.error)
    }, 5000);
  }
});

bot.login(process.env.BOT_TOKEN)
