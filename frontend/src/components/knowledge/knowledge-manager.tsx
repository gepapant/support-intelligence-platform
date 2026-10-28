"use client";

import {
  FormEvent,
  useEffect,
  useState,
} from "react";
import { useRouter } from "next/navigation";

import type {
  KnowledgeArticle,
} from "@/lib/api";

type KnowledgeManagerProps = {
  articles: KnowledgeArticle[];
};

export default function KnowledgeManager({
  articles,
}: KnowledgeManagerProps) {
  const router = useRouter();

  const [title, setTitle] = useState("");
  const [content, setContent] =
    useState("");
  const [sourceUrl, setSourceUrl] =
    useState("");

  const [creating, setCreating] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const [message, setMessage] =
    useState<string | null>(null);

  const [editingId, setEditingId] =
    useState<number | null>(null);

  const [editTitle, setEditTitle] =
    useState("");

  const [editContent, setEditContent] =
    useState("");

  const [editSourceUrl, setEditSourceUrl] =
    useState("");

  const [savingId, setSavingId] =
    useState<number | null>(null);

  const [reindexingId, setReindexingId] =
    useState<number | null>(null);

  const [retryingId, setRetryingId] =
    useState<number | null>(null);

  const hasIndexingWork = articles.some(
    (article) =>
      article.indexing_status === "queued" ||
      article.indexing_status === "indexing",
  );

  useEffect(() => {
    if (!hasIndexingWork) {
      return;
    }

    const interval = window.setInterval(
      () => {
        router.refresh();
      },
      2000,
    );

    return () => {
      window.clearInterval(interval);
    };
  }, [hasIndexingWork, router]);

  function clearFeedback() {
    setError(null);
    setMessage(null);
  }

  async function handleCreate(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    clearFeedback();

    if (
      !title.trim() ||
      !content.trim()
    ) {
      setError(
        "Title and content are required.",
      );
      return;
    }

    setCreating(true);

    try {
      const response = await fetch(
        "/api/knowledge",
        {
          method: "POST",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            title: title.trim(),
            content: content.trim(),
            source_url:
              sourceUrl.trim() || null,
          }),
        },
      );

      const data = await response.json();

      if (!response.ok) {
        setError(
          data.detail ??
            "Unable to create article",
        );
        return;
      }

      setTitle("");
      setContent("");
      setSourceUrl("");

      if (
        data.indexing_status === "failed"
      ) {
        setMessage(
          "Article created, but indexing could not be queued.",
        );
      } else {
        setMessage(
          "Article created and queued for indexing.",
        );
      }

      router.refresh();
    } catch {
      setError(
        "Unable to connect to the server",
      );
    } finally {
      setCreating(false);
    }
  }

  function startEditing(
    article: KnowledgeArticle,
  ) {
    clearFeedback();

    setEditingId(article.id);
    setEditTitle(article.title);
    setEditContent(article.content);
    setEditSourceUrl(
      article.source_url ?? "",
    );
  }

  function cancelEditing() {
    setEditingId(null);
  }

  async function saveEdit(
    articleId: number,
  ) {
    clearFeedback();

    if (
      !editTitle.trim() ||
      !editContent.trim()
    ) {
      setError(
        "Title and content are required.",
      );
      return;
    }

    setSavingId(articleId);

    try {
      const response = await fetch(
        `/api/knowledge/${articleId}`,
        {
          method: "PATCH",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            title: editTitle.trim(),
            content: editContent.trim(),
            source_url:
              editSourceUrl.trim() || null,
          }),
        },
      );

      const data = await response.json();

      if (!response.ok) {
        setError(
          data.detail ??
            "Unable to update article",
        );
        return;
      }

      setEditingId(null);

      if (
        data.indexing_status === "failed"
      ) {
        setMessage(
          "Article updated, but re-indexing could not be queued.",
        );
      } else {
        setMessage(
          "Article updated. Re-indexing queued.",
        );
      }

      router.refresh();
    } catch {
      setError(
        "Unable to connect to the server",
      );
    } finally {
      setSavingId(null);
    }
  }

  async function toggleActive(
    article: KnowledgeArticle,
  ) {
    clearFeedback();

    setSavingId(article.id);

    try {
      const response = await fetch(
        `/api/knowledge/${article.id}`,
        {
          method: "PATCH",
          headers: {
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            is_active:
              !article.is_active,
          }),
        },
      );

      const data = await response.json();

      if (!response.ok) {
        setError(
          data.detail ??
            "Unable to update article",
        );
        return;
      }

      setMessage(
        article.is_active
          ? "Article deactivated."
          : "Article activated.",
      );

      router.refresh();
    } catch {
      setError(
        "Unable to connect to the server",
      );
    } finally {
      setSavingId(null);
    }
  }

  async function retryIndexing(
    articleId: number,
  ) {
    clearFeedback();

    setRetryingId(articleId);

    try {
      const response = await fetch(
        `/api/knowledge/${articleId}/reindex`,
        {
          method: "POST",
        },
      );

      const data = await response.json();

      if (!response.ok) {
        setError(
          data.detail ??
            "Unable to retry indexing",
        );
        return;
      }

      setMessage(
        "Indexing retry queued.",
      );

      router.refresh();
    } catch {
      setError(
        "Unable to connect to the indexing service",
      );
    } finally {
      setRetryingId(null);
    }
  }

  async function reindexArticle(
    articleId: number,
  ) {
    clearFeedback();

    setReindexingId(articleId);

    try {
      const response = await fetch(
        `/api/knowledge/${articleId}/reindex`,
        {
          method: "POST",
        },
      );

      const data = await response.json();

      if (!response.ok) {
        setError(
          data.detail ??
            "Unable to re-index article",
        );
        return;
      }

      setMessage(
        "Re-indexing queued.",
      );

      router.refresh();
    } catch {
      setError(
        "Unable to connect to the indexing service",
      );
    } finally {
      setReindexingId(null);
    }
  }

  return (
    <div className="space-y-8">
      <form
        onSubmit={handleCreate}
        className="rounded-2xl border border-slate-800 bg-slate-900 p-6"
      >
        <h2 className="text-xl font-bold">
          Create article
        </h2>

        <p className="mt-2 text-sm text-slate-400">
          New content is automatically queued
          for background indexing and RAG
          retrieval.
        </p>

        <div className="mt-6 space-y-4">
          <div>
            <label
              htmlFor="knowledge-title"
              className="text-sm text-slate-300"
            >
              Title
            </label>

            <input
              id="knowledge-title"
              value={title}
              onChange={(event) =>
                setTitle(event.target.value)
              }
              className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
            />
          </div>

          <div>
            <label
              htmlFor="knowledge-content"
              className="text-sm text-slate-300"
            >
              Content
            </label>

            <textarea
              id="knowledge-content"
              value={content}
              onChange={(event) =>
                setContent(
                  event.target.value,
                )
              }
              rows={6}
              className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
            />
          </div>

          <div>
            <label
              htmlFor="knowledge-source"
              className="text-sm text-slate-300"
            >
              Source URL
            </label>

            <input
              id="knowledge-source"
              type="url"
              value={sourceUrl}
              onChange={(event) =>
                setSourceUrl(
                  event.target.value,
                )
              }
              placeholder="https://example.com/help/article"
              className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={creating}
          className="mt-5 rounded-lg bg-emerald-600 px-5 py-2 font-semibold transition hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {creating
            ? "Creating..."
            : "Create article"}
        </button>
      </form>

      {error && (
        <p className="rounded-xl border border-red-900 bg-red-950 p-4 text-sm text-red-300">
          {error}
        </p>
      )}

      {message && (
        <p className="rounded-xl border border-emerald-900 bg-emerald-950 p-4 text-sm text-emerald-300">
          {message}
        </p>
      )}

      <section>
        <h2 className="text-xl font-bold">
          Articles
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Active articles are available to the
          RAG retrieval pipeline.
        </p>

        <div className="mt-5 grid gap-4">
          {articles.length === 0 ? (
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8 text-center text-slate-400">
              No Knowledge Base articles yet.
            </div>
          ) : (
            articles.map((article) => {
              const isEditing =
                editingId === article.id;

              return (
                <article
                  key={article.id}
                  className="rounded-2xl border border-slate-800 bg-slate-900 p-6"
                >
                  {isEditing ? (
                    <div className="space-y-4">
                      <input
                        value={editTitle}
                        onChange={(event) =>
                          setEditTitle(
                            event.target.value,
                          )
                        }
                        className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 font-semibold"
                      />

                      <textarea
                        value={editContent}
                        onChange={(event) =>
                          setEditContent(
                            event.target.value,
                          )
                        }
                        rows={7}
                        className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
                      />

                      <input
                        type="url"
                        value={editSourceUrl}
                        onChange={(event) =>
                          setEditSourceUrl(
                            event.target.value,
                          )
                        }
                        placeholder="Source URL"
                        className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2"
                      />

                      <div className="flex flex-wrap gap-3">
                        <button
                          type="button"
                          disabled={
                            savingId ===
                            article.id
                          }
                          onClick={() =>
                            saveEdit(
                              article.id,
                            )
                          }
                          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold hover:bg-blue-500 disabled:opacity-60"
                        >
                          {savingId ===
                          article.id
                            ? "Saving..."
                            : "Save changes"}
                        </button>

                        <button
                          type="button"
                          onClick={
                            cancelEditing
                          }
                          className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-semibold"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                        <div>
                          <div className="flex flex-wrap items-center gap-3">
                            <h3 className="text-lg font-bold">
                              {article.title}
                            </h3>

                            <span
                              className={`rounded-full px-3 py-1 text-xs font-semibold ${
                                article.is_active
                                  ? "bg-emerald-950 text-emerald-300"
                                  : "bg-slate-800 text-slate-400"
                              }`}
                            >
                              {article.is_active
                                ? "Active"
                                : "Inactive"}
                            </span>

                            <span
                              className={`rounded-full px-3 py-1 text-xs font-semibold ${
                                article.indexing_status ===
                                "ready"
                                  ? "bg-emerald-950 text-emerald-300"
                                  : article.indexing_status ===
                                      "failed"
                                    ? "bg-red-950 text-red-300"
                                    : article.indexing_status ===
                                        "indexing"
                                      ? "bg-blue-950 text-blue-300"
                                      : "bg-amber-950 text-amber-300"
                              }`}
                            >
                              Index:{" "}
                              {
                                article.indexing_status
                              }
                            </span>
                          </div>

                          <p className="mt-4 whitespace-pre-wrap text-sm leading-6 text-slate-300">
                            {article.content}
                          </p>

                          {article.indexing_status ===
                            "failed" &&
                            article.indexing_error && (
                              <div className="mt-4 rounded-lg border border-red-900 bg-red-950 p-3 text-sm text-red-300">
                                Indexing failed:{" "}
                                {
                                  article.indexing_error
                                }
                              </div>
                            )}

                          {article.indexing_status ===
                            "ready" &&
                            article.indexed_at && (
                              <p className="mt-3 text-xs text-slate-500">
                                Indexed{" "}
                                {new Date(
                                  article.indexed_at,
                                ).toLocaleString()}
                              </p>
                            )}
                        </div>

                        <span className="text-xs text-slate-500">
                          #{article.id}
                        </span>
                      </div>

                      <div className="mt-5 flex flex-wrap gap-3 border-t border-slate-800 pt-4">
                        <button
                          type="button"
                          onClick={() =>
                            startEditing(
                              article,
                            )
                          }
                          className="rounded-lg border border-blue-800 px-4 py-2 text-sm font-semibold text-blue-300 hover:bg-blue-950"
                        >
                          Edit
                        </button>

                        <button
                          type="button"
                          disabled={
                            savingId ===
                            article.id
                          }
                          onClick={() =>
                            toggleActive(
                              article,
                            )
                          }
                          className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-semibold"
                        >
                          {article.is_active
                            ? "Deactivate"
                            : "Activate"}
                        </button>

                        {article.indexing_status ===
                          "failed" && (
                          <button
                            type="button"
                            disabled={
                              retryingId ===
                              article.id
                            }
                            onClick={() =>
                              retryIndexing(
                                article.id,
                              )
                            }
                            className="rounded-lg border border-amber-700 px-4 py-2 text-sm font-semibold text-amber-300 hover:bg-amber-950 disabled:opacity-60"
                          >
                            {retryingId ===
                            article.id
                              ? "Retrying..."
                              : "Retry indexing"}
                          </button>
                        )}

                        <button
                          type="button"
                          disabled={
                            reindexingId ===
                            article.id
                          }
                          onClick={() =>
                            reindexArticle(
                              article.id,
                            )
                          }
                          className="rounded-lg border border-emerald-800 px-4 py-2 text-sm font-semibold text-emerald-300 hover:bg-emerald-950 disabled:opacity-60"
                        >
                          {reindexingId ===
                          article.id
                            ? "Queueing..."
                            : "Re-index"}
                        </button>

                        {article.source_url && (
                          <a
                            href={
                              article.source_url
                            }
                            target="_blank"
                            rel="noreferrer"
                            className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-300"
                          >
                            Open source
                          </a>
                        )}
                      </div>
                    </>
                  )}
                </article>
              );
            })
          )}
        </div>
      </section>
    </div>
  );
}