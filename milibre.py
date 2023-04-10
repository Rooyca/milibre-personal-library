import argparse, requests, json, os, datetime, re

from termcolor import colored
from pymongo import MongoClient
from bson import ObjectId

from dotenv import load_dotenv
load_dotenv()

# Loading environment variables
user = os.getenv('MONGO_USER')
password = os.getenv('MONGO_PASSWORD')
cluster = os.getenv('MONGO_CLUSTER')
db_ = os.getenv('MONGO_DB')
collection_ = os.getenv('MONGO_COLLECTION')

# Parsing arguments
parser = argparse.ArgumentParser(description='MiLibre - A simple command line tool to manage your book library.')
parser.add_argument('-m', '--mode', required=True, choices=['add', 'auth', 'show', 'list', 'search', 'delete', 'update'], help='Modes are: add, auth, update, delete, list, search, show')
parser.add_argument('-t', '--title', help='Book title')
parser.add_argument('-a', '--author', help='Book author')
parser.add_argument('-n', '--number', default='1', type=int, help='Number of results to display (default: 1)')
parser.add_argument('-s', '--status', default='unread', help='Status of the book (default: unread)')
parser.add_argument('-i', '--id', help='Book ID')
parser.add_argument('-f', '--file', help='Book path. Example: /home/user/Desktop/book.epub')
parser.add_argument('-l', '--list', help='File with list of books. File format: title, author, status')
parser.add_argument('-md','--max_docs', default=10, help='Number of documents to display.')
parser.add_argument('-sb','--sort_by', default='_id A', help='Sort documents by this field in this order [A: Ascending, D: Descending]. (default: _id A)')
parser.add_argument('-sq','--search_query', help='Search query, example: "title:Karamasov"')
args = parser.parse_args()

# Connecting to MongoDB and getting the collection
client = MongoClient(f'mongodb+srv://{user}:{password}@{cluster}/?retryWrites=true&w=majority')

try:
    db = client[db_]
except:
    db = client['library']

try:
    collection = db[collection_]
except:
    collection = db['books']


# Defining functions

def book_not_found():
    print('------------------------------------')
    print(colored('Book not found.', 'red'))
    print('------------------------------------')
    exit(1)

def id_not_found():
    print('------------------------------------')
    print(colored('ERROR: ', 'red'), 'Please specify a book ID.')
    print('------------------------------------')

def print_usage_and_exit():
    print()
    parser.print_usage()
    exit(1)

def print_book(number, volume_info):
    print('------------------------------------')
    print(colored('ID:', 'cyan', attrs=['bold']), number)
    print(colored('Title:', 'cyan', attrs=['bold']), volume_info.get('title'))
    try:
        print(colored('Author:', 'cyan', attrs=['bold']), volume_info['author'])
    except:
        print(colored('Author:', 'cyan', attrs=['bold']), volume_info.get('authors', []))
    print(colored('Publisher:', 'cyan', attrs=['bold']), volume_info.get('publisher'))
    print(colored('Published Date:', 'cyan', attrs=['bold']), volume_info.get('publishedDate'))
    print(colored('Description:', 'cyan', attrs=['bold']), volume_info.get('description'))
    try:
        print(colored('ISBN:', 'cyan', attrs=['bold']), volume_info['isbn'])
    except:
        print(colored('ISBN:', 'cyan', attrs=['bold']), volume_info.get('industryIdentifiers', []))
    print(colored('Page Count:', 'cyan', attrs=['bold']), volume_info.get('pageCount'))
    print(colored('Categories:', 'cyan', attrs=['bold']), volume_info.get('categories', []))
    print(colored('Language:', 'cyan', attrs=['bold']), volume_info.get('language'))
    print(colored('Preview Link:', 'cyan', attrs=['bold']), volume_info.get('previewLink'))
    print(colored('Status:', 'cyan', attrs=['bold']), volume_info.get('status'))
    print(colored('Added:', 'cyan', attrs=['bold']), volume_info.get('addedDate'))
    print(colored('Book URL:', 'cyan', attrs=['bold']), volume_info.get('urlBook'))
    print('------------------------------------')

def request_book(query):
    url = f'https://www.googleapis.com/books/v1/volumes?q={query}'

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        items = data.get('items')
        if items:
            return items

        print('No results found.')
        print(colored('Title: ', 'cyan'), ''.join(url.split('?q=')[1].split(':')[1].split('+')[:-1]).capitalize())
        print(colored('Author: ', 'cyan'), url.split('?q=')[1].split(':')[2].replace('+',' ').capitalize())
        print('-' * 20)
        return edit_metadata_book()

    print('Error:', response.status_code)
    exit(1)

def loader():
    print(colored("[*]", 'cyan'), "Uploading... ", end="")
    while True:
        for c in "-\\|/":
            print(colored("\b{}", 'cyan').format(c), end="", flush=True)
            time.sleep(0.1)
            if not uploading:
                break
        else:
            continue
        break
    print(colored("\b Done!", 'green'))

