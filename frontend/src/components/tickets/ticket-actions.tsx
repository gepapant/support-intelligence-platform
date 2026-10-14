"use client";

import {
  FormEvent,
  useState,
} from "react";
import { useRouter } from "next/navigation";

import type {
  Ticket,
  TicketStatus,
  User,
} from "@/lib/api";

type TicketActionsProps = {
  ticket: Ticket;
  user: User;
  assignableUsers: User[];
};

function getNextStatus(
  status: TicketStatus,
): {
  status: TicketStatus;
  label: string;
} {
  switch (status) {
    case "open":
      return {
        status: "in_progress",
        label: "Start progress",
      };

    case "in_progress":
      return {
        status: "closed",
        label: "Close ticket",
      };

    case "closed":
      return {
        status: "open",
        label: "Reopen ticket",
      };
  }
}

export default function TicketActions({
  ticket,
  user,
  assignableUsers,
}: TicketActionsProps) {
  const router = useRouter();

  const [statusLoading, setStatusLoading] =
    useState(false);

  const [statusError, setStatusError] =
    useState<string | null>(null);

  const [
    assignmentLoading,
    setAssignmentLoading,
  ] = useState(false);

  const [
    assignmentError,
    setAssignmentError,
  ] = useState<string | null>(null);

  const [assigneeId, setAssigneeId] =
    useState(
      ticket.assignee_id?.toString() ?? "",
    );

  const canChangeStatus =
    user.role === "admin" ||
    ticket.assignee_id === user.id;

  const nextStatus =
    getNextStatus(ticket.status);

  async function handleStatusChange() {
    setStatusError(null);
    setStatusLoading(true);

    try {
      const response = await fetch(
        `/api/tickets/${ticket.id}/status`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            status: nextStatus.status,
          }),
        },
      );

      const data = await response.json();

      if (!response.ok) {
        setStatusError(
          data.detail ??
            "Unable to update ticket status",
        );
        return;
      }

      router.refresh();
    } catch {
      setStatusError(
        "Unable to connect to the server",
      );
    } finally {
      setStatusLoading(false);
    }
  }

  async function handleAssignment(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setAssignmentError(null);
    setAssignmentLoading(true);

    const parsedAssigneeId =
      assigneeId === ""
        ? null
        : Number(assigneeId);

    try {
      const response = await fetch(
        `/api/tickets/${ticket.id}/assignment`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            assignee_id: parsedAssigneeId,
          }),
        },
      );

      const data = await response.json();

      if (!response.ok) {
        setAssignmentError(
          data.detail ??
            "Unable to update assignment",
        );
        return;
      }

      router.refresh();
    } catch {
      setAssignmentError(
        "Unable to connect to the server",
      );
    } finally {
      setAssignmentLoading(false);
    }
  }

  return (
    <section className="mt-6 space-y-5">
      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <h2 className="font-semibold">
          Workflow
        </h2>

        {canChangeStatus ? (
          <>
            <p className="mt-2 text-sm text-slate-400">
              Current status:{" "}
              <span className="font-semibold text-slate-200">
                {ticket.status}
              </span>
            </p>

            <button
              type="button"
              onClick={handleStatusChange}
              disabled={statusLoading}
              className="mt-4 rounded-lg bg-blue-600 px-4 py-2 font-semibold transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {statusLoading
                ? "Updating..."
                : nextStatus.label}
            </button>

            {statusError && (
              <p className="mt-3 text-sm text-red-400">
                {statusError}
              </p>
            )}
          </>
        ) : (
          <p className="mt-2 text-sm text-slate-400">
            Only the assigned agent or an admin
            can change this ticket&apos;s status.
          </p>
        )}
      </div>

      {user.role === "admin" && (
        <form
          onSubmit={handleAssignment}
          className="rounded-2xl border border-slate-800 bg-slate-900 p-6"
        >
          <h2 className="font-semibold">
            Assignment
          </h2>

          <label
            htmlFor="assignee"
            className="mt-4 block text-sm text-slate-400"
          >
            Assign to agent
          </label>

          <select
            id="assignee"
            value={assigneeId}
            onChange={(event) =>
              setAssigneeId(
                event.target.value,
              )
            }
            className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
          >
            <option value="">
              Unassigned
            </option>

            {assignableUsers.map(
              (assignableUser) => (
                <option
                  key={assignableUser.id}
                  value={assignableUser.id}
                >
                  {assignableUser.email}
                </option>
              ),
            )}
          </select>

          <button
            type="submit"
            disabled={assignmentLoading}
            className="mt-4 rounded-lg bg-blue-600 px-4 py-2 font-semibold transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {assignmentLoading
              ? "Saving..."
              : "Save assignment"}
          </button>

          {assignmentError && (
            <p className="mt-3 text-sm text-red-400">
              {assignmentError}
            </p>
          )}
        </form>
      )}
    </section>
  );
}