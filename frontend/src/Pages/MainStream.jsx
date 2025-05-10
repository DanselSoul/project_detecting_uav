import React from "react";
import { useNavigate } from "react-router-dom";
import { useWebSocket } from "../WebSocketProvider/WebSocketProvider";
import Header from "../Components/Header";

const cameras = [1, 2, 3, 4].map((i) => ({
  id: i,
  name: `Камера ${i}`,
  src: `http://localhost:8000/video-feed?cam=${i}`,
}));

export default function MainStream({ onLogout }) {
  const navigate = useNavigate();
  const { alertMap } = useWebSocket();

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Header onLogout={onLogout} />

      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">Потоки с камер</h1>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          {cameras.map((cam) => (
            <div
              key={cam.id}
              onClick={() => navigate(`/camera/${cam.id}`)}
              className={`cursor-pointer rounded-lg overflow-hidden transition
               border-4 ${
                 alertMap[cam.id]?.length
                   ? "border-red-600"
                   : "border-gray-700"
               }`}
            >
              <img
                src={cam.src}
                alt={cam.name}
                className="w-full h-64 object-cover bg-black"
              />
              <div className="p-3 text-center bg-gray-800">{cam.name}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
