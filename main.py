import sqlite3
from datetime import datetime
import os
import pandas as pd

# Database path
db_path = 'ecommerce.db'

def execute_query(query):
    '''
    General method to exeucte queries
    Input Parameters:
    query : query to execute,  type string
    '''
    conn = sqlite3.connect(db_path)
    cur = False
    try:
        cur = conn.execute(query)
        conn.commit()
    except Exception as e:
        print(e)
    conn.close()
    return cur

def help():
    print('''
1: Register Product
2: Register Customer
3: Purchase
4: Reporting
9: Help ( Operations )
0: Exit
''')

def init():
    # Connect database
    conn = sqlite3.connect(db_path)
    # Try to create product table
    try:
        execute_query("""CREATE TABLE Product(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name TEXT NOT NULL,
            price  FLOAT NOT NULL
            );""")
        print('Product table created.')
    except Exception as e:
        print('Product table creation failed !')

    # Try to create customer table
    try:
        execute_query("""CREATE TABLE Customer(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name TEXT NOT NULL,
            email VARCHAR NOT NULL,
            number VARCHAR,
            balance FLOAT DEFAULT 0
            );""")
        print('Customer table created.')
    except Exception as e:
        print('Customer table creation failed !')

    # Try to create purchase record table
    try:
        execute_query("""CREATE TABLE Purchase(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
            product_id INTEGER NOT NULL,
            product_name VARCHAR  NOT NULL,
            customer_id INTEGER NOT NULL,
            customer_name VARCHAR  NOT NULL,
            price FLOAT NOT NULL DEFAULT 0,
            quantity FLOAT NOT NULL,
            amount FLOAT NOT NULL,
            discount FLOAT NOT NULL DEFAULT 0,
            subtotal FLOAT NOT NULL,
            purchase_date DATETIME DEFAULT (strftime('%m-%d-%Y %H:%M:%S','now'))
            );""")
        print('Purchase table created.')
    except Exception as e:
        print('Purchase table creation failed !')


def register_product():
    name = input('Product Name :')
    while not name:
        name = input('Product Name :')
    try:
        price = float(input('Price ($):'))
        while not isinstance(price,float or int) or not price:
            price = float(input('Price ($): '))
    except ValueError:
        print('Invalid Value for Price.\n\nRegistration Cancellled !')
        return
    # query to insert product record.
    query  = """INSERT INTO Product (name,price) VALUES ('{}',{});""".format(name,price)
    result = execute_query(query)
    if result:
        print('Product {} registered successfully !'.format(name))

def register_customer():
    name = input('Name :')
    email = input('Email :')
    while not email:
        email = input('Email :')
    number = input('Number :')
    balance = 0
    
    query = """INSERT INTO Customer (name,email,number,balance) VALUES ('{}','{}',{},{});""".format(name or '',email or '',number or 'NULL',balance)
    try:
        result = execute_query(query)
        if result:
            print('Customer registered successfully !')
    except Exception as e:
        print(e)

def all_products():
    conn = sqlite3.connect(db_path)
    products = []
    try:
        all_product_res = conn.execute('''SELECT id,name,price FROM Product;''')
        products = all_product_res.fetchall()
    except Exception as e:
        print('Product data import interrupted !')
    conn.close()
    return products

def select_product():
    products = all_products()
    if not len(products):
        print('Please register product first !')
        return False
    print('\nProducts :\nID : Name')
    product_data = {}
    for product in products:
        product_data[product[0]] = {'name':product[1],'price':product[2]}
        print('{} : {}'.format(product[0],product[1]))
    
    product_id = False
    product_name = False
    while True:
        try:
            product_id = input('Select product : ')
            product_id = int(product_id)
            if product_id not in product_data.keys():
                print('Product ID is not available.')
                continue
            break
        except Exception as e:
            print('Select one of the id of product !')
    
    price = 0
    if product_id:
        price = product_data[product_id]['price']
        product_name = product_data[product_id]['name']
    return product_id,product_name,price


def create_purchase(email):
    '''
    Input Parameters:
    customer_id : ID of the customer who is puchasing, TYPE int
    '''
    # Confirm how purchase is gonna be done.
    confirm_customer = 'SELECT * from Customer where email = \'{}\''.format(email)
    conn = sqlite3.connect(db_path)
    cur = conn.execute(confirm_customer)
    result = cur.fetchone()
    if not result or not len(result):
        print('Customer not found')
        print('Purchase Failed !')
        conn.close()
        return
    conn.close()
    customer_id = result[0]
    customer_name = result[1]
    
    product_id,product_name,price = select_product()
    if product_id:
        print('Price is {}.'.format(price))
    
    quantity = 0
    while True:
        quantity = input('Quantity : ')
        try:
            quantity = int(quantity)
            break
        except Exception as e:
            print('Invalid Value !')
        
    
    amount = price * quantity
    discount = 0.0
    while True:
        discount = input('Discount (%): ')
        try:
            discount = float(discount)
            break
        except Exception as e:
            print('Invalid Value !')
    subtotal = (price - (price * discount * 0.01)) * quantity
    query = '''INSERT INTO Purchase (product_id,product_name,customer_id,customer_name,price,quantity,amount,discount,subtotal) VALUES ({},\'{}\',{},\'{}\',{},{},{},{},{})'''.format(product_id,product_name,customer_id,customer_name,price,quantity,amount,discount,subtotal)
    try:
        cur = execute_query(query)
        if cur.rowcount:
            print('Purchase done.')
    except Exception as e:
        print(e)
    

def flush_database():
    execute_query('DROP TABLE Product;')
    print('Product table dropped !')
    execute_query('DROP TABLE Customer;')
    print('Customer table dropped !')
    execute_query('DROP TABLE Purchase;')
    print('Purchase table dropped !')
    print('\n')

def get_all_purchase():
    query = """SELECT 
    purchase_date as 'Purchase Date',
    customer_name as 'Customer',
    product_name as 'Product',
    price as 'Price',
    quantity as 'Quantity',
    discount as 'Discount',
    amount as 'Amount',
    subtotal as 'Subtotal'
    FROM Purchase;"""
    result = []
    conn = sqlite3.connect(db_path)
    try:
        result = conn.execute(query)
        result = result.fetchall()
    except Exception as e:
        print(str(e))
    finally:
        conn.close()
    return result

def process():
    print('\nStarting...')
    operation = False
    help()
    while True:
        try:
            operation = int(input('--> '))
        except Exception as e:
            print('Invalid value for operation')
            help()
            continue
        try:
            if operation == 1:
                print('\nRegister Product ...')
                register_product()
            elif operation == 2:
                print('\nRegister Customer ...')
                register_customer()
            elif operation == 3:
                print('\nPurchasing ...')
                customer_email = input('Email :')
                create_purchase(customer_email)
            elif operation == 4:
                print("\nReporting ...")
                products = get_all_purchase()
                df = pd.DataFrame(products,columns=['Date','Customer','Product','Price','Quantity','Discount','Amount','Subtotal'])
                df.to_excel("Report.xlsx",index=False) 
                print('Report has been printed !')
            elif operation == 9:
                os.system('cls')
                help()
            elif operation == 0:
                break
            elif operation == 10:
                flush_database()
                init()
            else:
                print('\nInvalid operation !')
                help()
        except Exception as e:
            print(e)
    print('\nExiting...')


init()
try:
    process()
except Exception as e:
    print(' \nProcess ending...')