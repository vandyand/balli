# Benchmarks

Balli includes a small repeatable benchmark harness:

```bash
basilisp run benchmarks/bench_core.lpy
```

The benchmark prints operation counts and elapsed milliseconds for common
schema workloads:

- validating large maps
- validating vectors
- parsing tagged branches
- decoding string values
- generating sample values

Benchmark output is intended for trend tracking, not cross-machine absolute
claims.
