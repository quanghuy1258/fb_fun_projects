const fs = require("fs");
const login = require("facebook-chat-api");

const credential = {appState: JSON.parse(fs.readFileSync('appstate.json', 'utf-8'))}

login(credential, (err, api) => {
    if(err) return console.error(err);

    var currentUserID = api.getCurrentUserID();
    var msg = {body: "Hello World!"};

    console.log(currentUserID);
    console.log(msg);
    api.sendMessage(msg, currentUserID);
});
