# 基金定投收益率测算
## 使用方法：
  python3 fund_calculate_return.py 513500 --start_date '2023-01-01' --end_date '2024-12-31' --amount 1000 --freq 'M' --day_offset 10
  - 在2023-01-01至2024-12-31期间每月10日定投一笔1000元 513500基金（若当月10号没有基金净值数据默认取10号最近一天进行定投）
  - 使用前先去改脚本中的文件保存路径file_path
### 参数说明：
  - 513500：基金代码，必填
  - --start_date:回测开始日期
  - --end_date:回测结束日期
  - --amount:每次定投金额
  - --freq:定投频率，M-每月，Q-每季度，Y-每年，W-每周
  - --day_offset:频率偏移量，频率月/季/年从月/季/年初开始计算，频率周从周一开始计算

### 返回结果
<img width="736" alt="image" src="https://github.com/user-attachments/assets/3931fde9-adfb-4f53-b9c7-9bcdbc18d9ac" />

  
