import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const API_BASE_URL =
  process.env.API_BASE_URL ??
  "http://127.0.0.1:8000";

type CreateTicketBody = {
  title?: string;
  description?: string;
  priority?: string;
};

export async function POST(
  request: Request,
) {
  let body: CreateTicketBody;

  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      {
        detail:
          "Invalid request body",
      },
      {
        status: 400,
      },
    );
  }

  const cookieStore =
    await cookies();

  const token =
    cookieStore.get(
      "access_token",
    )?.value;

  if (!token) {
    return NextResponse.json(
      {
        detail:
          "Not authenticated",
      },
      {
        status: 401,
      },
    );
  }

  try {
    const backendResponse =
      await fetch(
        `${API_BASE_URL}/tickets`,
        {
          method: "POST",
          headers: {
            Authorization:
              `Bearer ${token}`,
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            title: body.title,
            description:
              body.description,
            priority:
              body.priority ??
              "medium",
          }),
        },
      );

    const data =
      await backendResponse.json();

    return NextResponse.json(
      data,
      {
        status:
          backendResponse.status,
      },
    );
  } catch {
    return NextResponse.json(
      {
        detail:
          "Ticket service unavailable",
      },
      {
        status: 503,
      },
    );
  }
}