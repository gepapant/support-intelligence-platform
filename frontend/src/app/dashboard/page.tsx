import { Suspense } from "react";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { getCurrentUser } from "@/lib/api";

import LogoutButton from "./logout-button";

async function DashboardContent() {
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

  return (
    <>
      <header className="flex items-center justify-between border-b border-slate-800 pb-6">
        <div>
          <p className="text-sm font-semibold uppercase tracking-widest text-blue-400">
            Support Intelligence
          </p>

          <h1 className="mt-2 text-2xl font-bold">
            Dashboard
          </h1>
        </div>

        <LogoutButton />
      </header>

      <section className="mt-10">
        <p className="text-sm text-slate-400">
          Signed in as
        </p>

        <h2 className="mt-2 text-3xl font-bold">
          {user.email}
        </h2>

        <p className="mt-3 text-slate-400">
          Role:{" "}
          <span className="font-semibold text-slate-200">
            {user.role}
          </span>
        </p>
      </section>
    </>
  );
}

function DashboardFallback() {
  return (
    <p className="text-slate-400">
      Loading workspace...
    </p>
  );
}

export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto max-w-6xl">
        <Suspense
          fallback={<DashboardFallback />}
        >
          <DashboardContent />
        </Suspense>
      </div>
    </main>
  );
}