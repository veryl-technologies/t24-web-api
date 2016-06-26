import datetime


def num_to_short_alphanumeric(i):
    # Note that there is no Z, which is used for other purposes
    chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXY'
    length = len(chars)

    result = ''
    while i:
        result = chars[i % length] + result
        i = i // length
    if not result:
        result = chars[0]
    return result


def get_unique_new_customer_mnemonic():
    base = datetime.datetime(2016, 2, 1, 00, 00)
    secondsPassed = int((datetime.datetime.now() - base).total_seconds())
    code = num_to_short_alphanumeric(secondsPassed)
    result = code.rjust(8, 'Z')
    return result


def add_t24_days(date_str, num_days):
    date = datetime.datetime.strptime(date_str, '%Y%m%d') + datetime.timedelta(days=num_days)
    return date.strftime('%Y%m%d')

