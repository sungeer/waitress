


-- 查看有哪些行号符合
grep -n -e "- ERROR" waitress.log


-- 定位到指定行
less +3 waitress.log


-- 带上行号
less -N +3 waitress.log




