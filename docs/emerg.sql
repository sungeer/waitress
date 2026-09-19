


-- 查看有哪些行号符合
grep -n -F " ERR " waitress_2026-09-19.log

-- 同时满足
grep -n -F " ERR " waitress_2026-09-19.log | grep "20:47"

-- 任有其一
grep -n -F -e " ERR " -e "20:47" waitress_2026-09-19.log


-- 定位到指定行
less +4 waitress_2026-09-19.log


-- 带上行号
less -N +4 waitress_2026-09-19.log




