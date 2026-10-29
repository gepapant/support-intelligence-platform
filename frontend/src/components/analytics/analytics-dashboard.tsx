"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type {
  AnalyticsSummary,
  AnalyticsTrends,
} from "@/lib/api";

type AnalyticsDashboardProps = {
  summary: AnalyticsSummary;
  trends: AnalyticsTrends;
};

function formatLabel(
  value: string,
) {
  return value
    .replaceAll("_", " ")
    .replace(
      /\b\w/g,
      (character) =>
        character.toUpperCase(),
    );
}

function recordToChartData(
  values: Record<string, number>,
  order: string[],
) {
  return order.map((key) => ({
    name: formatLabel(key),
    value: values[key] ?? 0,
  }));
}

export default function AnalyticsDashboard({
  summary,
  trends,
}: AnalyticsDashboardProps) {
  const trendData =
    trends.created_per_day.map(
      (point) => ({
        date: new Date(
          `${point.date}T00:00:00`,
        ).toLocaleDateString(
          "en-GB",
          {
            day: "2-digit",
            month: "short",
          },
        ),
        tickets: point.tickets_created,
      }),
    );

  const statusData =
    recordToChartData(
      summary.status_counts,
      [
        "open",
        "in_progress",
        "closed",
      ],
    );

  const priorityData =
    recordToChartData(
      summary.priority_counts,
      [
        "low",
        "medium",
        "high",
      ],
    );

  const categoryData =
    recordToChartData(
      summary.category_counts,
      [
        "account",
        "billing",
        "technical",
        "refund",
        "feature_request",
        "other",
      ],
    );

  const sentimentData =
    recordToChartData(
      summary.sentiment_counts,
      [
        "negative",
        "neutral",
        "positive",
      ],
    );

  return (
    <div className="space-y-8">
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <article className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">
            Total tickets
          </p>

          <p className="mt-2 text-3xl font-bold">
            {summary.total_tickets}
          </p>
        </article>

        <article className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">
            Unassigned
          </p>

          <p className="mt-2 text-3xl font-bold text-amber-300">
            {
              summary.unassigned_tickets
            }
          </p>
        </article>

        <article className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">
            AI analyzed
          </p>

          <p className="mt-2 text-3xl font-bold text-blue-300">
            {
              summary.ai_analyzed_tickets
            }
          </p>
        </article>

        <article className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">
            High priority active
          </p>

          <p className="mt-2 text-3xl font-bold text-orange-300">
            {
              summary
                .high_priority_active_tickets
            }
          </p>
        </article>

        <article className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">
            Negative active
          </p>

          <p className="mt-2 text-3xl font-bold text-red-300">
            {
              summary
                .negative_active_tickets
            }
          </p>
        </article>
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <div className="mb-6">
          <h2 className="text-lg font-bold">
            Ticket volume
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Tickets created during the last{" "}
            {trends.days} days.
          </p>
        </div>

        <div className="h-80">
          <ResponsiveContainer
            width="100%"
            height="100%"
          >
            <LineChart
              data={trendData}
              margin={{
                top: 10,
                right: 20,
                bottom: 10,
                left: 0,
              }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#334155"
              />

              <XAxis
                dataKey="date"
                stroke="#94a3b8"
                tickLine={false}
              />

              <YAxis
                allowDecimals={false}
                stroke="#94a3b8"
                tickLine={false}
              />

              <Tooltip
                contentStyle={{
                  backgroundColor:
                    "#0f172a",
                  border:
                    "1px solid #334155",
                  borderRadius: "8px",
                }}
              />

              <Line
                type="monotone"
                dataKey="tickets"
                stroke="#60a5fa"
                strokeWidth={3}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <ChartCard
          title="Tickets by status"
          description="Current ticket workflow distribution."
          data={statusData}
        />

        <ChartCard
          title="Tickets by priority"
          description="Priority distribution across all tickets."
          data={priorityData}
        />

        <ChartCard
          title="AI categories"
          description="AI-detected support request categories."
          data={categoryData}
        />

        <ChartCard
          title="Customer sentiment"
          description="AI sentiment distribution for analyzed tickets."
          data={sentimentData}
        />
      </section>
    </div>
  );
}

type ChartCardProps = {
  title: string;
  description: string;
  data: {
    name: string;
    value: number;
  }[];
};

function ChartCard({
  title,
  description,
  data,
}: ChartCardProps) {
  return (
    <article className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <div className="mb-6">
        <h2 className="text-lg font-bold">
          {title}
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          {description}
        </p>
      </div>

      <div className="h-72">
        <ResponsiveContainer
          width="100%"
          height="100%"
        >
          <BarChart
            data={data}
            margin={{
              top: 10,
              right: 10,
              bottom: 20,
              left: 0,
            }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#334155"
            />

            <XAxis
              dataKey="name"
              stroke="#94a3b8"
              tickLine={false}
              fontSize={12}
            />

            <YAxis
              allowDecimals={false}
              stroke="#94a3b8"
              tickLine={false}
            />

            <Tooltip
              contentStyle={{
                backgroundColor:
                  "#0f172a",
                border:
                  "1px solid #334155",
                borderRadius: "8px",
              }}
            />

            <Bar
              dataKey="value"
              fill="#60a5fa"
              radius={[6, 6, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </article>
  );
}