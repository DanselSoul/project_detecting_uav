import React from "react";
import { useNavigate } from "react-router-dom";
import { useWebSocket } from "../WebSocketProvider/WebSocketProvider";

const cameras = [
  { id: 1, name: "Камера 1", src: "http://localhost:8000/video-feed?cam=1" },
  { id: 2, name: "Камера 2", src: "http://localhost:8000/video-feed?cam=2" },
  { id: 3, name: "Камера 3", src: "http://localhost:8000/video-feed?cam=3" },
  { id: 4, name: "Камера 4", src: "http://localhost:8000/video-feed?cam=4" },
];

export default function MainStream({ onLogout }) {
  const navigate = useNavigate();
  const { message, alertCamera } = useWebSocket();  // Получаем информацию о камере с тревогой

  console.log("alertCamera in MainStream:", alertCamera);  // Логируем значение alertCamera
  console.log("message in MainStream:", message);  // Логируем сообщение

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Потоки с камер</h1>
        <button
          onClick={onLogout}
          className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
        >
          Выйти
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-6">
        {cameras.map((cam) => (
          <div
            key={cam.id}
            className={`cursor-pointer border-2 ${alertCamera === cam.id ? "border-red-600" : "border-gray-700"} rounded-lg overflow-hidden hover:shadow-xl transition duration-200`}
            onClick={() => navigate(`/camera/${cam.id}`)}
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

      {message && (
        <div className="alert-box text-red-500 font-bold mt-4">
          {message}
        </div>
      )}
    </div>
  );
}
