from src._count import kmer_count
from src._count import kmer_count_m_k
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import time
import os
import method
import argparse

Suffix = ['.fasta', '.fsa', '.fna', '.fa']
Alphabeta = ['A', 'C', 'G', 'T']
Alpha_dict = dict(zip(Alphabeta, range(4)))

def num2nuc(num, k):
    num_bin = format(num, '0%sb'%(k*2))
    return ''.join([Alphabeta[int(num_bin[i:i+2], 2)] for i in range(0, len(num_bin), 2)])

def shift(num, K, M, x):
    mask = 2**(2*M)-1
    num = num >> ((K-M)*2 - 2*x)
    num &= mask
    return num

def seqname_strip(seqname, from_seq):
    if not from_seq:
        seqname = os.path.basename(seqname)
        for suffix in Suffix:
            seqname = seqname.replace(suffix, '')
    return seqname

def get_sequence_from_file(filename):
    sequence_list = []
    with open(filename) as f:
        for line in f.readlines():
            line = line.strip()
            if not os.path.exists(line):
                e = 'File %s do no exsits!'%line
                raise Exception(e)
            for suffix in Suffix:
                if line.endswith(suffix):
                    sequence_list.append(line)
    return sequence_list 
   
def check_arguments(K, M, filename, filename1, filename2, seqfile, seqfile1, seqfile2, P_dir, output, threads):
    if K <= 0:
        raise ValueError('Kmer length must be a positive integer!')
    if M <= 0:
        raise ValueError('Markovian order must be a non-negative integer!')
    '''
    if M >= K:
        raise ValueError('Markovian order cannot be greater than K-2!') 
    '''
    if threads <= 0:
        raise ValueError('Number of threads must be a positive integer!')
    if filename and not (filename1 or filename2 or seqfile or seqfile1 or seqfile2):
        pass
    elif (filename1 and filename2) and not (filename or seqfile or seqfile1 or seqfile2):
        pass
    elif seqfile and not (filename or filename1 or filename2 or seqfile1 or seqfile2):
        pass
    elif (seqfile1 and seqfile2) and not (filename or filename1 or filename2 or seqfile):
        pass
    else:
        e = 'Use either -f OR -f1, -f2 OR -s OR -s1, -s2 to indicate input sequences!'
        raise Exception(e)
    if P_dir == 'None':
        print('Warning: Using -d option to save kmer counts in a directory can save you a lot of counting time.')
    else:
        os.system('mkdir -p %s'%P_dir)
    if output == './':
        print('Warning: Using -o option to change output directory and prefix. Otherwise, output will be generated in the current directory.')
    else:
        d = os.path.dirname(output)
        if d:
            os.system('mkdir -p %s'%d)

def get_matrix(a_method):
    if a_method not in ['d2star', 'd2shepp', 'cvtree', 'ma', 'eu', 'd2']:
        print('Invalid method %s'%a_method)
        print('Only d2star,d2shepp,CVtree,Ma,Eu,d2 are supported') 
        raise NameError
    else:
        if a_method == 'd2star':
            return method.d2star_matrix_pairwise
        elif a_method == 'd2shepp':
            return method.d2shepp_matrix_pairwise
        elif a_method == 'cvtree':
            return method.CVTree_matrix_pairwise
        elif a_method == 'ma':
            return method.Ma_matrix_pairwise
        elif a_method == 'eu':
            return method.Eu_matrix_pairwise
        else:
            return method.d2_matrix_pairwise
 
def get_bias(a_method):
    if a_method == 'd2star':
        return method.d2star_bias_array
    elif a_method == 'd2shepp':
        return method.d2shepp_bias_array
    else:
        return None

def get_matrix_group(a_method):
    if a_method not in ['d2star', 'd2shepp', 'cvtree', 'ma', 'eu', 'd2']:
        print('Invalid method %s'%a_method)
        print('Only d2star,d2shepp,CVtree,Ma,Eu,d2 are supported')
        raise NameError
    else:
        if a_method == 'd2star':
            return method.d2star_matrix_groupwise
        elif a_method == 'd2shepp':
            return method.d2shepp_matrix_groupwise
        elif a_method == 'cvtree':
            return method.CVTree_matrix_groupwise
        elif a_method == 'ma':
            return method.Ma_matrix_groupwise
        elif a_method == 'eu':
            return method.Eu_matrix_groupwise
        else:
            return method.d2_matrix_groupwise

def write_phy(output, a_method, seqname_list, matrix, from_seq):
    if output.endswith('/'):
        filename = output + a_method + '.' + 'phy'
    else:
        filename = '.'.join([output, a_method, 'phy'])
    num = len(seqname_list)
    with open(filename, 'wt') as f:
        f.write('%d\n'%num)
        for i in range(num):
            seqname = seqname_strip(seqname_list[i], from_seq)
            f.write(seqname)
            for value in matrix[i]:
                f.write('\t%.4f'%value)
            f.write('\n')

