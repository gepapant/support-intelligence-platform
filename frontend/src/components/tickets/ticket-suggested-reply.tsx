"use client";

import { useState } from "react";

import type {
  ReplyDecision,
  ReplySuggestionReviewResponse,
  SuggestedReplyResponse,
  Ticket,
  User,
} from "@/lib/api";

type TicketSuggestedReplyProps = {
  ticket: Ticket;
  user: User;
};

export default function TicketSuggestedReply({
  ticket,
  user,
}: TicketSuggestedReplyProps) {
  const [result, setResult] =
    useState<SuggestedReplyResponse | null>(
      null,
    );

  const [draft, setDraft] =
    useState("");

  const [reviewResult, setReviewResult] =
    useState<ReplySuggestionReviewResponse | null>(
      null,
    );

  const [loading, setLoading] =
    useState(false);

  const [reviewLoading, setReviewLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const canGenerate =
    user.role === "admin" ||
    ticket.assignee_id === user.id;

  const hasEditedDraft =
    result !== null &&
    draft.trim() !== result.reply.trim();

  async function handleGenerate() {
    setError(null);
    setLoading(true);

    try {
      const response = await fetch(
        `/api/tickets/${ticket.id}/suggested-reply`,
        {
          method: "POST",
        },
      );

      const data = await response.json();

      if (!response.ok) {
        setError(
          data.detail ??
            "Unable to generate suggested reply",
        );
        return;
      }

      const suggestedReply =
        data as SuggestedReplyResponse;

      setResult(suggestedReply);
      setDraft(suggestedReply.reply);
      setReviewResult(null);
    } catch {
      setError(
        "Unable to connect to the suggested reply service",
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleReview(
    decision: ReplyDecision,
  ) {
    if (!result) {
      return;
    }

    setError(null);
    setReviewLoading(true);

    const body =
      decision === "edited"
        ? {
            decision,
            final_reply: draft.trim(),
          }
        : {
            decision,
          };

    try {
      const response = await fetch(
        `/api/tickets/${ticket.id}/suggested-replies/${result.suggestion_id}`,
        {
          method: "PATCH",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify(body),
        },
      );

      const data = await response.json();

      if (!response.ok) {
        setError(
          data.detail ??
            "Unable to review suggested reply",
        );
        return;
      }

      setReviewResult(
        data as ReplySuggestionReviewResponse,
      );
    } catch {
      setError(
        "Unable to connect to the reply review service",
      );
    } finally {
      setReviewLoading(false);
    }
  }

  return (
    <section className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wider text-emerald-400">
            RAG Assistant
          </p>

          <h2 className="mt-2 text-xl font-bold">
            Suggested reply
          </h2>

          <p className="mt-2 text-sm text-slate-400">
            Generate a draft using relevant
            Knowledge Base sources, then review
            it before use.
          </p>
        </div>

        {canGenerate &&
          (!result || reviewResult) && (
            <button
              type="button"
              onClick={handleGenerate}
              disabled={loading}
              className="rounded-lg bg-emerald-600 px-4 py-2 font-semibold transition hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading
                ? "Generating..."
                : result
                  ? "Generate another"
                  : "Generate suggested reply"}
            </button>
          )}
      </div>

      {!canGenerate && (
        <p className="mt-4 text-sm text-slate-400">
          Only the assigned agent or an admin
          can generate a suggested reply.
        </p>
      )}

      {error && (
        <p className="mt-4 text-sm text-red-400">
          {error}
        </p>
      )}

      {result && (
        <div className="mt-6 space-y-6">
          <div>
            <label
              htmlFor="suggested-reply"
              className="text-sm font-semibold text-slate-300"
            >
              Draft reply
            </label>

            <textarea
              id="suggested-reply"
              value={draft}
              disabled={
                reviewResult !== null
              }
              onChange={(event) =>
                setDraft(
                  event.target.value,
                )
              }
              rows={8}
              className="mt-3 w-full rounded-xl border border-slate-700 bg-slate-950 p-4 leading-7 text-slate-200 outline-none transition focus:border-emerald-500 disabled:cursor-not-allowed disabled:opacity-70"
            />
          </div>

          {!reviewResult && (
            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                disabled={reviewLoading}
                onClick={() =>
                  handleReview("accepted")
                }
                className="rounded-lg bg-emerald-600 px-4 py-2 font-semibold transition hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {reviewLoading
                  ? "Saving..."
                  : "Accept"}
              </button>

              <button
                type="button"
                disabled={
                  reviewLoading ||
                  !hasEditedDraft ||
                  !draft.trim()
                }
                onClick={() =>
                  handleReview("edited")
                }
                className="rounded-lg bg-blue-600 px-4 py-2 font-semibold transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
              >
                Save edited reply
              </button>

              <button
                type="button"
                disabled={reviewLoading}
                onClick={() =>
                  handleReview("rejected")
                }
                className="rounded-lg border border-red-800 px-4 py-2 font-semibold text-red-300 transition hover:bg-red-950 disabled:cursor-not-allowed disabled:opacity-60"
              >
                Reject
              </button>
            </div>
          )}

          {reviewResult && (
            <div className="rounded-xl border border-slate-700 bg-slate-950 p-4">
              <p className="text-sm text-slate-400">
                Human review
              </p>

              <p className="mt-2 font-semibold capitalize">
                {reviewResult.decision}
              </p>

              {reviewResult.final_reply && (
                <p className="mt-3 text-sm text-slate-300">
                  Final reply saved.
                </p>
              )}
            </div>
          )}

          <div>
            <h3 className="font-semibold">
              Retrieved sources
            </h3>

            {result.sources.length > 0 ? (
              <div className="mt-3 space-y-3">
                {result.sources.map(
                  (source) => (
                    <div
                      key={`${source.article_id}-${source.article_title}`}
                      className="rounded-xl border border-slate-800 bg-slate-950 p-4"
                    >
                      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                        <p className="font-semibold">
                          {
                            source.article_title
                          }
                        </p>

                        <p className="text-xs text-slate-500">
                          Similarity:{" "}
                          {(
                            source.similarity *
                            100
                          ).toFixed(1)}
                          %
                        </p>
                      </div>

                      {source.source_url && (
                        <a
                          href={
                            source.source_url
                          }
                          target="_blank"
                          rel="noreferrer"
                          className="mt-2 inline-block text-sm text-emerald-400 hover:text-emerald-300"
                        >
                          Open source
                        </a>
                      )}
                    </div>
                  ),
                )}
              </div>
            ) : (
              <p className="mt-3 text-sm text-slate-400">
                No sufficiently relevant
                Knowledge Base sources were found.
              </p>
            )}
          </div>

          <div className="flex flex-wrap gap-x-6 gap-y-2 text-xs text-slate-500">
            <span>
              Provider: {result.provider}
            </span>

            <span>
              Suggestion #{result.suggestion_id}
            </span>
          </div>
        </div>
      )}

      {!result && canGenerate && (
        <p className="mt-6 text-sm text-slate-400">
          No suggested reply generated yet.
        </p>
      )}
    </section>
  );
}