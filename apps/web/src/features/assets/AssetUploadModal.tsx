import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { useAssetUpload } from "./useAssets";
import type { AssetDetail } from "../../lib/types";

type AssetUploadModalProps = {
  open: boolean;
  onClose: () => void;
  // Bundle A: surface the resolved AssetDetail so the page can flash the new
  // row + show a "matches: N (M incidents)" toast without a re-fetch.
  onUploaded?: (asset: AssetDetail) => void;
};

// Bundle A1: keep the form honest. Backend imagehash chokes on >25 MB blobs
// on the demo box, and the matcher only consumes images today.
const MAX_FILE_BYTES = 25 * 1024 * 1024;
const IMAGE_MIME_PREFIX = "image/";

export function AssetUploadModal({ open, onClose, onUploaded }: AssetUploadModalProps) {
  const upload = useAssetUpload();
  const [title, setTitle] = useState("");
  const [assetType, setAssetType] = useState("image");
  const [eventName, setEventName] = useState("Championship Night");
  const [provenanceStatus, setProvenanceStatus] = useState("present");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string>("");
  const [fieldError, setFieldError] = useState<{ title?: string; file?: string }>({});
  const titleRef = useRef<HTMLInputElement>(null);

  // Bundle A1: autofocus the first required field every time the modal opens.
  useEffect(() => {
    if (open && titleRef.current) {
      titleRef.current.focus();
    }
  }, [open]);

  const canSubmit = useMemo(
    () => !!title.trim() && !!file && !upload.isPending,
    [file, title, upload.isPending],
  );

  function validateFile(f: File | null): string | undefined {
    if (!f) return "Please choose a file to upload.";
    if (f.size > MAX_FILE_BYTES) {
      const mb = (f.size / (1024 * 1024)).toFixed(1);
      return `File is ${mb} MB — max 25 MB for the demo matcher.`;
    }
    if (!f.type.startsWith(IMAGE_MIME_PREFIX)) {
      return "Only image files are matched today (image/* mime type).";
    }
    return undefined;
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const titleErr = title.trim() ? undefined : "Title is required.";
    const fileErr = validateFile(file);
    if (titleErr || fileErr) {
      setFieldError({ title: titleErr, file: fileErr });
      setError("");
      return;
    }

    setFieldError({});
    setError("");
    try {
      const detail = await upload.mutateAsync({
        title: title.trim(),
        asset_type: assetType,
        event_name: eventName.trim(),
        provenance_status: provenanceStatus,
        description: description.trim() || undefined,
        file: file!,
      });

      setTitle("");
      setAssetType("image");
      setEventName("Championship Night");
      setProvenanceStatus("present");
      setDescription("");
      setFile(null);
      onUploaded?.(detail);
      onClose();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Upload failed.");
    }
  }

  if (!open) return null;

  return (
    <article className="panel panel--detail">
      <div className="panel__header">
        <div>
          <span className="eyebrow eyebrow--muted">Register asset</span>
          <h2 className="panel__title">Add official media to protection watch</h2>
        </div>
      </div>

      <form className="auth-panel__form" onSubmit={onSubmit}>
        <label className="auth-panel__field">
          <span>Title</span>
          <input
            aria-invalid={!!fieldError.title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="Final whistle broadcast clip"
            ref={titleRef}
            type="text"
            value={title}
          />
          {fieldError.title && (
            <span className="auth-panel__field-error" role="alert">
              {fieldError.title}
            </span>
          )}
        </label>

        <div className="table-grid table-grid--form">
          <label className="auth-panel__field">
            <span>Type</span>
            <select onChange={(event) => setAssetType(event.target.value)} value={assetType}>
              <option value="image">Image</option>
              <option value="video">Video</option>
              <option value="live_watch">Live Watch</option>
            </select>
          </label>

          <label className="auth-panel__field">
            <span>Provenance</span>
            <select onChange={(event) => setProvenanceStatus(event.target.value)} value={provenanceStatus}>
              <option value="verified">Verified</option>
              <option value="present">Present</option>
              <option value="pending">Pending</option>
              <option value="missing">Missing</option>
            </select>
          </label>
        </div>

        <label className="auth-panel__field">
          <span>Event</span>
          <input
            onChange={(event) => setEventName(event.target.value)}
            placeholder="Championship Night"
            type="text"
            value={eventName}
          />
        </label>

        <label className="auth-panel__field">
          <span>Description</span>
          <textarea
            onChange={(event) => setDescription(event.target.value)}
            placeholder="Optional context for operators"
            rows={3}
            value={description}
          />
        </label>

        <label className="auth-panel__field">
          <span>Media file</span>
          <input
            accept="image/*"
            aria-invalid={!!fieldError.file}
            onChange={(event) => {
              const next = event.target.files?.[0] ?? null;
              setFile(next);
              setFieldError((prev) => ({ ...prev, file: validateFile(next) }));
            }}
            type="file"
          />
          {file && !fieldError.file && (
            <span className="auth-panel__field-hint">
              {file.name} · {(file.size / (1024 * 1024)).toFixed(1)} MB
            </span>
          )}
          {fieldError.file && (
            <span className="auth-panel__field-error" role="alert">
              {fieldError.file}
            </span>
          )}
        </label>

        <div className="auth-panel__actions">
          <button className="pill-link pill-link--solid" disabled={!canSubmit} type="submit">
            {upload.isPending ? "Uploading..." : "Upload and protect"}
          </button>
          <button className="pill-link pill-link--ghost" onClick={onClose} type="button">
            Cancel
          </button>
        </div>

        {error && (
          <p className="auth-panel__error" role="alert">
            {error}
          </p>
        )}
      </form>
    </article>
  );
}