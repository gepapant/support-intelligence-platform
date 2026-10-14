import { Suspense } from "react";

import { getBackendHealth } from "@/lib/api";

async function BackendStatus() {
  let backendOnline = false;

  try {
    const health = await getBackendHealth();
    backendOnline = health.status === "ok";
  } catch {
    backendOnline = false;
  }

  return (
    <article className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <p className="text-sm text-slate-400">
        Backend API
      </p>

      <div className="mt-4 flex items-center gap-3">
        <span
          className={`h-3 w-3 rounded-full ${
            backendOnline
              ? "bg-emerald-400"
              : "bg-red-400"
          }`}
        />

        <span className="font-semibold">
          {backendOnline ? "Online" : "Offline"}
        </span>
      </div>
    </article>
  );
}

function BackendStatusFallback() {
  return (
    <article className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <p className="text-sm text-slate-400">
        Backend API
      </p>

      <p className="mt-4 font-semibold text-slate-400">
        Checking...
      </p>
    </article>
  );
}

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <header className="mb-16">
          <p className="mb-3 text-sm font-semibold uppercase tracking-widest text-blue-400">
            Support Operations
          </p>

          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
            Support Intelligence Platform
          </h1>

          <p className="mt-5 max-w-2xl text-lg text-slate-400">
            AI-assisted ticket management, workflow automation,
            knowledge retrieval, and support analytics.
          </p>
        </header>

        <section className="grid gap-6 md:grid-cols-3">
          <Suspense fallback={<BackendStatusFallback />}>
            <BackendStatus />
          </Suspense>

          <article className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-sm text-slate-400">
              Ticket workspace
            </p>

            <p className="mt-4 text-2xl font-semibold">
              Coming next
            </p>
          </article>

          <article className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <p className="text-sm text-slate-400">
              AI assistance
            </p>

            <p className="mt-4 text-2xl font-semibold">
              Planned
            </p>
          </article>
        </section>
      </div>
    </main>
  );
}