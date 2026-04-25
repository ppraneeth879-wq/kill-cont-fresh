import type { CSSProperties } from "react";

type Aspect = "16/9" | "4/3" | "1/1";

interface MediaFrameProps {
  src?: string | null;
  alt: string;
  aspect?: Aspect;
  variant?: "default" | "official" | "detected";
  caption?: string;
  className?: string;
  style?: CSSProperties;
}

/**
 * Shared media surface used across Assets / Incidents / Monitor / Evidence /
 * LiveWatch. Renders a real image when `src` resolves, otherwise a neutral
 * dark-grey tile with a camera-slash icon + "No preview available" copy.
 * Replaces the old ad-hoc `.media-frame` gradient fallback.
 */
export function MediaFrame({
  src,
  alt,
  aspect = "16/9",
  variant = "default",
  caption,
  className,
  style,
}: MediaFrameProps) {
  const aspectRatio =
    aspect === "16/9" ? "16 / 9" : aspect === "4/3" ? "4 / 3" : "1 / 1";
  const baseClass = `media-frame media-frame--${variant}`;
  const mergedClass = className ? `${baseClass} ${className}` : baseClass;

  if (src) {
    return (
      <div
        className={mergedClass}
        style={{ aspectRatio, padding: 0, overflow: "hidden", ...style }}
      >
        <img
          src={src}
          alt={alt}
          loading="lazy"
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            display: "block",
          }}
          onError={(e) => {
            // Swap to no-preview state on load error
            const el = e.currentTarget;
            el.style.display = "none";
            const parent = el.parentElement;
            if (parent && !parent.querySelector(".media-frame__empty")) {
              parent.insertAdjacentHTML(
                "beforeend",
                '<div class="media-frame__empty"><span class="media-frame__empty-icon" aria-hidden="true">⎚</span><span>Preview unavailable</span></div>',
              );
            }
          }}
        />
        {caption ? <div className="media-frame__caption">{caption}</div> : null}
      </div>
    );
  }

  return (
    <div
      className={mergedClass}
      style={{ aspectRatio, padding: 0, overflow: "hidden", ...style }}
    >
      <div className="media-frame__empty">
        <span className="media-frame__empty-icon" aria-hidden="true">
          ⎚
        </span>
        <span>No preview available</span>
      </div>
      {caption ? <div className="media-frame__caption">{caption}</div> : null}
    </div>
  );
}

export default MediaFrame;
