// useAuth.js
import { useState, useEffect } from "react";

export function useAuth() {
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [username, setUsername] = useState(() => localStorage.getItem("username"));

  const login = (newToken) => {
    const payload = JSON.parse(atob(newToken.split('.')[1]));
    const name = payload?.sub || "пользователь";
    localStorage.setItem("token", newToken);
    localStorage.setItem("username", name);
    setToken(newToken);
    setUsername(name);
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    setToken(null);
    setUsername(null);
  };

  return { token, username, login, logout };
}
