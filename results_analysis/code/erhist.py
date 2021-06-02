#!/usr/bin/env python
# coding: utf-8
import numpy as np
from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt
from obspy import UTCDateTime, read
import time


def to_percent(y, position):
    return str(100 * y) + "%"


def xfj_errhist(phnet_file, eqt_file, catalog, snr_file=None):
    catalog = np.load(catalog, allow_pickle=True).item()
    phnet = np.load(phnet_file, allow_pickle=True).item()
    eqt = np.load(eqt_file, allow_pickle=True).item()
    if snr_file:
        snr = np.load(snr_file, allow_pickle=True)['snr'].item()
        ph_SNR = []
        eqt_SNR = []
    phnerr = {}
    phnerr['P'] = []
    phnerr['S'] = []
    phndist = []
    phnmag = []
    phnfp = 0
    phntp = 0
    eqterr = {}
    eqterr['P'] = []
    eqterr['S'] = []
    eqtdist = []
    eqtmag = []
    eqtfp = 0
    eqttp = 0
    for evn in phnet:
        if (evn in eqt) and (evn in catalog['phase']):
            # print(evn)
            for st in phnet[evn]:
                if (st in eqt[evn]) and (st in catalog['phase'][evn]):
                    # print(st)
                    # print(catalog['phase'][evn][st])
                    if ('P' in phnet[evn][st]) and ('P' in eqt[evn][st]) \
                            and ('P' in catalog['phase'][evn][st]):
                        # ----phnet
                        phnet_erral = np.array(phnet[evn][st]['P']) - \
                                      catalog['phase'][evn][st]['P'] + 8 * 3600
                        if min(abs(phnet_erral)) < 0.5:
                            phnfp = phnfp + len(phnet_erral) - 1
                            phntp += 1
                            phnerr['P'].append(phnet_erral[np.argmin(abs(phnet_erral))])
                            phndist.append(catalog['dist'][evn][st])
                            phnmag.append(catalog['head'][evn]['ML'])
                            if snr_file and (st in snr[evn]):
                                ph_SNR.append(snr[evn][st])
                        else:
                            phnfp = phnfp + len(phnet_erral)
                        # ----EQT
                        EQT_erral = np.array(eqt[evn][st]['P']) - \
                                    catalog['phase'][evn][st]['P'] + 8 * 3600
                        if min(abs(EQT_erral)) < 0.5:
                            eqtfp = eqtfp + len(EQT_erral) - 1
                            eqttp += 1
                            eqterr['P'].append(min(EQT_erral))
                            eqtdist.append(catalog['dist'][evn][st])
                            eqtmag.append(catalog['head'][evn]['ML'])
                            if snr_file and (st in snr[evn]):
                                eqt_SNR.append(snr[evn][st])
                        else:
                            eqtfp = eqtfp + len(EQT_erral)
                    if ('S' in phnet[evn][st]) and ('S' in eqt[evn][st]) \
                            and ('S' in catalog['phase'][evn][st]):
                        # ----phnet
                        phnet_erral = np.array(phnet[evn][st]['S']) - \
                                      catalog['phase'][evn][st]['S'] + 8 * 3600
                        if min(abs(phnet_erral)) < 0.5:
                            phnfp = phnfp + len(phnet_erral) - 1
                            phntp += 1
                            phnerr['S'].append(min(phnet_erral))
                            phndist.append(catalog['dist'][evn][st])
                            phnmag.append(catalog['head'][evn]['ML'])
                        else:
                            phnfp = phnfp + len(phnet_erral)
                        # ----EQT
                        EQT_erral = np.array(eqt[evn][st]['S']) - \
                                    catalog['phase'][evn][st]['S'] + 8 * 3600
                        if min(abs(EQT_erral)) < 0.5:
                            eqtfp = eqtfp + len(EQT_erral) - 1
                            eqttp += 1
                            eqterr['S'].append(min(EQT_erral))
                            eqtdist.append(catalog['dist'][evn][st])
                            eqtmag.append(catalog['head'][evn]['ML'])
                        else:
                            eqtfp = eqtfp + len(EQT_erral)
    eqt_accuracy = eqttp/(eqtfp+eqttp)
    phn_accuracy = phntp / (phnfp + phntp)
    # breakpoint()
    # P pick image
    num_bins = 41
    plt.hist(phnerr['P'], num_bins, weights=[1. / len(phnerr['P'])] * len(phnerr['P']), edgecolor='red', linewidth=1,
             facecolor='red', range=[-0.2, 0.2], alpha=0.3, label='PhaseNet')
    plt.hist(eqterr['P'], num_bins, weights=[1. / len(eqterr['P'])] * len(eqterr['P']), edgecolor='blue', linewidth=1,
             facecolor='blue', range=[-0.2, 0.2], alpha=0.3, label='EQT')
    formatter = FuncFormatter(to_percent)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(formatter)
    plt.legend(loc="best")
    plt.grid()
    plt.xlabel('Tai - Tmanual')
    plt.ylabel('Frequency')
    plt.title(r'P Picks')
    plt.savefig('P_Pick.png')
    plt.close()
    # S pick image
    num_bins = 41
    plt.hist(phnerr['S'], num_bins, weights=[1. / len(phnerr['S'])] * len(phnerr['S']), edgecolor='red', linewidth=1,
             facecolor='red', range=[-0.2, 0.2], alpha=0.3, label='PhaseNet')
    plt.hist(eqterr['S'], num_bins, weights=[1. / len(eqterr['S'])] * len(eqterr['S']), edgecolor='blue', linewidth=1,
             facecolor='blue', range=[-0.2, 0.2], alpha=0.3, label='EQT')
    formatter = FuncFormatter(to_percent)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(formatter)
    plt.legend(loc="best")
    plt.grid()
    plt.xlabel('Tai - Tmanual')
    plt.ylabel('Frequency')
    plt.title(r'S Picks')
    plt.savefig('S_Pick.png')
    plt.close()
    # SNR pick image
    num_bins = 71
    plt.hist(ph_SNR, num_bins, weights=[1. / len(ph_SNR)] * len(ph_SNR), edgecolor='red', linewidth=1,
             facecolor='red', range=[-10, 60.], alpha=0.3, label='PhaseNet')
    plt.hist(eqt_SNR, num_bins, weights=[1. / len(eqt_SNR)] * len(eqt_SNR), edgecolor='blue', linewidth=1,
             facecolor='blue', range=[-10, 60], alpha=0.3, label='EQT')
    formatter = FuncFormatter(to_percent)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(formatter)
    plt.legend(loc="best")
    plt.grid()
    plt.xlabel('SNR')
    plt.ylabel('Frequency')
    # plt.title(r'SNR Picks')
    plt.savefig('SNR_Pick.png')
    plt.close()
    with open('error_report.txt', 'a') as the_file:
        the_file.write(r'EQT: std' + str(np.std(eqterr['P']))[0:5] + ' var: ' + str(np.var(eqterr['P']))[0:5]
                       + ' mean/abs:' + str(np.mean(np.abs(eqterr['P'])))[0:5] + ' mean:' +
                       str(np.mean(eqterr['P']))[0:5] + '\n')
        the_file.write(r'PhaseNet: std' + str(np.std(phnerr['P']))[0:5] + ' var: ' + str(np.var(phnerr['P']))[0:5]
                       + ' mean/abs:' + str(np.mean(np.abs(phnerr['P'])))[0:5] + ' mean:' +
                       str(np.mean(phnerr['P']))[0:5] + '\n')
    # breakpoint()


