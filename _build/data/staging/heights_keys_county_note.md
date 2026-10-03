# Keys unincorporated seawall-height rows: cover on the Monroe County page

Rows held at status `needs-content` in `_build/data/CityTopics.csv` (topic `seawall-height-requirement`):
key-largo, big-pine-key, tavernier, cudjoe-key.

## Why they are held

All four are unincorporated, so the same Monroe County sections govern each one:

- Monroe County LDC Sec. 118-12(k) (bulkheads, seawalls and riprap): no minimum or maximum top
  elevation in any datum; the only height rule is that grade behind the wall sits at least six inches
  below the top of the wall (118-12(k)(2)); 2 ft cap limit on a seawall without a principal use
  (118-12(k)(1)); vertical walls only on manmade canals, channels or basins (118-12(k)(3)); repair or
  replacement of lawful deteriorated walls (118-12(k)(4)); no walls on turtle nesting beaches
  (118-12(k)(7)).
- Monroe County LDC Sec. 122-31(d)(1): Zone V conditions for bulkheads and seawalls.

The four rows carry the same facts with only the place name changed. Once the place name is removed,
the publishing guard (`_build/guard.py`, `doorway_problems`) sees near-identical pages, and there is
no place-specific code to add: Key Largo, Big Pine Key, Tavernier and Cudjoe Key have no local code of
their own. Adding text just to get past the guard would be padding, which the brand rule forbids.

## Recommendation

Cover the rule once on the Monroe County page (under `/monroe/`, currently `/monroe/seawalls/`) as "Unincorporated Monroe County
(Key Largo, Tavernier, Big Pine Key, Cudjoe Key and the other unincorporated Keys)", citing LDC
118-12(k) and 122-31(d)(1). The verified wording in the four rows (and in
`staging/heights_keys.csv` / `staging/heights_vetted.csv`) can be reused as is. Then either:

1. leave the four place rows unpublished, or
2. publish them later only if a real place-specific fact turns up (for example a Livable CommuniKeys
   or community master plan provision that touches shorelines, or a county ordinance that applies to
   one key only), each read in the primary source.

The county page itself was not edited (out of scope for this pass). The incorporated Keys cities
(Key West, Marathon, Islamorada, Key Colony Beach) have their own codes and are unaffected.

Written 3 Oct 2026.
