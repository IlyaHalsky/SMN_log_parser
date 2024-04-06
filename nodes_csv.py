from smn_logs import minions_by_dbfId

with open('nodes.csv', 'w') as f:
    f.write('Id,Label,Interval' + '\n')
    for k, v in minions_by_dbfId.items():
        f.write(f'{k},{v['name'].replace(",", "")},\n')