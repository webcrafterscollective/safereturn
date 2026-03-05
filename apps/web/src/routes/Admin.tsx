/** Admin dashboard for pack generation, inventory tracking, and user provisioning. */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "preact/hooks";

import { QRCodeImage } from "../components/common/QRCodeImage";
import {
  adminCreateUserAndAssignPack,
  adminGeneratePack,
  adminOverview,
  adminPackStickers,
  adminListPacks,
  ApiError,
  getSessionSnapshot,
  type StickerSummary,
} from "../lib/api/client";

function StickerCard({ sticker }: { sticker: StickerSummary }) {
  return (
    <article className="rounded border border-slate-200 p-3 text-sm dark:border-slate-700">
      <p className="font-medium">{sticker.code}</p>
      <p className="mt-1 text-xs text-slate-600 dark:text-slate-300">status: {sticker.status}</p>
      <p className="mt-1 text-xs text-slate-600 dark:text-slate-300">
        assigned_once: {sticker.assigned_once ? "yes" : "no"}
      </p>
      <div className="mt-2">
        <QRCodeImage value={sticker.qr_scan_url} alt={`QR for ${sticker.code}`} />
      </div>
    </article>
  );
}

export function AdminRoute() {
  const queryClient = useQueryClient();
  const session = getSessionSnapshot();
  const [quantity, setQuantity] = useState(10);
  const [selectedPackId, setSelectedPackId] = useState("");
  const [newUserEmail, setNewUserEmail] = useState("");
  const [newUserPassword, setNewUserPassword] = useState("password123");
  const [assignPackCode, setAssignPackCode] = useState("");
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");

  const overviewQuery = useQuery({
    queryKey: ["admin", "overview"],
    queryFn: adminOverview,
    enabled: session.isAuthenticated && session.isAdmin,
  });

  const packsQuery = useQuery({
    queryKey: ["admin", "packs"],
    queryFn: adminListPacks,
    enabled: session.isAuthenticated && session.isAdmin,
  });

  const packStickersQuery = useQuery({
    queryKey: ["admin", "packs", selectedPackId, "stickers"],
    queryFn: () => adminPackStickers(selectedPackId),
    enabled: session.isAuthenticated && session.isAdmin && selectedPackId.length > 0,
  });

  const generateMutation = useMutation({
    mutationFn: (value: number) => adminGeneratePack(value),
    onSuccess: async () => {
      setNotice("Sticker pack generated successfully.");
      setError("");
      await queryClient.invalidateQueries({ queryKey: ["admin", "packs"] });
      await queryClient.invalidateQueries({ queryKey: ["admin", "overview"] });
    },
    onError: (mutationError) => {
      setNotice("");
      if (mutationError instanceof ApiError) {
        setError(`Generate failed (${mutationError.status}).`);
      } else {
        setError("Generate failed.");
      }
    },
  });

  const createUserMutation = useMutation({
    mutationFn: (payload: { email: string; password: string; packCode: string | null }) =>
      adminCreateUserAndAssignPack(payload.email, payload.password, payload.packCode),
    onSuccess: async (payload) => {
      setNotice(
        payload.assigned_pack_code
          ? `User created and assigned pack ${payload.assigned_pack_code}.`
          : "User created.",
      );
      setError("");
      setNewUserEmail("");
      setAssignPackCode("");
      await queryClient.invalidateQueries({ queryKey: ["admin", "overview"] });
      await queryClient.invalidateQueries({ queryKey: ["admin", "packs"] });
    },
    onError: (mutationError) => {
      setNotice("");
      if (mutationError instanceof ApiError) {
        setError(`Create user failed (${mutationError.status}).`);
      } else {
        setError("Create user failed.");
      }
    },
  });

  if (!session.isAuthenticated) {
    return (
      <section className="rounded-xl border border-amber-300 bg-amber-50 p-6 text-amber-800 dark:border-amber-700 dark:bg-amber-950/30 dark:text-amber-300">
        Please login to access the admin portal.
      </section>
    );
  }

  if (!session.isAdmin) {
    return (
      <section className="rounded-xl border border-red-300 bg-red-50 p-6 text-red-700 dark:border-red-700 dark:bg-red-950/30 dark:text-red-300">
        Your account is not an admin account.
      </section>
    );
  }

  return (
    <section className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
      <article className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
        <h1 className="text-xl font-semibold">Admin Portal</h1>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
          Generate sticker packs, view inventory, and provision owner accounts.
        </p>

        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          <div className="rounded border border-slate-200 p-3 dark:border-slate-700">
            <p className="text-xs text-slate-500">Users</p>
            <p className="text-lg font-semibold">{overviewQuery.data?.users ?? "-"}</p>
          </div>
          <div className="rounded border border-slate-200 p-3 dark:border-slate-700">
            <p className="text-xs text-slate-500">Packs</p>
            <p className="text-lg font-semibold">{overviewQuery.data?.packs ?? "-"}</p>
          </div>
          <div className="rounded border border-slate-200 p-3 dark:border-slate-700">
            <p className="text-xs text-slate-500">Stickers</p>
            <p className="text-lg font-semibold">{overviewQuery.data?.stickers ?? "-"}</p>
          </div>
          <div className="rounded border border-slate-200 p-3 dark:border-slate-700">
            <p className="text-xs text-slate-500">Claimed Packs</p>
            <p className="text-lg font-semibold">{overviewQuery.data?.claimed_packs ?? "-"}</p>
          </div>
          <div className="rounded border border-slate-200 p-3 dark:border-slate-700">
            <p className="text-xs text-slate-500">Unassigned</p>
            <p className="text-lg font-semibold">{overviewQuery.data?.unassigned_stickers ?? "-"}</p>
          </div>
        </div>

        <form
          className="mt-6 rounded border border-slate-200 p-4 dark:border-slate-700"
          onSubmit={(event) => {
            event.preventDefault();
            generateMutation.mutate(quantity);
          }}
        >
          <h2 className="text-sm font-semibold">Generate Sticker Pack</h2>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <input
              type="number"
              min={1}
              max={500}
              value={quantity}
              onInput={(event) => setQuantity(Number((event.target as HTMLInputElement).value))}
              className="w-32 rounded border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
            />
            <button
              type="submit"
              className="rounded bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
            >
              Generate
            </button>
          </div>
        </form>

        <form
          className="mt-4 rounded border border-slate-200 p-4 dark:border-slate-700"
          onSubmit={(event) => {
            event.preventDefault();
            createUserMutation.mutate({
              email: newUserEmail.trim(),
              password: newUserPassword.trim(),
              packCode: assignPackCode.trim() || null,
            });
          }}
        >
          <h2 className="text-sm font-semibold">Create User + Optional Pack Assignment</h2>
          <div className="mt-3 grid gap-2">
            <input
              required
              type="email"
              value={newUserEmail}
              onInput={(event) => setNewUserEmail((event.target as HTMLInputElement).value)}
              className="rounded border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
              placeholder="owner@example.com"
            />
            <input
              required
              type="password"
              minLength={8}
              value={newUserPassword}
              onInput={(event) => setNewUserPassword((event.target as HTMLInputElement).value)}
              className="rounded border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
              placeholder="Password"
            />
            <input
              value={assignPackCode}
              onInput={(event) => setAssignPackCode((event.target as HTMLInputElement).value)}
              className="rounded border border-slate-300 px-3 py-2 dark:border-slate-700 dark:bg-slate-950"
              placeholder="PACK-XXXX (optional)"
            />
            <button
              type="submit"
              className="rounded border border-brand-500 px-4 py-2 text-sm font-medium text-brand-700 hover:bg-brand-50 dark:text-brand-400 dark:hover:bg-slate-800"
            >
              Create User
            </button>
          </div>
        </form>

        {notice && (
          <p className="mt-4 rounded border border-emerald-300 bg-emerald-50 p-2 text-sm text-emerald-700 dark:border-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-300">
            {notice}
          </p>
        )}
        {error && (
          <p className="mt-4 rounded border border-red-300 bg-red-50 p-2 text-sm text-red-700 dark:border-red-700 dark:bg-red-950/30 dark:text-red-300">
            {error}
          </p>
        )}
      </article>

      <article className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
        <h2 className="text-lg font-semibold">Pack Inventory</h2>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
          Select a pack to inspect all generated sticker codes and QR payloads.
        </p>
        <div className="mt-4 max-h-64 space-y-2 overflow-auto pr-2">
          {packsQuery.data?.packs.map((pack) => (
            <button
              key={pack.id}
              type="button"
              onClick={() => setSelectedPackId(pack.id)}
              className={`w-full rounded border px-3 py-2 text-left text-sm ${
                selectedPackId === pack.id
                  ? "border-brand-500 bg-brand-50 dark:bg-slate-800"
                  : "border-slate-200 dark:border-slate-700"
              }`}
            >
              <p className="font-medium">{pack.pack_code}</p>
              <p className="text-xs text-slate-500">
                {pack.total_stickers} stickers | status: {pack.status}
              </p>
            </button>
          ))}
        </div>

        {selectedPackId && (
          <div className="mt-4 max-h-80 space-y-2 overflow-auto pr-2">
            {packStickersQuery.isPending && <p className="text-sm text-slate-500">Loading stickers...</p>}
            {packStickersQuery.data?.stickers.map((sticker) => (
              <StickerCard key={sticker.code} sticker={sticker} />
            ))}
          </div>
        )}
      </article>
    </section>
  );
}