def xc_errhist(phnet_file, eqt_file, catalog):
    catalog = np.load(catalog, allow_pickle=True).item()
    phnet = np.load(phnet_file, allow_pickle=True).item()
    eqt = np.load(eqt_file, allow_pickle=True).item()
    phnerr = {};phnerr['P'] = [];phnerr['S'] = [];phndist = [];phnmag = [];phnfp = 0;phntp = 0
    eqterr = {};eqterr['P'] = [];eqterr['S'] = [];eqtdist = [];eqtmag = [];eqtfp = 0;eqttp = 0
    for evn in phnet:
        if (evn in eqt) and (evn in catalog['phase']):
            # print(evn)
            for st in phnet[evn]:
                if (st in eqt[evn]) and (st in catalog['phase'][evn]):
                    # print(st)
                    # print(catalog['phase'][evn][st])
                    if ('P' in phnet[evn][st]) and ('P' in eqt[evn][st]) \
                            and ('P' in catalog['phase'][evn][st]):
                        # ----phnet
                        phnet_erral = np.array(phnet[evn][st]['P']) - \
                                      catalog['phase'][evn][st]['P']
                        if abs(phnet_erral) < 0.5:
                            phnfp = phnfp
                            phntp += 1
                            phnerr['P'].append(phnet_erral)
                            phndist.append(catalog['dist'][evn][st])
                            phnmag.append(catalog['head'][evn]['ML'])
                        else:
                            phnfp = phnfp + 1
                        # ----EQT
                        EQT_erral = np.array(eqt[evn][st]['P']) - \
                                    catalog['phase'][evn][st]['P']
                        if min(abs(EQT_erral)) < 0.5:
                            eqtfp = eqtfp + len(EQT_erral) - 1
                            eqttp += 1
                            eqterr['P'].append(min(EQT_erral))
                            eqtdist.append(catalog['dist'][evn][st])
                            eqtmag.append(catalog['head'][evn]['ML'])
                        else:
                            eqtfp = eqtfp + len(EQT_erral)
                    if ('S' in phnet[evn][st]) and ('S' in eqt[evn][st]) \
                            and ('S' in catalog['phase'][evn][st]):
                        # ----phnet
                        phnet_erral = np.array(phnet[evn][st]['S']) - \
                                      catalog['phase'][evn][st]['S']
                        if abs(phnet_erral) < 0.5:
                            phnfp = phnfp
                            phntp += 1
                            phnerr['S'].append(phnet_erral)
                            phndist.append(catalog['dist'][evn][st])
                            phnmag.append(catalog['head'][evn]['ML'])
                        else:
                            phnfp = phnfp + 1
                        # ----EQT
                        EQT_erral = np.array(eqt[evn][st]['S']) - \
                                    catalog['phase'][evn][st]['S']
                        if min(abs(EQT_erral)) < 0.5:
                            eqtfp = eqtfp + len(EQT_erral) - 1
                            eqttp += 1
                            eqterr['S'].append(min(EQT_erral))
                            eqtdist.append(catalog['dist'][evn][st])
                            eqtmag.append(catalog['head'][evn]['ML'])
                        else:
                            eqtfp = eqtfp + len(EQT_erral)
    # P pick image
    num_bins = 101
    plt.hist(phnerr['P'], num_bins, weights=[1. / len(phnerr['P'])] * len(phnerr['P']), edgecolor='red', linewidth=1,
             facecolor='red', range=[-0.5, 0.5], alpha=0.3, label='PhaseNet')
    plt.hist(eqterr['P'], num_bins, weights=[1. / len(eqterr['P'])] * len(eqterr['P']), edgecolor='blue', linewidth=1,
             facecolor='blue', range=[-0.5, 0.5], alpha=0.3, label='EQT')
    formatter = FuncFormatter(to_percent)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(formatter)
    plt.legend(loc="best")
    plt.grid()
    plt.xlabel('Tai - Tmanu')
    plt.ylabel('Frequency')
    plt.title(r'P Picks')
    plt.savefig('P_Pick.png')
    plt.close()
    # S pick image
    num_bins = 101
    plt.hist(phnerr['S'], num_bins, weights=[1. / len(phnerr['S'])] * len(phnerr['S']), edgecolor='red', linewidth=1,
             facecolor='red', range=[-0.5, 0.5], alpha=0.3, label='PhaseNet')
    plt.hist(eqterr['S'], num_bins, weights=[1. / len(eqterr['S'])] * len(eqterr['S']), edgecolor='blue', linewidth=1,
             facecolor='blue', range=[-0.5, 0.5], alpha=0.3, label='EQT')
    formatter = FuncFormatter(to_percent)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(formatter)
    plt.legend(loc="best")
    plt.grid()
    plt.xlabel('Tai - Tmanu')
    plt.ylabel('Frequency')
    plt.title(r'S Picks')
    plt.savefig('S_Pick.png')
    plt.close()
    with open('error_report.txt', 'a') as the_file:
        the_file.write(r'EQT: std' + str(np.std(eqterr['P']))[0:5] + ' var: ' + str(np.var(eqterr['P']))[0:5]
                       + ' mean/abs:' + str(np.mean(np.abs(eqterr['P'])))[0:5] + ' mean:' +
                       str(np.mean(eqterr['P']))[0:5] + '\n')
        the_file.write(r'PhaseNet: std' + str(np.std(phnerr['P']))[0:5] + ' var: ' + str(np.var(phnerr['P']))[0:5]
                       + ' mean/abs:' + str(np.mean(np.abs(phnerr['P'])))[0:5] + ' mean:' +
                       str(np.mean(phnerr['P']))[0:5] + '\n')


