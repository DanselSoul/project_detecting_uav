import React, { createContext, useContext, useEffect, useState } from "react";

const WebSocketContext = createContext();

export const useWebSocket = () => {
  return useContext(WebSocketContext);
};

export const WebSocketProvider = ({ children }) => {
  const [message, setMessage] = useState(""); // Сообщение о тревоге
  const [alertCamera, setAlertCamera] = useState(null); // Номер камеры, для которой сработала тревога
  const [ws, setWs] = useState(null); // Хранение WebSocket-соединения

  useEffect(() => {
    const websocket = new WebSocket("ws://localhost:8000/ws/alerts");

    websocket.onopen = () => {
      console.log("WebSocket connection opened");
    };

    websocket.onmessage = (event) => {
      const alertMessage = event.data;
      // Добавляем временную метку, чтобы сообщение было уникальным при каждом получении
      const uniqueMessage = alertMessage + "_" + new Date().getTime();
      console.log("Received alert in WebSocketProvider:", uniqueMessage);
      setMessage(uniqueMessage);

      // Извлекаем номер камеры из исходного текста сообщения (без временной метки)
      const match = alertMessage.match(/camera (\d+)/);
      if (match) {
        const camId = parseInt(match[1], 10);
        setAlertCamera(camId);
        console.log("Alert Camera ID:", camId);
      }
    };

    websocket.onclose = () => {
      console.log("WebSocket connection closed");
    };

    websocket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    setWs(websocket);

    return () => {
      if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.close();
      }
    };
  }, []);

  return (
    <WebSocketContext.Provider value={{ ws, message, alertCamera }}>
      {children}
    </WebSocketContext.Provider>
  );
};
