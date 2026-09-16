


-- 查看有哪些行号符合
grep -n -e "- ERROR" waitress.log

-- 同时满足
grep -n -e "- ERROR" waitress.log | grep "0916"

-- 任有其一
grep -n -e "- ERROR" -e "0916" waitress.log


-- 定位到指定行
less +3 waitress.log


-- 带上行号
less -N +3 waitress.log




