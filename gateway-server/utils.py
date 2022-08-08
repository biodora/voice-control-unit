from struct import pack, unpack

def float_to_two_int(data_in):
    data_binary = pack(">f", data_in)
    data_out = list(unpack(">HH", data_binary))
    data_out.reverse()
    return data_out

def two_int_to_float(data_in):
    data_in.reverse()
    data_binary = pack('>HH', *data_in)
    data_out = round(unpack('>f', data_binary)[0], 3)
    return data_out

def ulong_to_two_ints(data_in):
    data_binary = pack('>L', data_in)
    data_out = list(unpack(">HH", data_binary))
    data_out.reverse()
    return data_out

def two_ints_to_ulong(data_in):
    data_in.reverse()
    data_binary = pack(">HH", data_in)
    data_out = unpack(">L", data_binary)[0]
    return data_out

if __name__ == "__main__":
    a = float_to_two_int(345.678)
    b = two_int_to_float(a)
