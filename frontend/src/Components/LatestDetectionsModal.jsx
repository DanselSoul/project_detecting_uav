import React, { useEffect, useState } from "react";
import { useWebSocket } from "../WebSocketProvider/WebSocketProvider";

export default function LatestDetectionsModal({ visible, onClose }) {
  const [data, setData] = useState([]);
  const { alarms } = useWebSocket();

  // Fetch latest 100 detections when modal opens
  useEffect(() => {
    if (!visible) return;
    const fetchDetections = async () => {
      try {
        const res = await fetch("http://localhost:8000/detections?limit=100");
        if (!res.ok) throw new Error("Не удалось получить данные");
        const json = await res.json();
        setData(json);
      } catch (e) {
        console.error("LatestDetectionsModal fetch error:", e);
      }
    };
    fetchDetections();
  }, [visible]);

  // Automatically close modal when any alarm arrives
  useEffect(() => {
    if (visible && alarms.length > 0) {
      onClose();
    }
  }, [alarms, visible, onClose]);

  if (!visible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div className="bg-white bg-opacity-90 text-black rounded-lg shadow-lg p-6 w-3/4 max-h-[80vh] overflow-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Последние 100 обнаружений</h2>
          <button
            className="text-gray-600 hover:text-gray-800"
            onClick={onClose}
          >
            ✕
          </button>
        </div>
        {data.length === 0 ? (
          <p className="text-gray-500">Нет обнаружений.</p>
        ) : (
          <ul className="space-y-2">
            {data.map((item, idx) => (
              <li key={idx} className="border-b pb-1">
                <span className="font-medium">Камера {item.camera}</span>, объект <span className="font-semibold">{item.track_id}</span>, время <span className="text-sm">{new Date(item.timestamp).toLocaleString()}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
