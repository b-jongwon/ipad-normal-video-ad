# Versioned follow-up improvements

See `docs/IMPROVEMENT_FOLLOWUP.md` in the publication checkout and
`output/improvements_20261005/NUMERIC_RESULTS.md` for actual results and limits.

Modules:

- `memory`: normal CLS prototype64/256,causal difference memory,few-shot,AE/GRU fusion.
- `covariance`: normal LedoitWolf global/unsupervised-state mixture covariance.
- `finetune`: genuine normal-only DINO last-block/layernorm adaptation R01/R04.
- `llm`: matched grammar generation and narrow frame-phase scoring; paid API.
- `stream`: serialized causal replay of new memory/covariance models.
- `guard`: opt-in old13stage wrapper; uncertain is never certified normal.
- `adapt`: new-process normal MP4 manifest fitting and file inference; frame memory only.
- `tests`,`verify`,`adapt_smoke`,`report`: automated checks and numeric evidence.

Keep original runs unchanged. All current follow-ups are posthoc IPAD development,
not independent final/unseen-factory evaluation. No new candidate replaced the old
baseline. API receipts and failed generation attempts are distinct from accepted
grammars; never retry a rejected API response or change a confirmed key silently.

New experiments must use new RUN/OUT constants so seals and scores remain immutable.
Historical caches/checkpoints are excluded from public source; reproduce the earlier
feature extraction and normal splits first. Never commit `.env` files or raw IPAD data.