def write_tsv(output, a_method, seqname_list, matrix, from_seq):
    if output.endswith('/'):
        filename = output + a_method + '.' + 'tsv'
    else:
        filename = '.'.join([output, a_method, 'tsv'])
    num = len(seqname_list)
    with open(filename, 'wt') as f:
        for i in range(num):
            seq_1 = seqname_strip(seqname_list[i], from_seq)
            for j in np.argsort(matrix[i]):
                seq_2 = seqname_strip(seqname_list[j], from_seq)
                if i != j:
                    f.write('%s\t%s\t%.4f\n'%(seq_1, seq_2, matrix[i][j]))

def write_phy_group(output, a_method, seqname_list_1, seqname_list_2, matrix, from_seq):
    if output.endswith('/'):
        filename = output + a_method + '.' + 'phy'
    else:
        filename = '.'.join([output, a_method, 'phy'])
    num1 = len(seqname_list_1)
    num2 = len(seqname_list_2)
    with open(filename, 'wt') as f:
        f.write('%d,%d\n'%(num1, num2))
        for j in range(num2):
            f.write('\t'+seqname_strip(seqname_list_2[j], from_seq))
        f.write('\n')
        for i in range(num1):
            f.write(seqname_strip(seqname_list_1[i], from_seq))
            for value in matrix[i]:
                f.write('\t%.4f'%value)
            f.write('\n')

def write_tsv_group(output, a_method, seqname_list_1, seqname_list_2, matrix, from_seq):
    if output.endswith('/'):
        filename = output + a_method + '.' + 'tsv'
    else:
        filename = '.'.join([output, a_method, 'tsv'])
    num1 = len(seqname_list_1)
    with open(filename, 'wt') as f:
        for i in range(num1):
            seq_1 = seqname_strip(seqname_list_1[i], from_seq)
            for j in np.argsort(matrix[i]):
                seq_2 = seqname_strip(seqname_list_2[j], from_seq)
                f.write('%s\t%s\t%.4f\n'%(seq_1, seq_2, matrix[i][j]))

def write_bias(output, a_method, seqname_list_1, seqname_list_2, array1, array2, from_seq):
    if output.endswith('/'):
        filename = output + a_method + '.bias' + '.' + 'tsv'
    else:
        filename = '.'.join([output, a_method, 'bias', 'tsv'])
    with open(filename, 'wt') as f:
        for i in range(len(array1)):
            seq = seqname_strip(seqname_list_1[i], from_seq)
            f.write('%s\t%.4f\n'%(seq, array1[i]))
        for j in range(len(array2)):
            seq = seqname_strip(seqname_list_2[i], from_seq) 
            f.write('%s\t%.4f\n'%(seq, array2[i]))

