# -*- coding: utf-8 -*-

import sys
import csv
import os
from operator import itemgetter
from DivideData import DivideData

class EvaluateMaeInDiffentN(object):

    def __init__(self):
        self.train_set = {}
        self.test_set = {}
        self.sim_matrix = {}
        self.average_matrix = {}
        self.prediction_rate_matrix = {}

    def generate_data_matrix(self, train_set_file, test_set_file, sim_file):
        for line in DivideData.loadfile(train_set_file):
            user, movie, rate, _ = line.split('::')
            self.train_set.setdefault(user, {})
            self.train_set[user][movie] = float(rate)
        for line in DivideData.loadfile(test_set_file):
            user, movie, rate, _ = line.split('::')
            self.test_set.setdefault(user, {})
            self.test_set[user][movie] = float(rate)
        for line in DivideData.loadfile(sim_file):
            forward_user, backward_user, sim = line.split('::')
            self.sim_matrix.setdefault(forward_user, {})
            self.sim_matrix[forward_user][backward_user] = float(sim)

    def generate_average_matrix(self):
        for user in self.train_set:
            for movie, rate in self.train_set[user].iteritems():
                self.average_matrix.setdefault(user, 0)
                self.average_matrix[user] += rate / len(self.train_set[user])

    def dfs_prediction_one_user_rate(self, target_user, target_item, n=20):
        fen_zi, fen_mu = float(0), float(0)
        for user, sim in sorted(self.sim_matrix[target_user].iteritems(), key=itemgetter(1), reverse=True)[:n]:
            if target_item in self.train_set[user]:
                fen_zi += (self.train_set[user][target_item] - self.average_matrix[user]) * self.sim_matrix[target_user][user]
                fen_mu += self.sim_matrix[target_user][user]
        if fen_mu == 0:
            return 0
        else:
            return fen_zi / fen_mu

    def evaluate_mae_in_different_n(self, n=5):
        mae_list = []
        while n <= 200:
            fen_zi = 0
            fen_mu = 0
            for user in self.test_set:
                if int(user) in range(100, 200):
                    for movie in self.test_set[user]:
                        prediction_rate = self.average_matrix[user] + self.dfs_prediction_one_user_rate(user, movie, n)
                        if prediction_rate > 5:
                            prediction_rate = 5
                        fen_zi += abs(self.test_set[user][movie] - prediction_rate)
                        fen_mu += 1
                    a = [n, fen_zi / fen_mu]
            mae_list.append(a)
            print >> sys.stderr, a
            n += 5
        self.export_file('ml-1m/coldstart_mae_cosup_dfm.csv', mae_list)

    def export_file(self, filename, data):
        with open(filename, "wb") as csvFile:
            csv_writer = csv.writer(csvFile)
            for line in data:
                csv_writer.writerow(line)
        csvFile.close()

if __name__ == '__main__':
    train_set_file = os.path.join('ml-1m', 'train_set.csv')
    test_set_file = os.path.join('ml-1m', 'test_set.csv')
    sim_file = os.path.join('ml-1m', 'ColdStart_COS_UPsim.csv')
    '''
    通过换不同的相似度文件，实现不同相似度算法进行的评分预测
    '''
    emidn = EvaluateMaeInDiffentN()
    emidn.generate_data_matrix(train_set_file, test_set_file, sim_file)
    emidn.generate_average_matrix()
    emidn.evaluate_mae_in_different_n()