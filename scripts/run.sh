#!/bin/zsh
# Generate a cover set by handing the task files to Codex's built-in image
# generator: task-master.md first (16:9), then task-ratios.md (other ratios).
# Sleeps until the ChatGPT usage-limit reset whenever the limit is hit, and
# skips any ratio whose PNG already exists in the output folder.
#
# usage: zsh run.sh <work_dir> <out_dir>
W=${1:?work dir}; OUT=${2:?out dir}
CODEX=${CODEX_BIN:-$(command -v codex 2>/dev/null)}
[[ -x $CODEX ]] || CODEX=/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex
[[ -x $CODEX ]] || { echo "codex CLI not found; set CODEX_BIN"; exit 1; }
RATIOS=(${(f)"$(cat $W/ratios.txt 2>/dev/null)"})

wait_reset() {  # $1 = log file; sleep until "try again at H:MM PM" + 1 min
  local t=$(grep -o 'try again at [0-9:]* [AP]M' "$1" | tail -1 | sed 's/try again at //')
  [[ -z $t ]] && { sleep 600; return; }
  local target=$(date -j -f "%I:%M %p" "$t" +%s 2>/dev/null)
  local now=$(date +%s)
  (( target < now - 3600 )) && target=$((target + 86400))
  local s=$((target - now + 60)); (( s < 60 )) && s=60
  echo "$(date +%T) usage limit, sleeping ${s}s until $t"; sleep $s
}
missing_ratios() { for r in $RATIOS; do [[ -f $OUT/$r-高清.png ]] || echo $r; done; }
images() {  # $1 = list file from make_tasks.py; prints --image=<f> for each existing file
  local f; for f in ${(f)"$(cat $1 2>/dev/null)"}; do [[ -f $f ]] && echo "--image=$f"; done
}

mkdir -p $OUT; cd $W
for i in 1 2 3 4; do
  [[ -f $OUT/YouTube-16比9-高清.png ]] && break
  grep -q 'hit your usage limit' codex-run.log 2>/dev/null && wait_reset codex-run.log
  echo "$(date +%T) run 16:9 attempt $i"
  $CODEX exec --skip-git-repo-check -s danger-full-access -o codex-last.md ${(f)"$(images images-master.txt)"} -- "$(cat task-master.md)" > codex-run.log 2>&1 < /dev/null
done
[[ -f $OUT/YouTube-16比9-高清.png ]] || { echo "16:9 still missing, giving up"; exit 1; }
echo "$(date +%T) 16:9 done"
[[ -f task-ratios.md && -n $RATIOS ]] || { echo "$(date +%T) finished (master only)"; exit 0; }

for i in 1 2 3 4 5; do
  [[ -z $(missing_ratios) ]] && break
  grep -q 'hit your usage limit' codex-run-2.log 2>/dev/null && wait_reset codex-run-2.log
  echo "$(date +%T) run other ratios attempt $i, missing: $(missing_ratios | tr '\n' ' ')"
  $CODEX exec --skip-git-repo-check -s danger-full-access -o codex-last-2.md ${(f)"$(images images-ratios.txt)"} -- "$(cat task-ratios.md)" > codex-run-2.log 2>&1 < /dev/null
done
echo "$(date +%T) finished, missing: $(missing_ratios | tr '\n' ' ')"
