import { FormEvent, useMemo, useState } from "react";
import { useAssetUpload } from "./useAssets";

type AssetUploadModalProps = {
  open: boolean;
  onClose: () => void;
};

export function AssetUploadModal({ open, onClose }: AssetUploadModalProps) {
  const upload = useAssetUpload();
  const [title, setTitle] = useState("");
  const [assetType, setAssetType] = useState("image");
  const [eventName, setEventName] = useState("Championship Night");
  const [provenanceStatus, setProvenanceStatus] = useState("present");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string>("");

  const canSubmit = useMemo(() => !!title.trim() && !!file && !upload.isPending, [file, title, upload.isPending]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setError("Please choose a file to upload.");
      return;
    }

    setError("");
    try {
      await upload.mutateAsync({
        title: title.trim(),
        asset_type: assetType,
        event_name: eventName.trim(),
        provenance_status: provenanceStatus,
        description: description.trim() || undefined,
        file,
      });

      setTitle("");
      setAssetType("image");
      setEventName("Championship Night");
      setProvenanceStatus("present");
      setDescription("");
      setFile(null);
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
            onChange={(event) => setTitle(event.target.value)}
            placeholder="Final whistle broadcast clip"
            type="text"
            value={title}
          />
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
            accept="image/*,video/*"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            type="file"
          />
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