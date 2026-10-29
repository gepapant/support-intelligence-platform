import Link from "next/link";

import LoginForm from "./login-form";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-slate-100">
      <div className="w-full max-w-md">
        <div className="mb-8">
          <p className="text-sm font-semibold uppercase tracking-widest text-blue-400">
            Support Intelligence
          </p>

          <h1 className="mt-3 text-3xl font-bold">
            Sign in
          </h1>

          <p className="mt-2 text-slate-400">
            Access your support workspace.
          </p>
        </div>

        <LoginForm />

        <p className="mt-6 text-center text-sm text-slate-400">
          Don&apos;t have an account?{" "}
          <Link
            href="/register"
            className="font-semibold text-blue-400 transition hover:text-blue-300"
          >
            Create account
          </Link>
        </p>
      </div>
    </main>
  );
}