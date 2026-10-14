import { NextResponse } from "next/server";

const API_BASE_URL =
  process.env.API_BASE_URL ?? "http://127.0.0.1:8000";

type LoginBody = {
  email?: string;
  password?: string;
};

type TokenResponse = {
  access_token: string;
  token_type: string;
};

export async function POST(request: Request) {
  let body: LoginBody;

  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      { detail: "Invalid request body" },
      { status: 400 },
    );
  }

  if (!body.email || !body.password) {
    return NextResponse.json(
      { detail: "Email and password are required" },
      { status: 400 },
    );
  }

  try {
    const backendResponse = await fetch(
      `${API_BASE_URL}/auth/login`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: body.email,
          password: body.password,
        }),
      },
    );

    const data = await backendResponse.json();

    if (!backendResponse.ok) {
      return NextResponse.json(
        {
          detail:
            data.detail ?? "Login failed",
        },
        {
          status: backendResponse.status,
        },
      );
    }

    const tokenData = data as TokenResponse;

    const response = NextResponse.json({
      success: true,
    });

    response.cookies.set({
      name: "access_token",
      value: tokenData.access_token,
      httpOnly: true,
      secure:
        process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: 30 * 60,
    });

    return response;
  } catch {
    return NextResponse.json(
      {
        detail: "Authentication service unavailable",
      },
      {
        status: 503,
      },
    );
  }
}