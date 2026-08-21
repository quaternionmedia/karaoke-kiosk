// ════════════════════════════════════════════════════════════════════
//  ADMIN APP STATE
// ════════════════════════════════════════════════════════════════════

export interface AdminState {
  selectedVenueId: number | null;
}

export const AdminState: AdminState = {
  selectedVenueId: null,
};
