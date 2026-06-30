# True Solar Time Reference

Read this for 真太阳时, strict true solar time, local solar time, equation of time, timezone/longitude handling, or birth times near two-hour branch boundaries.

## Terminology

Use precise terms:

- Clock time: the recorded civil time at the birthplace.
- Standard meridian correction: converts clock time from the timezone meridian to local mean solar time.
- Local mean solar time: clock time corrected by longitude only.
- Apparent/true solar time: local mean solar time plus equation-of-time correction.

The current project labels a longitude-only correction as "true solar time". Keep that for compatibility, but call strict mode "apparent true solar time" or "strict true solar time" in new design notes.

## Current Project Behavior

The tracked BaZi service uses the current legacy correction:

```ts
adjusted = clockTime + (longitude - 120) * 4 minutes
```

This is compatible with the existing app and is appropriate when the input time is interpreted against Beijing time / UTC+8's standard meridian. It is a longitude-only correction and does not include equation of time.

Important limitation:

- For non-China locations, a fixed `120°E` standard meridian is not a general local-civil-time conversion.
- Strict global handling needs the event or birth timezone.

## Strict Apparent Solar Time

Use this formula when strict mode is requested:

```text
standardMeridian = timezoneOffsetHours * 15
longitudeCorrectionMinutes = (longitude - standardMeridian) * 4
apparentSolarTime = clockTime + longitudeCorrectionMinutes + equationOfTimeMinutes
```

Where:

- longitude is east-positive and west-negative.
- timezone offset is east-positive, e.g. China UTC+8 -> `+8`, New York standard time UTC-5 -> `-5`.
- use the actual UTC offset for that date and location, including daylight saving time when applicable.
- equation of time varies by date, roughly from about -14 to +16 minutes.

Approximate equation of time:

```ts
const dayOfYear = n; // 1..366
const b = (2 * Math.PI * (dayOfYear - 81)) / 364;
const equationOfTimeMinutes =
  9.87 * Math.sin(2 * b) -
  7.53 * Math.cos(b) -
  1.5 * Math.sin(b);
```

This approximation is enough for BaZi boundary warnings. For high-precision astronomy, use a vetted astronomy library instead of hand-written formulas.

## Boundary-Hour Policy

Hour branches are two-hour windows:

- 子: 23:00-01:00
- 丑: 01:00-03:00
- 寅: 03:00-05:00
- 卯: 05:00-07:00
- 辰: 07:00-09:00
- 巳: 09:00-11:00
- 午: 11:00-13:00
- 未: 13:00-15:00
- 申: 15:00-17:00
- 酉: 17:00-19:00
- 戌: 19:00-21:00
- 亥: 21:00-23:00

When adjusted time is near a boundary:

- Use a default warning window of 15 minutes.
- Use 30 minutes when birth time is approximate, rounded, or supplied only as "around X".
- If legacy longitude-only and strict apparent solar time fall into different branches, mark the hour pillar as ambiguous and compute/show both possibilities.
- If adjusted time crosses midnight, re-evaluate date-sensitive pillars using the adjusted date.
- For Zi time in any future Zi Wei implementation, state which convention is being used. Do not assume the repo currently contains a tracked Zi Wei service.

## Proposed Project API

Add a shared utility rather than duplicating logic across current or future chart services:

```ts
export type SolarTimeMode =
  | 'legacy-cn-meridian'
  | 'local-mean-solar'
  | 'strict-apparent-solar';

export interface SolarTimeOptions {
  mode: SolarTimeMode;
  longitude: number;
  timezoneOffsetMinutes?: number; // actual UTC offset at that date, east positive
  boundaryWindowMinutes?: number;  // default 15
}

export interface SolarTimeResult {
  adjustedDate: Date;
  displayTime: string; // HH:mm
  mode: SolarTimeMode;
  standardMeridian: number;
  longitudeCorrectionMinutes: number;
  equationOfTimeMinutes: number;
  totalOffsetMinutes: number;
  boundaryRisk: boolean;
  boundaryDistanceMinutes: number;
  branchBefore?: string;
  branchAfter?: string;
}

export function calculateSolarTime(
  birthDate: string,
  birthTime: string,
  options: SolarTimeOptions
): SolarTimeResult;
```

Mode behavior:

- `legacy-cn-meridian`: preserve current `(longitude - 120) * 4` behavior. Use this as the default until the UI and cache keys are migrated.
- `local-mean-solar`: use `timezoneOffsetMinutes` to compute the local timezone standard meridian, no equation of time.
- `strict-apparent-solar`: use local mean solar time plus equation of time.

## Migration Checklist

If implementing strict mode in the repository:

- Add `timezoneOffsetMinutes` or an IANA timezone field to `UserInput`.
- Add `solarTimeMode` to input/config and include it in cache keys.
- Replace the time adjustment in `baziService.ts` with one shared utility. If a tracked Zi Wei service is added later, make it call the same utility.
- Preserve legacy mode for existing behavior and saved/shared reports.
- Add UI copy explaining "longitude correction" vs "strict true solar time".
- Add boundary warnings on the confirmation screen.
- In professional mode, do not apply solar-time correction because pillars are user-confirmed truth.
- Keep all solar-time and boundary calculations in code. Do not ask AI to decide which hour branch applies.

## Output Wording

Use:

- "Current app mode uses longitude-corrected solar time."
- "Strict mode adds equation-of-time correction."
- "This birth time is close to a two-hour boundary; both hour pillars should be reviewed."

Avoid:

- Claiming current mode is full astronomical true solar time.
- Silently changing the hour pillar without warning.
- Applying strict correction to already confirmed professional-mode pillars.
