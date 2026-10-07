// Section icons. Original filled glyphs on a 24 x 24 grid; holes are cut with even-odd
// fill so they show whatever is behind (active and inactive tabs differ).

type IconProps = { size?: number };

const svg = (size: number) => ({
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "currentColor",
  "aria-hidden": true,
});

/** A horse's head in profile. */
export function HorseIcon({ size = 18 }: IconProps) {
  return (
    <svg {...svg(size)}>
      <path
        fillRule="evenodd"
        d="M9 22c.2-2.8-.3-4.9-1.2-6.2l-2.1.5C4 16.6 2.6 15.4 2.8 13.8c.1-.7.4-1.2.9-1.6l6.7-7.4.9-3.1c.1-.5.8-.6 1.1-.2l1.9 2.4c4 1.1 6.7 4.7 6.7 9.1V22zM10.6 8.6a1 1 0 1 0-2 0 1 1 0 1 0 2 0z"
      />
    </svg>
  );
}

/** A lottery ball marked with a star (not the EuroMillions logo, which is a trademark). */
export function StarBallIcon({ size = 18 }: IconProps) {
  return (
    <svg {...svg(size)}>
      <path
        fillRule="evenodd"
        d="M12 2a10 10 0 1 1 0 20 10 10 0 1 1 0-20zM12 6.2l1.7 3.5 3.9.6-2.8 2.7.7 3.8L12 15l-3.5 1.8.7-3.8-2.8-2.7 3.9-.6z"
      />
    </svg>
  );
}
