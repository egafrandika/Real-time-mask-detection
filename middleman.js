const { io } = require("socket.io-client");

const express = require("express");
const app = express();
const http = require("http");
const server = http.createServer(app);
const { Server } = require("socket.io");
const ioServer = new Server(server);
const socketio = io("ws://192.168.1.4:5000/", { transports: ["websocket"] });

ioServer.on("connection", (socket) => {
  console.log("raspberry pi connected to middleman");
});

server.listen(3000, () => {});

socketio.on("gateStatus", (data) => {
  if (data === "close") {
    ioServer.emit("gateStatus", "close");
  } else if (data === "open") {
    ioServer.emit("gateStatus", "open");
  }
});

socketio.on("connect", () => {
  socketio.emit("server");
  console.log("middleman connected to server");
});
