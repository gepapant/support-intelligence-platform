import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const API_BASE_URL =
  process.env.API_BASE_URL ??
  "http://127.0.0.1:8000";

type RouteContext = {
  params: Promise<{
    articleId: string;
  }>;
};

export async function POST(
  _request: Request,
  { params }: RouteContext,
) {
  const { articleId } = await params;

  const id = Number(articleId);

  if (!Number.isInteger(id) || id <= 0) {
    return NextResponse.json(
      { detail: "Invalid article ID" },
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

  try {
    const response = await fetch(
      `${API_BASE_URL}/knowledge/${id}/reindex`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );

    const data = await response.json();

    return NextResponse.json(data, {
      status: response.status,
    });
  } catch {
    return NextResponse.json(
      {
        detail:
          "Knowledge indexing service unavailable",
      },
      { status: 503 },
    );
  }
}