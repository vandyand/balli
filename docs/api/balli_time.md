# `balli.time`

Pure Python datetime helpers for Balli time schemas. This namespace is deliberately a leaf: no balli.* requires. Higher-level namespaces consume the `types` table for validation, transformation, generation, and JSON Schema wiring.

## `aware-datetime?`

Kind: `defn`

Return true for Python datetimes carrying tzinfo.

## `zoned-datetime?`

Kind: `defn`

Return true for aware datetimes backed by a zoneinfo.ZoneInfo timezone.

## `local-date-time?`

Kind: `defn`

Return true for naive Python datetimes.

## `local-date?`

Kind: `defn`

Return true for Python dates that are not datetimes.

## `local-time?`

Kind: `defn`

Return true for Python times without tzinfo.

## `offset-time?`

Kind: `defn`

Return true for Python times carrying tzinfo.

## `duration?`

Kind: `defn`

Return true for Python datetime.timedelta values.

## `period?`

Kind: `defn`

Return true for Balli period maps with integer :years/:months/:days keys.

## `zone-id?`

Kind: `defn`

Return true for strings accepted by Python zoneinfo.ZoneInfo.

## `zone-offset?`

Kind: `defn`

Return true for fixed-offset Python datetime.timezone values.

## `parse-duration`

Kind: `defn`

Parse the supported ISO-8601 duration subset into datetime.timedelta. Supports PnW, PnD, TnHnMnS, optional sign, and fractional components. Returns nil for unsupported/invalid strings.

## `parse-period`

Kind: `defn`

Parse an ISO-8601 calendar period subset (PnYnMnD) into {:years y :months m :days d}. Weeks and time components are intentionally not accepted; use :time/duration for elapsed time.

## `format-period`

Kind: `defn`

Format a Balli period map as an ISO-8601 period string.

## `format-duration`

Kind: `defn`

Format datetime.timedelta as a canonical ISO-8601 duration string. Weeks are canonicalized to days; zero renders PT0S.

## `parse-zone-offset`

Kind: `defn`

Parse Z, +HH, +HHMM, or +HH:MM into datetime.timezone.

## `format-zone-offset`

Kind: `defn`

Format a Python datetime.timezone value as Z or +/-HH:MM.

## `decode`

Kind: `defn`

Decode a string for time schema `type`, returning nil on parse/type miss.

## `encode`

Kind: `defn`

Encode a time value for time schema `type` as a JSON-friendly string.

## `types`

Kind: `def`

Table of Balli time schema specs consumed by validators and transformers.

## `time-type?`

Kind: `defn`

Return true when `t` is a supported Balli time schema keyword.

## `type-spec`

Kind: `defn`

Return the internal time schema spec map for schema keyword `t`.
