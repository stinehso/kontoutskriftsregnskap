import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
#import matplotlib.axes.Axes as ax
#import seaborn
import sys
import locale as loc



'''
Hensikten med dette skriptet er å kunne skrive ut pene filer og lage plott og
et oversiktlig regnskap basert på gitte kontoutskrifter.
'''

def read_accounts_file(accounts_file):
    '''Read the yearly accounts from a csv file'''
    print('reading file..')
    df = pd.read_csv(accounts_file, sep=';', decimal=',', index_col=False)
    return df



def read_category_file(filename):
    '''
    reads a text file for categories. Must be formatted with lines of
    category_name and list of descriptors, all separated by ';'
    '''
    if not isinstance(filename, str):
        filename = input('Please input a category file or type "make" to create one\n')
    if filename == 'make':
        name = input('Give the file a name: ')
        filename = f'{name}.csv'
        open(filename, 'w+')

    print('reading file..')

    names = []
    patterns = []

    with open(filename) as infile:
        for line in infile.readlines():
            names.append(line.split(';')[0])
            list = line.split(';')[1:]
            tmp = ''
            for item in list:
                tmp = '|'.join((tmp, item.strip()))
            patterns.append(tmp)

    return names, patterns



def categories_from_file(df_old, category_file):
    '''Add categories from file to transactions based on description'''
    names, patterns = read_category_file(category_file)

    print('adding categories..')

    df = df_old.assign(Konto='')
    length = df.get('Beskrivelse').size             # Sparebank1 specific

    for i in range(length):
        beskrivelse = df.get('Beskrivelse')[i]
        if not isinstance(beskrivelse, str):
            continue
        for p in range(len(patterns)):
            if re.search(patterns[p], beskrivelse):
                #df.loc[i, ('Konto')] = p+1         # assign number instead of name
                df.loc[i, ('Konto')] = names[p]

    #df = df.set_index('Dato')

    return df



def print_category(df):
    '''Print entries in selected category'''

    print('''Konti:
    0 Ingen konto
    1 Dagligvarer
    2 Mat/drikke ute
    3 Husleie, klesvask
    4 Forsikringer
    5 Abonnementer
    6 Reise
    7 Kultur
    8 Klær/ ting
    9 Sparing
    10 Annet''')

    category = int(input())

    df1 = df.loc[df.loc[:, 'Konto']==category]
    print(df1)
    print(-sum(df1['Ut']))
    print(sum(df1['Inn']))

    menu(df)
    return



def print_belop(df):
    '''Print entries above or below selected amount'''

    print('''- MENY:
    1 Betalt over beløp
    2 Betalt under beløp
    3 Fått inn over beløp
    4 Fått inn under beløp''')

    valg = input()
    belop = int(input('Beløp:'))

    if valg == '1':
        df2 = df.loc[df.loc[:, 'Ut']<-belop]
        print(df2)
    if valg == '2':
        df2 = df.loc[df.loc[:, 'Ut']>-belop]
        print(df2)
    if valg == '3':
        df2 = df.loc[df.loc[:, 'Inn']>belop]
        print(df2)
    if valg == '4':
        df2 = df.loc[df.loc[:, 'Inn']<belop]
        print(df2)

    menu(df)



def print_sum(df):
    '''Print sum of each category for each month'''

    dato = pd.to_datetime(df.loc[:, 'Dato'], dayfirst=True)#, format='%d.%m.%y')
    sparemaske = (df['Konto'] != 8)
    bruk = df.loc[sparemaske]
    bruk = df
    mask = []
    d = 31
    mnd = ['jan', 'feb', 'mar', 'apr', 'mai', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'des']

    for i in range(12):
        if i in [0, 2, 4, 6, 7, 9, 11]:
            d = 31
        elif i in [3, 5, 8, 10]:
            d = 30
        else:
            d = 28
        if i < 9:
            mask.append((f'2018-0{i+1}-01', f'2018-0{i+1}-{d}'))
        else:
            mask.append((f'2018-{i+1}-01', f'2018-{i+1}-{d}'))

    inn = []
    ut = []
    for i in range(12):
        themask = (dato > mask[i][0]) & (dato < mask[i][1])
        df1 = bruk.loc[themask]
        ut.append(np.nansum(df1['Ut']))
        inn.append(np.nansum(df1['Inn']))
        print('---', mnd[i], '---')
        print(np.nansum(df1['Ut']))
        print(np.nansum(df1['Inn']))
        #print('***')

    ut = [s*-1 for s in ut]
    ut = ut[6:]
    inn = inn[6:]

    plt.plot(ut)
    plt.plot(inn)
    plt.grid()
    plt.legend(['ut', 'inn'])
    plt.show()

    cum_ut = np.cumsum(ut)
    cum_inn = np.cumsum(inn)
    plt.plot(cum_ut)
    plt.plot(cum_inn)
    plt.grid()
    plt.legend(['ut', 'inn'])
    plt.show()

    print('Overskudd i perioden: {:.2f} kr'.format(cum_inn[-1]-cum_ut[-1]))



def plot_menu(df):
    menu = {}
    menu['1'] = 'Plot hele utskriften'
    menu['2'] = 'Velg kategori'
    menu['3'] = 'Velg dato'
    menu['4'] = 'Velg avgrenset beløp'
    menu['q'] = 'Quit'

    while True:
        print('---- PRINT MENU ----')
        [print(key, value) for (key, value) in sorted(menu.items())]

        selection=input("Please Select: ")
        if selection =='1':
            print(df)
        elif selection == '2':
            print_category(df)
        elif selection == '3':
            #print_dato(df)
            continue
        elif selection == '4':
            print_belop(df)
        elif selection == 'q':
          break
        else:
          print ("Unknown Option Selected!")


def print_menu(df):
    menu = {}
    menu['1'] = 'Print hele utskriften'
    menu['2'] = 'Velg kategori'
    menu['3'] = 'Velg dato'
    menu['4'] = 'Velg avgrenset beløp'
    menu['q'] = 'Quit'

    while True:
        print('---- PRINT MENU ----')
        [print(key, value) for (key, value) in sorted(menu.items())]

        selection=input("Please Select: ")
        if selection =='1':
            print(df)
        elif selection == '2':
            print_category(df)
        elif selection == '3':
            #print_dato(df)
            continue
        elif selection == '4':
            print_belop(df)
        elif selection == 'q':
          break
        else:
          print ("Unknown Option Selected!")


def menu(df):
    menu = {}
    menu['1'] = 'Print'
    menu['2'] = 'Plot'
    menu['3'] = 'Edit categories'
    menu['q'] = 'Quit'

    while True:
        print('---- MAIN MENU ----')
        [print(key, value) for (key, value) in sorted(menu.items())]

        selection=input("Please Select: ")
        if selection =='1':
            print_menu(df)
        elif selection == '2':
            plot_menu(df)
        elif selection == '3':
            edit_menu(df)
        elif selection == 'q':
          break
        else:
          print ("Unknown Option Selected!")


def input_args():
    try:
        accounts_file = sys.argv[1]
    except:
        print('Wrong arguments passed')
        print('Usage: python regnskap.py [accounts_file] [category_file](optional)')
        sys.exit()
    try:
        category_file = sys.argv[2]
    except:
        category_file = None

    return accounts_file, category_file



def main():
    accounts_file, category_file = input_args()
    acc = read_accounts_file(accounts_file)
    #df = add_categories(acc)
    df = categories_from_file(acc, category_file)
    #df = df.reset_index()
    # print(df.head())
    # print()
    menu(df)






if __name__ == '__main__':
    main()
