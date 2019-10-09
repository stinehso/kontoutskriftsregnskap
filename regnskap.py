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
    df = pd.read_csv(accounts_file, sep=';', thousands=' ', decimal=',',
         index_col=False)
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

    names = []
    patterns = []
    with open(filename) as infile:
        for line in infile.readlines():
            names.append(line.split(';')[0])
            list = line.split(';')[1:]
            tmp = list[0].strip()
            for item in list[1:]:
                tmp = '|'.join((tmp, item.strip()))
            patterns.append(tmp)

    return names, patterns




def categories_from_file(df_old, category_file):
    '''Add categories from file to transactions based on description'''
    names, patterns = read_category_file(category_file)

    df = df_old.assign(Konto='')
    length = df.get('Beskrivelse').size             # Sparebank1 specific

    for i in range(length):
        beskrivelse = df.get('Beskrivelse')[i]
        if not isinstance(beskrivelse, str):
            continue
        for p in range(len(patterns)):
            if re.search(patterns[p].lower(), beskrivelse.lower()):
                #df.loc[i, ('Konto')] = p+1         # assign number instead of name
                df.loc[i, ('Konto')] = names[p]

    #df = df.set_index('Dato')
    return df, names




def filter_data(df, categories, from_date='2018-10-01', to_date='2019-12-31',
                min=0, max=100000):
    '''Print the account info based on input options. Default is to print all'''
    ## filter categories - only one or all for now
    if categories != 'all':
        # just one for now
        df1 = df.loc[df.loc[:, 'Konto'] == categories[0]]


        # mask = []
        # i=0
        # for cat in categories:
        #     mask.append(df.loc[:, 'Konto'] == cat)
        #     print(mask[i])
        #     i+=1
        # newdf = pd.concat([mask[0], mask[1]], axis=1)
        # #newdf = pd.merge(pd.DataFrame(mask[0]), pd.DataFrame(mask[1]), )
        # print(newdf)
        # return
        # df1 = df.loc[mask]
    else:
        df1 = df

    ## filter dates
    # create series of all dates
    dates = pd.to_datetime(df.loc[:, 'Dato'], dayfirst=True)#, format='%d.%m.%y')
    # series filter by date
    date_mask = (dates >= from_date) & (dates <= to_date)
    df2 = df1.loc[date_mask]

    ## filter amount
    # 'Ut' has negative values, makes filter counterintuitive
    amount_mask = ((df2.loc[:, 'Ut']< -min) & (df2.loc[:, 'Ut']> -max)) |\
        ((df2.loc[:, 'Inn']>min) & (df2.loc[:, 'Inn']<max))
    df3 = df2.loc[amount_mask]

    return df3




def print_data(df):
    '''print all data in a dataframe'''
    #df1 = df.loc[df.loc[:, 'Konto']==category]
    print(df)
    print()
    in_ = np.nansum(df['Inn'])
    out = -np.nansum(df['Ut'])
    print('Total in:', in_)
    print('Total out:', out)
    print('Result:', in_ - out)



#
# def print_belop(df):
#     '''Print entries above or below selected amount'''
#
#     print('''- MENY:
#     1 Betalt over beløp
#     2 Betalt under beløp
#     3 Fått inn over beløp
#     4 Fått inn under beløp''')
#
#     valg = input()
#     belop = int(input('Beløp:'))
#
#     if valg == '1':
#         df2 = df.loc[df.loc[:, 'Ut']<-belop]
#         print(df2)
#     if valg == '2':
#         df2 = df.loc[df.loc[:, 'Ut']>-belop]
#         print(df2)
#     if valg == '3':
#         df2 = df.loc[df.loc[:, 'Inn']>belop]
#         print(df2)
#     if valg == '4':
#         df2 = df.loc[df.loc[:, 'Inn']<belop]
#         print(df2)
#
#     menu(df)




