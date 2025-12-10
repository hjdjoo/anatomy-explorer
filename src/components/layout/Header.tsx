/**
 * Application header with branding.
 * Kept minimal to maximize viewport for 3D content.
 */
export function Header() {
  return (
    <header className="absolute top-0 left-0 right-0 z-10 pointer-events-none">
      <div className="flex items-center justify-between p-4">
        {/* Logo / Title */}
        <div className="pointer-events-auto">
          <h1 className="text-xl font-semibold text-surface-100 tracking-tight">
            Anatomy<span className="text-surface-500">Explorer</span>
          </h1>
          <p className="text-xs text-surface-500 mt-0.5">
            Interactive 3D Anatomy · Torso
          </p>
        </div>

        {/* Right side actions could go here */}
        <div className="pointer-events-auto flex items-center gap-2">
          {/* Placeholder for future features like search, settings, etc. */}
        </div>
      </div>
    </header>
  );
}
