const API_BASE_URL =
  process.env.API_BASE_URL ?? "http://127.0.0.1:8000";

export type HealthResponse = {
  status: string;
};

export type User = {
  id: number;
  email: string;
  role: "agent" | "admin";
  is_active: boolean;
};

export type TicketPriority =
  | "low"
  | "medium"
  | "high";

export type TicketStatus =
  | "open"
  | "in_progress"
  | "closed";

export type TicketCategory =
  | "account"
  | "billing"
  | "technical"
  | "refund"
  | "feature_request"
  | "other";

export type TicketSentiment =
  | "negative"
  | "neutral"
  | "positive";

export type Ticket = {
  id: number;
  title: string;
  description: string;
  priority: TicketPriority;
  status: TicketStatus;
  assignee_id: number | null;
  created_at: string;
  updated_at: string; 

  ai_category: TicketCategory | null;
  ai_sentiment: TicketSentiment | null;
  ai_suggested_priority: TicketPriority | null;
  ai_summary: string | null;
  ai_model: string | null;
  ai_analyzed_at: string | null;

  
};

export type TicketFilters = {
  status?: TicketStatus;
  priority?: TicketPriority;
  assigneeId?: number;
  limit?: number;
  offset?: number;
};

export async function getBackendHealth(): Promise<HealthResponse> {
  const response = await fetch(
    `${API_BASE_URL}/health`,
    {
      cache: "no-store",
    },
  );

  if (!response.ok) {
    throw new Error(
      `Backend health check failed with status ${response.status}`,
    );
  }

  return response.json();
}

export async function getCurrentUser(
  token: string,
): Promise<User | null> {
  const response = await fetch(
    `${API_BASE_URL}/auth/me`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    },
  );

  if (!response.ok) {
    return null;
  }

  return response.json();
}

export async function getTickets(
  token: string,
  filters: TicketFilters = {},
): Promise<Ticket[]> {
  const params = new URLSearchParams();

  if (filters.status) {
    params.set(
      "status",
      filters.status,
    );
  }

  if (filters.priority) {
    params.set(
      "priority",
      filters.priority,
    );
  }

  if (filters.assigneeId !== undefined) {
    params.set(
      "assignee_id",
      String(filters.assigneeId),
    );
  }

  params.set(
    "limit",
    String(filters.limit ?? 20),
  );

  params.set(
    "offset",
    String(filters.offset ?? 0),
  );

  const response = await fetch(
    `${API_BASE_URL}/tickets?${params.toString()}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    },
  );

  if (!response.ok) {
    throw new Error(
      `Failed to load tickets: ${response.status}`,
    );
  }

  return response.json();
}

export async function getTicket(
  token: string,
  ticketId: number,
): Promise<Ticket | null> {
  const response = await fetch(
    `${API_BASE_URL}/tickets/${ticketId}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    },
  );

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error(
      `Failed to load ticket: ${response.status}`,
    );
  }

  return response.json();
}

export async function getAdminUsers(
  token: string,
): Promise<User[]> {
  const response = await fetch(
    `${API_BASE_URL}/admin/users`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    },
  );

  if (!response.ok) {
    throw new Error(
      `Failed to load users: ${response.status}`,
    );
  }

  return response.json();
}