import Link from "next/link";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import TicketTable from "@/components/tickets/ticket-table";
import {
  getCurrentUser,
  getTickets,
  type TicketPriority,
  type TicketStatus,
} from "@/lib/api";

import LogoutButton from "./logout-button";

type DashboardSearchParams = {
  status?: string;
  priority?: string;
  view?: string;
  page?: string;
};

type DashboardPageProps = {
  searchParams: Promise<DashboardSearchParams>;
};

function parseStatus(
  value: string | undefined,
): TicketStatus | undefined {
  if (
    value === "open" ||
    value === "in_progress" ||
    value === "closed"
  ) {
    return value;
  }

  return undefined;
}

function parsePriority(
  value: string | undefined,
): TicketPriority | undefined {
  if (
    value === "low" ||
    value === "medium" ||
    value === "high"
  ) {
    return value;
  }

  return undefined;
}

function buildDashboardUrl({
  view,
  status,
  priority,
  page,
}: {
  view: "all" | "mine";
  status?: TicketStatus;
  priority?: TicketPriority;
  page?: number;
}) {
  const params = new URLSearchParams();

  if (view === "mine") {
    params.set("view", "mine");
  }

  if (status) {
    params.set("status", status);
  }

  if (priority) {
    params.set("priority", priority);
  }

  if (page && page > 1) {
    params.set("page", String(page));
  }

  const query = params.toString();

  return query
    ? `/dashboard?${query}`
    : "/dashboard";
}

