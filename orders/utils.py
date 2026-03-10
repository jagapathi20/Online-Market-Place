import datetime

def generate_order_number(pk):
    return f"{datetime.datetime.now().strftime('%Y%m%d%H%m%S')}+{str(pk)}"