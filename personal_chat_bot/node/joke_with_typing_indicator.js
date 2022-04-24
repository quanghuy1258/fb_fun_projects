const fs = require("fs");
const login = require("facebook-chat-api");

const credential = {appState: JSON.parse(fs.readFileSync('appstate.json', 'utf-8'))}

login(credential, (err, api) => {
    if(err) return console.error(err);

    var someoneID = "000000000000000";

    console.log(someoneID);
    async function loop() {
      while (true) {
        api.sendTypingIndicator(someoneID);
        console.log(Date());
        await new Promise(resolve => setTimeout(resolve, 25000));
      }
    }
    loop();
});
