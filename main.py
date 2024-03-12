import os
import json
import datetime
from tabulate import tabulate
from tqdm import tqdm


def print_summary(summary):
    total_files = sum(summary['FileType'].values())
    data = [('Folder', summary['Folder'])] + list(summary['FileType'].items()) + [('Total Files', total_files)]
    print(tabulate(data, headers=['Type', 'Count'], tablefmt='fancy_grid'))


def get_folder_summary(path):
    summary = {'FileType': {}, 'Folder': 0, 'Files': {}}

    # Get the total number of files for the progress bar
    total_files = sum([len(files) for _, _, files in os.walk(path)])

    progress_bar = tqdm(total=total_files, ncols=100, bar_format='Scanning: {l_bar}{bar}| {percentage:3.0f}% ({n_fmt}/{total_fmt})')

    for root, dirs, files in os.walk(path):
        summary['Folder'] += len(dirs)
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext not in summary['FileType']:
                summary['FileType'][ext] = 0
                summary['Files'][ext] = []
            summary['FileType'][ext] += 1
            summary['Files'][ext].append(os.path.join(root, file))
            progress_bar.update(1)  # update progress bar for each file

    progress_bar.close()

    return summary


def find_files(summary, file_type):
    file_type = file_type.lower()
    if not file_type.startswith('.'):
        file_type = '.' + file_type
    if file_type in summary['Files']:
        for file in summary['Files'][file_type]:
            print(file)
    else:
        print('No files of this type found.')


def save_as_json(summary, path):
    timestamp = datetime.datetime.now().strftime('%H-%M-%S-%d-%m-%Y')
    filename = f'saves/{timestamp}.json'
    data = {'path': path, 'summary': summary}
    with open(filename, 'w') as f:
        json.dump(data, f)


def read_json(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    print_summary(data['summary'])


def update_json(filename, path):
    with open(filename, 'r') as f:
        data = json.load(f)
    data['path'] = path
    data['summary'] = get_folder_summary(path)
    with open(filename, 'w') as f:
        json.dump(data, f)


def remove_empty_dirs(path):
    for root, dirs, _ in os.walk(path, topdown=False):
        for name in dirs:
            try:
                os.rmdir(os.path.join(root, name))
                print(f'Removed empty directory: {os.path.join(root, name)}')
            except OSError as ex:
                print(f'Error removing directory: {os.path.join(root, name)}, {ex.strerror}')


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_menu():
    clear_screen()
    print('[MENU]')
    print('0) Exit')
    print('1) Set Path')
    print('2) Summary')
    print('3) Find')
    print('4) Save as JSON (only if summary was made)')
    print('5) Read JSON')
    print('6) Update JSON')
    print('7) Remove Empty Folders')


def print_ascii_art():
    print('''
.____    .__  __    __  .__           ________                 
|    |   |__|/  |__/  |_|  |   ____   \______ \   ____   ____  
|    |   |  \   __\   __\  | _/ __ \   |    |  \ /  _ \ / ___\ 
|    |___|  ||  |  |  | |  |_\  ___/   |    `   (  <_> ) /_/  >
|_______ \__||__|  |__| |____/\___  > /_______  /\____/\___  / 
        \/                        \/          \/      /_____/  
        ''')
    print('                            by tsuki_kami')


def main():
    print_ascii_art()
    path = input('Enter the path: ')
    summary = None
    while True:
        print_menu()
        option = input('Enter your option: ')
        if option == '0':
            break
        elif option == '1':
            path = input('Enter the new path: ')
        elif option == '2':
            summary = get_folder_summary(path)
            print_summary(summary)
        elif option == '3':
            if summary is None:
                print('Please generate a summary first.')
            else:
                file_type = input('Enter the file type: ')
                find_files(summary, file_type)
        elif option == '4':
            if summary is None:
                print('Please generate a summary first.')
            else:
                save_as_json(summary, path)
        elif option == '5':
            filename = input('Enter the JSON file name: ')
            read_json(filename)
        elif option == '6':
            filename = input('Enter the JSON file name: ')
            update_json(filename, path)
        elif option == '7':
            confirm = input('Are you sure you want to remove all empty folders? Type "confirm" to proceed: ')
            if confirm.lower() == 'confirm':
                remove_empty_dirs(path)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nExiting...')
    except Exception as ex:
        print(f'An error occurred: {ex}')
    finally:
        input('Press any key to exit...')
