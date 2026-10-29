"use client";

import {
  FormEvent,
  useState,
} from "react";
import { useRouter } from "next/navigation";

import type {
  TicketPriority,
} from "@/lib/api";

export default function TicketCreate() {
  const router = useRouter();

  const [open, setOpen] =
    useState(false);

  const [title, setTitle] =
    useState("");

  const [
    description,
    setDescription,
  ] = useState("");

  const [priority, setPriority] =
    useState<TicketPriority>(
      "medium",
    );

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setError(null);

    if (
      !title.trim() ||
      !description.trim()
    ) {
      setError(
        "Title and description are required.",
      );
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        "/api/tickets",
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            title: title.trim(),
            description:
              description.trim(),
            priority,
          }),
        },
      );

      const data =
        await response.json();

      if (!response.ok) {
        setError(
          data.detail ??
            "Unable to create ticket",
        );
        return;
      }

      setTitle("");
      setDescription("");
      setPriority("medium");
      setOpen(false);

      router.push(
        `/dashboard/tickets/${data.id}`,
      );

      router.refresh();
    } catch {
      setError(
        "Unable to connect to the server",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <button
        type="button"
        onClick={() =>
          setOpen(true)
        }
        className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-500"
      >
        + Create ticket
      </button>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4">
          <div className="w-full max-w-xl rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-2xl">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold">
                  Create ticket
                </h2>

                <p className="mt-1 text-sm text-slate-400">
                  Add a new support
                  request to the
                  workspace.
                </p>
              </div>

              <button
                type="button"
                onClick={() =>
                  setOpen(false)
                }
                className="text-xl text-slate-400 transition hover:text-white"
              >
                ×
              </button>
            </div>

            <form
              onSubmit={
                handleSubmit
              }
              className="mt-6 space-y-5"
            >
              <div>
                <label
                  htmlFor="ticket-title"
                  className="mb-2 block text-sm font-medium text-slate-300"
                >
                  Title
                </label>

                <input
                  id="ticket-title"
                  value={title}
                  onChange={(event) =>
                    setTitle(
                      event.target.value,
                    )
                  }
                  placeholder="Customer charged twice"
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label
                  htmlFor="ticket-description"
                  className="mb-2 block text-sm font-medium text-slate-300"
                >
                  Description
                </label>

                <textarea
                  id="ticket-description"
                  value={
                    description
                  }
                  onChange={(event) =>
                    setDescription(
                      event.target.value,
                    )
                  }
                  rows={5}
                  placeholder="The customer reports that the same order was charged twice."
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label
                  htmlFor="ticket-priority"
                  className="mb-2 block text-sm font-medium text-slate-300"
                >
                  Priority
                </label>

                <select
                  id="ticket-priority"
                  value={priority}
                  onChange={(event) =>
                    setPriority(
                      event.target
                        .value as TicketPriority,
                    )
                  }
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 outline-none focus:border-blue-500"
                >
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

              {error && (
                <p className="rounded-lg border border-red-900 bg-red-950 p-3 text-sm text-red-300">
                  {error}
                </p>
              )}

              <div className="flex justify-end gap-3 border-t border-slate-800 pt-5">
                <button
                  type="button"
                  onClick={() =>
                    setOpen(false)
                  }
                  disabled={loading}
                  className="rounded-lg border border-slate-700 px-4 py-2 font-semibold text-slate-300"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={loading}
                  className="rounded-lg bg-blue-600 px-5 py-2 font-semibold transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {loading
                    ? "Creating..."
                    : "Create ticket"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}