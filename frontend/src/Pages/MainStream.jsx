// MainStream.jsx
import React from "react";
import { useNavigate } from "react-router-dom";
import { useWebSocket } from "../WebSocketProvider/WebSocketProvider";

const BACKEND = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

const cameras = [1,2,3,4].map(i => ({
  id: i,
  name: `Камера ${i}`,
  src: `${BACKEND}/video-feed?cam=${i}`
}));

export default function MainStream({ onLogout }) {
  const navigate = useNavigate();
  const { message, alertCameras } = useWebSocket();

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      {/* шапка */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Потоки с камер</h1>
        <button onClick={onLogout} className="bg-red-500 px-4 py-2 rounded">Выйти</button>
      </div>

      {/* сетка */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-6">
        {cameras.map(cam => {
          const isAlert = alertCameras.includes(cam.id);
          return (
            <div
              key={cam.id}
              onClick={()=>navigate(`/camera/${cam.id}`)}
              className={`cursor-pointer border-4 ${
                isAlert ? "border-red-600" : "border-gray-700"
              } rounded-lg overflow-hidden transition`}
            >
              <img src={cam.src} alt={cam.name}
                   className="w-full h-64 object-cover bg-black" />
              <div className="p-3 text-center bg-gray-800">{cam.name}</div>
            </div>
          );
        })}
      </div>

      {/* снизу */}
      {message && (
        <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2
                        bg-red-600 text-white px-6 py-3 rounded">
          {message}
        </div>
      )}
    </div>
  );
}