def edit_metadata_book():
    print('Leave blank if you don\'t want to edit the value.')
    print('-' * 30)
    metadata_book = dict()   
    metadata_book['title'] = input('Title: ')
    metadata_book['author'] = input('Author: ')
    metadata_book['publisher'] = input('Publisher: ')
    metadata_book['publishedDate'] = input('Published Date: ')
    metadata_book['description'] = input('Description: ')
    metadata_book['isbn'] = input('ISBN: ')
    metadata_book['pageCount'] = input('Page Count: ')
    metadata_book['categories'] = input('Categories: ')
    metadata_book['language'] = input('Language: ')
    metadata_book['previewLink'] = input('Preview Link: ')
    metadata_book['status'] = input('Status: ')
    metadata_book['addedDate'] = input('Added Date: ')
    metadata_book['bookUrl'] = input('Book URL: ')

    os.system('cls' if os.name == 'nt' else 'clear')
    print('-' * 30)
    return metadata_book

def print_book_id(inserted_id):
    print('-' * 30)
    print('Book added successfully.')
    print('-' * 30)
    print(colored('Book ID: ', 'green', attrs=['bold']), inserted_id)

def print_url_book(upload_file):
    print('-' * 30)
    print('File uploaded successfully.')
    print('-' * 30)
    print(colored('BOOK URL: ', 'green', attrs=['bold']), upload_file)
    print('-' * 30)

def add_more_metadata(book, upload_file):
    book['status'] = str(args.status)
    book['addedDate'] = str(datetime.date.today())
    book['urlBook'] = upload_file
    return book
"""

CURRENT MODES ARE:
- add
- show
- list
- search
- delete
- update

"""

# SEARCH a book in the database with the id
if args.mode == 'search':
    if not args.search_query:
        if not args.id:
            id_not_found()
            print_usage_and_exit()

        result = collection.find_one({'_id': ObjectId(args.id)})
        if result:
            print_book(result.get('_id'), result)
            exit()
        else:
            book_not_found()

    search_this = args.search_query.split(':')[1]
    search_in = args.search_query.split(':')[0]
    print('Searching for', search_this, 'in', search_in, '...')

    result = collection.find({search_in: {'$regex': search_this, '$options': 'i'}})

    for doct in result:
        print_book(doct['_id'], doct)

# SHOW all books in the database
if args.mode == 'show':
    # show all ids of database
    sort_by = args.sort_by.split(' ')[0]
    in_order = args.sort_by.split(' ')[1]
    in_order = -1 if in_order.upper() != 'A' else 1
    max_docs = int(args.max_docs)

    for book in collection.find().sort(sort_by, in_order).limit(max_docs):
        print('ID: ', book.get('_id'))
        print('Title: ', book.get('title'))
        print('Author: ', book.get('authors', []))
        print('-' * 30)


# DELETE a book from the database with the id
if args.mode == 'delete':
    # delete a element with id from database
    if not args.id:
        id_not_found()
        print_usage_and_exit()

    result = collection.delete_one({'_id': ObjectId(args.id)})
    if result.deleted_count == 1:
        print('-' * 30)
        print('Book deleted successfully.')
        print('-' * 30)

    else:
        book_not_found()
        

# UPDATE a book from the database with the id
if args.mode == 'update':
    if not args.id:
        id_not_found()
        print_usage_and_exit()

    result = collection.find_one({'_id': ObjectId(args.id)})

    if result:
        print_book(result.get('_id'), result)

        meta_book = edit_metadata_book()

        if meta_book['title']:
            collection.update_one({'_id': ObjectId(args.id)}, {'$set': {'title': meta_book['title']}})
        if meta_book['author']:
            collection.update_one({'_id': ObjectId(args.id)}, {'$set': {'authors': [meta_book['author']]}})
        if meta_book['publisher']:
            collection.update_one({'_id': ObjectId(args.id)}, {'$set': {'publisher': meta_book['publisher']}})
        if meta_book['publishedDate']:
            collection.update_one({'_id': ObjectId(args.id)}, {'$set': {'publishedDate': meta_book['publishedDate']}})
        if meta_book['description']:
            collection.update_one({'_id': ObjectId(args.id)}, {'$set': {'description': meta_book['description']}})
        if meta_book['isbn']:
            collection.update_one({'_id': ObjectId(args.id)}, {'$set': {'industryIdentifiers': [{'type': 'ISBN_13', 'identifier': meta_book['isbn']}]}})
        if meta_book['pageCount']:
            collection.update_one({'_id': ObjectId(args.id)}, {'$set': {'pageCount': meta_book['pageCount']}})
        if meta_book['categories']:
            collection.update_one({'_id': ObjectId(args.id)}, {'$set': {'categories': [meta_book['categories']]}})
        if meta_book['language']:
            collection.update_one({'_id': ObjectId(args.id)}, {'$set': {'language': meta_book['language']}})
        if meta_book['previewLink']:
            collection.update_one({'_id': ObjectId(args.id)}, {'$set': {'previewLink': meta_book['previewLink']}})
        if meta_book['status']:
            collection.update_one({'_id': ObjectId(args.id)}, {'$set': {'status': meta_book['status']}})
        if meta_book['addedDate']:
            collection.update_one({'_id': ObjectId(args.id)}, {'$set': {'addedDate': meta_book['addedDate']}})
        if meta_book['bookUrl']:
            collection.update_one({'_id': ObjectId(args.id)}, {'$set': {'urlBook': meta_book['bookUrl']}})

        print('-' * 30)
        print('Book updated successfully.')
        print('-' * 30)

    else:
        book_not_found()