def write_BIC(output, seqname_list, BIC_list, from_seq):
    #print(seqname_list)
    if output.endswith('/'):
        filename = output + 'BIC'
    else:
        filename = '.'.join([output, 'BIC'])
    with open(filename, 'wt') as f:
        for i in range(len(seqname_list)):
            seqname = seqname_strip(seqname_list[i], from_seq)
            f.write('%s\t%d\n'%(seqname, BIC_list[i]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Example: python alignmentfree.py -r -a d2star,d2shepp,CVtree -k 12 -m 10 -f filename -d dir -o output') 
    parser.add_argument('-a', dest='method', help='A list of alignment-free method, separated by comma: d2star,d2shepp,CVtree,Ma,Eu,d2')
    parser.add_argument('-k', dest='K', required = True, type = int, help='Kmer length')
    parser.add_argument('-m', dest='M', type = int, default=0, help='Markovian Order, required for d2star, d2shepp and CVtree')
    parser.add_argument('-f', dest='filename', help='A file that lists the paths of all samples, cannot be used together with -f1, -f2, -s, -s1, -s2')
    parser.add_argument('-s', dest='sequence_file', help='A fasta file that lists the sequences of all samples, cannot be used together with -f, -f1, -f2, -s1, -s2')
    parser.add_argument('-f1', dest='filename1', help='A file that lists the paths of the first group of samples, must be used together with -f2, cannot be used together with -f, -s, -s1, -s2')
    parser.add_argument('-f2', dest='filename2', help='A file that lists the paths of the second group of samples, must be used together with -f1, cannot be used together with -f, -s, -s1, -s2')
    parser.add_argument('-s1', dest='sequence_file_1', help='A fasta file that lists the sequences of the first group of samples, must be used together with -s2, cannot be used together with -f, -f1, -f2, -s')
    parser.add_argument('-s2', dest='sequence_file_2', help='A fasta file that lists the sequences of the second group of samples, must be used together with -s1, cannot be used together with -f, -f1, -f2, -s')
    parser.add_argument('-d', dest='Dir', default='None', help='A directory that saves kmer count')
    parser.add_argument('-o', dest='output', help='Prefix of output (defualt: Current directory)', default='./')
    parser.add_argument('-t', dest='threads', type = int, default=1, help='Number of threads')
    parser.add_argument('-r', dest='reverse_complement', action='store_true', default=False, help='Count the reverse complement of kmers (default: False)')
    parser.add_argument('--adjust', dest='adjust', action='store_true', default=False, help='Adjust d2star and/or d2shepp distances for NGS samples, -r will be set automatically')
    parser.add_argument('--BIC', dest='BIC', action='store_true', default=False, help='Use BIC to estimate the Markovian orders of sequences')
    parser.add_argument('--slow', dest='slow', action='store_true', default=False, help='Use slow mode for calculation with less memory usage (default: False)')
    args = parser.parse_args()
    K = args.K 
    M = args.M + 1
    filename = args.filename
    filename1 = args.filename1
    filename2 = args.filename2
    seqfile = args.sequence_file
    seqfile1 = args.sequence_file_1
    seqfile2 = args.sequence_file_2
    if seqfile or (seqfile1 and seqfile2):
        from_seq = True
    else:
        from_seq = False
    Reverse = args.reverse_complement
    adjust = args.adjust 
    if adjust:
        Reverse = True
    BIC = args.BIC
    slow = args.slow
    P_dir = args.Dir
    seqname_list = []
    sequence_list = []
    sequence_list_1 = []
    sequence_list_2 = []
    Num_Threads = args.threads
    output = args.output
    check_arguments(K, M, filename, filename1, filename2, seqfile, seqfile1, seqfile2, P_dir, output, Num_Threads)
    if BIC:
        if from_seq:
            seqname_old_list, seqname_list, sequence_list = method.get_sequences(seqfile) 
        else:
            seqname_list = get_sequence_from_file(filename)
        print('Calculating Markovian order.')
        BIC_list = method.all_BIC(seqname_list, K, Num_Threads, Reverse, P_dir, sequence_list, from_seq)
        if from_seq:
            write_BIC(output, seqname_old_list, BIC_list, from_seq)
        else:
            write_BIC(output, seqname_list, BIC_list, from_seq)
    else:
        methods = [x.strip().lower() for x in args.method.split(',')]
        if filename or seqfile:
            if from_seq:
                seqname_old_list, seqname_list, sequence_list = method.get_sequences(seqfile)
            else:
                seqname_list = get_sequence_from_file(filename)
            for a_method in methods:
                print('Calculating %s.'%a_method)
                matrix = get_matrix(a_method)(seqname_list, M, K, Num_Threads, Reverse, P_dir, sequence_list, from_seq, slow)
                if from_seq:
                    seqname_list = seqname_old_list
                write_tsv(output, a_method, seqname_list, matrix, from_seq)
                write_phy(output, a_method, seqname_list, matrix, from_seq)
                if a_method in ['d2star', 'd2shepp'] and Reverse and adjust:
                    bias_array = get_bias(a_method)(seqname_list, M, K, Num_Threads, Reverse, P_dir,  sequence_list, from_seq, slow)
                    write_bias(output, a_method, seqname_list, [], bias_array, [], from_seq)
                    new_matrix = method.matrix_adjusted_pairwise(matrix, bias_array, a_method)
                    write_tsv(output, a_method + '_adjusted', seqname_list, new_matrix, from_seq)
                    write_phy(output, a_method + '_adjusted', seqname_list, new_matrix, from_seq)
        else: 
            if from_seq:
                seqname_old_list_1, seqname_list_1, sequence_list_1 = method.get_sequences(seqfile1)
                seqname_old_list_2, seqname_list_2, sequence_list_2 = method.get_sequences(seqfile2)
            else:
                seqname_list_1 = get_sequence_from_file(filename1)
                seqname_list_2 = get_sequence_from_file(filename2)
            for a_method in methods:
                print('Calculating %s.'%a_method)
                matrix = get_matrix_group(a_method)(seqname_list_1, seqname_list_2, M, K, Num_Threads, Reverse, P_dir, sequence_list_1, sequence_list_2, from_seq, slow)
                if from_seq:
                    seqname_list_1 = seqname_old_list_1
                    seqname_list_2 = seqname_old_list_2
                write_phy_group(output, a_method, seqname_list_1, seqname_list_2, matrix, from_seq)
                write_tsv_group(output, a_method, seqname_list_1, seqname_list_2, matrix, from_seq)
                if a_method in ['d2star', 'd2shepp'] and Reverse and adjust:
                    bias_array_1 = get_bias(a_method)(seqname_list_1, M, K, Num_Threads, Reverse, P_dir,  sequence_list_1, from_seq, slow)
                    bias_array_2 = get_bias(a_method)(seqname_list_2, M, K, Num_Threads, Reverse, P_dir,  sequence_list_2, from_seq, slow)
                    write_bias(output, a_method, seqname_list_1, seqname_list_2, bias_array_1, bias_array_2, from_seq)
                    new_matrix = method.matrix_adjusted_groupwise(matrix, bias_array_1, bias_array_2, a_method)
                    write_phy_group(output, a_method + '_adjusted', seqname_list_1, seqname_list_2, new_matrix, from_seq)
                    write_tsv_group(output, a_method + '_adjusted', seqname_list_1, seqname_list_2, new_matrix, from_seq)