async function DashboardContent({
  searchParams,
}: DashboardPageProps) {
  const params = await searchParams;

  const cookieStore = await cookies();

  const token =
    cookieStore.get("access_token")?.value;

  if (!token) {
    redirect("/login");
  }

  const user = await getCurrentUser(token);

  if (!user) {
    redirect("/login");
  }

  const status = parseStatus(params.status);
  const priority = parsePriority(
    params.priority,
  );

  const view =
    params.view === "mine" ? "mine" : "all";

  const parsedPage = Number(params.page);

  const page =
    Number.isInteger(parsedPage) &&
    parsedPage > 0
      ? parsedPage
      : 1;

  const pageSize = 10;

  const results = await getTickets(token, {
    status,
    priority,
    assigneeId:
      view === "mine"
        ? user.id
        : undefined,
    limit: pageSize + 1,
    offset: (page - 1) * pageSize,
  });

  const hasNextPage =
    results.length > pageSize;

  const tickets = results.slice(
    0,
    pageSize,
  );

  const openTickets = tickets.filter(
    (ticket) =>
      ticket.status === "open",
  ).length;

  const inProgressTickets =
    tickets.filter(
      (ticket) =>
        ticket.status === "in_progress",
    ).length;

  const closedTickets = tickets.filter(
    (ticket) =>
      ticket.status === "closed",
  ).length;

  return (
    <>
      <header className="flex flex-col gap-5 border-b border-slate-800 pb-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-widest text-blue-400">
            Support Intelligence
          </p>

          <h1 className="mt-2 text-2xl font-bold">
            Ticket Workspace
          </h1>

          <p className="mt-2 text-sm text-slate-400">
            {user.email} · {user.role}
          </p>
        </div>

        <div className="flex flex-wrap gap-3">
          {user.role === "admin" && (
            <Link
              href="/knowledge"
              className="rounded-lg border border-emerald-800 px-4 py-2 text-sm font-semibold text-emerald-300 transition hover:bg-emerald-950"
            >
              Knowledge Base
            </Link>
          )}

          <LogoutButton />
        </div>
      </header>

      <section className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <article className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">
            Shown
          </p>

          <p className="mt-2 text-3xl font-bold">
            {tickets.length}
          </p>
        </article>

        <article className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">
            Open
          </p>

          <p className="mt-2 text-3xl font-bold text-blue-300">
            {openTickets}
          </p>
        </article>

        <article className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">
            In progress
          </p>

          <p className="mt-2 text-3xl font-bold text-amber-300">
            {inProgressTickets}
          </p>
        </article>

        <article className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">
            Closed
          </p>

          <p className="mt-2 text-3xl font-bold text-emerald-300">
            {closedTickets}
          </p>
        </article>
      </section>

      <section className="mt-10">
        <div className="mb-6 flex flex-col gap-5">
          <div className="flex flex-wrap gap-2">
            <Link
              href={buildDashboardUrl({
                view: "all",
                status,
                priority,
              })}
              className={`rounded-lg px-4 py-2 text-sm font-semibold ${
                view === "all"
                  ? "bg-blue-600 text-white"
                  : "border border-slate-700 text-slate-300"
              }`}
            >
              All tickets
            </Link>

            <Link
              href={buildDashboardUrl({
                view: "mine",
                status,
                priority,
              })}
              className={`rounded-lg px-4 py-2 text-sm font-semibold ${
                view === "mine"
                  ? "bg-blue-600 text-white"
                  : "border border-slate-700 text-slate-300"
              }`}
            >
              My tickets
            </Link>
          </div>

          <form
            action="/dashboard"
            method="get"
            className="flex flex-col gap-3 rounded-2xl border border-slate-800 bg-slate-900 p-4 md:flex-row md:items-end"
          >
            {view === "mine" && (
              <input
                type="hidden"
                name="view"
                value="mine"
              />
            )}

            <div className="flex-1">
              <label
                htmlFor="status"
                className="mb-2 block text-sm text-slate-400"
              >
                Status
              </label>

              <select
                id="status"
                name="status"
                defaultValue={status ?? ""}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
              >
                <option value="">
                  All statuses
                </option>
                <option value="open">
                  Open
                </option>
                <option value="in_progress">
                  In progress
                </option>
                <option value="closed">
                  Closed
                </option>
              </select>
            </div>

            <div className="flex-1">
              <label
                htmlFor="priority"
                className="mb-2 block text-sm text-slate-400"
              >
                Priority
              </label>

              <select
                id="priority"
                name="priority"
                defaultValue={priority ?? ""}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
              >
                <option value="">
                  All priorities
                </option>
                <option value="low">
                  Low
                </option>
                <option value="medium">
                  Medium
                </option>
                <option value="high">
                  High
                </option>
              </select>
            </div>

            <button
              type="submit"
              className="rounded-lg bg-blue-600 px-5 py-2 font-semibold transition hover:bg-blue-500"
            >
              Apply filters
            </button>

            <Link
              href={
                view === "mine"
                  ? "/dashboard?view=mine"
                  : "/dashboard"
              }
              className="rounded-lg border border-slate-700 px-5 py-2 text-center font-semibold text-slate-300"
            >
              Clear
            </Link>
          </form>
        </div>

        <TicketTable tickets={tickets} />

        <div className="mt-6 flex items-center justify-between">
          <div>
            {page > 1 && (
              <Link
                href={buildDashboardUrl({
                  view,
                  status,
                  priority,
                  page: page - 1,
                })}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-semibold"
              >
                ← Previous
              </Link>
            )}
          </div>

          <p className="text-sm text-slate-400">
            Page {page}
          </p>

          <div>
            {hasNextPage && (
              <Link
                href={buildDashboardUrl({
                  view,
                  status,
                  priority,
                  page: page + 1,
                })}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-semibold"
              >
                Next →
              </Link>
            )}
          </div>
        </div>
      </section>
    </>
  );
}

function DashboardFallback() {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8 text-slate-400">
      Loading ticket workspace...
    </div>
  );
}

export default function DashboardPage({
  searchParams,
}: DashboardPageProps) {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto max-w-7xl">
        <Suspense
          fallback={<DashboardFallback />}
        >
          <DashboardContent
            searchParams={searchParams}
          />
        </Suspense>
      </div>
    </main>
  );
}