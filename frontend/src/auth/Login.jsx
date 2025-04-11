
import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    const res = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
          username,
          password
        })
      });

    if (res.ok) {
      const data = await res.json();
      onLogin(data.access_token);
      navigate("/");
    } else {
      alert("Ошибка авторизации");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4 p-10">
      <input placeholder="Логин" value={username} onChange={(e) => setUsername(e.target.value)} />
      <input placeholder="Пароль" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      <button type="submit">Войти</button>
    </form>
  );
}
