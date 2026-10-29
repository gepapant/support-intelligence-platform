import { NextResponse } from "next/server";

const API_BASE_URL =
  process.env.API_BASE_URL ??
  "http://127.0.0.1:8000";

type RegisterBody = {
  email?: string;
  password?: string;
};

export async function POST(
  request: Request,
) {
  let body: RegisterBody;

  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      {
        detail: "Invalid request body",
      },
      {
        status: 400,
      },
    );
  }

  if (!body.email || !body.password) {
    return NextResponse.json(
      {
        detail:
          "Email and password are required",
      },
      {
        status: 400,
      },
    );
  }

  try {
    const backendResponse =
      await fetch(
        `${API_BASE_URL}/auth/register`,
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            email: body.email,
            password: body.password,
          }),
        },
      );

    const data =
      await backendResponse.json();

    if (!backendResponse.ok) {
      return NextResponse.json(
        {
          detail:
            data.detail ??
            "Registration failed",
        },
        {
          status:
            backendResponse.status,
        },
      );
    }

    return NextResponse.json(
      {
        success: true,
      },
      {
        status: 201,
      },
    );
  } catch {
    return NextResponse.json(
      {
        detail:
          "Registration service unavailable",
      },
      {
        status: 503,
      },
    );
  }
}