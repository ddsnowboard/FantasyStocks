$(document).ready(function() {
    // I guess here is as good a place as any to do some design. 
    // So what I'm going to do is first get the name of each
    // StockWidget's value box, from the StockWidgets list
    // that I put in the stockWidget.js file. I'll have variables that hold 
    // the HTML class names of all the things in question, either hard-coded 
    // or with template variables, and I'll use those variables to figure out
    // which stock box is which. Then I'll read the usernames from the user
    // boxes and call the changeURL() methods on the corresponding 
    // StockWidgets with the usernames and floor number as properly-positioned 
    // arguments so that the server will send back the JSON for that user's stocks. 
    // I'll get the floor number from the URL of the trade page.
});
