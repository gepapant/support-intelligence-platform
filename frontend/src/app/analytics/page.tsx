import Link from "next/link";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import AnalyticsDashboard from "@/components/analytics/analytics-dashboard";
import {
  getAnalyticsSummary,
  getAnalyticsTrends,
  getCurrentUser,
} from "@/lib/api";

type AnalyticsSearchParams = {
  days?: string;
};

type AnalyticsPageProps = {
  searchParams: Promise<
    AnalyticsSearchParams
  >;
};

function parseDays(
  value: string | undefined,
): 7 | 30 {
  if (value === "30") {
    return 30;
  }

  return 7;
}

async function AnalyticsContent({
  searchParams,
}: AnalyticsPageProps) {
  const params = await searchParams;

  const days = parseDays(
    params.days,
  );

  const cookieStore =
    await cookies();

  const token =
    cookieStore.get(
      "access_token",
    )?.value;

  if (!token) {
    redirect("/login");
  }

  const user =
    await getCurrentUser(token);

  if (!user) {
    redirect("/login");
  }

  if (user.role !== "admin") {
    redirect("/dashboard");
  }

  const [
    summary,
    trends,
  ] = await Promise.all([
    getAnalyticsSummary(token),
    getAnalyticsTrends(
      token,
      days,
    ),
  ]);

  return (
    <>
      <header className="flex flex-col gap-5 border-b border-slate-800 pb-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-widest text-blue-400">
            Support Intelligence
          </p>

          <h1 className="mt-2 text-2xl font-bold">
            Analytics Dashboard
          </h1>

          <p className="mt-2 text-sm text-slate-400">
            Operational workload,
            AI insights, and ticket
            trends.
          </p>
        </div>

        <div className="flex flex-wrap gap-3">
          <Link
            href="/dashboard"
            className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-300 transition hover:bg-slate-900"
          >
            Ticket Workspace
          </Link>

          <Link
            href="/knowledge"
            className="rounded-lg border border-emerald-800 px-4 py-2 text-sm font-semibold text-emerald-300 transition hover:bg-emerald-950"
          >
            Knowledge Base
          </Link>
        </div>
      </header>

      <section className="mt-8">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="font-semibold">
              Reporting window
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              Change the period used
              by the ticket volume
              chart.
            </p>
          </div>

          <div className="flex gap-2">
            <Link
              href="/analytics?days=7"
              className={`rounded-lg px-4 py-2 text-sm font-semibold ${
                days === 7
                  ? "bg-blue-600 text-white"
                  : "border border-slate-700 text-slate-300"
              }`}
            >
              7 days
            </Link>

            <Link
              href="/analytics?days=30"
              className={`rounded-lg px-4 py-2 text-sm font-semibold ${
                days === 30
                  ? "bg-blue-600 text-white"
                  : "border border-slate-700 text-slate-300"
              }`}
            >
              30 days
            </Link>
          </div>
        </div>

        <AnalyticsDashboard
          summary={summary}
          trends={trends}
        />
      </section>
    </>
  );
}

function AnalyticsFallback() {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8 text-slate-400">
      Loading analytics...
    </div>
  );
}

export default function AnalyticsPage({
  searchParams,
}: AnalyticsPageProps) {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto max-w-7xl">
        <Suspense
          fallback={
            <AnalyticsFallback />
          }
        >
          <AnalyticsContent
            searchParams={
              searchParams
            }
          />
        </Suspense>
      </div>
    </main>
  );
}