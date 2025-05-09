import React, { createContext, useContext, useEffect, useState } from "react";

const WSContext = createContext();
export const useWebSocket = () => useContext(WSContext);

export function WebSocketProvider({ children }) {
  const [message, setMessage] = useState("");
  const [alertMap, setAlertMap] = useState({});

  useEffect(() => {
    const socket = new WebSocket(`ws://localhost:8000/ws/alerts`);

    // При подключении запрашиваем текущие активные тревоги
    fetch("http://localhost:8000/active-alerts")
      .then((res) => res.json())
      .then((initial) => {
        console.log("[WS] Initial alerts:", initial);
        setAlertMap(initial);
      });

    socket.onopen = () => {
      console.log("[WS] Connected to /ws/alerts");
    };

    socket.onmessage = (e) => {
      console.log("[WS] Message received:", e.data);
      setMessage(e.data);

      const match = e.data.match(/camera (\d+): track (\d+) detected/);
      if (match) {
        const cam = Number(match[1]);
        const tid = Number(match[2]);

        setAlertMap((prev) => {
          const current = prev[cam] || [];
          const updated = current.includes(tid) ? current : [...current, tid];
          return { ...prev, [cam]: updated };
        });
      }
    };

    socket.onerror = (err) => {
      console.error("[WS] Error:", err);
    };

    socket.onclose = () => {
      console.warn("[WS] Connection closed");
    };

    return () => {
      socket.close();
    };
  }, []);

  const clearTrack = (cam, trackId) => {
    setAlertMap((prev) => ({
      ...prev,
      [cam]: (prev[cam] || []).filter((t) => t !== trackId),
    }));
    setMessage("");
  };

  return (
    <WSContext.Provider value={{ message, alertMap, clearTrack }}>
      {children}
    </WSContext.Provider>
  );
}
