

class QNumber:

    def __init__(self, m: int, n: int, value: int) -> None:
        self.m = m
        self.n = n
        self.size = m+n
        self.value = value

    def __str__(self) -> str:
        return hex(self.value)

    @staticmethod
    def from_float(value: float, m: int, n: int):
        int_part = int(value)
        float_part = value%1
        bin_int_part = bin(int_part)[2::].rjust(m, "0")
        bin_float_part = bin(int(float_part*2**n))[2::].rjust(n, "0")
        res_bin = bin_int_part + bin_float_part
        res = int(res_bin, 2)

        return QNumber(m, n, res)

    def from_q_format_to_float(self):
        
        bin_value = bin(self.value)[2::].rjust(self.size, "0")

        int_part = int(bin_value[0:self.m], 2)
        decimal_part = int(bin_value[self.m::], 2)/2**self.n
        res = int_part + decimal_part

        return res

