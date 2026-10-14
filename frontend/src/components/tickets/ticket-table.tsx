import type {
  Ticket,
  TicketPriority,
  TicketStatus,
} from "@/lib/api";

import Link from "next/link";

type TicketTableProps = {
  tickets: Ticket[];
};

function getStatusLabel(
  status: TicketStatus,
) {
  switch (status) {
    case "open":
      return "Open";

    case "in_progress":
      return "In progress";

    case "closed":
      return "Closed";
  }
}

function getStatusClasses(
  status: TicketStatus,
) {
  switch (status) {
    case "open":
      return "bg-blue-500/10 text-blue-300";

    case "in_progress":
      return "bg-amber-500/10 text-amber-300";

    case "closed":
      return "bg-emerald-500/10 text-emerald-300";
  }
}

function getPriorityClasses(
  priority: TicketPriority,
) {
  switch (priority) {
    case "low":
      return "text-slate-400";

    case "medium":
      return "text-amber-300";

    case "high":
      return "text-red-300";
  }
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(value));
}

export default function TicketTable({
  tickets,
}: TicketTableProps) {
  if (tickets.length === 0) {
    return (
      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-10 text-center">
        <p className="font-semibold">
          No tickets found
        </p>

        <p className="mt-2 text-sm text-slate-400">
          Tickets will appear here when they are created.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900">
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead className="border-b border-slate-800 text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th className="px-6 py-4">
                Ticket
              </th>

              <th className="px-6 py-4">
                Status
              </th>

              <th className="px-6 py-4">
                Priority
              </th>

              <th className="px-6 py-4">
                Assignee
              </th>

              <th className="px-6 py-4">
                Created
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-800">
            {tickets.map((ticket) => (
              <tr
                key={ticket.id}
                className="transition hover:bg-slate-800/50"
              >
                <td className="px-6 py-5">
                  <Link
                    href={`/dashboard/tickets/${ticket.id}`}
                    className="font-semibold transition hover:text-blue-300"
                  >
                    {ticket.title}
                  </Link>

                  <p className="mt-1 max-w-md truncate text-sm text-slate-400">
                    {ticket.description}
                  </p>
                </td>

                <td className="px-6 py-5">
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${getStatusClasses(
                      ticket.status,
                    )}`}
                  >
                    {getStatusLabel(
                      ticket.status,
                    )}
                  </span>
                </td>

                <td
                  className={`px-6 py-5 text-sm font-semibold capitalize ${getPriorityClasses(
                    ticket.priority,
                  )}`}
                >
                  {ticket.priority}
                </td>

                <td className="px-6 py-5 text-sm text-slate-300">
                  {ticket.assignee_id
                    ? `#${ticket.assignee_id}`
                    : "Unassigned"}
                </td>

                <td className="px-6 py-5 text-sm text-slate-400">
                  {formatDate(
                    ticket.created_at,
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}