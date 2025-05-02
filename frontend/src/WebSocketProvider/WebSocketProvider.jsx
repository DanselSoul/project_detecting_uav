// WebSocketProvider.jsx
import React, { createContext, useContext, useEffect, useState } from "react";
import { useParams } from "react-router-dom";

const WebSocketContext = createContext();
export const useWebSocket = () => useContext(WebSocketContext);

export const WebSocketProvider = ({ children, cameraId: propCameraId }) => {
  const routeParams = useParams();
  const camId = propCameraId || routeParams.id || "1";

  const [message, setMessage] = useState("");
  const [alertCameras, setAlertCameras] = useState([]);  // теперь массив
  const [ws, setWs] = useState(null);

  useEffect(() => {
    const websocket = new WebSocket(`ws://localhost:8000/ws/alerts?cam=${camId}`);

    websocket.onopen = () => console.log("WS open for cam", camId);

    websocket.onmessage = (e) => {
      let obj;
      try { obj = JSON.parse(e.data); }
      catch { return console.warn("WS не JSON:", e.data); }

      const cams = obj.alerts || [];
      setMessage(`Обнаружено на камерах: ${cams.join(", ")}`);
      setAlertCameras(cams);
    };

    websocket.onclose = () => console.log("WS closed for cam", camId);
    websocket.onerror = (err) => console.error("WS error", err);

    setWs(websocket);
    return () => { if (websocket.readyState===WebSocket.OPEN) websocket.close(); };
  }, [camId]);

  return <WebSocketContext.Provider value={{ ws, message, alertCameras }}>
    {children}
  </WebSocketContext.Provider>;
};
