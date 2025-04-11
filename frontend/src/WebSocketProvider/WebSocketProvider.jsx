import React, { createContext, useContext, useEffect, useState } from "react";
import { useParams } from "react-router-dom";

const WebSocketContext = createContext();

export const useWebSocket = () => useContext(WebSocketContext);

export const WebSocketProvider = ({ children, cameraId: propCameraId }) => {
  const routeParams = useParams();
  // Если передан проп, используем его; если нет – пытаемся взять из параметров маршрута, иначе используем "1"
  const camId = propCameraId || (routeParams.id ? routeParams.id : "1");
  console.log("WebSocketProvider: using camera id =", camId);

  const [message, setMessage] = useState("");
  const [alertCamera, setAlertCamera] = useState(null);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    const wsUrl = `ws://localhost:8000/ws/alerts?cam=${camId}`;
    const websocket = new WebSocket(wsUrl);

    websocket.onopen = () => {
      console.log("WebSocket connection opened for camera", camId);
    };

    websocket.onmessage = (event) => {
      const alertMessage = event.data;
      const uniqueMessage = alertMessage + "_" + new Date().getTime();
      console.log("Received alert:", uniqueMessage);
      setMessage(uniqueMessage);

      // Извлекаем номер камеры из сообщения
      const match = alertMessage.match(/camera (\d+)/);
      if (match) {
        const receivedCamId = parseInt(match[1], 10);
        setAlertCamera(receivedCamId);
        console.log("Alert Camera ID:", receivedCamId);
      }
    };

    websocket.onclose = () => {
      console.log("WebSocket connection closed for camera", camId);
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
  }, [camId]);

  return (
    <WebSocketContext.Provider value={{ ws, message, alertCamera }}>
      {children}
    </WebSocketContext.Provider>
  );
};
