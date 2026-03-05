/** Owner dashboard route for sticker registration, loss reporting, and inbox replies. */
import { useQuery } from "@tanstack/react-query";
import { useState } from "preact/hooks";

import {
  ApiError,
  listOwnerMessages,
  markItemLost,
  registerSticker,
  sendOwnerMessage,
} from "../lib/api/client";

export function InboxRoute() {
  const [stickerCode, setStickerCode] = useState("");
  const [itemName, setItemName] = useState("");
  const [itemCategory, setItemCategory] = useState("general");
  const [itemDescription, setItemDescription] = useState("");
  const [registeredItemId, setRegisteredItemId] = useState("");
  const [sessionToken, setSessionToken] = useState("");
  const [replyMessage, setReplyMessage] = useState("");
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");

  const inboxQuery = useQuery({
    queryKey: ["owner", "messages"],
    queryFn: listOwnerMessages,
    refetchInterval: 8000,
  });

  async function handleRegister(event: Event) {
    event.preventDefault();
    setError("");
    setNotice("");
    try {
      const response = await registerSticker({
        sticker_code: stickerCode.trim(),
        item_name: itemName.trim(),
        item_category: itemCategory.trim(),
        item_description: itemDescription.trim(),
      });
      setRegisteredItemId(response.item_id);
      setNotice(`Sticker ${response.sticker_code} registered successfully.`);
    } catch (err: unknown) {
      if (err instanceof ApiError && err.status === 401) {
        setError("Please login first to register stickers.");
      } else if (err instanceof ApiError && err.status === 409) {
        setError("Sticker code already exists.");
      } else {
        setError("Failed to register sticker.");
      }
    }
  }

  async function handleMarkLost(event: Event) {
    event.preventDefault();
    if (!registeredItemId) {
      setError("Register a sticker first to get an item id.");
      return;
    }
    setError("");
    try {
      await markItemLost(registeredItemId, {
        last_known_location: "Not specified",
        notes: "Marked lost from owner dashboard",
      });
      setNotice("Item marked as lost. Finder scans will now trigger alerts.");
    } catch {
      setError("Failed to mark item as lost.");
    }
  }

  async function handleReply(event: Event) {
    event.preventDefault();
    if (!sessionToken.trim()) {
      setError("Provide a session reference from the inbox list.");
      return;
    }
    setError("");
    try {
      await sendOwnerMessage(sessionToken.trim(), { message_body: replyMessage.trim() });
      setReplyMessage("");
      setNotice("Reply sent to finder.");
    } catch {
      setError("Could not send owner reply. Check session reference validity.");
    }
  }

  return (
    <section className="grid gap-6 lg:grid-cols-2">
      <article className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
        <h1 className="text-xl font-semibold">Owner Recovery Dashboard</h1>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
          Register stickers, report loss, and manage anonymous communication.
        </p>

        <form className="mt-5 grid gap-3" onSubmit={handleRegister}>
          <input
            required
            value={stickerCode}
            onInput={(event) => setStickerCode((event.target as HTMLInputElement).value)}
            className="rounded border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
            placeholder="Sticker code (SAFE-ABCD-001)"
          />
          <input
            required
            value={itemName}
            onInput={(event) => setItemName((event.target as HTMLInputElement).value)}
            className="rounded border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
            placeholder="Item name"
          />
          <input
            required
            value={itemCategory}
            onInput={(event) => setItemCategory((event.target as HTMLInputElement).value)}
            className="rounded border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
            placeholder="Category"
          />
          <textarea
            value={itemDescription}
            onInput={(event) => setItemDescription((event.target as HTMLTextAreaElement).value)}
            className="min-h-24 rounded border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
            placeholder="Description"
          />
          <button
            type="submit"
            className="rounded bg-brand-500 px-4 py-2 font-medium text-white hover:bg-brand-700"
          >
            Register Sticker
          </button>
        </form>

        <form className="mt-4" onSubmit={handleMarkLost}>
          <button
            type="submit"
            className="rounded border border-brand-500 px-4 py-2 text-brand-700 hover:bg-brand-50 dark:text-brand-400 dark:hover:bg-slate-800"
          >
            Mark Registered Item Lost
          </button>
        </form>
      </article>

      <article className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
        <h2 className="text-lg font-semibold">Anonymous Inbox</h2>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
          Use `session_reference` from messages to send owner-side replies.
        </p>

        <div className="mt-4 max-h-64 space-y-3 overflow-auto pr-2">
          {inboxQuery.isPending && <p className="text-sm text-slate-500">Loading messages...</p>}
          {inboxQuery.isError && (
            <p className="text-sm text-red-600">Unable to load inbox. Ensure you are logged in.</p>
          )}
          {inboxQuery.data?.messages.map((message) => (
            <article
              key={`${message.session_reference}-${message.created_at}`}
              className="rounded border border-slate-200 p-3 text-sm dark:border-slate-700"
            >
              <p className="font-medium">
                {message.sender_role} • session {message.session_reference}
              </p>
              <p className="mt-1 text-slate-700 dark:text-slate-300">{message.body}</p>
            </article>
          ))}
        </div>

        <form className="mt-5 grid gap-3" onSubmit={handleReply}>
          <input
            required
            value={sessionToken}
            onInput={(event) => setSessionToken((event.target as HTMLInputElement).value)}
            className="rounded border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
            placeholder="Session reference from inbox"
          />
          <textarea
            required
            value={replyMessage}
            onInput={(event) => setReplyMessage((event.target as HTMLTextAreaElement).value)}
            className="min-h-24 rounded border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
            placeholder="Reply message"
          />
          <button
            type="submit"
            className="rounded bg-brand-500 px-4 py-2 font-medium text-white hover:bg-brand-700"
          >
            Send Reply
          </button>
        </form>

        {error && (
          <p className="mt-4 rounded border border-red-300 bg-red-50 p-2 text-sm text-red-700 dark:border-red-700 dark:bg-red-950/40 dark:text-red-300">
            {error}
          </p>
        )}
        {notice && (
          <p className="mt-4 rounded border border-emerald-300 bg-emerald-50 p-2 text-sm text-emerald-700 dark:border-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-300">
            {notice}
          </p>
        )}
      </article>
    </section>
  );
}
