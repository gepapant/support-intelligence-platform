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
      </div>
    </main>
  );
}