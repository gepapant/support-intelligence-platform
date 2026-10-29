import Link from "next/link";

import RegisterForm from "./register-form";

export default function RegisterPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 py-10 text-slate-100">
      <div className="w-full max-w-md">
        <div className="mb-8">
          <p className="text-sm font-semibold uppercase tracking-widest text-blue-400">
            Support Intelligence
          </p>

          <h1 className="mt-3 text-3xl font-bold">
            Create account
          </h1>

          <p className="mt-2 text-slate-400">
            Join the support workspace
            as an agent.
          </p>
        </div>

        <RegisterForm />

        <p className="mt-6 text-center text-sm text-slate-400">
          Already have an account?{" "}
          <Link
            href="/login"
            className="font-semibold text-blue-400 transition hover:text-blue-300"
          >
            Sign in
          </Link>
        </p>
      </div>
    </main>
  );
}