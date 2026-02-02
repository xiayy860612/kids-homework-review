import axios, { AxiosInstance, AxiosError } from "axios";

const TOKEN_KEY = "access_token";

// 创建 axios 实例
export const apiClient: AxiosInstance = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

// 请求拦截器：自动添加 token
apiClient.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器：处理 401 错误
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      removeAuthToken();
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// Token 管理
export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setAuthToken(token: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_KEY, token);
}

export function removeAuthToken(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_KEY);
}

// 验证 token
export async function validateToken(): Promise<boolean> {
  const token = getAuthToken();
  if (!token) return false;

  try {
    const response = await api.getCurrentUserInfo();
    return response.status === 200;
  } catch {
    removeAuthToken();
    return false;
  }
}

// API 方法
export const api = {
  // 认证相关
  login: (username: string, password: string) =>
    apiClient.post<{ access_token: string }>("/auth/login", { username, password }),

  logout: () =>
    apiClient.post<{ access_token: string }>("/auth/logout"),

  getCurrentUserInfo: () => apiClient.get(`/auth/me`),

  changePassword: (data: { current_password: string; new_password: string }) =>
    apiClient.put("/auth/change-password", data),

  // 错题相关
  // 获取错题列表
  getWrongQuestions: () => apiClient.get("/wrong-questions"),

  // 获取错题详情
  getWrongQuestion: (id: number) => apiClient.get(`/wrong-questions/${id}`),

  // 创建错题
  createWrongQuestion: (data: {
    title: string;
    subject_id: number;
    tag_ids: number[];
    image_base64: string;
  }) => apiClient.post("/wrong-questions", data),

  // 更新错题
  updateWrongQuestion: (
    id: number,
    data: {
      title?: string;
      subject_id?: number;
      tag_ids?: number[];
      image_base64?: string;
    }
  ) => apiClient.put(`/wrong-questions/${id}`, data),

  // 分析错题
  analyzeWrongQuestion: (id: number) =>
    apiClient.post(`/wrong-questions/${id}/analyze`),

  // 学科相关
  getSubjects: () => apiClient.get("/subjects"),

  createSubject: (data: { name: string; description?: string }) =>
    apiClient.post("/subjects", data),

  // 标签相关
  getTags: () => apiClient.get("/tags"),

  createTag: (data: { name: string }) => apiClient.post("/tags", data),
};

// 类型定义
export type AnalysisStatus = "pending" | "processing" | "completed" | "failed"

export interface Subject {
  id: number;
  name: string;
  description: string | null;
}

export interface Tag {
  id: number;
  name: string;
  is_preset: boolean;
}

export interface WrongQuestion {
  id: number;
  title: string;
  subject: Subject;
  tags: Tag[];
  image_base64: string;
  analysis_status: AnalysisStatus;
  analysis_result: string | null;
  analysis_error: string | null;
  analyzed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ApiError {
  message: string;
  code?: string;
  details?: unknown;
}

// 错误处理辅助函数
export function getApiError(error: unknown): ApiError {
  if (axios.isAxiosError(error)) {
    return {
      message: (error.response?.data as { message?: string })?.message || error.message || "请求失败",
      code: (error.response?.data as { code?: string })?.code,
      details: error.response?.data,
    };
  }
  return {
    message: error instanceof Error ? error.message : "未知错误",
  };
}