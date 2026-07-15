import axios from "axios";

// 배포 시 .env 의 VITE_API_BASE_URL 을 Render 백엔드 URL로 설정
const baseURL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const client = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
});

export default client;
