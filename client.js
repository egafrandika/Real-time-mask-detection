const { Boards, Led, LCD } = require("johnny-five");
const { io } = require("socket.io-client");

const socketio = io("ws://192.168.1.4:5000/", { transports: ["websocket"] });

const boards = new Boards([
  { id: "pi", io: new RaspiIO() },
  { id: "uno", repl: false },
]);

let devices = {};

boards.on("ready", () => {
  const lcd = new LCD({
    controller: "PCF8574T",
    board: boards.byId("uno"),
  });

  devices.lcd = lcd;

  boards.on("exit", () => {
    lcd.clear();
  });
});

const gateOpen = async () => {
  const { lcd } = await devices;
  lcd.useChar("heart");
  lcd.cursor(0, 0);
  lcd.print("Silahkan masuk :heart:");
};

const gateClose = async () => {
  const { lcd } = await devices;
  lcd.useChar("x");
  lcd.cursor(0, 0);
  lcd.print("Dilarang masuk! :x:");
};

socketio.on("gateStatus", (data) => {
  if (data === "close") {
    gateClose();
  } else if (data === "open") {
    gateOpen();
  }
});

socketio.on("connect", () => {
  socketio.emit("server");
  console.log("middleman connected to server");
});
