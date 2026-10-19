import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const API_BASE_URL =
  process.env.API_BASE_URL ??
  "http://127.0.0.1:8000";

type RouteContext = {
  params: Promise<{
    ticketId: string;
  }>;
};

export async function POST(
  _request: Request,
  { params }: RouteContext,
) {
  const { ticketId } = await params;

  const id = Number(ticketId);

  if (!Number.isInteger(id) || id <= 0) {
    return NextResponse.json(
      {
        detail: "Invalid ticket ID",
      },
      {
        status: 400,
      },
    );
  }

  const cookieStore = await cookies();

  const token =
    cookieStore.get("access_token")?.value;

  if (!token) {
    return NextResponse.json(
      {
        detail: "Not authenticated",
      },
      {
        status: 401,
      },
    );
  }

  try {
    const backendResponse = await fetch(
      `${API_BASE_URL}/tickets/${id}/suggested-reply`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );

    const data = await backendResponse.json();

    return NextResponse.json(
      data,
      {
        status: backendResponse.status,
      },
    );
  } catch {
    return NextResponse.json(
      {
        detail:
          "Suggested reply service unavailable",
      },
      {
        status: 503,
      },
    );
  }
}