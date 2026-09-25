# Public conformance tests

These tests are a **small public falsifier suite for claims already implemented in this repository**.
They are not a claim that the customer artifact is fully certified.

The suite currently checks four public invariants:

1. **Tier-0 authority**
   - the authority manifest cannot be mutated by the running agent;
   - forbidden protected roots are denied;
   - an explicitly allowed root remains writable;
   - literal shell mutations against denied roots are rejected;
   - ordinary reads are not mislabeled as mutations.

2. **Authority-aware current-state retrieval**
   - a superseded typed-memory row is not eligible for the current working-context packet.

3. **Bounded-context receipts**
   - the receipt records selection metadata and a SHA-256 of the query;
   - raw query text is not copied into the receipt;
   - irrelevant non-identity candidates can be excluded for lack of task relevance.

4. **Supersession lifecycle**
   - superseding a record moves the old row to `lifecycle_status='superseded'`, not only `superseded_by`;
   - across a chain of supersessions, exactly one row is active and none is both active and superseded;
   - stores written before this rule are repaired when opened.

   Regression for the defect reported by the September 18, 2026 external runtime evaluation.

Run locally:

```bash
python3.14 -m pip install pytest pyyaml
PYTHONPATH=src python3.14 -m pytest -q tests
```

## Scope boundary

These tests exercise the **public engineering source tree**. They do not replace the
customer-artifact certification gate described in `docs/STATUS.md`. A mechanism passing here is
not automatically a customer-certified claim; the exact frozen install artifact still has to pass
its own conformance run.

The shell authority checks here cover the in-process semantic authority boundary that is implemented
in `src/agent/authority.py`. That module explicitly states that it is **not an OS security
boundary** for hostile shell expansion/symlink cases. Strong deployments may add service-user,
filesystem, container, or other OS controls as defense in depth.
