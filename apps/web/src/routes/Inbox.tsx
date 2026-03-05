/** Owner dashboard for claiming packs, managing stickers/items, and relay inbox. */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "preact/hooks";
import { Link } from "wouter-preact";

import { QRCodeImage } from "../components/common/QRCodeImage";
import {
  ApiError,
  claimPack,
  getSessionSnapshot,
  invalidateSticker,
  listMyItems,
  listMyStickers,
  listOwnerMessages,
  markItemFound,
  markItemLost,
  regenerateSticker,
  registerSticker,
  sendOwnerMessage,
} from "../lib/api/client";

export function InboxRoute() {
  const queryClient = useQueryClient();
  const session = getSessionSnapshot();

  const [packCode, setPackCode] = useState("");
  const [stickerCode, setStickerCode] = useState("");
  const [itemName, setItemName] = useState("");
  const [itemCategory, setItemCategory] = useState("general");
  const [itemDescription, setItemDescription] = useState("");
  const [sessionReference, setSessionReference] = useState("");
  const [replyMessage, setReplyMessage] = useState("");
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");

  const stickersQuery = useQuery({
    queryKey: ["owner", "stickers"],
    queryFn: listMyStickers,
    enabled: session.isAuthenticated,
  });

  const itemsQuery = useQuery({
    queryKey: ["owner", "items"],
    queryFn: listMyItems,
    enabled: session.isAuthenticated,
  });

  const inboxQuery = useQuery({
    queryKey: ["owner", "messages"],
    queryFn: listOwnerMessages,
    refetchInterval: 8000,
    enabled: session.isAuthenticated,
  });

  const availableStickerCodes = useMemo(
    () =>
      (stickersQuery.data?.stickers ?? [])
        .filter((sticker) => !sticker.assigned_once && !sticker.invalidated_at)
        .map((sticker) => sticker.code),
    [stickersQuery.data?.stickers],
  );

  const refreshOwnerData = async () => {
    await queryClient.invalidateQueries({ queryKey: ["owner", "stickers"] });
    await queryClient.invalidateQueries({ queryKey: ["owner", "items"] });
    await queryClient.invalidateQueries({ queryKey: ["owner", "messages"] });
  };

  const claimPackMutation = useMutation({
    mutationFn: (value: string) => claimPack(value),
    onSuccess: async (payload) => {
      setNotice(`Pack ${payload.pack_code} claimed with ${payload.total_stickers} stickers.`);
      setError("");
      setPackCode("");
      await refreshOwnerData();
    },
    onError: (mutationError) => {
      setNotice("");
      if (mutationError instanceof ApiError) {
        setError(`Pack claim failed (${mutationError.status}).`);
      } else {
        setError("Pack claim failed.");
      }
    },
  });

  const registerStickerMutation = useMutation({
    mutationFn: () =>
      registerSticker({
        sticker_code: stickerCode.trim(),
        item_name: itemName.trim(),
        item_category: itemCategory.trim(),
        item_description: itemDescription.trim(),
      }),
    onSuccess: async (payload) => {
      setNotice(`Sticker ${payload.sticker_code} attached to item.`);
      setError("");
      setItemName("");
      setItemDescription("");
      setStickerCode("");
      await refreshOwnerData();
    },
    onError: (mutationError) => {
      setNotice("");
      if (mutationError instanceof ApiError) {
        const details = mutationError.details as { error?: { code?: string } } | null;
        if (details?.error?.code === "STICKER_UNCLAIMED") {
          setError("Claim a sticker pack first.");
          return;
        }
      }
      setError("Sticker registration failed.");
    },
  });

  const regenerateMutation = useMutation({
    mutationFn: (code: string) => regenerateSticker(code),
    onSuccess: async (payload) => {
      setNotice(`Sticker ${payload.replaced_code} replaced with ${payload.replacement.code}.`);
      setError("");
      await refreshOwnerData();
    },
    onError: () => {
      setNotice("");
      setError("Sticker regeneration failed.");
    },
  });

  const invalidateMutation = useMutation({
    mutationFn: (code: string) => invalidateSticker(code),
    onSuccess: async () => {
      setNotice("Sticker invalidated.");
      setError("");
      await refreshOwnerData();
    },
    onError: () => {
      setNotice("");
      setError("Sticker invalidation failed.");
    },
  });

  const markLostMutation = useMutation({
    mutationFn: (itemId: string) =>
      markItemLost(itemId, {
        last_known_location: "Not provided",
        notes: "Marked lost from owner dashboard",
      }),
    onSuccess: async () => {
      setNotice("Item marked as lost.");
      setError("");
      await refreshOwnerData();
    },
    onError: () => {
      setNotice("");
      setError("Mark lost failed.");
    },
  });

  const markFoundMutation = useMutation({
    mutationFn: (itemId: string) => markItemFound(itemId),
    onSuccess: async () => {
      setNotice("Item marked as found.");
      setError("");
      await refreshOwnerData();
    },
    onError: () => {
      setNotice("");
      setError("Mark found failed.");
    },
  });

  const replyMutation = useMutation({
    mutationFn: () =>
      sendOwnerMessage(sessionReference.trim(), {
        message_body: replyMessage.trim(),
      }),
    onSuccess: async () => {
      setNotice("Reply sent.");
      setError("");
      setReplyMessage("");
      await refreshOwnerData();
    },
    onError: () => {
      setNotice("");
      setError("Reply failed. Check session reference.");
    },
  });

  if (!session.isAuthenticated) {
    return (
      <section className="rounded-xl border border-amber-300 bg-amber-50 p-6 text-amber-800 dark:border-amber-700 dark:bg-amber-950/30 dark:text-amber-300">
        Please <Link href="/login" className="underline">login</Link> to access the owner dashboard.
      </section>
    );
  }

  return (
    <section className="grid gap-6 lg:grid-cols-2">
      <article className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
        <h1 className="text-xl font-semibold">Owner Recovery Dashboard</h1>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
          Claim sticker packs, attach one-time stickers to items, and manage item recovery status.
        </p>

        <form
          className="mt-5 rounded border border-slate-200 p-4 dark:border-slate-700"
          onSubmit={(event) => {
            event.preventDefault();
            claimPackMutation.mutate(packCode.trim());
          }}
        >
          <h2 className="text-sm font-semibold">Claim Sticker Pack</h2>
          <div className="mt-3 flex gap-2">
            <input
              required
              value={packCode}
              onInput={(event) => setPackCode((event.target as HTMLInputElement).value)}
              className="w-full rounded border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
              placeholder="PACK-XXXXXXXX"
            />
            <button
              type="submit"
              className="rounded bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
            >
              Claim
            </button>
          </div>
        </form>

        <form
          className="mt-4 rounded border border-slate-200 p-4 dark:border-slate-700"
          onSubmit={(event) => {
            event.preventDefault();
            registerStickerMutation.mutate();
          }}
        >
          <h2 className="text-sm font-semibold">Register Item with Sticker</h2>
          <div className="mt-3 grid gap-2">
            <select
              required
              value={stickerCode}
              onChange={(event) => setStickerCode((event.target as HTMLSelectElement).value)}
              className="rounded border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
            >
              <option value="">Select available sticker</option>
              {availableStickerCodes.map((code) => (
                <option key={code} value={code}>
                  {code}
                </option>
              ))}
            </select>
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
              className="min-h-20 rounded border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
              placeholder="Description"
            />
            <button
              type="submit"
              className="rounded border border-brand-500 px-4 py-2 text-sm font-medium text-brand-700 hover:bg-brand-50 dark:text-brand-400 dark:hover:bg-slate-800"
            >
              Attach Sticker to Item
            </button>
          </div>
        </form>

        {notice && (
          <p className="mt-4 rounded border border-emerald-300 bg-emerald-50 p-2 text-sm text-emerald-700 dark:border-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-300">
            {notice}
          </p>
        )}
        {error && (
          <p className="mt-4 rounded border border-red-300 bg-red-50 p-2 text-sm text-red-700 dark:border-red-700 dark:bg-red-950/40 dark:text-red-300">
            {error}
          </p>
        )}
      </article>

      <article className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
        <h2 className="text-lg font-semibold">My Stickers</h2>
        <div className="mt-4 max-h-64 space-y-3 overflow-auto pr-2">
          {stickersQuery.isPending && <p className="text-sm text-slate-500">Loading stickers...</p>}
          {stickersQuery.data?.stickers.map((sticker) => (
            <article key={sticker.code} className="rounded border border-slate-200 p-3 dark:border-slate-700">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="text-sm font-medium">{sticker.code}</p>
                  <p className="text-xs text-slate-500">
                    status: {sticker.status} | assigned_once: {sticker.assigned_once ? "yes" : "no"}
                  </p>
                  <p className="mt-1 text-xs text-slate-500">scan url: {sticker.qr_scan_url}</p>
                </div>
                <QRCodeImage value={sticker.qr_scan_url} alt={`QR for ${sticker.code}`} />
              </div>
              {!sticker.assigned_once && !sticker.invalidated_at && (
                <div className="mt-2 flex gap-2">
                  <button
                    type="button"
                    onClick={() => regenerateMutation.mutate(sticker.code)}
                    className="rounded border border-slate-300 px-2 py-1 text-xs hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800"
                  >
                    Regenerate QR
                  </button>
                  <button
                    type="button"
                    onClick={() => invalidateMutation.mutate(sticker.code)}
                    className="rounded border border-red-300 px-2 py-1 text-xs text-red-700 hover:bg-red-50 dark:border-red-700 dark:text-red-300 dark:hover:bg-red-950/30"
                  >
                    Invalidate
                  </button>
                </div>
              )}
            </article>
          ))}
        </div>
      </article>

      <article className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
        <h2 className="text-lg font-semibold">My Items</h2>
        <div className="mt-4 max-h-64 space-y-3 overflow-auto pr-2">
          {itemsQuery.isPending && <p className="text-sm text-slate-500">Loading items...</p>}
          {itemsQuery.data?.items.map((item) => (
            <article key={item.item_id} className="rounded border border-slate-200 p-3 dark:border-slate-700">
              <p className="text-sm font-medium">{item.item_name}</p>
              <p className="text-xs text-slate-500">
                sticker: {item.sticker_code ?? "none"} | status: {item.sticker_status ?? "none"}
              </p>
              <p className="text-xs text-slate-500">lost: {item.is_lost ? "yes" : "no"}</p>
              <div className="mt-2 flex gap-2">
                <button
                  type="button"
                  onClick={() => markLostMutation.mutate(item.item_id)}
                  disabled={item.is_lost}
                  className="rounded border border-amber-300 px-2 py-1 text-xs text-amber-800 hover:bg-amber-50 disabled:opacity-40 dark:border-amber-700 dark:text-amber-300 dark:hover:bg-amber-950/30"
                >
                  Mark Lost
                </button>
                <button
                  type="button"
                  onClick={() => markFoundMutation.mutate(item.item_id)}
                  disabled={!item.is_lost}
                  className="rounded border border-emerald-300 px-2 py-1 text-xs text-emerald-700 hover:bg-emerald-50 disabled:opacity-40 dark:border-emerald-700 dark:text-emerald-300 dark:hover:bg-emerald-950/30"
                >
                  Mark Found
                </button>
              </div>
            </article>
          ))}
        </div>
      </article>

      <article className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
        <h2 className="text-lg font-semibold">Anonymous Inbox</h2>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
          Use session reference from incoming messages to reply to finders.
        </p>
        <div className="mt-4 max-h-64 space-y-3 overflow-auto pr-2">
          {inboxQuery.isPending && <p className="text-sm text-slate-500">Loading messages...</p>}
          {inboxQuery.data?.messages.map((message) => (
            <button
              key={`${message.session_reference}-${message.created_at}`}
              type="button"
              onClick={() => setSessionReference(message.session_reference)}
              className="w-full rounded border border-slate-200 p-3 text-left text-sm hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800"
            >
              <p className="font-medium">
                {message.sender_role} | session {message.session_reference}
              </p>
              <p className="mt-1 text-slate-700 dark:text-slate-300">{message.body}</p>
            </button>
          ))}
        </div>

        <form
          className="mt-4 grid gap-2"
          onSubmit={(event) => {
            event.preventDefault();
            replyMutation.mutate();
          }}
        >
          <input
            required
            value={sessionReference}
            onInput={(event) => setSessionReference((event.target as HTMLInputElement).value)}
            className="rounded border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
            placeholder="Session reference"
          />
          <textarea
            required
            value={replyMessage}
            onInput={(event) => setReplyMessage((event.target as HTMLTextAreaElement).value)}
            className="min-h-20 rounded border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
            placeholder="Reply message"
          />
          <button
            type="submit"
            className="rounded bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
          >
            Send Reply
          </button>
        </form>
      </article>
    </section>
  );
}
