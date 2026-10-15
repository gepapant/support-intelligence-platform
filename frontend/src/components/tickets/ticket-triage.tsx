"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import type {
  Ticket,
  User,
} from "@/lib/api";

type TicketTriageProps = {
  ticket: Ticket;
  user: User;
};

export default function TicketTriage({
  ticket,
  user,
}: TicketTriageProps) {
  const router = useRouter();

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const canRunTriage =
    user.role === "admin" ||
    ticket.assignee_id === user.id;

  async function handleTriage() {
    setError(null);
    setLoading(true);

    try {
      const response = await fetch(
        `/api/tickets/${ticket.id}/triage`,
        {
          method: "POST",
        },
      );

      const data = await response.json();

      if (!response.ok) {
        setError(
          data.detail ??
            "Unable to run AI triage",
        );
        return;
      }

      router.refresh();
    } catch {
      setError(
        "Unable to connect to the AI triage service",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wider text-violet-400">
            AI Analysis
          </p>

          <h2 className="mt-2 text-xl font-bold">
            Ticket triage
          </h2>
        </div>

        {canRunTriage && (
          <button
            type="button"
            onClick={handleTriage}
            disabled={loading}
            className="rounded-lg bg-violet-600 px-4 py-2 font-semibold transition hover:bg-violet-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading
              ? "Analyzing..."
              : ticket.ai_analyzed_at
                ? "Re-run AI triage"
                : "Run AI triage"}
          </button>
        )}
      </div>

      {!canRunTriage && (
        <p className="mt-4 text-sm text-slate-400">
          Only the assigned agent or an admin
          can run AI triage.
        </p>
      )}

      {error && (
        <p className="mt-4 text-sm text-red-400">
          {error}
        </p>
      )}

      {ticket.ai_analyzed_at ? (
        <div className="mt-6 space-y-5">
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
              <p className="text-xs uppercase tracking-wide text-slate-500">
                Category
              </p>

              <p className="mt-2 font-semibold capitalize">
                {ticket.ai_category?.replaceAll(
                  "_",
                  " ",
                )}
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
              <p className="text-xs uppercase tracking-wide text-slate-500">
                Sentiment
              </p>

              <p className="mt-2 font-semibold capitalize">
                {ticket.ai_sentiment}
              </p>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4">
              <p className="text-xs uppercase tracking-wide text-slate-500">
                Suggested priority
              </p>

              <p className="mt-2 font-semibold capitalize">
                {ticket.ai_suggested_priority}
              </p>
            </div>
          </div>

          <div>
            <p className="text-sm text-slate-400">
              AI summary
            </p>

            <p className="mt-2 leading-7 text-slate-200">
              {ticket.ai_summary}
            </p>
          </div>

          <p className="text-xs text-slate-500">
            Provider: {ticket.ai_model}
          </p>
        </div>
      ) : (
        <p className="mt-6 text-sm text-slate-400">
          This ticket has not been analyzed yet.
        </p>
      )}
    </div>
  );
}