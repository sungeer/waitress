


-- 查看有哪些行号符合
grep -n -F "- ERROR" waitress.log

-- 同时满足
grep -n -F "- ERROR" waitress.log | grep "2026-09-02"

-- 任有其一
grep -n -F -e "- ERROR" -e "2026-09-02" waitress.log


-- 定位到指定行
less +3 waitress.log


-- 带上行号
less -N +3 waitress.log




