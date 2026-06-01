# MLAgentBench House-Price Setup Probe

This setup probe records why the next official MLAgentBench tabular task was
not used in the current pilot package.

Attempted command on `ubuntu-heshi`:

```bash
cd /home/heshi/work/bench-probes/MLAgentBench
. .venv/bin/activate
printf "\n" | python -u -m MLAgentBench.prepare_task house-price "$(which python)"
```

Observed result:

```text
Running prepare.py ...
Consent to the competition at https://www.kaggle.com/competitions/home-data-for-ml-course/data; Press any key
FileNotFoundError: [Errno 2] No such file or directory: 'kaggle'
prepare.py failed
```

Interpretation:

- The benchmark code is present.
- The task requires Kaggle tooling and likely Kaggle account/rule consent.
- No official MLAgentBench house-price score is reported.
- The current package uses the controlled sklearn diabetes tabular probe as a
  credential-free non-FML modeling proxy, with an explicit caveat that it is not
  an official MLAgentBench score.
