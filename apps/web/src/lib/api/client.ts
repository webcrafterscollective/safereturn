/** Typed HTTP client wrapper used by route-level API calls. */

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(
  /\/$/,
  "",
) ?? "";

function apiUrl(path: string): string {
  // Return API URL with optional Vite-configured base.
  return `${API_BASE_URL}${path}`;
}

export class ApiError extends Error {
  status: number;
  details: unknown;

  constructor(message: string, status: number, details: unknown) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

async function request<TResponse>(input: string, init?: RequestInit): Promise<TResponse> {
  const response = await fetch(input, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (response.status === 401 && window.location.pathname !== "/login") {
    window.location.href = "/login";
    throw new ApiError("Unauthorized", 401, null);
  }

  if (!response.ok) {
    let payload: unknown = null;
    try {
      payload = await response.json();
    } catch {
      payload = null;
    }
    throw new ApiError("Request failed", response.status, payload);
  }

  if (response.status === 204) {
    return undefined as TResponse;
  }

  return (await response.json()) as TResponse;
}

export interface LiveHealthResponse {
  status: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface RefreshRequest {
  refresh_token: string;
}

export async function getHealthLive(): Promise<LiveHealthResponse> {
  return request<LiveHealthResponse>(apiUrl("/health/live"), { method: "GET" });
}

export async function login(payload: LoginRequest): Promise<TokenResponse> {
  return request<TokenResponse>(apiUrl("/api/v1/auth/login"), {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function refresh(payload: RefreshRequest): Promise<TokenResponse> {
  return request<TokenResponse>(apiUrl("/api/v1/auth/refresh"), {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function logout(payload: RefreshRequest): Promise<void> {
  return request<void>(apiUrl("/api/v1/auth/logout"), {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
