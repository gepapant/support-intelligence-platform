const API_BASE_URL =
  process.env.API_BASE_URL ??
  "http://127.0.0.1:8000";

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

  ai_category: TicketCategory | null;
  ai_sentiment: TicketSentiment | null;
  ai_suggested_priority: TicketPriority | null;
  ai_summary: string | null;
  ai_model: string | null;
  ai_analyzed_at: string | null;

  created_at: string;
  updated_at: string;
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

  if (
    filters.assigneeId !== undefined
  ) {
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

export type RAGSource = {
  article_id: number;
  article_title: string;
  source_url: string | null;
  similarity: number;
};

export type SuggestedReplyResponse = {
  suggestion_id: number;
  reply: string;
  provider: string;
  sources: RAGSource[];
};

export type ReplyDecision =
  | "accepted"
  | "edited"
  | "rejected";

export type ReplySuggestionReviewResponse = {
  suggestion_id: number;
  decision: ReplyDecision;
  final_reply: string | null;
  reviewed_at: string;
};

export type KnowledgeIndexStatus =
  | "queued"
  | "indexing"
  | "ready"
  | "failed";

export type KnowledgeArticle = {
  id: number;
  title: string;
  content: string;
  source_url: string | null;
  is_active: boolean;

  indexing_status: KnowledgeIndexStatus;
  indexing_error: string | null;
  indexed_at: string | null;

  created_at: string;
  updated_at: string;
};

export async function getKnowledgeArticles(
  token: string,
): Promise<KnowledgeArticle[]> {
  const response = await fetch(
    `${API_BASE_URL}/knowledge`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    },
  );

  if (!response.ok) {
    throw new Error(
      `Failed to load knowledge articles: ${response.status}`,
    );
  }

  return response.json();
}

export type KnowledgeIndexResponse = {
  article_id: number;
  chunks_indexed: number;
  embedding_model: string;
};

export type AnalyticsSummary = {
  total_tickets: number;
  unassigned_tickets: number;
  ai_analyzed_tickets: number;
  high_priority_active_tickets: number;
  negative_active_tickets: number;

  status_counts: Record<string, number>;
  priority_counts: Record<string, number>;
  category_counts: Record<string, number>;
  sentiment_counts: Record<string, number>;
};

export type AnalyticsTrendPoint = {
  date: string;
  tickets_created: number;
};

export type AnalyticsTrends = {
  days: number;
  created_per_day: AnalyticsTrendPoint[];
};

export async function getAnalyticsSummary(
  token: string,
): Promise<AnalyticsSummary> {
  const response = await fetch(
    `${API_BASE_URL}/analytics/summary`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    },
  );

  if (!response.ok) {
    throw new Error(
      `Failed to load analytics summary: ${response.status}`,
    );
  }

  return response.json();
}

export async function getAnalyticsTrends(
  token: string,
  days: 7 | 30,
): Promise<AnalyticsTrends> {
  const response = await fetch(
    `${API_BASE_URL}/analytics/trends?days=${days}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    },
  );

  if (!response.ok) {
    throw new Error(
      `Failed to load analytics trends: ${response.status}`,
    );
  }

  return response.json();
}