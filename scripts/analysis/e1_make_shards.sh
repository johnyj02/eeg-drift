#!/usr/bin/env bash
# D25-E1: pack the RELEASED preprocessing outputs into tar shards for S3 staging (no upload here).
# processed_seg/{train,val,test}/*.pkl -> chbmit_seg-<split>-NNN.tar (20,000 files each, paths
# relative to processed_seg/, so `tar -xf` in a datasets_dir recreates the layout), and the SSL
# LMDB directory as one tar. Writes MANIFEST.tsv (shard, files, bytes, sha256).
#
#   bash e1_make_shards.sh <released chbmit output root> <shard dir>
set -euo pipefail
SRC=$1 OUT=$2 PER=20000
mkdir -p "$OUT/lists"
cd "$SRC/processed_seg"
for split in train val test; do
  find "$split" -maxdepth 1 -name '*.pkl' | LC_ALL=C sort > "$OUT/lists/$split.txt"
  split -d -a 3 -l $PER "$OUT/lists/$split.txt" "$OUT/lists/$split-"
done
ls "$OUT"/lists/*-[0-9][0-9][0-9] | xargs -P 8 -I{} sh -c \
  'b=$(basename {}); tar -cf "'"$OUT"'/chbmit_seg-$b.tar" -T {}'
cd "$SRC"
tar -cf "$OUT/chbmit_preprocessed_30S.lmdb.tar" chbmit_preprocessed_30S.lmdb
cd "$OUT"
printf "shard\tfiles\tbytes\tsha256\n" > MANIFEST.tsv
for t in *.tar; do
  b=${t#chbmit_seg-}; b=${b%.tar}
  n=$( [ -f "lists/$b" ] && wc -l < "lists/$b" || tar -tf "$t" | wc -l )
  printf "%s\t%s\t%s\t%s\n" "$t" "$n" "$(stat -c %s "$t")" "$(sha256sum "$t" | cut -d' ' -f1)"
done >> MANIFEST.tsv
cat MANIFEST.tsv