def xfj_eqt_hist(eqt_file, catalog, snr_file=None):
    catalog = np.load(catalog, allow_pickle=True).item()
    eqt = np.load(eqt_file, allow_pickle=True).item()
    if snr_file:
        snr = np.load(snr_file, allow_pickle=True)['snr'].item()
        SNR = []
    eqterr = {}
    eqterr['P'] = []
    eqterr['S'] = []
    eqtdist = []
    eqtmag = []
    eqtfp = 0
    eqttp = 0
    for evn in eqt:
        if evn in catalog['phase']:
            for st in eqt[evn]:
                if st in catalog['phase'][evn]:
                    if ('P' in eqt[evn][st]) and ('P' in catalog['phase'][evn][st]):
                        EQT_erral = np.array(eqt[evn][st]['P']) - \
                                    catalog['phase'][evn][st]['P'] + 8 * 3600
                        if abs(min(EQT_erral)) < 1:
                            eqtfp = eqtfp + len(EQT_erral) - 1
                            eqttp += 1
                            eqterr['P'].append(min(EQT_erral))
                            eqtdist.append(catalog['dist'][evn][st])
                            eqtmag.append(catalog['head'][evn]['ML'])
                            if snr_file and (st in snr[evn]):
                                SNR.append(snr[evn][st])
                        else:
                            eqtfp = eqtfp + len(EQT_erral)
                    if ('S' in eqt[evn][st]) and ('S' in catalog['phase'][evn][st]):
                        # ----EQT
                        EQT_erral = np.array(eqt[evn][st]['S']) - \
                                    catalog['phase'][evn][st]['S'] + 8 * 3600
                        if abs(min(EQT_erral)) < 1:
                            eqtfp = eqtfp + len(EQT_erral) - 1
                            eqttp += 1
                            eqterr['S'].append(min(EQT_erral))
                            eqtdist.append(catalog['dist'][evn][st])
                            eqtmag.append(catalog['head'][evn]['ML'])
                        else:
                            eqtfp = eqtfp + len(EQT_erral)
    # P pick image
    num_bins = 101
    plt.hist(eqterr['P'], num_bins, weights=[1. / len(eqterr['P'])] * len(eqterr['P']), edgecolor='blue',
             linewidth=1,
             facecolor='blue', range=[-0.5, 0.5], alpha=0.3, label='EQT')
    formatter = FuncFormatter(to_percent)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(formatter)
    plt.legend(loc="best")
    plt.grid()
    plt.xlabel('Tai - Tmanu')
    plt.ylabel('Frequency')
    plt.title(r'P Picks')
    plt.savefig('P_Pick.png')
    plt.close()
    # S pick image
    num_bins = 101
    plt.hist(eqterr['S'], num_bins, weights=[1. / len(eqterr['S'])] * len(eqterr['S']), edgecolor='blue',
             linewidth=1,
             facecolor='blue', range=[-0.5, 0.5], alpha=0.3, label='EQT')
    formatter = FuncFormatter(to_percent)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(formatter)
    plt.legend(loc="best")
    plt.grid()
    plt.xlabel('Tai - Tmanu')
    plt.ylabel('Frequency')
    plt.title(r'S Picks')
    plt.savefig('S_Pick.png')
    plt.close()
    # SNR pick image
    num_bins = 101
    plt.hist(SNR, num_bins, weights=[1. / len(SNR)] * len(SNR), edgecolor='blue',
             linewidth=1,
             facecolor='blue', range=[-10, 60], alpha=0.3, label='EQT')
    formatter = FuncFormatter(to_percent)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(formatter)
    plt.legend(loc="best")
    plt.grid()
    plt.xlabel('SNR')
    plt.ylabel('Frequency')
    # plt.title(r'SNR Picks')
    plt.savefig('SNR_Pick.png')
    plt.close()


