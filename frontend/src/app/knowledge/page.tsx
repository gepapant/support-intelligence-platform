import Link from "next/link";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import KnowledgeManager from "@/components/knowledge/knowledge-manager";
import {
  getCurrentUser,
  getKnowledgeArticles,
} from "@/lib/api";

async function KnowledgeContent() {
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

  if (user.role !== "admin") {
    redirect("/dashboard");
  }

  const articles =
    await getKnowledgeArticles(token);

  const activeArticles = articles.filter(
    (article) => article.is_active,
  ).length;

  const inactiveArticles =
    articles.length - activeArticles;

  return (
    <>
      <header className="flex flex-col gap-5 border-b border-slate-800 pb-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-widest text-emerald-400">
            Support Intelligence
          </p>

          <h1 className="mt-2 text-2xl font-bold">
            Knowledge Base
          </h1>

          <p className="mt-2 text-sm text-slate-400">
            Manage the knowledge used by the
            RAG assistant.
          </p>
        </div>

        <Link
          href="/dashboard"
          className="rounded-lg border border-slate-700 px-4 py-2 text-center text-sm font-semibold text-slate-300 transition hover:bg-slate-900"
        >
          ← Ticket workspace
        </Link>
      </header>

      <section className="mt-8 grid gap-4 sm:grid-cols-3">
        <article className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">
            Total articles
          </p>

          <p className="mt-2 text-3xl font-bold">
            {articles.length}
          </p>
        </article>

        <article className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">
            Active
          </p>

          <p className="mt-2 text-3xl font-bold text-emerald-300">
            {activeArticles}
          </p>
        </article>

        <article className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
          <p className="text-sm text-slate-400">
            Inactive
          </p>

          <p className="mt-2 text-3xl font-bold text-slate-400">
            {inactiveArticles}
          </p>
        </article>
      </section>

      <section className="mt-10">
        <KnowledgeManager
          articles={articles}
        />
      </section>
    </>
  );
}

function KnowledgeFallback() {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8 text-slate-400">
      Loading Knowledge Base...
    </div>
  );
}

export default function KnowledgePage() {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto max-w-7xl">
        <Suspense
          fallback={<KnowledgeFallback />}
        >
          <KnowledgeContent />
        </Suspense>
      </div>
    </main>
  );
}