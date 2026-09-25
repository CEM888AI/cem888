# Contributing to CEM888

Thanks for looking. CEM888 is a public beta maintained by one person, so the process is short and strict.

## Before you open a pull request

1. **Agree to the CLA.** Every pull request must include this line in its description:

   `I have read and agree to the CEM888 Contributor License Agreement (CLA.md).`

   Pull requests without it are not reviewed or merged. The CLA is what lets CEM888 offer the same code under AGPL-3.0 and under a commercial license. See [CLA.md](./CLA.md).

2. **Open an issue first for anything larger than a small fix**, so scope can be agreed before you spend time.

3. **Security issues do not go in public issues or pull requests.** Follow [SECURITY.md](./SECURITY.md).

## What a pull request needs

- A falsifiable claim: what was wrong, what is true after the change, and the test that proves it.
- A test under `tests/` for any behavior change. The suite must pass:

  ```bash
  python3.14 -m pip install pytest
  PYTHONPATH=src python3.14 -m pytest -q tests
  ```

  CI runs the same command on every push and pull request.
- No credentials, tokens, personal data, machine-specific paths, logs or state databases.
- Documentation changes follow the claim policy in [docs/STATUS.md](./docs/STATUS.md): do not describe a mechanism as customer-certified unless it has passed on the exact installed customer artifact.

## What is out of scope here

This repository is the public source and audit record. The customer installer, private prompts, routing and scoring policy, and operational infrastructure are not maintained here, so pull requests against them cannot be accepted.

## License of contributions

Contributions are accepted under AGPL-3.0 and the terms of [CLA.md](./CLA.md).
