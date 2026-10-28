# FHD_Trade — complete sources for Nexus Mods review

**All 61 uploaded runtime files rebuild byte for byte from editable source.** This includes four DAT files, 56 GI images and ModuleInfo. There is no native DLL, EXE or SCR. Five automated tests passed, including 11 invocations of seven retained supplied regression scripts. **Other supplied checks fail against this upload; their results and limits are recorded below.** Runtime behavior was preserved.

The input is named `FHD_Trade-v2.0.rar` but is a ZIP container. Its version labels are inconsistent: ModuleInfo displays `ver.6.5`, the change note refers to 6.9, the root README describes v19, and another check is named `verify_v20.py`. This preparation does not select a new gameplay version or alter the original metadata. Author remains **Prolog_D**; conflicts remain **EvoFreeInflation,EvoNoInflation** and Dependence remains empty.

## Mod and source layout

The mod provides trade-route searches, commodity selection/filtering, availability and profit/quantity sorting, service menus, contraband highlighting and graphical buy/sell markers. All executable game statements are visible in the supplied configuration text. An RSON recovery project is not required.

| Path | Purpose |
| --- | --- |
| `SOURCE/CFG/Main.txt` | Complete supplied UI configuration, event handlers and dynamic styles |
| `SOURCE/CFG/Lang.txt` | Shared current language/script source, copied from the supplied Rus/Lang.txt |
| `SOURCE/CFG/CacheData.txt` | Complete supplied resource aliases |
| `SOURCE/ModuleInfo.txt` | UTF-8 metadata source, emitted as original CP1251 bytes and line endings |
| `SOURCE/Graphics/*.json` | Complete editable sources for all 56 GI files |
| `SOURCE/compile_srhd_dat.py` | Supplied DAT compiler/reader |
| `SOURCE/gi_codec.py` | Independent lossless GI types 0/1/2 codec |
| `SOURCE/verify_*.py`, `fixture.js`, `goods_fixture.js` | Seven retained regression scripts and their JS fixtures |
| `SOURCE/fixtures/` | The two supplied vanilla configuration excerpts needed by retained checks |
| `scripts/dat_codec.py` | Independent DAT roundtrip checker |
| `build.py`, `tests/test_source.py` | Complete builder and automated verification |
| `original-file-sha256.json`, `build-verification.json` | Uploaded runtime hashes, completed checks and original-check discrepancies |
| `.github/workflows/build.yml` | GitHub build/check workflow |

The supplied Rus and Eng language text files are identical, and their compiled DATs are identical too. One shared text source builds both original runtime paths. This preserves the upload; it does not add an English translation. The other `SOURCE/CFG/Lang.txt` in the upload was a different older file and is excluded.

Screenshots, historical README/change files, reference exports, old comparison releases, unused test fixtures, original compiled binaries, duplicate assets and the optional Pillow/NumPy artwork generator are excluded. All final graphics are retained as independently editable pixel/packet sources. No original GI, DAT, DLL or game installation is a build input.

## Build and checks

Building requires **Python 3.10+ and its standard library only**. The regression fixtures additionally require Node.js. Verified environment on 28 October 2026: Python 3.12.14, zlib 1.3.2 and Node.js 24.22.1.

```sh
python3 build.py --strict-original
python3 -m unittest discover -s tests -v
```

Output: `dist/FHD_Trade_FROM_SOURCE.zip`, ready for installation at `Mods/FHD_MODS/FHD_Trade`, and `dist/build-report.json`. Generated CFG/Data/ModuleInfo are ignored by git. The delivered GitHub review archive contains source files, not an installed mod. For deliberate changes, omit `--strict-original`; differing original hashes are reported.

The build reconstructs every runtime file, validates exact file membership and all SHA-256 hashes, independently decodes/re-encodes DAT output, checks all 52 local CacheData references and validates ZIP integrity. The tests also rebuild in an isolated directory with no precompiled mod binaries, check source edits, verify shared-language output and edit pixels in GI types 0, 1 and 2.

