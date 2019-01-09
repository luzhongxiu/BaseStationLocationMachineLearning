# -*- coding: utf-8 -*-
# @date         : 18-11-5
# @author       : 何泳澔
# @module       :

import sys
import mysql.connector
import numpy

mysql_connection_config = {
    'user': 'unicom',
    'password': 'unicom',
    'host': '127.0.0.1',
    'port': '3306',
    'database': 'unicomDecision'
}


def get_train_samples():
    '''
    该函数用于读取数据库中的训练样本。
    对所有训练样本的操作有：1，None值转化为0；2，去除重复样本（所有字段都一样）；3，还原成原始得分
    :return: 返回numpy类型训练数据集合
    '''

    try:
        con = mysql.connector.connect(**mysql_connection_config)
    except Exception as err:
        print(err)
        print('FAILURE')
        sys.exit(1)
    cursor = con.cursor()
    query_statement = 'SELECT * FROM u_ml_training_data;'
    cursor.execute(query_statement)
    results = cursor.fetchall()
    # columns: id, worksheetId, bTypeScore, bTypeWeight, bAreaScore, bAreaWeight, valueZoneScore, valueZoneWeight,
    # nodeScore, nodeWeight, complaintScore, complaintWeight, customScore, customWeight, totalScore, constMethodClass
    scores = set()
    weights = []
    for idx, item in enumerate(results):
        _, worksheetId, bTypeScore, bTypeWeight, bAreaScore, bAreaWeight, valueZoneScore, valueZoneWeight, nodeScore, nodeWeight,\
            complaintScore, complaintWeight, customScore, customWeight, totalScore, constMethodClass = item
        if constMethodClass != 12 and constMethodClass != 13:
            continue
        scores.add((
            bTypeScore if bTypeScore is not None else 0,
            bAreaScore if bAreaScore is not None else 0,
            valueZoneScore if valueZoneScore is not None else 0,
            nodeScore if nodeScore is not None else 0,
            complaintScore if complaintScore is not None else 0,
            customScore if customScore is not None else 0,
            constMethodClass
        ))
        if idx == 0:
            weights += [
                bTypeWeight.__float__(),
                bAreaWeight.__float__(),
                valueZoneWeight.__float__(),
                nodeWeight.__float__(),
                complaintWeight.__float__(),
                customWeight.__float__()
            ]
    cursor.close()
    con.close()

    scores = list(scores)
    samples = numpy.zeros((len(scores), 7), dtype=numpy.float32)
    counter = {}
    for i in range(len(scores)):
        samples[i, 0] = scores[i][0] / weights[0]
        samples[i, 1] = scores[i][1] / weights[1]
        samples[i, 2] = scores[i][2] / weights[2]
        samples[i, 3] = scores[i][3] / weights[3]
        samples[i, 4] = scores[i][4] / weights[4]
        samples[i, 5] = scores[i][5] / weights[5]
        samples[i, 6] = 1 if scores[i][6] == 12 else -1

        if scores[i][6] in counter:
            counter[scores[i][6]] += 1
        else:
            counter[scores[i][6]] = 1
    for key in counter:
        print('类别-%d-的样本个数为：%d.' % (key, counter[key]))
    return samples


def save_result_to_table(weight_result):
    '''
    该函数用于保存训练后的权重结果
    :param weight_result: 权重结果，包含六个权重
    :return:
    '''
    try:
        con = mysql.connector.connect(**mysql_connection_config)
    except Exception as err:
        print(err)
        print('FAILURE')
        sys.exit(1)
    cursor = con.cursor()
    insert_statement = 'insert into u_ml_result (bTypeWeight, bAreaWeight, valueZoneWeight, nodeWeight, complaintWeight, customWeight, genTime) ' \
                       'values (%.4f, %.4f, %.4f, %.4f, %.4f, %.4f,now());' % (
                           weight_result[0], weight_result[1], weight_result[2], weight_result[3], weight_result[4], weight_result[5])
    cursor.execute(insert_statement)
    con.commit()  # 必须要执行次操作后才能生效
    done = cursor.rowcount
    cursor.close()
    con.close()

    if done != 1:
        print('权重结果插入数据库失败！')
        print('FAILURE')
        sys.exit(1)
    else:
        print('权重结果插入数据库成功！')


