def write_list_to(filename, ls):
    print('writing list to {}...'.format(filename))
    file = open(filename, 'w', encoding='utf-8')
    for item in ls:
        file.write(item + '\n')
    file.close()


def read_list_from(filename):
    print('reading list from {}...'.format(filename))
    file = open(filename, 'r', encoding='utf-8')
    file_str = file.read()
    file_str = file_str.rstrip()
    return file_str.split('\n')

if __name__ == '__main__':
    s = 'Bảo Trân kla'
    # s = s[:2]
    file = open('temp.txt', 'w', encoding='utf-8')
    file.write(s + '\n')
    file.close()
    file = open('temp.txt', 'r', encoding='utf-8')
    file_str = file.read()
    file_str = file_str.rstrip()
    print(file_str)
