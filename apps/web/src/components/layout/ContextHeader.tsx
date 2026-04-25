import type { ReactNode } from "react";

interface ContextHeaderProps {
  eyebrow?: ReactNode;
  title: ReactNode;
  subtitle?: ReactNode;
  actions?: ReactNode;
}

/**
 * Single source of truth for product-page headers. Provides a three-row
 * rhythm (eyebrow → title + actions → subtitle) so every page lines up at
 * the same baseline regardless of content length.
 */
export function ContextHeader({
  eyebrow,
  title,
  subtitle,
  actions,
}: ContextHeaderProps) {
  return (
    <header className="context-header">
      {eyebrow ? (
        <div className="context-header__eyebrow">{eyebrow}</div>
      ) : null}
      <div className="context-header__row">
        <h1 className="context-header__title">{title}</h1>
        {actions ? (
          <div className="context-header__actions">{actions}</div>
        ) : null}
      </div>
      {subtitle ? (
        <p className="context-header__subtitle">{subtitle}</p>
      ) : null}
    </header>
  );
}

export default ContextHeader;
