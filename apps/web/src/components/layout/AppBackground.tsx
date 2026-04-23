export function AppBackground() {
  return (
    <div className="canvas" aria-hidden="true">
      <div className="canvas__vignette" />
      <div className="canvas__blue-glow canvas__blue-glow--left" />
      <div className="canvas__blue-glow canvas__blue-glow--right" />
      <div className="canvas__grid" />
      <div className="canvas__spotlight" />
    </div>
  );
}