def xfj_phnet_hist(phnet_file, catalog):
    catalog = np.load(catalog, allow_pickle=True).item()
    phnet = np.load(phnet_file, allow_pickle=True).item()
    phneterr = {}
    phneterr['P'] = []
    phneterr['S'] = []
    phnetdist = []
    phnetmag = []
    phnetfp = 0
    phnettp = 0
    for evn in phnet:
        if evn in catalog['phase']:
            for st in phnet[evn]:
                if st in catalog['phase'][evn]:
                    if ('P' in phnet[evn][st]) and ('P' in catalog['phase'][evn][st]):
                        PHN_erral = np.array(phnet[evn][st]['P']) - \
                                    catalog['phase'][evn][st]['P'] + 8 * 3600
                        if abs(min(PHN_erral)) < 1:
                            phnetfp = phnetfp + len(PHN_erral) - 1
                            phnettp += 1
                            phneterr['P'].append(min(PHN_erral))
                            phnetdist.append(catalog['dist'][evn][st])
                            phnetmag.append(catalog['head'][evn]['ML'])
                        else:
                            phnetfp = phnetfp + len(PHN_erral)
                    if ('S' in phnet[evn][st]) and ('S' in catalog['phase'][evn][st]):
                        # ----EQT
                        PHN_erral = np.array(phnet[evn][st]['S']) - \
                                    catalog['phase'][evn][st]['S'] + 8 * 3600
                        if abs(min(PHN_erral)) < 1:
                            phnetfp = phnetfp + len(PHN_erral) - 1
                            phnettp += 1
                            phneterr['S'].append(min(PHN_erral))
                            phnetdist.append(catalog['dist'][evn][st])
                            phnetmag.append(catalog['head'][evn]['ML'])
                        else:
                            phnetfp = phnetfp + len(PHN_erral)
    # P pick image
    num_bins = 101
    plt.hist(phneterr['P'], num_bins, weights=[1. / len(phneterr['P'])] * len(phneterr['P']), edgecolor='blue',
             linewidth=1,
             facecolor='blue', range=[-0.5, 0.5], alpha=0.3, label='EQT')
    formatter = FuncFormatter(to_percent)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(formatter)
    plt.legend(loc="best")
    plt.grid()
    plt.xlabel('Tai - Tmanu')
    plt.ylabel('Frequency')
    plt.title(r'P Picks')
    plt.savefig('P_Pick.png')
    plt.close()
    # P pick image
    num_bins = 101
    plt.hist(phneterr['S'], num_bins, weights=[1. / len(phneterr['S'])] * len(phneterr['S']), edgecolor='blue',
             linewidth=1,
             facecolor='blue', range=[-0.5, 0.5], alpha=0.3, label='EQT')
    formatter = FuncFormatter(to_percent)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(formatter)
    plt.legend(loc="best")
    plt.grid()
    plt.xlabel('Tai - Tmanu')
    plt.ylabel('Frequency')
    plt.title(r'S Picks')
    plt.savefig('S_Pick.png')
    plt.close()


if __name__ == '__main__':
    start = time.process_time()
    xfj_errhist(phnet_file='../../../SeismicData/XFJ1121/phasenet_output/phnet.npy',
                eqt_file='../../../SeismicData/XFJ1121/eqtoutputv2/EQT.npy',
                catalog='../../../SeismicData/XFJ1121/catalog.npy',
                snr_file='../../../SeismicData/XFJ1121/snr.npz')
    # xc_errhist(phnet_file='../../../SeismicData/phasenet_manul/xc/phnet.npy',
    #            eqt_file='../../../SeismicData/phasenet_manul/xc/EQT.npy',
    #            catalog='../../../SeismicData/phasenet_manul/xc/catalog.npy')
    # xfj_eqt_hist(eqt_file='../../../SeismicData/XFJ1121/eqtoutput0.02/EQT.npy',
    #              catalog='../../../SeismicData/XFJ1121/catalog.npy',
    #              snr_file='../../../SeismicData/XFJ1121/snr.npz')
    # xfj_phnet_hist(phnet_file='/home/jc/work/XFJ1121/phasenet_output/phnet.npy',
    #                catalog='/home/jc/work/XFJ1121/catalog.npy')
    end = time.process_time()
    print(end - start)
