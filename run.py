import json
from sys import path as root_path
from os import path
from news.News import News

CURRENT_PATH = path.join(root_path[0], 'configs')
CHECK_POINTS_PATH = path.join(CURRENT_PATH, 'checkpoints.json')

with open(CHECK_POINTS_PATH, 'r', encoding='utf-8-sig') as f:
    latest_checkpoints = json.loads(f.read())
news_system = News(
    delay=60, 
    trace_limit=2, 
    summarize_algorithm='text_rank', 
    compression_rate=.6, 
    checkpoints=latest_checkpoints)
#checkpoints = news_system.start()
checkpoints = news_system.run_tasks()
with open(CHECK_POINTS_PATH, 'w', encoding='utf-8-sig') as f:
    json.dump(checkpoints, f, ensure_ascii=False)