def print_sum(df, period='month'):
    '''Print sum of each category for each month'''
    year = 2019

    mask = []
    mnd = ['jan', 'feb', 'mar', 'apr', 'mai', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'des']

    # append tuples with first and last day of month to list mask
    for i in range(12):
        if i in [0, 2, 4, 6, 7, 9, 11]:
            d = 31
        if i in [3, 5, 8, 10]:
            d = 30
        else:
            d = 28
        if i < 9:
            mask.append((f'{year}-0{i+1}-01', f'{year}-0{i+1}-{d}'))
        else:
            mask.append((f'{year}-{i+1}-01', f'{year}-{i+1}-{d}'))

    in_ = []
    out = []
    for i in range(12):
        df1 = filter_data(df, 'all', from_date=mask[i][0], to_date=mask[i][1])
        out.append(np.nansum(df1['Ut']))
        in_.append(np.nansum(df1['Inn']))

        print('---', mnd[i], '---')
        print(np.nansum(df1['Ut']))
        print(np.nansum(df1['Inn']))

    out = [sum_*-1 for sum_ in out]
    out = out[6:]
    in_ = in_[6:]

    plt.plot(out)
    plt.plot(in_)
    plt.grid()
    plt.legend(['out', 'in'])
    plt.show()

    cum_out = np.cumsum(out)
    cum_in = np.cumsum(in_)
    plt.plot(cum_out)
    plt.plot(cum_in)
    plt.grid()
    plt.legend(['out', 'in'])
    plt.show()

    print('Overskudd i perioden: {:.2f} kr'.format(cum_in[-1]-cum_out[-1]))




def plot_menu(df):
    menu = {}
    menu['1'] = 'Plot all'
    menu['2'] = 'Choose categories'
    menu['3'] = 'Choose dates'
    menu['4'] = 'Choose amount limits'
    menu['q'] = 'Quit'

    while True:
        print('---- PLOT MENU ----')
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




def choose_categories(categories):
    '''allows user to select a subset of the categories'''
    menu = {}
    chosen = []
    for i in range(len(categories)):
        menu[f'{i}'] = categories[i]
    menu['s'] = 'Show selected'
    menu['q'] = 'Finish'

    while True:
        print('---- CATEGORIES ----')
        [print(key, value) for (key, value) in sorted(menu.items())]

        selection = input("Please Select: ")
        if selection == 's':
            print(chosen)
        elif selection == 'q':
            break
        elif selection in menu.keys():
            chosen.append(categories[int(selection)])
        else:
          print ("Unknown Option Selected!")

    return chosen




def options_menu(df, output_func, categories):
    menu = {}
    menu['1'] = 'Output data'
    menu['2'] = 'Choose categories'
    menu['3'] = 'Choose dates'
    menu['4'] = 'Choose amount limits'
    menu['5'] = 'Show selection'
    menu['q'] = 'Quit'

    while True:
        print('---- OPTIONS ----')
        [print(key, value) for (key, value) in sorted(menu.items())]

        selection=input("Please Select: ")
        if selection =='1':
            output_func(df)
            break
        elif selection == '2':
            categories_chosen = choose_categories(categories)
            df = filter_data(df, categories_chosen)
        elif selection == '3':
            df = filter_data(df, categories, from_date='2018-10-01', to_date='2019-12-31',
                min=0, max=100000)
            #print_dato(df)
            continue
        elif selection == '4':
            filter_data(df, categories, from_date='2018-10-01', to_date='2019-12-31',
                min=0, max=100000)
            print_belop(df)
        elif selection == 'q':
          break
        else:
          print ("Unknown Option Selected!")




def menu(df, categories):
    menu = {}
    menu['1'] = 'Print'
    menu['2'] = 'Sum'
    menu['3'] = 'Plot'
    menu['4'] = 'Edit categories'
    menu['q'] = 'Quit'

    while True:
        print('---- MAIN MENU ----')
        [print(key, value) for (key, value) in sorted(menu.items())]

        selection=input("Please Select: ")
        if selection =='1':
            options_menu(df, print_data, categories)
        elif selection == '2':
            options_menu(df, print_sum, categories)
        elif selection == '3':
            edit_menu(df)
        elif selection == '4':
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
    #print(acc)
    df, categories = categories_from_file(acc, category_file)
    #df = filter_data(df, 'Helse', min=0, max=30000)
    #print(df)
    #print_sum(df)
    #print_data(df)
    menu(df, categories)






if __name__ == '__main__':
    main()
