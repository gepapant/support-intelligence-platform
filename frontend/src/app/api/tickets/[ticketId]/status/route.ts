import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const API_BASE_URL =
  process.env.API_BASE_URL ?? "http://127.0.0.1:8000";

type RouteContext = {
  params: Promise<{
    ticketId: string;
  }>;
};

export async function PATCH(
  request: Request,
  { params }: RouteContext,
) {
  const { ticketId } = await params;

  const id = Number(ticketId);

  if (!Number.isInteger(id) || id <= 0) {
    return NextResponse.json(
      { detail: "Invalid ticket ID" },
      { status: 400 },
    );
  }

  const cookieStore = await cookies();

  const token =
    cookieStore.get("access_token")?.value;

  if (!token) {
    return NextResponse.json(
      { detail: "Not authenticated" },
      { status: 401 },
    );
  }

  let body: unknown;

  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      { detail: "Invalid request body" },
      { status: 400 },
    );
  }

  try {
    const backendResponse = await fetch(
      `${API_BASE_URL}/tickets/${id}/status`,
      {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
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
        detail: "Ticket service unavailable",
      },
      {
        status: 503,
      },
    );
  }
}