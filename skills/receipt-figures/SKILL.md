---
name: receipt-figures
description: "Draw a map or a time series from an attested computation receipt, and from nothing else: the renderer runs the receipt's attester, verifies the per-cell fields file and every array against the hashes in the receipt, and writes the run id, code hash and verdict into the caption. Keywords: plot, map, figure, chart, where, Ekman pumping map, geostrophic speed map, shear skill map, OHC time series, deseasonalized series, trend plot."
---

# receipt-figures

The attested computations answer how much and how well with scalars in
a receipt. The "where" questions (where is the wind pumping water
down, where does density control the shear, where does the
reconstruction fail) and the "show me the series" questions need a
picture, and a picture is the easiest place for an unattested number
to slip in. This skill draws only from receipts that attest, only from
arrays the receipt hashes, and stamps every figure with what it was
drawn from.

The renderer ships beside this skill (`receipt_figure.py`, PEP 723,
numpy and matplotlib). It finds the attesters in the installed
provider bundle through the installer's record (`claude plugin list
--json`), or in a checkout named by `NASA_DAAC_KNOWLEDGE`.

## Behavior

1. Get the receipt. A map needs a receipt whose computation was run
   with `--fields PATH`, so the receipt carries a `fields` block and a
   `.npz` sits at the recorded path or beside the receipt. The
   computations that write fields today are the geostrophic balance
   (`ecco_geostrophy.py`), the wind-stress curl and Ekman pumping
   (`ecco_curl_ekman.py`) and the thermal-wind reconstruction from a
   level of no motion (`ecco_thermal_wind_reconstruction.py`); each
   concept under `knowledge/podaac/computations/` lists its arrays. A
   series needs a trend-with-interval receipt (`ecco_trend_ci.py`),
   which carries the deseasonalized series it fitted.
2. Name the attester from the concept's `attester.resource`
   (`curl_check`, `geos_check`, `thermal_wind_check`,
   `trend_ci_check`). The renderer runs it first and refuses to draw on
   anything but PASS. Do not draw around a FAIL; report it.
3. Draw, from the plugin root:

   ```bash
   uv run skills/receipt-figures/receipt_figure.py map RECEIPT.json \
     --attester curl_check --array w_ekman --mask mask_interior \
     --symmetric --scale 1e6 --units "1e-6 m/s (positive up)" \
     --title "Ekman pumping from wind-stress curl" --out w_ekman.png

   uv run skills/receipt-figures/receipt_figure.py map RECEIPT.json \
     --attester geos_check --speed u_geostrophic v_geostrophic \
     --mask mask_interior --units "m/s" --out geostrophic_speed.png

   uv run skills/receipt-figures/receipt_figure.py map RECEIPT.json \
     --attester thermal_wind_check --array shear_skill_100_1000m \
     --mask mask_domain --vmin 0 --vmax 1 --out shear_skill.png

   uv run skills/receipt-figures/receipt_figure.py series TREND.json \
     --out ohc_series.png
   ```

   Use the mask the scalar was scored on (`mask_interior`,
   `mask_domain`): the figure then shows exactly the cells behind the
   number in the receipt. Use `--symmetric` for signed fields (a
   vertical velocity, a curl, an anomaly) so zero sits at the center of
   a diverging colormap.
4. Hand over the figure WITH its caption line (the renderer prints it):
   receipt run id, code sha256 prefix, fields sha256 prefix, data
   record, attester verdict. Say what the mask was and how many cells
   were drawn; the renderer prints both.
5. Explain the white when it shows. The renderer paints the grid's
   own cells edge to edge, so every unpainted cell is one the
   computation left unscored, and there are three kinds. Vertical
   seams about six cells wide at the four face boundaries of the LLC
   grid (longitudes -127.5, -37.5, 52.5 and 142.5): the stencil of a
   derivative (curl, Ekman pumping, shear) does not cross a tile edge,
   so each tile gives up a three-cell margin on each side of the
   boundary. The band along the equator: the validation domain is 10
   to 55 degrees in each hemisphere. Scattered single cells: the
   seafloor-depth criterion. All three are the computation's scoring
   mask, not gaps in the model or in the data.

## Reading the maps

- Ekman pumping: negative (downward) across the subtropical gyres,
  positive (upward) in the subpolar gyres and along the Southern Ocean.
  Compare with `w_model` at the same interface; the concept says why
  the two agree in sign and pattern and not in value.
- Shear skill 100 to 1000 m: one where thermal wind explains the
  model's shear, zero where it does not. The zero band under deep
  winter mixed layers is real and measured; the concept records it.
- Reconstruction error at depth: `error_absolute_at_depth` is the
  question as asked (against the model's actual current);
  `error_relative_at_depth` isolates the shear. Show the absolute one
  unless the question is about shear.

## Must NOT

- Never draw from a receipt that does not PASS its attester, and never
  draw an array the receipt does not hash. The renderer refuses both;
  do not work around it with a hand-loaded file.
- Never draw tile-frame velocity components (`u_*`, `v_*`) as eastward
  and northward. Speeds and scalars need no rotation and are what this
  renderer draws; a vector map needs the CS and SN rotation the
  vector-orientation gotcha describes, and is not this tool's job.
- Never crop or drop the caption line, and never put a number in the
  title that the receipt does not carry.
- Never interpret the tile seams or the scoring mask as data gaps.
