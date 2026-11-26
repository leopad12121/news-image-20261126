# The World in One Day — Thursday 26 November 2026

[![make.fun](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/leopad12121/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/leopad12121/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126)

A one-image newspaper front page summing up the world's news of
Thursday 26 November 2026, entered in the
[make.fun bounty](https://make.fun/bounty/news-image-20261126).

`main.py` (Python 3.13, standard library only at module level) draws a
1024x1024 front page — masthead, lead story, a 2x2 grid and a
Thanksgiving travel strip — with Pillow when it is available, and
otherwise copies the shipped `entry.png` so the program still exits 0
with the verified image. It writes to `$MAKEFUN_OUTPUT_DIR/entry.png`,
else `/output/entry.png` when `/output` exists, else `./entry.png`.
Deterministic: two runs produce byte-identical output.

## The day's six stories

All six led the news cycle on the morning of Thursday 26 November
2026 (overnight developments, first reported in the Asia morning
papers dated 26 Nov); none was used in the 25 November round.

1. **Houthis strike Saudi ports** (Jeddah and Jazan) — the Houthis say
   they hit both ports in retaliation for the coalition's strike on
   Hodeida; Riyadh confirms a projectile hit Jazan, minor damage, no
   casualties.
   Sources: Reuters, Times of Israel.
2. **S&P eyes Nvidia downgrade** (Wall Street) — S&P puts Nvidia's AA
   rating on CreditWatch Negative, citing governance risks after the
   CEO's ousting and return; shares fell 3.9% on Wednesday.
   Sources: Reuters, Nikkei.
3. **Vance defends Huang's return** (Washington) — the vice-president
   says the Justice Department assured him the Nvidia chief is not
   under investigation; no pardon needed.
   Sources: CNN, AP.
4. **Swiss envoy ordered out** (Pyongyang) — North Korea declares the
   head of Switzerland's diplomatic office persona non grata, gives
   him 48 hours to leave and orders the office closed, in a row over
   sanctions on a children's camp.
   Sources: Reuters, Al Jazeera.
5. **China, Cambodia open big drills** (Ream Naval Base) — Golden
   Dragon 2026 begins with nearly 3,000 troops, the largest edition
   yet; land, sea and air drills run to 9 December.
   Sources: AFP, Xinhua.
6. **Storm slams Thanksgiving travel** (United States) — an East Coast
   storm brings rain, 50mph winds and snow as 81.5 million Americans
   travel; the Macy's parade moves to Saturday.
   Sources: AP, Fox Weather.

Also noted: US tariff salvo hits 14 partners; Colombia: 76 held in
the Cartagena siege, all freed; Duran Duran guitarist Andy Taylor
dies at 65.

## Run it

```sh
python3 main.py
# or: MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see [LICENSE](LICENSE).
