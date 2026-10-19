import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const API_BASE_URL =
  process.env.API_BASE_URL ??
  "http://127.0.0.1:8000";

type RouteContext = {
  params: Promise<{
    ticketId: string;
    suggestionId: string;
  }>;
};

export async function PATCH(
  request: Request,
  { params }: RouteContext,
) {
  const { ticketId, suggestionId } =
    await params;

  const ticketIdNumber = Number(ticketId);
  const suggestionIdNumber =
    Number(suggestionId);

  if (
    !Number.isInteger(ticketIdNumber) ||
    ticketIdNumber <= 0 ||
    !Number.isInteger(suggestionIdNumber) ||
    suggestionIdNumber <= 0
  ) {
    return NextResponse.json(
      {
        detail: "Invalid ticket or suggestion ID",
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
    const body = await request.json();

    const backendResponse = await fetch(
      `${API_BASE_URL}/tickets/${ticketIdNumber}/suggested-replies/${suggestionIdNumber}`,
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
        detail:
          "Reply review service unavailable",
      },
      {
        status: 503,
      },
    );
  }
}