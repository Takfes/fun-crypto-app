import os
import logging
import datetime
import pandas as pd

# dir_path = '/home/takis/Desktop/sckool/my-crypto-app/'
current_file_name = os.path.basename(__file__)
dir_path = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dir_path,f'logs/{current_file_name}.log')
os.chdir(dir_path)

logging.basicConfig(filename=filename,level=logging.DEBUG,
                    format='%(asctime)s:%(filename)s:%(message)s')

date = datetime.datetime.now().strftime('%Y-%m-%d, %H:%M')
print(f'this is a print message from parser.py @ {date}')
logging.warning(f'this is a logging message from parser.py @ {date}')


# pd.read_csv('signals.csv').to_csv('takis.csv')
# pd.read_csv('/home/takis/Desktop/sckool/my-crypto-app/signals.csv').to_csv('/home/takis/Desktop/sckool/my-crypto-app/takis.csv')

# print(__name__)
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)
# file_handler  = logging.FileHandler(filename)
# file_handler.setLevel(logging.INFO)
# file_handler.setFormatter(logging.Formatter('%(asctime)s:%(filename)s:%(message)s'))
# logger.addHandler(file_handler)
# logger.info('hello')
# logger.info('i wrote a line')

# if __name__ == '__main__':
#     do_logging()