/** Finder scan route for starting session and relaying anonymous message. */
import { useState } from "preact/hooks";

import { ApiError, scanSticker, sendFinderMessage } from "../lib/api/client";

export function ScanRoute() {
  const [stickerCode, setStickerCode] = useState("");
  const [finderNote, setFinderNote] = useState("");
  const [sessionToken, setSessionToken] = useState("");
  const [itemName, setItemName] = useState("");
  const [messageBody, setMessageBody] = useState("");
  const [feedback, setFeedback] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleScan(event: Event) {
    event.preventDefault();
    setError("");
    setFeedback("");
    setIsSubmitting(true);
    try {
      const response = await scanSticker({
        sticker_code: stickerCode.trim(),
        finder_note: finderNote.trim() || undefined,
      });
      setSessionToken(response.session_token);
      setItemName(response.item_name);
      setFeedback("Session created. You can now send a message to the owner.");
    } catch (err: unknown) {
      if (err instanceof ApiError && err.status === 404) {
        setError("Sticker not found. Check the code and try again.");
      } else {
        setError("Unable to start finder session right now.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleSendMessage(event: Event) {
    event.preventDefault();
    if (!sessionToken) {
      setError("Start a session first.");
      return;
    }
    setError("");
    setFeedback("");
    setIsSubmitting(true);
    try {
      await sendFinderMessage(sessionToken, { message_body: messageBody.trim() });
      setMessageBody("");
      setFeedback("Message sent. The owner has been notified.");
    } catch {
      setError("Unable to send message. The session may have expired.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="mx-auto grid max-w-3xl gap-6">
      <article className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
        <h1 className="text-xl font-semibold">Finder Contact Flow</h1>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
          Enter sticker code from QR scan. Owner contact details remain private.
        </p>

        <form className="mt-5 grid gap-4" onSubmit={handleScan}>
          <label className="text-sm font-medium" for="sticker-code">
            Sticker code
          </label>
          <input
            id="sticker-code"
            required
            value={stickerCode}
            onInput={(event) => setStickerCode((event.target as HTMLInputElement).value)}
            className="rounded border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
            placeholder="SAFE-ABCD-001"
          />

          <label className="text-sm font-medium" for="finder-note">
            Optional finder note
          </label>
          <textarea
            id="finder-note"
            value={finderNote}
            onInput={(event) => setFinderNote((event.target as HTMLTextAreaElement).value)}
            className="min-h-24 rounded border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
            placeholder="Where you found the item"
          />

          <button
            type="submit"
            disabled={isSubmitting}
            className="rounded bg-brand-500 px-4 py-2 font-medium text-white hover:bg-brand-700 disabled:opacity-70"
          >
            {isSubmitting ? "Starting..." : "Start Secure Session"}
          </button>
        </form>
      </article>

      <article className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
        <h2 className="text-lg font-semibold">Anonymous Message</h2>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
          {itemName ? `Item: ${itemName}` : "Start a session before sending a message."}
        </p>

        <form className="mt-4 grid gap-4" onSubmit={handleSendMessage}>
          <label className="text-sm font-medium" for="finder-message">
            Message to owner
          </label>
          <textarea
            id="finder-message"
            required
            minLength={1}
            maxLength={2000}
            value={messageBody}
            onInput={(event) => setMessageBody((event.target as HTMLTextAreaElement).value)}
            className="min-h-24 rounded border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
            placeholder="I found your item and can hand it over safely."
          />
          <button
            type="submit"
            disabled={isSubmitting || !sessionToken}
            className="rounded bg-brand-500 px-4 py-2 font-medium text-white hover:bg-brand-700 disabled:opacity-70"
          >
            {isSubmitting ? "Sending..." : "Send Anonymous Message"}
          </button>
        </form>

        {error && (
          <p
            className="mt-4 rounded border border-red-300 bg-red-50 p-2 text-sm text-red-700 dark:border-red-700 dark:bg-red-950/40 dark:text-red-300"
            role="alert"
          >
            {error}
          </p>
        )}
        {feedback && (
          <p className="mt-4 rounded border border-emerald-300 bg-emerald-50 p-2 text-sm text-emerald-700 dark:border-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-300">
            {feedback}
          </p>
        )}
      </article>
    </section>
  );
}
