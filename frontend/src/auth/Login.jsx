import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
          const res = await fetch("http://localhost:8000/auth/login", {
            method: "POST",
            headers: {
              "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams({
              grant_type: "password",   // ← вот это поле обязательно
              username,
              password,
            }),
          });
      if (!res.ok) {
        alert("Ошибка авторизации");
        return;
      }
      const data = await res.json();
      // Вот тут мы берём токен из поля data.access_token
      const accessToken = data.access_token;
      // сохраняем его, чтобы потом добавлять в headers защищённых запросов
      localStorage.setItem("token", accessToken);
      // переходим на главную
      navigate("/");
    } catch (err) {
      console.error("Login error:", err);
      alert("Ошибка сети");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900 text-white">
      <form onSubmit={handleSubmit} className="bg-gray-800 p-6 rounded shadow-md">
        <h1 className="text-2xl mb-4">Войти</h1>
        <label className="block mb-2">
          Логин
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="mt-1 block w-full p-2 rounded bg-gray-700"
            required
          />
        </label>
        <label className="block mb-4">
          Пароль
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 block w-full p-2 rounded bg-gray-700"
            required
          />
        </label>
        <button
          type="submit"
          className="w-full bg-blue-600 hover:bg-blue-500 py-2 rounded text-white"
        >
          Войти
        </button>
      </form>
    </div>
  );
}
