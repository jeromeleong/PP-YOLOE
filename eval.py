import argparse
import functools
import os

import paddle
from paddle.io import DataLoader

from data_utils.reader import CustomDataset
from metrics.metrics import COCOMetric
from model.yolo import PPYOLOE_S, PPYOLOE_M, PPYOLOE_L, PPYOLOE_X
from utils.logger import setup_logger
from utils.utils import add_arguments, print_arguments

logger = setup_logger(__name__)

parser = argparse.ArgumentParser(description=__doc__)
add_arg = functools.partial(add_arguments, argparser=parser)
add_arg('model_type',       str,    'M',                           '所使用PPYOLOE的模型类型', choices=["X", "L", "M", "S"])
add_arg('batch_size',       int,    8,                             '训练的批量大小')
add_arg('num_workers',      int,    4,                             '读取数据的线程数量')
add_arg('num_classes',      int,    80,                            '分类的类别数量')
add_arg('image_size',       str,    '640,640',                     '评估时图像输入大小')
add_arg('image_dir',        str,    'dataset/',                    '图片存放的路径')
add_arg('eval_anno_path',   str,    'dataset/eval.json',           '评估标注信息json文件路径')
add_arg('resume_model',     str,    'output/PPYOLOE_M/best_model', '恢复模型文件夹路径')
args = parser.parse_args()
print_arguments(args)


# 评估模型
def evaluate():
    image_size = [int(s) for s in args.image_size.split(',')]
    # 评估数据
    eval_dataset = CustomDataset(image_dir=args.image_dir,
                                 anno_path=args.eval_anno_path,
                                 data_fields=['image'],
                                 eval_image_size=image_size,
                                 mode='eval')
    eval_loader = DataLoader(dataset=eval_dataset,
                             batch_size=args.batch_size,
                             num_workers=args.num_workers)

    # 获取模型
    if args.model_type == 'X':
        model = PPYOLOE_X(num_classes=args.num_classes)
    elif args.model_type == 'L':
        model = PPYOLOE_L(num_classes=args.num_classes)
    elif args.model_type == 'M':
        model = PPYOLOE_M(num_classes=args.num_classes)
    elif args.model_type == 'S':
        model = PPYOLOE_S(num_classes=args.num_classes)
    else:
        raise Exception(f'模型类型不存在，model_type：{args.model_type}')
    # 获取评估器
    metrics = COCOMetric(anno_file=args.eval_anno_path)

    # 加载恢复模型
    assert os.path.exists(os.path.join(args.resume_model, 'model.pdparams')), "模型参数文件不存在！"
    model.set_state_dict(paddle.load(os.path.join(args.resume_model, 'model.pdparams')))
    logger.info('成功恢复模型参数和优化方法参数：{}'.format(args.resume_model))

    model.eval()
    for batch_id, data in enumerate(eval_loader()):
        outputs = model(data)
        metrics.update(inputs=data, outputs=outputs)
    mAP = metrics.accumulate()[0]
    metrics.reset()
    logger.info('mAP: {:.5f}'.format(mAP))


if __name__ == '__main__':
    evaluate()
