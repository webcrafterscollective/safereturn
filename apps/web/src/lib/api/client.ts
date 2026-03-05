/** Typed API client and auth-session helpers for the SafeReturn frontend. */

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(
  /\/$/,
  "",
) ?? "";

const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";
export const AUTH_CHANGED_EVENT = "safereturn:auth-changed";

function apiUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

function parseJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const payloadB64 = token.split(".")[1];
    if (!payloadB64) {
      return null;
    }
    const normalized = payloadB64.replace(/-/g, "+").replace(/_/g, "/");
    const decoded = atob(normalized);
    return JSON.parse(decoded) as Record<string, unknown>;
  } catch {
    return null;
  }
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

export interface SessionSnapshot {
  isAuthenticated: boolean;
  isAdmin: boolean;
  accessToken: string | null;
  refreshToken: string | null;
}

export function getSessionSnapshot(): SessionSnapshot {
  const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
  if (!accessToken) {
    return {
      isAuthenticated: false,
      isAdmin: false,
      accessToken: null,
      refreshToken,
    };
  }

  const payload = parseJwtPayload(accessToken);
  const isAdmin = Boolean(payload?.is_admin);
  return {
    isAuthenticated: true,
    isAdmin,
    accessToken,
    refreshToken,
  };
}

function emitAuthChange(): void {
  window.dispatchEvent(new Event(AUTH_CHANGED_EVENT));
}

export function storeSessionTokens(tokens: TokenResponse): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
  emitAuthChange();
}

export function clearStoredSessionTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  emitAuthChange();
}

