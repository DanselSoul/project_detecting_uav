import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useWebSocket } from "../WebSocketProvider/WebSocketProvider";

export default function SingleCamera() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { message, alertCamera } = useWebSocket(); // Получаем сообщение и номер камеры из контекста

  const [isDroneConfirmed, setIsDroneConfirmed] = useState(null); // Результат действия пользователя
  const [showAlert, setShowAlert] = useState(false); // Флаг показа окна предупреждения
  const [consecutiveFrames, setConsecutiveFrames] = useState(0); // Счётчик сообщений
  const [isObjectDetected, setIsObjectDetected] = useState(false); // Флаг срабатывания детекции

  // При каждом новом сообщении, если уведомление касается текущей камеры, увеличиваем счётчик
  useEffect(() => {
    const cameraId = parseInt(id, 10);
    if (alertCamera === cameraId && message) {
      setConsecutiveFrames((prev) => prev + 1);
    } else {
      setConsecutiveFrames(0);
      setIsObjectDetected(false);
    }
  }, [message, alertCamera, id]);

  // Если число подряд полученных сообщений превышает порог – показываем окно
  useEffect(() => {
    if (consecutiveFrames >= 5 && !isObjectDetected) {
      setShowAlert(true);
      setIsObjectDetected(true);
    }
  }, [consecutiveFrames, isObjectDetected]);

  // Обработчик кнопки подтверждения или отклонения детекции
  const handleConfirmation = async (confirmation) => {
    try {
      await fetch("http://localhost:8000/alert/detection", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ cam: parseInt(id, 10), detected: confirmation }),
      });
      // После успешной отправки сбрасываем уведомления для этой камеры
      setIsDroneConfirmed(confirmation);
      setShowAlert(false);
      setConsecutiveFrames(0);
      setIsObjectDetected(false);
    } catch (error) {
      console.error("Ошибка отправки данных на сервер:", error);
    }
  };

  return (
    <div className="p-4">
      <button
        onClick={() => navigate(-1)}
        className="mb-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Назад
      </button>

      <h1 className="text-xl font-bold mb-4">Камера #{id}</h1>
      <img
        src={`http://localhost:8000/video-feed?cam=${id}`}
        alt={`Камера ${id}`}
        className="w-full border rounded"
      />

      {/* Показываем окно подтверждения, когда набежало достаточное число уведомлений */}
      {showAlert && isDroneConfirmed === null && (
        <div className="alert-box bg-red-500 text-white p-4 rounded mt-4">
          <p>{message}</p>
          <div className="mt-4">
            <button
              onClick={() => handleConfirmation(true)}
              className="bg-green-500 text-white px-4 py-2 rounded mr-2"
            >
              Дрон обнаружен
            </button>
            <button
              onClick={() => handleConfirmation(false)}
              className="bg-red-500 text-white px-4 py-2 rounded"
            >
              Нет
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