Seven supplied regression scripts are retained: goods UI/filtering, multiple goods, requested trading rules, declarations, visibility bounds, vanilla-form merging and resource resolution. The first four run for both Rus and Eng; the remaining three run once, totaling 11 successful invocations. These exercise JS-adapted compiled script statements against controlled game API fixtures. They are not the game's script compiler or a live game.

The drawing-resource check used its former Pillow/NumPy helper only to read image dimensions. It now uses the included lossless GI codec to check the same 80×29 bounds. Stale comments/log text in `goods_fixture.js` were corrected from 0..4 to 0..6 to match its already-existing assertions. These are test-only changes; no runtime values changed. Hosted GitHub execution was not performed during preparation.

## Supplied-check discrepancies

The upload contains checks from several revisions. They were run against the actual supplied runtime files before selecting the self-contained current checks. Failures are not hidden as successful game verification:

| Supplied check | Observed result |
| --- | --- |
| `verify_v20.py` | Fails with `goods_type is not defined`: the fixture directly calls BuildNeededRows without its required commodity parameter. Its expectations also differ from the retained current needed-goods fixture. |
| `verify_stations.py` | Expects four routes using stocks below the current 30-unit planet / 100-unit station thresholds; actual result is zero. The retained requested-rules check covers the current thresholds. |
| `verify_markers.py` | Stops at its old-version reproduction assertion: “Old version unexpectedly passed missing-size reproduction.” This does not establish current marker correctness. |
| `verification/verify_scope.py` | Fails the comparison asserting that trading/localization stayed equal to its bundled older release. The aggregate run_checks stops there. |
| `verification/verify_map.py` | Fails on an assumed fifth child Panel that is absent from the current merged tree. The advertised 212 overlay permutations were not successfully verified. |
| `verification/verify_lifecycle.py` | Fails for both language paths: its fixture expects marker position `[536,354,-10]`, while the actual compiled script produces `[705,487,0]`. |

The current `Markers.Place` uses fixed 768/527 projection constants and z=0. It does not implement the dynamic map-size projection expected by the supplied lifecycle fixture. That mismatch is preserved. Marker alignment on larger maps and compatibility with AModGalaxyLite, QuestMarker, GalaxySearch and FindQuest remain unverified; passing the ordinary form-merge check does not establish those separate contracts.

Only the retained checks are included in this compact package. The original-check assessment and concrete mismatch values remain in `build-verification.json`. The older failed checks were not changed to manufacture a pass.

## Graphics and provenance

GI sources expose version, frame bounds, masks, reserved fields, layer geometry and pixel data. The upload uses two type-0 raw RGB565 images, three type-1 single-plane RGB565 RLE images, and 51 type-2 images with two RGB565 planes plus 6-bit transparency. RLE skips, literals and row terminators are explicit. No opaque original image blob is embedded in JSON.

Input SHA-256: `c2a5904c0a1c67f5a5e4c1c4819b94b36fce22fa6c290ff9de5889880ca02c5d`. The 61 runtime files total 974,451 bytes before packaging. Existing authorship is preserved; original layered art and redistribution permissions were not independently established.

The DAT compiler comes from the upload. The independent DAT checker follows format conventions studied in the previously supplied MIT-licensed [rangers-utils](https://github.com/murgesku/rangers-utils). GI handling reuses the independently developed type-2 codec, extended for the type-0/type-1 layouts in this upload; conventions were checked against the previously supplied [SRHD-XenoModKit](https://github.com/Xenomorphchyma/SRHD-XenoModKit) materials. No third-party executable is bundled.

No live Windows game, actual in-game script compilation, UI drawing, full mixed-mod installation, antivirus verdict or Nexus moderation approval is claimed. Byte identity establishes faithful preservation of the supplied mod.