# Add books to the database from a LIST of books
if args.mode == 'list':
    if not args.list:
        print('Error: Please specify a list of books.')
        print_usage_and_exit()

    with open(args.list, 'r') as f:
        books = f.readlines()

        for book in books:
            try:
                title, author, status = book.split(',')
                author = author[1:]
                status = status.replace('\n', '')
            except:
                print(colored('[-] Error: ', 'red'), 'the following book is not in the correct format: ', colored(book, attrs=['bold']))
                with open('bookListError.log', 'a') as f:
                    f.write(book)
                continue

            query = f"intitle:{title.replace(' ','+')}+inauthor:{author.replace(' ','+')}"

            try:
                volume_info = request_book(query)

                for b in volume_info:
                    if b['volumeInfo']['title'].lower().replace(' ','') == title.lower().replace(' ',''):
                        if b['volumeInfo']['authors'][0].lower().replace(' ','') == author.lower().replace(' ',''):
                            volume_info = b
                            break


                volume_info['volumeInfo']['status'] = status
                volume_info['volumeInfo']['addedDate'] = datetime.datetime.now().strftime('%Y-%m-%d')
                volume_info['volumeInfo']['urlBook'] = ""
                collection.insert_one(volume_info['volumeInfo'])

                print('-' * 30)
                print('Book added successfully.')
                print('-' * 30)

            except:
                pass  

# AUTH to an object storage service
if args.mode == 'auth':
    from bb_api import auth
    print('-' * 30)
    auth.get_variables_auth()
    print('-' * 30)
    exit()

# ADD a book to the database
if args.mode == 'add':
    if not args.title and args.author:
        query = f'inauthor:{args.author}'

    elif args.title and not args.author:
        query = f'intitle:{args.title}'

    elif not args.title or not args.author:
        print('Error: Please specify a title and an author.')
        print_usage_and_exit()

    else:
        if args.file:
            print('-' * 30)
            print('UPLOADING FILE TO OBJECT STORAGE')
            print('-' * 30)
            from bb_api import upload
            file_name_orig = args.title.replace(' ','_')+'_'+args.author.replace(' ','_')+'.'+args.file.split('.')[-1]
            print(colored('Filename: ', 'cyan', attrs=['bold']), file_name_orig)
            file_name = input('Enter a new name (leave blank to keep the current name): ')

            if not file_name:
                file_name = file_name_orig

            import threading, time

            uploading = True
            loader_thread = threading.Thread(target=loader)
            loader_thread.start()

            try:
                upload_file = upload.upload_this_file(args.file, file_name)
                uploading = False
                loader_thread.join()
                print(colored('BOOK URL: ', 'green', attrs=['bold']), upload_file)

            except:
                print(colored('Error: ', 'red'), 'File not uploaded to object storage.')
                print('You may not be authenticated. Please run the ',colored('--auth', attrs=['bold']), ' flag to authenticate.')

        query = f'intitle:{args.title}+inauthor:{args.author}'
        

    items = request_book(query)

    try:

        for number, item in enumerate(items[:int(args.number)]):
            volume_info = item.get('volumeInfo')

            if volume_info:
                print_book(number+1, volume_info)

    except:
        try:
            book = add_more_metadata(items, upload_file)
        except:
            book = add_more_metadata(items, '')
        result = collection.insert_one(book)
        print_book_id(str(result.inserted_id))
        print('-' * 30)
        exit()

        try:
            print_url_book(upload_file)
        except:
            print('-' * 30)

    while True:
        try:
            choice = int(input(f'Enter the ID of the result you want to add (1-{int(args.number)}): '))
            if choice < 1 or choice > int(args.number):
                print('Invalid input. Please enter a valid integer.')
                continue
            book = items[choice-1]['volumeInfo']
            if book:
                try:
                    add_more_metadata(book, upload_file)
                except:
                    add_more_metadata(book, '')

                result = collection.insert_one(book)
                os.system('clear' if os.name == 'posix' else 'cls')
                print_book_id(str(result.inserted_id))

                try:
                    print_url_book(upload_file)
                except:
                    print('-' * 30)

            break
        except ValueError:
            print('Invalid input. Please enter a valid integer.')