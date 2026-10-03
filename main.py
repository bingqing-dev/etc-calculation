import argparse
from core import run

def parse_args():
    parser = argparse.ArgumentParser(description='作物需水量计算')
    parser.add_argument('--file',type=str ,required = True ,
                        help='气象数据 csv 路径')

    parser.add_argument('--crop',type=str ,default = 'corn',
                        help='作物类型 默认corn')

    parser.add_argument('--start',type=str ,default = None,
                        help='起始日期(YYY-MM-DD)')

    parser.add_argument('--end',type=str ,default = None,
                        help='截止日期(YYY-MM-DD)')

    parser.add_argument('--output', type=str, default='etc_result.csv',
                        help='输出文件路径')
    return parser.parse_args()

def main():
    args = parse_args()
    result = run(args.file,args.crop,args.start,args.end,args.output)
if __name__ == '__main__':
    main()