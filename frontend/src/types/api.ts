// ─── Channel & Status Enums ──────────────────────────────────────────────────
export type ChannelType = 'email' | 'sms' | 'push';
export type NotificationStatus = 'pending' | 'sent' | 'failed';

// ─── User Types ──────────────────────────────────────────────────────────────
export interface User {
  id: number;
  email: string;
  username: string;
  pokemon_team: number[];
  is_active: boolean;
}

// ─── Auth Types ──────────────────────────────────────────────────────────────
export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  token_type: string;
}

// ─── Notification Types ──────────────────────────────────────────────────────
export interface Notification {
  id: number;
  user_id: number;
  title: string;
  content: string;
  channel: ChannelType;
  recipient: string;
  status: NotificationStatus;
  created_at: string;
}

export interface NotificationCreateInput {
  title: string;
  content: string;
  channel: ChannelType;
  recipient: string;
}

export interface NotificationUpdateInput {
  title?: string;
  content?: string;
}

// ─── API Error Types ─────────────────────────────────────────────────────────
export interface ApiError {
  detail: string | { loc: string[]; msg: string; type: string }[];
}
