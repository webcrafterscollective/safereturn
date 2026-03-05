/** Finder scan route for session start, messaging, and claim-issue reporting. */

import { useEffect, useState } from "preact/hooks";
import { Link } from "wouter-preact";

import { ApiError, reportClaimIssue, scanSticker, sendFinderMessage } from "../lib/api/client";

function extractApiErrorCode(error: ApiError): string | null {
  const envelope = error.details as
    | { error?: { code?: string; message?: string } }
    | null
    | undefined;
  return envelope?.error?.code ?? null;
}

export function ScanRoute() {
  const [stickerCode, setStickerCode] = useState("");
  const [finderNote, setFinderNote] = useState("");
  const [sessionToken, setSessionToken] = useState("");
  const [itemName, setItemName] = useState("");
  const [messageBody, setMessageBody] = useState("");
  const [issueNote, setIssueNote] = useState("");
  const [feedback, setFeedback] = useState("");
  const [error, setError] = useState("");
  const [needsClaim, setNeedsClaim] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    if (code) {
      setStickerCode(code);
    }
  }, []);

  async function handleScan(event: Event) {
    event.preventDefault();
    setError("");
    setFeedback("");
    setNeedsClaim(false);
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
      if (err instanceof ApiError) {
        const code = extractApiErrorCode(err);
        if (err.status === 404) {
          setError("Sticker not found. Check the code and try again.");
        } else if (code === "STICKER_UNCLAIMED") {
          setNeedsClaim(true);
          setError(
            "This sticker pack is not claimed yet. Ask the owner to register and claim the pack.",
          );
        } else if (code === "STICKER_DISABLED") {
          setError("This sticker has been disabled.");
        } else {
          setError("Unable to start finder session right now.");
        }
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

  async function handleIssueReport(event: Event) {
    event.preventDefault();
    setError("");
    setFeedback("");
    setIsSubmitting(true);
    try {
      await reportClaimIssue(stickerCode.trim(), issueNote.trim());
      setFeedback("Claim issue submitted. Support will review and issue replacement if needed.");
      setIssueNote("");
    } catch {
      setError("Unable to submit claim issue right now.");
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
            placeholder="SR-AB12CD34EF"
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
      </article>

      {needsClaim && (
        <article className="rounded-xl border border-amber-300 bg-amber-50 p-6 dark:border-amber-700 dark:bg-amber-950/30">
          <h2 className="text-lg font-semibold text-amber-900 dark:text-amber-200">Unclaimed Sticker</h2>
          <p className="mt-2 text-sm text-amber-800 dark:text-amber-300">
            This sticker belongs to an unclaimed pack. The owner can{" "}
            <Link href="/login" className="underline">
              register/login
            </Link>{" "}
            and claim the pack first.
          </p>
          <form className="mt-4 grid gap-3" onSubmit={handleIssueReport}>
            <label className="text-sm font-medium text-amber-900 dark:text-amber-200" for="issue-note">
              If this sticker should already be active, report the issue
            </label>
            <textarea
              id="issue-note"
              required
              minLength={5}
              maxLength={500}
              value={issueNote}
              onInput={(event) => setIssueNote((event.target as HTMLTextAreaElement).value)}
              className="min-h-20 rounded border border-amber-300 bg-white px-3 py-2 dark:border-amber-700 dark:bg-slate-950"
              placeholder="Describe where you got this sticker and what happened."
            />
            <button
              type="submit"
              className="rounded border border-amber-400 px-4 py-2 text-sm font-medium text-amber-900 hover:bg-amber-100 dark:border-amber-700 dark:text-amber-300 dark:hover:bg-amber-950/50"
            >
              Submit Claim Issue
            </button>
          </form>
        </article>
      )}

      {error && (
        <p
          className="rounded border border-red-300 bg-red-50 p-2 text-sm text-red-700 dark:border-red-700 dark:bg-red-950/40 dark:text-red-300"
          role="alert"
        >
          {error}
        </p>
      )}
      {feedback && (
        <p className="rounded border border-emerald-300 bg-emerald-50 p-2 text-sm text-emerald-700 dark:border-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-300">
          {feedback}
        </p>
      )}
    </section>
  );
}
