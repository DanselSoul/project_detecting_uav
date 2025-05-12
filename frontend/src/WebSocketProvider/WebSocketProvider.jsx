import React, { createContext, useContext, useEffect, useRef, useState } from "react";

const WebSocketContext = createContext();
export const useWebSocket = () => useContext(WebSocketContext);

export const WebSocketProvider = ({ children }) => {
  const [alertMap, setAlertMap] = useState({});\
  const [alarms, setAlarms] = useState(new Set());   
  const ws = useRef(null);
  const isConnected = useRef(false);

  const connectWebSocket = () => {
    if (isConnected.current) return;

    console.log("[WebSocket] Connecting...");
    ws.current = new WebSocket("ws://localhost:8000/ws/alerts");
    isConnected.current = true;

    ws.current.onopen = () => {
      console.log("[WebSocket] Connected");
    };

    ws.current.onmessage = (event) => {
      console.log("[WebSocket] Received:", event.data);
      const match = event.data.match(/camera (\d+): track (\d+)/);
      if (!match) return;

      const cam = parseInt(match[1]);
      const trackId = parseInt(match[2]);

      setAlertMap((prev) => {
        const updated = structuredClone(prev);
        if (!updated[cam]) updated[cam] = [];
        if (!updated[cam].includes(trackId)) {
          updated[cam].push(trackId);
        }
        return updated;
      });
    };

    ws.current.onclose = () => {
      console.warn("[WebSocket] Disconnected. Reconnecting in 1s...");
      isConnected.current = false;
      setTimeout(connectWebSocket, 1000);
    };

    ws.current.onerror = (err) => {
      console.error("[WebSocket] Error:", err);
      ws.current.close();
    };
  };

  useEffect(() => {
    connectWebSocket();
    return () => {
      ws.current?.close();
      isConnected.current = false;
    };
  }, []);

  const clearTrack = (camId, trackId) => {
    setAlertMap((prev) => {
      const updated = { ...prev };
      updated[camId] = updated[camId]?.filter((tid) => tid !== trackId);
      if (!updated[camId]?.length) delete updated[camId];
      return updated;
    });
  };

  return (
    <WebSocketContext.Provider value={{ alertMap, clearTrack }}>
      {children}
    </WebSocketContext.Provider>
  );
};
