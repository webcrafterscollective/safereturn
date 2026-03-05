/** Local QR image renderer so sticker QRs work without external CDN/image services. */

import { useEffect, useState } from "preact/hooks";
import QRCode from "qrcode";

interface QRCodeImageProps {
  value: string;
  alt: string;
  size?: number;
}

export function QRCodeImage({ value, alt, size = 128 }: QRCodeImageProps) {
  const [dataUrl, setDataUrl] = useState("");

  useEffect(() => {
    let active = true;
    void QRCode.toDataURL(value, { width: size, margin: 1, errorCorrectionLevel: "M" }).then(
      (output) => {
        if (active) {
          setDataUrl(output);
        }
      },
    );
    return () => {
      active = false;
    };
  }, [size, value]);

  if (!dataUrl) {
    return <div className="h-24 w-24 animate-pulse rounded border border-slate-200 dark:border-slate-700" />;
  }

  return (
    <img
      src={dataUrl}
      alt={alt}
      className="h-24 w-24 rounded border border-slate-200 bg-white p-1 dark:border-slate-700"
    />
  );
}
