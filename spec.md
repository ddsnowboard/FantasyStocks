#Fantasy Stocks Spec
######Will Koster
=========
Any good spec has to have scenarios for who will use the product, otherwise they might have a CueCat, so here they are. 

Scenarios
==========
Scenario 1: Thomas is a high-school student who is not interested in sports, but wants to be able to have a similar communal experience to the one offered by fantasy sports. He and his friends have a fantasy stocks floor (league) and they trade during the day. They have heated debates as to which stocks will go up or down and who should accept or deny what trades.

Scenario 2: Mike is a financial professional who watches the stock market constantly as part of his job. He is an expert and would like to invest himself, but his company and/or the SEC forbid him from doing so. Mike and all of his stock-trader friends make a floor and make ridiculous and risky trades that they could never make in real life, living vicariously through their usernames.

Nongoals:
========
+ There will be no money system. There will be points, but you can't trade them for anything. It's just a number. Some might say "No one will play if you can't trade in your points for anything!" They have not played any mobile games recently.
+ There will not be any mobile apps in this specific repository. Maybe I'll get to an android verison one of these days, but not an iOS version because I don't have a Mac to program on.

###Overview
+ Base Page
  + Homepage (index.html)
  + Login page
    + Dashboard
    + Trade Page
      + Received Trade Page
    + Other User page
    + Create Floor Page
    + Join Floor Page
+ Epilogue: The Game

###Base Page

The page whence every other page will descend, both in a design and technical sense, is the "Base Page." At this point, all it defines is the navigation bar. The navigation bar will be grey, with "Fantasy Stocks" on the left side, and a button on the right side, with a black border on its left. The button will be changable by the pages that inherit it, but it will default to saying "How it works" and linking to a page that explains how the site works.

>For an image, see any of the mockups in this spec.  

###Homepage

The homepage will be dominated by a login box, with a username box and a password box, and a submit button below them. Beside the submit button, somewhere in that box, there will be a "Forgot password" link. Beside those will be a box that is used to register, with a username box, a password box, and another password box for confirmation.
The theory behind this page is that it is really, really simple. The easier it is to sign up, the idea goes, the more people will do it. 

Here is a mockup of the design.
![Image of homepage design](specResources/homepageDesign.png "Homepage")
[Here is more explanation of the design](specResources/homepage.png "Homepage")

Both enter buttons only act on their respective boxes. If you fill in one box, then the other, whichever button you click will only send information from its box. If you put in the wrong username or password, it will kick you back to the login page with an angry red message and the username pre-populated with whatever you put in if and only if that username already exists. If it doesn't exist, it will say that no username exists and give you a set of empty boxes. 

###Dashboard

The dashboard will have a few main parts. On the left side, there will be vertically stacked tabs that show the names of all the floors that you are on. If you click on one, it will select and the rest of the page will change to show the things happening on that floor.

>Technical note: The tabs will work by JavaScript, not with links like most of the rest of the site. All the JavaScript will be written by Django on the back-end and given to the client as a great big string, so there will be no fancy JavaScript formatting needed; just tell it to replace a huge string with a different huge string. Easy.  

Below that there will be a stock-board looking part which will list off all the stocks are being played on that floor and some information about them (price, change that day, points that day, owner, etc.). If you click on any of the stocks, a little javascript bubble will pop up asking if you want to trade for that stock, and if you say yes the trade page will come up with the owner of that stock and the stock pre-populated. Next to that will be a leaderboard which lists out all the other people on your floor in order of how many points they have, with their score next to them. You can click on any player and it will take you to their other player page.

