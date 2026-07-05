# `balli.time`

## `aware-datetime?`

Kind: `defn`

_No docstring._

## `zoned-datetime?`

Kind: `defn`

_No docstring._

## `local-date-time?`

Kind: `defn`

_No docstring._

## `local-date?`

Kind: `defn`

_No docstring._

## `local-time?`

Kind: `defn`

_No docstring._

## `offset-time?`

Kind: `defn`

_No docstring._

## `duration?`

Kind: `defn`

_No docstring._

## `period?`

Kind: `defn`

_No docstring._

## `zone-id?`

Kind: `defn`

_No docstring._

## `zone-offset?`

Kind: `defn`

_No docstring._

## `parse-duration`

Kind: `defn`

Parse the supported ISO-8601 duration subset into datetime.timedelta. Supports PnW, PnD, TnHnMnS, optional sign, and fractional components. Returns nil for unsupported/invalid strings.

## `parse-period`

Kind: `defn`

Parse an ISO-8601 calendar period subset (PnYnMnD) into {:years y :months m :days d}. Weeks and time components are intentionally not accepted; use :time/duration for elapsed time.

## `format-period`

Kind: `defn`

_No docstring._

## `format-duration`

Kind: `defn`

Format datetime.timedelta as a canonical ISO-8601 duration string. Weeks are canonicalized to days; zero renders PT0S.

## `parse-zone-offset`

Kind: `defn`

_No docstring._

## `format-zone-offset`

Kind: `defn`

_No docstring._

## `decode`

Kind: `defn`

Decode a string for time schema `type`, returning nil on parse/type miss.

## `encode`

Kind: `defn`

_No docstring._

## `types`

Kind: `def`

_No docstring._

## `time-type?`

Kind: `defn`

_No docstring._

## `type-spec`

Kind: `defn`

_No docstring._
