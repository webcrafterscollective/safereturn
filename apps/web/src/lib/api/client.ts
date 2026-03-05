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

function accessTokenHeader(): Record<string, string> {
  const accessToken = localStorage.getItem("access_token");
  if (!accessToken) {
    return {};
  }
  return { Authorization: `Bearer ${accessToken}` };
}

export interface LiveHealthResponse {
  status: string;
}

export interface ReadyHealthResponse {
  status: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface RegisterResponse {
  user_id: string;
  email: string;
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

export interface RegisterStickerRequest {
  sticker_code: string;
  item_name: string;
  item_category: string;
  item_description: string;
}

export interface RegisterStickerResponse {
  item_id: string;
  sticker_code: string;
  status: string;
}

export interface MarkItemLostRequest {
  last_known_location?: string;
  notes?: string;
}

export interface LostReportResponse {
  report_id: string;
  item_id: string;
  status: string;
  created_at: string;
}

export interface ScanStickerRequest {
  sticker_code: string;
  finder_note?: string;
}

export interface ScanStickerResponse {
  session_token: string;
  item_name: string;
  owner_hint: string;
  expires_at: string;
}

export interface RelayMessageRequest {
  message_body: string;
}

export interface RelayMessageResponse {
  session_reference: string;
  sender_role: string;
  body: string;
  created_at: string;
}

export interface OwnerInboxResponse {
  messages: RelayMessageResponse[];
}

export async function getHealthLive(): Promise<LiveHealthResponse> {
  return request<LiveHealthResponse>(apiUrl("/health/live"), { method: "GET" });
}

export async function getHealthReady(): Promise<ReadyHealthResponse> {
  return request<ReadyHealthResponse>(apiUrl("/health/ready"), { method: "GET" });
}

export async function getMetricsText(): Promise<string> {
  const response = await fetch(apiUrl("/metrics"), { method: "GET" });
  if (!response.ok) {
    throw new ApiError("Metrics request failed", response.status, null);
  }
  return response.text();
}

export async function login(payload: LoginRequest): Promise<TokenResponse> {
  return request<TokenResponse>(apiUrl("/api/v1/auth/login"), {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function register(payload: RegisterRequest): Promise<RegisterResponse> {
  return request<RegisterResponse>(apiUrl("/api/v1/auth/register"), {
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

export async function registerSticker(
  payload: RegisterStickerRequest,
): Promise<RegisterStickerResponse> {
  return request<RegisterStickerResponse>(apiUrl("/api/v1/recovery/stickers/register"), {
    method: "POST",
    headers: {
      ...accessTokenHeader(),
    },
    body: JSON.stringify(payload),
  });
}

export async function markItemLost(
  itemId: string,
  payload: MarkItemLostRequest,
): Promise<LostReportResponse> {
  return request<LostReportResponse>(apiUrl(`/api/v1/recovery/items/${itemId}/mark-lost`), {
    method: "POST",
    headers: {
      ...accessTokenHeader(),
    },
    body: JSON.stringify(payload),
  });
}

export async function scanSticker(payload: ScanStickerRequest): Promise<ScanStickerResponse> {
  return request<ScanStickerResponse>(apiUrl("/api/v1/recovery/scan"), {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function sendFinderMessage(
  sessionToken: string,
  payload: RelayMessageRequest,
): Promise<RelayMessageResponse> {
  return request<RelayMessageResponse>(apiUrl(`/api/v1/recovery/sessions/${sessionToken}/messages`), {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listOwnerMessages(): Promise<OwnerInboxResponse> {
  return request<OwnerInboxResponse>(apiUrl("/api/v1/recovery/owner/messages"), {
    method: "GET",
    headers: {
      ...accessTokenHeader(),
    },
  });
}

export async function sendOwnerMessage(
  sessionReference: string,
  payload: RelayMessageRequest,
): Promise<RelayMessageResponse> {
  return request<RelayMessageResponse>(
    apiUrl(`/api/v1/recovery/owner/sessions/${sessionReference}/messages`),
    {
      method: "POST",
      headers: {
        ...accessTokenHeader(),
      },
      body: JSON.stringify(payload),
    },
  );
}

export async function refreshStoredSession(): Promise<TokenResponse> {
  const refreshToken = localStorage.getItem("refresh_token");
  if (!refreshToken) {
    throw new ApiError("Missing refresh token", 400, null);
  }
  const nextTokens = await refresh({ refresh_token: refreshToken });
  localStorage.setItem("access_token", nextTokens.access_token);
  localStorage.setItem("refresh_token", nextTokens.refresh_token);
  return nextTokens;
}

export async function logoutStoredSession(): Promise<void> {
  const refreshToken = localStorage.getItem("refresh_token");
  if (refreshToken) {
    await logout({ refresh_token: refreshToken });
  }
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}
