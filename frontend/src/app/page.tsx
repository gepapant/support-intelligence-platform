import Link from "next/link";
import { Suspense } from "react";

import { getBackendHealth } from "@/lib/api";


async function BackendStatus() {
  let backendOnline = false;

  try {
    const health =
      await getBackendHealth();

    backendOnline =
      health.status === "ok";
  } catch {
    backendOnline = false;
  }

  return (
    <div className="flex items-center gap-3">
      <span
        className={`h-2.5 w-2.5 rounded-full ${
          backendOnline
            ? "bg-emerald-400"
            : "bg-red-400"
        }`}
      />

      <span className="text-sm text-slate-400">
        API{" "}
        {backendOnline
          ? "online"
          : "offline"}
      </span>
    </div>
  );
}


function BackendStatusFallback() {
  return (
    <span className="text-sm text-slate-500">
      Checking API...
    </span>
  );
}


const features = [
  {
    title: "Ticket Operations",
    description:
      "Manage support tickets with assignment, priorities, workflow states, filtering, and role-based access.",
  },
  {
    title: "AI Triage",
    description:
      "Analyze incoming tickets for category, sentiment, suggested priority, and concise support summaries.",
  },
  {
    title: "RAG Assistance",
    description:
      "Retrieve relevant Knowledge Base content and generate grounded reply suggestions with source references.",
  },
  {
    title: "Human Review",
    description:
      "Accept, edit, or reject AI-assisted replies while preserving a review and decision audit trail.",
  },
  {
    title: "Knowledge Pipeline",
    description:
      "Index support knowledge asynchronously with Celery, vector retrieval, failure states, and retry recovery.",
  },
  {
    title: "Support Analytics",
    description:
      "Monitor workload, priorities, AI categories, customer sentiment, and 7/30-day ticket trends.",
  },
];


export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-7xl px-6 py-10">
        <nav className="flex items-center justify-between border-b border-slate-800 pb-6">
          <div>
            <p className="font-bold">
              Support Intelligence
            </p>

            <Suspense
              fallback={
                <BackendStatusFallback />
              }
            >
              <BackendStatus />
            </Suspense>
          </div>

          <Link
            href="/login"
            className="rounded-lg bg-blue-600 px-5 py-2 text-sm font-semibold transition hover:bg-blue-500"
          >
            Sign in
          </Link>
        </nav>

        <section className="py-20 lg:py-28">
          <div className="max-w-4xl">
            <p className="text-sm font-semibold uppercase tracking-[0.25em] text-blue-400">
              AI-assisted support operations
            </p>

            <h1 className="mt-6 text-5xl font-bold tracking-tight sm:text-6xl lg:text-7xl">
              Support operations,
              intelligence, and AI
              assistance in one platform.
            </h1>

            <p className="mt-7 max-w-3xl text-lg leading-8 text-slate-400 sm:text-xl">
              A full-stack support
              operations platform combining
              ticket workflows, AI triage,
              retrieval-augmented assistance,
              asynchronous knowledge
              indexing, human review, and
              operational analytics.
            </p>

            <div className="mt-10 flex flex-wrap gap-4">
              <Link
                href="/login"
                className="rounded-lg bg-blue-600 px-6 py-3 font-semibold transition hover:bg-blue-500"
              >
                Open workspace
              </Link>

              <a
                href="https://github.com/gepapant/support-intelligence-platform"
                target="_blank"
                rel="noreferrer"
                className="rounded-lg border border-slate-700 px-6 py-3 font-semibold text-slate-300 transition hover:bg-slate-900"
              >
                View source
              </a>
            </div>
          </div>
        </section>

        <section className="border-t border-slate-800 py-14">
          <div className="mb-8">
            <p className="text-sm font-semibold uppercase tracking-widest text-slate-500">
              Platform capabilities
            </p>

            <h2 className="mt-3 text-3xl font-bold">
              Built as a complete support
              workflow
            </h2>
          </div>

          <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {features.map(
              (feature) => (
                <article
                  key={feature.title}
                  className="rounded-2xl border border-slate-800 bg-slate-900 p-6"
                >
                  <h3 className="text-lg font-bold">
                    {feature.title}
                  </h3>

                  <p className="mt-3 text-sm leading-6 text-slate-400">
                    {
                      feature.description
                    }
                  </p>
                </article>
              ),
            )}
          </div>
        </section>

        <section className="border-t border-slate-800 py-14">
          <p className="text-sm font-semibold uppercase tracking-widest text-slate-500">
            Engineering stack
          </p>

          <div className="mt-6 flex flex-wrap gap-3">
            {[
              "FastAPI",
              "PostgreSQL",
              "SQLAlchemy",
              "Alembic",
              "pgvector",
              "Celery",
              "Redis-compatible queue",
              "Next.js",
              "TypeScript",
              "React",
              "Tailwind CSS",
              "Recharts",
              "JWT / RBAC",
              "Pytest",
              "GitHub Actions",
            ].map((technology) => (
              <span
                key={technology}
                className="rounded-full border border-slate-700 bg-slate-900 px-4 py-2 text-sm text-slate-300"
              >
                {technology}
              </span>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}