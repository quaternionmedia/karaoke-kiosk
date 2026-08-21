import { fetchJson, apiUrl } from "../api/index";

// ════════════════════════════════════════════════════════════════════
//  ADMIN API CLIENT
// ════════════════════════════════════════════════════════════════════

export interface PerformanceRead {
  id: number;
  session_token: string;
  event_id: number | null;
  performer_id: number;
  song_id: number;
  status: string;
  queue_position: number | null;
  started_at: string | null;
  finished_at: string | null;
  recording: { id: number; status: string; url: string | null } | null;
}

export interface SongRead {
  id: number;
  name: string;
  artist: string;
  genre: string | null;
  duration_seconds: number | null;
}

export interface VenueRead {
  id: number;
  name: string;
  location: string | null;
  welcome_message: string | null;
  splash_delay_ms: number;
  countdown_from: number;
  thank_you_duration_ms: number;
  is_active: boolean;
}

export interface EmailTemplateRead {
  id: number;
  venue_id: number;
  slug: string;
  name: string;
  subject: string;
  body: string;
  is_active: boolean;
}

export interface SettingsRead {
  database_url: string | null;
  cors_origins: string[];
  obs_enabled: boolean;
  obs_ws_url: string | null;
  obs_ws_password: string | null;
  email_enabled: boolean;
  smtp_host: string | null;
  smtp_port: number;
  smtp_user: string | null;
  smtp_password: string | null;
  smtp_from: string | null;
  recording_base_url: string | null;
  admin_api_key: string | null;
}

// Queue operations
export async function listQueue(eventId?: number): Promise<PerformanceRead[]> {
  const params = new URLSearchParams();
  if (eventId !== undefined) params.set("event_id", String(eventId));
  return fetchJson(`/api/admin/queue${params.size ? "?" + params : ""}`);
}

export async function enqueuePerformance(
  songId: number,
  name: string,
  email: string,
  eventId?: number
): Promise<PerformanceRead> {
  return fetchJson("/api/admin/queue", {
    method: "POST",
    body: JSON.stringify({
      song_id: songId,
      singer: { name, email },
      event_id: eventId,
    }),
  });
}

export async function movePerformance(
  performanceId: number,
  toIndex: number
): Promise<PerformanceRead> {
  return fetchJson(`/api/admin/queue/${performanceId}/move`, {
    method: "POST",
    body: JSON.stringify({ to_index: toIndex }),
  });
}

export async function removePerformance(performanceId: number): Promise<void> {
  return fetchJson(`/api/admin/queue/${performanceId}`, {
    method: "DELETE",
  });
}

export async function startNext(eventId?: number): Promise<PerformanceRead> {
  const params = new URLSearchParams();
  if (eventId !== undefined) params.set("event_id", String(eventId));
  return fetchJson(
    `/api/admin/queue/start-next${params.size ? "?" + params : ""}`,
    { method: "POST" }
  );
}

// Venue
export async function listVenues(): Promise<VenueRead[]> {
  return fetchJson("/api/admin/venues");
}

export async function updateVenue(
  venueId: number,
  data: Record<string, any>
): Promise<VenueRead> {
  return fetchJson(`/api/admin/venues/${venueId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

// Songs
export async function listSongs(): Promise<SongRead[]> {
  return fetchJson("/api/admin/songs");
}

// Email Templates
export async function listEmailTemplates(
  venueId?: number
): Promise<EmailTemplateRead[]> {
  const params = new URLSearchParams();
  if (venueId !== undefined) params.set("venue_id", String(venueId));
  return fetchJson(
    `/api/admin/email-templates${params.size ? "?" + params : ""}`
  );
}

export async function createEmailTemplate(data: {
  venue_id: number;
  slug: string;
  name: string;
  subject: string;
  body: string;
  is_active?: boolean;
}): Promise<EmailTemplateRead> {
  return fetchJson("/api/admin/email-templates", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateEmailTemplate(
  templateId: number,
  data: Record<string, any>
): Promise<EmailTemplateRead> {
  return fetchJson(`/api/admin/email-templates/${templateId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteEmailTemplate(templateId: number): Promise<void> {
  return fetchJson(`/api/admin/email-templates/${templateId}`, {
    method: "DELETE",
  });
}

export async function previewEmailTemplate(templateId: number): Promise<{
  subject: string;
  body: string;
}> {
  return fetchJson(`/api/admin/email-templates/${templateId}/preview`, {
    method: "POST",
  });
}

// Settings
export async function getSettings(): Promise<SettingsRead> {
  return fetchJson("/api/admin/settings");
}
