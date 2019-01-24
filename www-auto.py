# encoding: utf-8
from glob import glob
from os import chdir, path, system
from datetime import date
import unicodedata
import sys
import re

chdir(sys.path[0])
fsys = sys.getfilesystemencoding()

IM         = 'ImageMagick/convert.exe '
ITEMS_DIR  = 'items/'
WWW_DIR    = 'www-auto/'
PRICE_TXT  = 'price'
TITLE_TXT  = 'title'
MISC_TXT   = 'misc'
WM_label   = 'ItemsListGenerator'

index      = open('index.htm').read()
category   = open('category.htm').read()
cat_list   = open('cat_list.htm').read()
sub_cat    = open('sub_cat.htm').read()
row        = open('row.htm').read()
row_tr     = open('row_tr.htm').read()
info_row   = open('info_row.htm').read()
descr      = open('descr.htm').read()

def remove_accents(txt):
    return unicodedata.normalize('NFKD', txt).encode('ascii', 'ignore')

def remove_special(txt, repl = '_'):
    return re.sub('[^\w]+', repl, txt)

def safe_chars(txt):
    return remove_special(remove_accents(txt)).lower()

def basename(dir):
    return path.basename(path.normpath(dir))

def replace_ext_safe(file, new_ext):
    file = path.basename(file)
    file = path.splitext(file)[0].decode(fsys)
    return safe_chars(file) + new_ext

def replace_ext(file, new_ext):
    return path.splitext(file)[0] + new_ext

def mreplace(txt, changes_list):
    for change in changes_list:
        txt = txt.replace(*change)
    return txt

def mglob(dir, *subs):
    paths = []
    for sub in subs:
        paths += glob(dir + '/' + sub)
    return paths

re_info_row = re.compile('(.*?):\s*(.*)')
re_sub_cats = re.compile('^!(.*)')

WM = ' -alpha set '+\
'( -pointsize 35 -fill grey87 label:"'+ WM_label +'" -rotate -20 -write mpr:tile +delete ) '+\
'( +clone -compose multiply -tile mpr:tile -draw "color 0,0 reset" ) -composite '

IM_small = '-resize x150 -normalize -sharpen 0x2 -define jpeg:extent=4KB "%s" "%s" '
IM_large = '-resize x800 -normalize -unsharp 2x2 -define jpeg:extent=100KB "%s"' + WM + '"%s" '
def IM_save(item_file, args = IM_small, img_pref = ''):
    img_file = replace_ext_safe(item_file, '.jpg')
    img_file_org = replace_ext(item_file, '.jpg')
    system( IM + args %(img_file_org, WWW_DIR + 'i/' + img_pref + img_file) )
    return 'i/' + img_pref + img_file

def sub_cats_to_id(sub_cats_list, ALL_sub_categories_list):
    sub_categories_txt = ''
    for sub_cat in sub_cats_list:
        sub_categories_txt += ' c' + str(ALL_sub_categories_list.index(sub_cat))
    return sub_categories_txt

categories_txt = [basename(dir) for dir in glob(ITEMS_DIR + '*/')]


DB = {}