def recalculate_scores():
    '''
    该函数使用最新优化得到的权重将所有训练集的样本得分重新计算，并保存
    :return:
    '''
    try:
        con = mysql.connector.connect(**mysql_connection_config)
    except Exception as err:
        print(err)
        print('FAILURE')
        sys.exit(1)

    cursor = con.cursor()
    query_statement = 'SELECT * FROM u_ml_training_data;'
    cursor.execute(query_statement)
    results = cursor.fetchall()
    scores = set()
    orig_weights = []
    for idx, item in enumerate(results):
        _, worksheetId, bTypeScore, bTypeWeight, bAreaScore, bAreaWeight, valueZoneScore, valueZoneWeight, nodeScore, nodeWeight,\
            complaintScore, complaintWeight, customScore, customWeight, totalScore, constMethodClass = item
        if constMethodClass != 12 and constMethodClass != 13:
            continue
        scores.add((
            bTypeScore if bTypeScore is not None else 0,
            bAreaScore if bAreaScore is not None else 0,
            valueZoneScore if valueZoneScore is not None else 0,
            nodeScore if nodeScore is not None else 0,
            complaintScore if complaintScore is not None else 0,
            customScore if customScore is not None else 0,
            constMethodClass
        ))
        if idx == 0:
            orig_weights += [
                bTypeWeight.__float__(),
                bAreaWeight.__float__(),
                valueZoneWeight.__float__(),
                nodeWeight.__float__(),
                complaintWeight.__float__(),
                customWeight.__float__()
            ]

    scores = list(scores)
    samples = numpy.zeros((len(scores), 7), dtype=numpy.float32)
    for i in range(len(scores)):
        samples[i, 0] = scores[i][0] / orig_weights[0]
        samples[i, 1] = scores[i][1] / orig_weights[1]
        samples[i, 2] = scores[i][2] / orig_weights[2]
        samples[i, 3] = scores[i][3] / orig_weights[3]
        samples[i, 4] = scores[i][4] / orig_weights[4]
        samples[i, 5] = scores[i][5] / orig_weights[5]
        samples[i, 6] = scores[i][6]

    # 读取最新权重
    query_statement = 'select * from u_ml_result order by genTime DESC limit 1;'
    cursor.execute(query_statement)
    results = cursor.fetchall()
    _, bTypeWeight, bAreaWeight, valueZoneWeight, nodeWeight, complaintWeight, customWeight, genTime = results[
        0]
    new_weights = [bTypeWeight.__float__(), bAreaWeight.__float__(), valueZoneWeight.__float__(),
                   nodeWeight.__float__(), complaintWeight.__float__(), customWeight.__float__()]
    new_weights = numpy.array(new_weights)

    # 开始写入文件
    import csv
    fout_csv = csv.writer(open('new_scores_%s.csv' % genTime.strftime(
        '%Y-%m-%d_%H:%M:%S'), 'w'), dialect='excel')
    fout_csv.writerow(['bTypeScore', 'bAreaScore', 'valueZoneScore', 'nodeScore',
                       'complaintScore', 'customScore', 'totalScore', 'constMethodClass'])
    for idx, orig_score in enumerate(scores):
        item = []
        new_score = samples[idx, :6] * new_weights
        for j in range(6):
            item.append('%.04f(%.04f)' % (new_score[j], orig_score[j]))
        item.append('%.02f(%.02f)' %
                    (numpy.sum(new_score), numpy.sum(orig_score[:6])))
        item.append('%d' % (orig_score[-1]))

        fout_csv.writerow(item)


if __name__ == '__main__':
    # get_train_samples()
    recalculate_scores()
