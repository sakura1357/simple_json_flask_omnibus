

def test_str():
    sql = 'abc'
    for item in ['d', 'e','f']:
        sql = sql + "AND" + item
    return sql

if __name__ == '__main__':
    print(test_str())