for category_txt in categories_txt:
    C = DB[category_txt.decode(fsys).encode('utf-8')] = {
        'id':str(len(DB)),
        'ALL_sub_categories_list':set(),
        'groups':{} }

    for item_file in mglob(ITEMS_DIR + category_txt, '*.txt', '*/*.txt'):
        upDir = path.basename(path.dirname(item_file))
        fileGroup = fileName = path.basename(item_file)
        isMulti = upDir!=category_txt
        if isMulti:
            fileGroup = upDir
        fileGroup = fileGroup.decode(fsys).replace('.txt','')

        item_txt = open(item_file).read().decode(fsys).encode('utf-8')
        item_txt, _, n_descr = item_txt.partition('\n##\n')

        G = C['groups'].setdefault(fileGroup, {
            'id':safe_chars(fileGroup),
            'ALL_sub_list':set(),
            'items':{} })

        F = G['items'][fileName] = {
            'info':re.findall(re_info_row, item_txt),
            'descr':n_descr.replace('\n', '<br/>'),
            'img':IM_save(item_file),
            'imgl':IM_save(item_file, IM_large, 'l_') }

        if isMulti:
            G['title'], G['price'] = fileGroup.encode('utf-8').split('#')
        else:
            F_info_dict = dict(F['info'])
            G['title'] = F_info_dict.get(TITLE_TXT, fileGroup.encode('utf-8'))
            G['price'] = F_info_dict.get(PRICE_TXT, '')

        sub_cats_find = re.findall(re_sub_cats, item_txt)
        sub_cats_find = (sub_cats_find or [MISC_TXT])[0].split()
        G['ALL_sub_list'].update(sub_cats_find)
        C['ALL_sub_categories_list'].update(sub_cats_find)

    C['ALL_sub_categories_list'] = list(C['ALL_sub_categories_list'])


def find_int(str_int):
   return int((re.findall('\d+', str_int)+[0])[0])

def sorted_by(values, sort_key='title'):
   key = lambda x:x[sort_key]
   if sort_key == 'price':
       key = lambda x:find_int(x[sort_key])
   return sorted([dict(v, sort_order=sort_key[0]) for v in values], key=key)

ALL_categories_htm = ''
ALL_cat_list_htm = ''
for category_txt in DB:
    C = DB[category_txt]
    ALL_cat_list_htm += mreplace(cat_list, [
        ['%ITEM_CAT%', category_txt],
        ['%CAT_ID%', C['id']] ])

    ALL_sub_cats_htm = ''
    for sub_cat_id, sub_cat_txt in enumerate(C['ALL_sub_categories_list']):
        ALL_sub_cats_htm += mreplace(sub_cat, [
            ['%SUB_CAT_ID%', str(sub_cat_id)],
            ['%SUB_CAT%', sub_cat_txt.replace('_', ' ')],
            ['%CAT_ID%', C['id']] ])

    ALL_rows_htm = ''
    for G in sorted_by(C['groups'].values(), 'title') +\
             sorted_by(C['groups'].values(), 'price'):
        ALL_n_row = ''
        for F in G['items'].values():
            ALL_n_info_row = ''
            for info_arg, info_txt in F['info']:
                ALL_n_info_row += mreplace(info_row, [
                    ['%INFO_ARG%', info_arg],
                    ['%INFO_TXT%', info_txt] ])
            if F['descr']:
                ALL_n_info_row += descr.replace('%DESCR%', F['descr'])
            ALL_n_row += mreplace(row_tr, [
                ['%INFO_TABLE%', ALL_n_info_row],
                ['%IMG%', F['img']],
                ['%IMGL%', F['imgl']] ])

        ALL_rows_htm += mreplace(row, [
            ['%TITLE%', G['title']],
            ['%PRICE%', G['price']],
            ['%ITEM_SUB_CATS%',
                sub_cats_to_id(G['ALL_sub_list'], C['ALL_sub_categories_list']) +\
                ' s'+G['sort_order']],
            ['%ITEM_ID%', G['id']],
            ['%ROW_TR%', ALL_n_row] ])

    ALL_categories_htm += mreplace(category, [
        ['%ITEM_CAT%', category_txt],
        ['%CAT_ID%', C['id']],
        ['%SUB_CATS_LIST%', ALL_sub_cats_htm],
        ['%ITEM_ROW%', ALL_rows_htm] ])



index = mreplace(index, [
    ['%DATE%', date.today().strftime('%d.%m.%Y')],
    ['%CATEGORY%', ALL_categories_htm],
    ['%CAT_LIST%', ALL_cat_list_htm] ])

with open(WWW_DIR + 'index.htm', 'w') as file:
    file.write(index)