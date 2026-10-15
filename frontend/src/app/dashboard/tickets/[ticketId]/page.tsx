import Link from "next/link";
import { cookies } from "next/headers";
import {
  notFound,
  redirect,
} from "next/navigation";
import { Suspense } from "react";

import TicketActions from "@/components/tickets/ticket-actions";

import {
  getAdminUsers,
  getCurrentUser,
  getTicket,
} from "@/lib/api";

import TicketTriage from "@/components/tickets/ticket-triage";

type TicketDetailPageProps = {
  params: Promise<{
    ticketId: string;
  }>;
};

async function TicketDetailContent({
  params,
}: TicketDetailPageProps) {
  const { ticketId } = await params;

  const id = Number(ticketId);

  if (
    !Number.isInteger(id) ||
    id <= 0
  ) {
    notFound();
  }

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

  const ticket = await getTicket(
    token,
    id,
  );

  if (!ticket) {
    notFound();
  }

  const assignableUsers =
    user.role === "admin"
      ? (
          await getAdminUsers(token)
        ).filter(
          (candidate) =>
            candidate.is_active &&
            candidate.role === "agent",
        )
      : [];

  return (
    <>
      <Link
        href="/dashboard"
        className="text-sm font-semibold text-blue-400 hover:text-blue-300"
      >
        ← Back to tickets
      </Link>

      <header className="mt-8 border-b border-slate-800 pb-6">
        <p className="text-sm text-slate-400">
          Ticket #{ticket.id}
        </p>

        <h1 className="mt-2 text-3xl font-bold">
          {ticket.title}
        </h1>
      </header>

      <section className="mt-8 grid gap-6 md:grid-cols-3">
        <div className="md:col-span-2">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h2 className="font-semibold">
              Description
            </h2>

            <p className="mt-4 whitespace-pre-wrap text-slate-300">
              {ticket.description}
            </p>
          </div>

          <div className="mt-6">
            <TicketTriage
              ticket={ticket}
              user={user}
            />
          </div>

          <TicketActions
            ticket={ticket}
            user={user}
            assignableUsers={assignableUsers}
          />
        </div>

        <aside className="space-y-4">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">
              Status
            </p>

            <p className="mt-2 font-semibold">
              {ticket.status}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">
              Priority
            </p>

            <p className="mt-2 font-semibold capitalize">
              {ticket.priority}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">
              Assignee
            </p>

            <p className="mt-2 font-semibold">
              {ticket.assignee_id
                ? `User #${ticket.assignee_id}`
                : "Unassigned"}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">
              Created
            </p>

            <p className="mt-2 text-sm font-semibold">
              {new Date(
                ticket.created_at,
              ).toLocaleString("en-GB")}
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
            <p className="text-sm text-slate-400">
              Updated
            </p>

            <p className="mt-2 text-sm font-semibold">
              {new Date(
                ticket.updated_at,
              ).toLocaleString("en-GB")}
            </p>
          </div>
        </aside>
      </section>
    </>
  );
}

function TicketDetailFallback() {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8 text-slate-400">
      Loading ticket...
    </div>
  );
}

export default function TicketDetailPage({
  params,
}: TicketDetailPageProps) {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto max-w-4xl">
        <Suspense
          fallback={<TicketDetailFallback />}
        >
          <TicketDetailContent
            params={params}
          />
        </Suspense>
      </div>
    </main>
  );
}