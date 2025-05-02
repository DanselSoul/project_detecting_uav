import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

export default function SingleCamera() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [detection, setDetection] = useState(null); // {cam, detId}
  const [showToast, setShowToast] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/alerts?cam=${id}`);
    ws.onmessage = (e) => {
      const [cam, detId] = e.data.split("|").map(Number);
      setDetection({ cam, detId });
      setShowToast(true);
    };
    ws.onclose = () => console.log("WS closed");
    return () => ws.close();
  }, [id]);

  const respond = async (valid) => {
    await fetch("http://localhost:8000/validate", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ detection_id: detection.detId, validated: valid })
    });
    setShowToast(false);
  };

  return (
    <div className="p-4 relative">
      <button
        onClick={() => navigate(-1)}
        className="mb-4 px-4 py-2 bg-blue-500 text-white rounded"
      >Назад</button>

      <h1 className="text-xl font-bold mb-4">Камера #{id}</h1>
      <img
        src={`http://localhost:8000/video-feed?cam=${id}`}
        alt={`Камера ${id}`}
        className="w-full border rounded"
      />

      {showToast && (
        <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 bg-white bg-opacity-90 p-4 rounded shadow-lg flex items-center space-x-4">
          <span className="font-medium">Дрон обнаружен на камере #{id}</span>
          <button
            onClick={() => respond(true)}
            className="px-3 py-1 bg-green-500 text-white rounded"
          >Подтвердить</button>
          <button
            onClick={() => respond(false)}
            className="px-3 py-1 bg-red-500 text-white rounded"
          >Отклонить</button>
        </div>
      )}
    </div>
  );
}
