"""Break each check inside check_article.py and confirm the test suite fails.

Run from the repo root: python3 plugins/article-writer/tests/mutations.py
Each mutation is applied to a COPY-restored file and the restore is compared
byte for byte before the next one runs; never revert with git checkout (an
uncommitted edit would go with it). Exit 1 if any mutation survives.
"""
import filecmp, os, shutil, subprocess, sys, tempfile
F = "plugins/article-writer/skills/article-writer/scripts/check_article.py"
ORIG = os.path.join(tempfile.mkdtemp(), "check_article.orig.py")
shutil.copy(F, ORIG)
M=[
("required off", 'return [f"frontmatter {k!r} is missing or empty"', 'return [] and [f"frontmatter {k!r} is missing or empty"'),
("description > to >=", "if len(desc) > limit:", "if len(desc) > limit + 1:"),
("em dash off", 'return [f"{n} em dash(es) in rendered copy"] if n else []', 'return []'),
("banned off", '            found.setdefault(word, m.group(0))', '            pass'),
("unlock narrowing dropped", 'if word == "unlock" and not UNLOCK_HYPE.search(line):', 'if word == "unlock":'),
("leverage noun strip dropped", 'm = pat.search(LEVERAGE_NOUN.sub("", line) if word == "leverage" else line)', 'm = pat.search(line)'),
("banned_extra ignored", '        pats[w] = re.compile(rf"\\b{re.escape(w)}\\b", re.I)', '        pass'),
("comments not stripped", 'r"```.*?```|<!--.*?-->|`[^`\\n]*`"', 'r"```.*?```|`[^`\\n]*`"'),
("internal heading off", 'return ["the file carries an internal-only source heading"] if INTERNAL_HEADING.search(full_text) else []', 'return []'),
("internal heading reads copy only", 'check_internal_heading(text)', 'check_internal_heading(copy_text)'),
("placeholder off", 'if PLACEHOLDER.search(copy_text) else []', 'if False else []'),
("source log presence off", '        return ["no \'<!-- Sources checked YYYY-MM-DD:\' comment"]', '        return []'),
("source log bare URL accepted", r'(https?://\S+\s+(?::\s*)?\S|Internal:\s*\S)', r'(https?://\S+|Internal:\s*\S)'),
("source_log optional ignored", '    if cfg["source_log"] == "optional":\n        return []', '    if False:\n        return []'),
("placements off", '        elif not contains_keyword(targets[p], keyword):', '        elif False:'),
("slug half rule off", 'if words and len(hits) * 2 < len(words):', 'if False:'),
("h1 from body ignored", '"h1": body_h1(body) or title,', '"h1": title,'),
("unknown profile key accepted", '            raise UsageError(f"profile checks: unknown key', '            continue\n            raise UsageError(f"profile checks: unknown key'),
("banned_allow unchecked", '    if unknown:\n        raise', '    if False:\n        raise'),
("placements severity always WARN", 'return "FAIL" if flag == "yes" else "WARN"', 'return "WARN"'),
("placements severity always FAIL", 'return "FAIL" if flag == "yes" else "WARN"', 'return "FAIL"'),
("exit 1 dropped", '        return 1\n    note', '        return 0\n    note'),
]
src=open(ORIG).read(); bad=0
for name,old,new in M:
    if src.count(old)!=1: print("ANCHOR?",name,src.count(old)); bad+=1; continue
    open(F,"w").write(src.replace(old,new))
    r=subprocess.run([sys.executable,"-m","unittest","discover","-s","plugins/article-writer/tests"],capture_output=True,text=True)
    shutil.copy(ORIG,F); assert filecmp.cmp(ORIG,F,shallow=False)
    caught = r.returncode!=0
    first=[l for l in r.stderr.splitlines() if l.startswith(("FAIL:","ERROR:"))][:1]
    print(("caught  " if caught else "SURVIVED"),name, first[0][:110] if first else "")
    bad+= not caught
print("survivors/anchor problems:",bad)
sys.exit(1 if bad else 0)