async function request<TResponse>(input: string, init?: RequestInit): Promise<TResponse> {
  const response = await fetch(input, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (response.status === 401) {
    clearStoredSessionTokens();
    if (window.location.pathname !== "/login") {
      window.location.href = "/login";
    }
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
  const snapshot = getSessionSnapshot();
  if (!snapshot.accessToken) {
    return {};
  }
  return { Authorization: `Bearer ${snapshot.accessToken}` };
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

export interface StickerSummary {
  code: string;
  status: string;
  item_id: string | null;
  assigned_once: boolean;
  claimed_at: string | null;
  invalidated_at: string | null;
  replaced_by_code: string | null;
  qr_scan_url: string;
}

export interface ClaimPackResponse {
  pack_code: string;
  total_stickers: number;
  stickers: StickerSummary[];
}

export interface UserStickersResponse {
  stickers: StickerSummary[];
}

export interface OwnerItemSummary {
  item_id: string;
  item_name: string;
  category: string;
  description: string;
  is_lost: boolean;
  sticker_code: string | null;
  sticker_status: string | null;
  created_at: string;
}

export interface UserItemsResponse {
  items: OwnerItemSummary[];
}

export interface RegenerateStickerResponse {
  replaced_code: string;
  replacement: StickerSummary;
}

export interface ClaimIssueResponse {
  audit_event_id: number;
  message: string;
}

export interface StickerPackSummary {
  id: string;
  pack_code: string;
  total_stickers: number;
  status: string;
  assigned_user_id: string | null;
  created_at: string;
  claimed_at: string | null;
}

export interface GeneratePackResponse {
  pack: StickerPackSummary;
  stickers: StickerSummary[];
}

export interface ListPacksResponse {
  packs: StickerPackSummary[];
}

export interface PackStickersResponse {
  pack: StickerPackSummary;
  stickers: StickerSummary[];
}

export interface AdminOverviewResponse {
  users: number;
  packs: number;
  stickers: number;
  claimed_packs: number;
  unassigned_stickers: number;
}

export interface CreateUserAndAssignPackResponse {
  user_id: string;
  email: string;
  assigned_pack_code: string | null;
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

export async function claimPack(packCode: string): Promise<ClaimPackResponse> {
  return request<ClaimPackResponse>(apiUrl("/api/v1/recovery/packs/claim"), {
    method: "POST",
    headers: accessTokenHeader(),
    body: JSON.stringify({ pack_code: packCode }),
  });
}

export async function listMyStickers(): Promise<UserStickersResponse> {
  return request<UserStickersResponse>(apiUrl("/api/v1/recovery/stickers/mine"), {
    method: "GET",
    headers: accessTokenHeader(),
  });
}

export async function listMyItems(): Promise<UserItemsResponse> {
  return request<UserItemsResponse>(apiUrl("/api/v1/recovery/items/mine"), {
    method: "GET",
    headers: accessTokenHeader(),
  });
}

export async function registerSticker(
  payload: RegisterStickerRequest,
): Promise<RegisterStickerResponse> {
  return request<RegisterStickerResponse>(apiUrl("/api/v1/recovery/stickers/register"), {
    method: "POST",
    headers: accessTokenHeader(),
    body: JSON.stringify(payload),
  });
}

export async function regenerateSticker(stickerCode: string): Promise<RegenerateStickerResponse> {
  return request<RegenerateStickerResponse>(
    apiUrl(`/api/v1/recovery/stickers/${stickerCode}/regenerate`),
    {
      method: "POST",
      headers: accessTokenHeader(),
    },
  );
}

export async function invalidateSticker(stickerCode: string): Promise<void> {
  return request<void>(apiUrl(`/api/v1/recovery/stickers/${stickerCode}/invalidate`), {
    method: "POST",
    headers: accessTokenHeader(),
  });
}

export async function markItemLost(
  itemId: string,
  payload: MarkItemLostRequest,
): Promise<LostReportResponse> {
  return request<LostReportResponse>(apiUrl(`/api/v1/recovery/items/${itemId}/mark-lost`), {
    method: "POST",
    headers: accessTokenHeader(),
    body: JSON.stringify(payload),
  });
}

export async function markItemFound(itemId: string): Promise<void> {
  return request<void>(apiUrl(`/api/v1/recovery/items/${itemId}/mark-found`), {
    method: "POST",
    headers: accessTokenHeader(),
  });
}

export async function scanSticker(payload: ScanStickerRequest): Promise<ScanStickerResponse> {
  return request<ScanStickerResponse>(apiUrl("/api/v1/recovery/scan"), {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function reportClaimIssue(
  stickerCode: string,
  note: string,
): Promise<ClaimIssueResponse> {
  return request<ClaimIssueResponse>(apiUrl("/api/v1/recovery/claim-issues"), {
    method: "POST",
    headers: accessTokenHeader(),
    body: JSON.stringify({ sticker_code: stickerCode, note }),
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
    headers: accessTokenHeader(),
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
      headers: accessTokenHeader(),
      body: JSON.stringify(payload),
    },
  );
}

export async function adminOverview(): Promise<AdminOverviewResponse> {
  return request<AdminOverviewResponse>(apiUrl("/api/v1/admin/overview"), {
    method: "GET",
    headers: accessTokenHeader(),
  });
}

export async function adminGeneratePack(quantity: number): Promise<GeneratePackResponse> {
  return request<GeneratePackResponse>(apiUrl("/api/v1/admin/packs/generate"), {
    method: "POST",
    headers: accessTokenHeader(),
    body: JSON.stringify({ quantity }),
  });
}

export async function adminListPacks(): Promise<ListPacksResponse> {
  return request<ListPacksResponse>(apiUrl("/api/v1/admin/packs"), {
    method: "GET",
    headers: accessTokenHeader(),
  });
}

export async function adminPackStickers(packId: string): Promise<PackStickersResponse> {
  return request<PackStickersResponse>(apiUrl(`/api/v1/admin/packs/${packId}/stickers`), {
    method: "GET",
    headers: accessTokenHeader(),
  });
}

export async function adminCreateUserAndAssignPack(
  email: string,
  password: string,
  packCode: string | null,
): Promise<CreateUserAndAssignPackResponse> {
  return request<CreateUserAndAssignPackResponse>(apiUrl("/api/v1/admin/users/create-and-assign-pack"), {
    method: "POST",
    headers: accessTokenHeader(),
    body: JSON.stringify({
      email,
      password,
      pack_code: packCode?.trim() ? packCode.trim() : null,
    }),
  });
}

export async function refreshStoredSession(): Promise<TokenResponse> {
  const snapshot = getSessionSnapshot();
  if (!snapshot.refreshToken) {
    throw new ApiError("Missing refresh token", 400, null);
  }
  const nextTokens = await refresh({ refresh_token: snapshot.refreshToken });
  storeSessionTokens(nextTokens);
  return nextTokens;
}

export async function logoutStoredSession(): Promise<void> {
  const snapshot = getSessionSnapshot();
  if (snapshot.refreshToken) {
    await logout({ refresh_token: snapshot.refreshToken });
  }
  clearStoredSessionTokens();
}