Below that, there will be a trade inbox. It will also change with the changes of the floor tabs. At the top, there are two tabs: "Received Trades" and "Sent Trades". The tabs will be colored just like the tabs for the floor, and they will also be controlled with JavaScript and all rendered from the server on page load. There will be horizontal bars, similar to how emails are displayed in the inbox in Gmail, holding each trade. The trades will be displayed thus: first, the name of the other participant in the trade (you'll know what the other person's role is by which tab you're in). After that will be the date that the trade was sent, and maybe some other stuff. If you click somewhere on the trade, it will take you to the Received Trade page, where you can accept, deny, or counter the trade.  

NB: This image is no longer accurate. It does not include the recent changes regarding the showing of multiple floors, and the removal of the chat box for the sake of simplicity, nor does it include the trades inbox at the bottom.
![Image of dashboard design](specResources/dashboardDesign.png "Dashboard")

###Trade Page

Design Mockup:

![Image of trade page design](specResources/tradePageDesign.png "Trade Page")

If you click on a stock from the dashboard, or go to a player's page and click "trade", you will come to the trade page. It will have two nearly identical sides. Each side will have a box for a name, with a regular text box that has a real-time suggestions dropdown, just like the Gmail address box. 

>Technical Note: Although the original spec complains about the complexity of this a bunch, I have since wrapped all that complexity into a nice package called StockChoiceField. 

The left side top box will always be the same:
>\[Your Username\] (You)

The right side will 99 times out of 100 be pre-populated. If you come from the dashboard, it will be have the name of the person who owns the stock you clicked on. If you come from someone else's player page, it will be populated by the name of the player from whose page you came and no stocks. If you click on a stock on the ticker that is owned by no one, it will be populated with "Floor" (the game equivalent of free-agency).

>Note that you need to go to the trade page to get free agents because you have a limited number of stocks, so in order to get another one, you may have to drop one. I also wanted to keep the idea of trading in the player's mind so that they are more likely to do it in the future, since it is such an important part of the design of this game. If I can manage it, I should make a little counter of how many stocks you have and how many you can have on this page so you know.

If and only if you come from your own player page will it be blank. You will be able to type in a name or "Floor" and it will be filled in automatically.

>Technical Note: I made a new Widget for player picking, similar to the one for picking stocks, but simpler. 

Right below that box on both sides will be the place where you will list the stocks to trade. It will be equal in width to the name boxes, which together will comprise about 70-75% of the screen, and the height will be 40-50% of the screen. Below each box will me a non-moving text box for you to type into. It will say "Type in a symbol or name" as default, but it will turn blank if you click it. If you clicked on a stock on the dashboard to get to this page, the right lower box, which lists stocks that you wish to receive in the trade, will be pre-populated with that stock, although you can add more. When you type in a stock, a suggestions dropdown will come down to suggest stocks for you. When you press enter to select a stock from the dropdown, it will fill it in.

The items in the list of stocks will have rounded corners, the company logo on the left, followed by the full name, followed by the stock symbol in parenthesis. The box will turn red on mouseover, and clicking will delete the stock. If you put in more stocks than will fit, the box will expand. You should be able to search by either symbol or full name. Both sides will have this functionality.

In between the banks of boxes there will be some sort of nice arrow image, probably two greenish arrows, one going each way. Finally, there will be a "Send" button in the traditional style below and with its right side lined up with the right side of the right bank of boxes.

###Received Trade Page

>Technical Note: Make sure you include the parameters for this page when you are writing the template for it. You should probably just have one base template for every page, and this and the Trade Page will be the same template, with the difference being made up in the data that I pass to it.

This will be aesthetically nearly identical to the Trade Page except the "Send" button will be replaced with an "Accept" button, and next to that will be a "Counter-Offer" button, which will take you to a trade page pre-populated with the stocks that were in the trade before, along with the proper names, for you to edit and then send back. If you type in a company name into any of the boxes, it will add to the list just like it would on the trade page.

###Other User Page

![Image of Other User Page](specResources/otherPlayer.png "Other Player")

In the top left corner there will be the avatar of the user. Next to that there will be their name, their username, the date they joined, and a motto or something, maybe a description. Something that they wrote, basically.

Below that there will be a table. On the left hand side there will be a list of all the floors that the person is a member of. You can click on one and it will select and next to it it will list the stocks they have on that floor next to their price and how they have been doing. The clicking will be handled in JavaScript. When you click, there will be a visual change in the background, similar to the above image. I can't get this to look good in paint.net, but the right hand table should have lines delineating the rows and in between the name and the numbers, in the middle. If you click on a stock, you will go to the Trade Page, and the stock, your name, and their name will be pre-populated. Below all the stocks will be a "Propose a trade" button, which you can also click to go to a trade page with their name and your name pre-populated.
>Make sure that there is some sort of feedback that says that clicking on the stock will take you somewhere else. It could get really annoying really quick if there's not. 

###Create Floor Page

There will be two sections. The first ("People") one will dictate whether the floor will be private or public, the limit to how big it can be, and how many stocks each person can have. It should warn you if you set it up such that too many stocks will be necessary. Second ("Stocks") will be the available stocks. It will be a vertical list with real-time suggestions just like the trade page, but here all stocks will be available to choose, not just available ones or ones already on the floor. If a stock is chosen that isn't in the database yet, when the floor is created, we will add it and start tracking it, completely unbeknownst to the user. I am using just a big JSON string that has every stock on every big exchange in the United States for searching. It's really fast. There will also be a dropdown menu in this division that selects the floor's policy on adding new stocks. There will be "closed", where you can't add new stocks at all, "permissive", where the owner of the floor can allow or deny the entrance of new stocks, or "open", where the whole stock market is available. At the bottom there will be a submit button. If you click the submit button and there aren't enough stocks at the beginning to have enough for everyone to fill their quota, it will warn you. Of course, this will never happen if the floor is "open". If the floor is set to "permissive", you can ignore it or not. If it is "closed", you have to add stocks until everyone can fill their quota. After you click submit and everything is in order, it will take you to your dashboard.

###Join Floor Page

The Join Floor page will be pretty simple: in the middle, there will be a real-time search box, with dropdown suggestions similar to the ones in other parts of the site, that will let you have your pick of public floors and private floors open to you. There will also be a link near the top to create your own floor. 

###Epilogue: The Game

When you first sign up, you get the option to either make a new Floor or join an existing one. If you make a new one, you pick the name and whether it is public or private. You also pick how many stocks everyone gets. 
>About how many stocks should everyone get? I guess I could just leave it up to the owner, but I should probably include some guidance. Maybe beta testing will tell me some things. 

If the floor is private, you have to invite people to join. If it is public, anyone can join and play. On the player page there will be "Join Floor" button. 
Once you're on a floor, you wait for the draft. At the draft, everyone gets to pick stocks just like in a normal draft. After the draft, you just watch how they do. You can trade with anyone at any time, or with the "free agent pool". 

Scores will be calculated by percentages and previous performance so that big-name stocks that always are rising are underpowered and making risky decisions is rewarded. The exact equation will be figured later, but it is important to note its goals: make risky bets on small or falling stocks more appealing and make sitting on big names with guaranteed gains less appealing to make the game more interesting and differentiate it from just watching the real stock market. For example, betting on Palm right before the Pre came out and winning would net many times more points than betting on Google, even if they both rise by the same percentage, because Palm was on a cold streak. 


