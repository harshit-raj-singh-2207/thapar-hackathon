import math
from typing import Dict, Any

class ProgramRunner:
    @staticmethod
    def execute(program_id: int, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes one of 30 algorithmic tasks based on program_id (1 to 30)
        and returns a structured execution response.
        """
        try:
            handler = getattr(ProgramRunner, f"_program_{program_id}", None)
            if not handler:
                return {
                    "program_id": program_id,
                    "title": f"Program {program_id}",
                    "success": False,
                    "error": f"Invalid program_id {program_id}. Must be between 1 and 30.",
                }
            result_data = handler(inputs or {})
            return {
                "program_id": program_id,
                "title": result_data.get("title", f"Program {program_id}"),
                "success": True,
                "inputs": inputs,
                "result": result_data.get("output"),
                "details": result_data.get("details"),
            }
        except Exception as e:
            return {
                "program_id": program_id,
                "title": f"Program {program_id}",
                "success": False,
                "inputs": inputs,
                "error": str(e),
            }

    # 1. Hello World & Basic I/O
    @staticmethod
    def _program_1(inp: dict) -> dict:
        name = str(inp.get("name", "Caregiver"))
        age = int(inp.get("age", 25))
        greeting = f"Hello, {name}! You are {age} years old. Welcome to NIVARA Community!"
        return {"title": "Hello World & Basic I/O", "output": greeting}

    # 2. Arithmetic Calculator
    @staticmethod
    def _program_2(inp: dict) -> dict:
        num1 = float(inp.get("num1", 10))
        num2 = float(inp.get("num2", 5))
        op = str(inp.get("operation", "add")).lower()

        if op in ["add", "+"]:
            res = num1 + num2
            op_symbol = "+"
        elif op in ["subtract", "-"]:
            res = num1 - num2
            op_symbol = "-"
        elif op in ["multiply", "*"]:
            res = num1 * num2
            op_symbol = "*"
        elif op in ["divide", "/"]:
            if num2 == 0:
                raise ValueError("Division by zero is not allowed.")
            res = num1 / num2
            op_symbol = "/"
        else:
            raise ValueError(f"Unknown operation '{op}'. Supported: add, subtract, multiply, divide.")

        return {
            "title": "Arithmetic Calculator",
            "output": f"{num1} {op_symbol} {num2} = {res}",
            "details": {"num1": num1, "num2": num2, "operation": op, "result": res}
        }

    # 3. Odd or Even Checker
    @staticmethod
    def _program_3(inp: dict) -> dict:
        n = int(inp.get("n", inp.get("number", 7)))
        is_even = (n % 2 == 0)
        status = "Even" if is_even else "Odd"
        return {
            "title": "Odd or Even Checker",
            "output": f"{n} is an {status} number.",
            "details": {"number": n, "is_even": is_even}
        }

    # 4. Area & Circumference
    @staticmethod
    def _program_4(inp: dict) -> dict:
        r = float(inp.get("radius", 5))
        if r < 0:
            raise ValueError("Radius cannot be negative.")
        area = math.pi * (r ** 2)
        circumference = 2 * math.pi * r
        return {
            "title": "Area & Circumference of Circle",
            "output": f"Radius: {r} -> Area: {area:.2f}, Circumference: {circumference:.2f}",
            "details": {"radius": r, "area": round(area, 4), "circumference": round(circumference, 4)}
        }

    # 5. Swap Two Variables
    @staticmethod
    def _program_5(inp: dict) -> dict:
        a = inp.get("a", "First")
        b = inp.get("b", "Second")

        # Auxiliary variable swap
        temp = a
        aux_a = b
        aux_b = temp

        # Pythonic tuple unpacking swap
        py_a, py_b = a, b
        py_a, py_b = py_b, py_a

        return {
            "title": "Swap Two Variables",
            "output": f"Original: (a={a}, b={b}) -> Swapped: (a={py_a}, b={py_b})",
            "details": {
                "original": {"a": a, "b": b},
                "auxiliary_swap": {"a": aux_a, "b": aux_b},
                "pythonic_unpacking": {"a": py_a, "b": py_b}
            }
        }

    # 6. Maximum of Three Numbers
    @staticmethod
    def _program_6(inp: dict) -> dict:
        a = float(inp.get("a", 10))
        b = float(inp.get("b", 25))
        c = float(inp.get("c", 15))

        if a >= b and a >= c:
            largest = a
        elif b >= a and b >= c:
            largest = b
        else:
            largest = c

        return {
            "title": "Maximum of Three Numbers",
            "output": f"The largest of [{a}, {b}, {c}] is {largest}.",
            "details": {"a": a, "b": b, "c": c, "largest": largest}
        }

    # 7. Leap Year Identifier
    @staticmethod
    def _program_7(inp: dict) -> dict:
        year = int(inp.get("year", 2024))
        is_leap = (year % 400 == 0) or (year % 4 == 0 and year % 100 != 0)
        status = "a Leap Year" if is_leap else "NOT a Leap Year"
        return {
            "title": "Leap Year Identifier",
            "output": f"Year {year} is {status}.",
            "details": {"year": year, "is_leap_year": is_leap}
        }

    # 8. Celsius to Fahrenheit & Vice Versa
    @staticmethod
    def _program_8(inp: dict) -> dict:
        temp = float(inp.get("temp", 37))
        mode = str(inp.get("mode", "c_to_f")).lower()

        if mode in ["c_to_f", "celsius_to_fahrenheit"]:
            res = (temp * 9 / 5) + 32
            out_str = f"{temp}°C = {res:.2f}°F"
        else:
            res = (temp - 32) * 5 / 9
            out_str = f"{temp}°F = {res:.2f}°C"

        return {
            "title": "Celsius to Fahrenheit Converter",
            "output": out_str,
            "details": {"input_temp": temp, "mode": mode, "converted_temp": round(res, 2)}
        }

    # 9. Simple Interest Calculator
    @staticmethod
    def _program_9(inp: dict) -> dict:
        p = float(inp.get("principal", 1000))
        r = float(inp.get("rate", 5))
        t = float(inp.get("time", 2))

        interest = (p * r * t) / 100
        total_amount = p + interest
        return {
            "title": "Simple Interest Calculator",
            "output": f"Principal: ${p:.2f}, Rate: {r}%, Time: {t} yrs -> Interest: ${interest:.2f}, Total: ${total_amount:.2f}",
            "details": {"principal": p, "rate": r, "time": t, "interest": interest, "total": total_amount}
        }

    # 10. Grading System
    @staticmethod
    def _program_10(inp: dict) -> dict:
        marks = float(inp.get("marks", 85))
        if marks < 0 or marks > 100:
            raise ValueError("Marks must be between 0 and 100.")

        if marks >= 90:
            grade = "A"
        elif marks >= 80:
            grade = "B"
        elif marks >= 70:
            grade = "C"
        elif marks >= 60:
            grade = "D"
        else:
            grade = "F"

        return {
            "title": "Grading System",
            "output": f"Marks: {marks}% -> Grade: {grade}",
            "details": {"marks": marks, "grade": grade}
        }

    # 11. Factorial Computation
    @staticmethod
    def _program_11(inp: dict) -> dict:
        n = int(inp.get("n", inp.get("number", 5)))
        if n < 0:
            raise ValueError("Factorial is not defined for negative integers.")

        result = 1
        curr = n
        while curr > 1:
            result *= curr
            curr -= 1

        return {
            "title": "Factorial Computation",
            "output": f"{n}! = {result}",
            "details": {"number": n, "factorial": result}
        }

    # 12. Multiplication Table
    @staticmethod
    def _program_12(inp: dict) -> dict:
        n = int(inp.get("n", inp.get("number", 7)))
        limit = int(inp.get("limit", 10))

        table = []
        table_lines = []
        for i in range(1, limit + 1):
            val = n * i
            table.append(val)
            table_lines.append(f"{n} x {i} = {val}")

        return {
            "title": f"Multiplication Table for {n}",
            "output": "\n".join(table_lines),
            "details": {"number": n, "table": table}
        }

    # 13. Sum of Natural Numbers
    @staticmethod
    def _program_13(inp: dict) -> dict:
        n = int(inp.get("n", 10))
        if n <= 0:
            raise ValueError("N must be a positive natural number (> 0).")

        total_sum = 0
        for i in range(1, n + 1):
            total_sum += i

        return {
            "title": f"Sum of First {n} Natural Numbers",
            "output": f"Sum of first {n} natural numbers is {total_sum}.",
            "details": {"n": n, "sum": total_sum}
        }

    # 14. Fibonacci Sequence
    @staticmethod
    def _program_14(inp: dict) -> dict:
        n = int(inp.get("n", 8))
        if n <= 0:
            return {"title": "Fibonacci Sequence", "output": "[]", "details": {"sequence": []}}

        seq = []
        a, b = 0, 1
        for _ in range(n):
            seq.append(a)
            a, b = b, a + b

        return {
            "title": f"First {n} terms of Fibonacci Sequence",
            "output": f"Fibonacci({n}): {seq}",
            "details": {"n": n, "sequence": seq}
        }

    # 15. Count Digits
    @staticmethod
    def _program_15(inp: dict) -> dict:
        n = int(inp.get("n", inp.get("number", 12345)))
        abs_n = abs(n)
        count = 0
        temp = abs_n
        if temp == 0:
            count = 1
        else:
            while temp > 0:
                count += 1
                temp //= 10

        return {
            "title": "Count Digits",
            "output": f"The number {n} contains {count} digit(s).",
            "details": {"number": n, "digit_count": count}
        }

    # 16. Reverse a Number
    @staticmethod
    def _program_16(inp: dict) -> dict:
        n = int(inp.get("n", inp.get("number", 9876)))
        is_neg = n < 0
        temp = abs(n)
        reversed_n = 0

        while temp > 0:
            digit = temp % 10
            reversed_n = (reversed_n * 10) + digit
            temp //= 10

        if is_neg:
            reversed_n = -reversed_n

        return {
            "title": "Reverse a Number",
            "output": f"Original: {n} -> Reversed: {reversed_n}",
            "details": {"original": n, "reversed": reversed_n}
        }

    # 17. Palindrome Number
    @staticmethod
    def _program_17(inp: dict) -> dict:
        n = int(inp.get("n", inp.get("number", 12321)))
        is_neg = n < 0
        if is_neg:
            is_palindrome = False
            reversed_n = -abs(n)
        else:
            temp = n
            reversed_n = 0
            while temp > 0:
                reversed_n = (reversed_n * 10) + (temp % 10)
                temp //= 10
            is_palindrome = (n == reversed_n)

        status = "a Palindrome" if is_palindrome else "NOT a Palindrome"
        return {
            "title": "Palindrome Number Checker",
            "output": f"Number {n} is {status}.",
            "details": {"number": n, "reversed": reversed_n, "is_palindrome": is_palindrome}
        }

    # 18. Prime Number Checker
    @staticmethod
    def _program_18(inp: dict) -> dict:
        n = int(inp.get("n", inp.get("number", 29)))
        if n <= 1:
            is_prime_num = False
        else:
            is_prime_num = True
            for i in range(2, int(math.isqrt(n)) + 1):
                if n % i == 0:
                    is_prime_num = False
                    break

        status = "a Prime Number" if is_prime_num else "a Composite Number"
        return {
            "title": "Prime Number Checker",
            "output": f"{n} is {status}.",
            "details": {"number": n, "is_prime": is_prime_num}
        }

    # 19. Armstrong Number
    @staticmethod
    def _program_19(inp: dict) -> dict:
        n = int(inp.get("n", inp.get("number", 153)))
        if n < 0:
            is_armstrong_num = False
            sum_pow = 0
        else:
            digits = [int(d) for d in str(n)]
            num_digits = len(digits)
            sum_pow = sum(d ** num_digits for d in digits)
            is_armstrong_num = (sum_pow == n)

        status = "an Armstrong Number" if is_armstrong_num else "NOT an Armstrong Number"
        return {
            "title": "Armstrong Number Verifier",
            "output": f"{n} is {status}.",
            "details": {"number": n, "sum_of_powers": sum_pow, "is_armstrong": is_armstrong_num}
        }

    # 20. Vowel or Consonant
    @staticmethod
    def _program_20(inp: dict) -> dict:
        char = str(inp.get("char", inp.get("character", "a"))).strip()
        if not char or not char.isalpha():
            raise ValueError("Input must be a single alphabetic character.")

        c = char[0].lower()
        is_vow = c in ["a", "e", "i", "o", "u"]
        status = "Vowel" if is_vow else "Consonant"
        return {
            "title": "Vowel or Consonant Checker",
            "output": f"'{char[0]}' is a {status}.",
            "details": {"character": char[0], "is_vowel": is_vow}
        }

    # 21. List Elements Sum
    @staticmethod
    def _program_21(inp: dict) -> dict:
        nums = inp.get("numbers", [10, 20, 30, 40, 50])
        if not isinstance(nums, list):
            nums = [float(x) for x in str(nums).split(",")]

        cum_sum = 0
        for num in nums:
            cum_sum += float(num)

        return {
            "title": "List Elements Sum",
            "output": f"Sum of {nums} = {cum_sum}",
            "details": {"numbers": nums, "sum": cum_sum}
        }

    # 22. Find Min and Max in List (No built-ins)
    @staticmethod
    def _program_22(inp: dict) -> dict:
        nums = inp.get("numbers", [45, 12, 89, 3, 67, 24])
        if not isinstance(nums, list):
            nums = [float(x) for x in str(nums).split(",")]

        if not nums:
            raise ValueError("List cannot be empty.")

        min_val = float(nums[0])
        max_val = float(nums[0])

        for val in nums[1:]:
            f_val = float(val)
            if f_val < min_val:
                min_val = f_val
            if f_val > max_val:
                max_val = f_val

        return {
            "title": "Find Min and Max in List",
            "output": f"List: {nums} -> Min: {min_val}, Max: {max_val}",
            "details": {"numbers": nums, "min": min_val, "max": max_val}
        }

    # 23. Count Elements
    @staticmethod
    def _program_23(inp: dict) -> dict:
        nums = inp.get("numbers", [1, 2, 3, 2, 4, 2, 5])
        target = inp.get("target", 2)
        if not isinstance(nums, list):
            nums = [x.strip() for x in str(nums).split(",")]

        freq = 0
        for item in nums:
            if str(item) == str(target):
                freq += 1

        return {
            "title": "Count Element Frequency",
            "output": f"Element '{target}' appears {freq} time(s) in list.",
            "details": {"numbers": nums, "target": target, "frequency": freq}
        }

    # 24. String Reversal
    @staticmethod
    def _program_24(inp: dict) -> dict:
        text = str(inp.get("text", "NIVARA Community"))
        rev_text = text[::-1]
        return {
            "title": "String Reversal",
            "output": f"Original: '{text}' -> Reversed: '{rev_text}'",
            "details": {"text": text, "reversed": rev_text}
        }

    # 25. Count Vowels in String
    @staticmethod
    def _program_25(inp: dict) -> dict:
        text = str(inp.get("text", "Autism Caregiver Support"))
        vowels = "aeiouAEIOU"
        count = sum(1 for ch in text if ch in vowels)
        return {
            "title": "Count Vowels in String",
            "output": f"Text: '{text}' contains {count} vowel(s).",
            "details": {"text": text, "vowel_count": count}
        }

    # 26. Length of String (Without len())
    @staticmethod
    def _program_26(inp: dict) -> dict:
        text = str(inp.get("text", "Hello World"))
        length = 0
        for _ in text:
            length += 1
        return {
            "title": "Length of String (Custom Loop)",
            "output": f"Length of '{text}' is {length} character(s).",
            "details": {"text": text, "length": length}
        }

    # 27. Pattern Printing - Square
    @staticmethod
    def _program_27(inp: dict) -> dict:
        size = int(inp.get("size", 4))
        if size <= 0:
            raise ValueError("Size must be greater than 0.")

        grid = []
        for _ in range(size):
            grid.append("* " * size)

        pattern = "\n".join(grid)
        return {
            "title": f"Square Pattern ({size}x{size})",
            "output": pattern,
            "details": {"size": size, "pattern_rows": grid}
        }

    # 28. Pattern Printing - Right Triangle
    @staticmethod
    def _program_28(inp: dict) -> dict:
        rows = int(inp.get("rows", 5))
        if rows <= 0:
            raise ValueError("Rows must be greater than 0.")

        grid = []
        for i in range(1, rows + 1):
            grid.append("* " * i)

        pattern = "\n".join(grid)
        return {
            "title": f"Right Triangle Pattern ({rows} rows)",
            "output": pattern,
            "details": {"rows": rows, "pattern_rows": grid}
        }

    # 29. List De-duplication (Order preserved)
    @staticmethod
    def _program_29(inp: dict) -> dict:
        nums = inp.get("numbers", [1, 3, 2, 3, 4, 1, 5, 2])
        if not isinstance(nums, list):
            nums = [x.strip() for x in str(nums).split(",")]

        unique_list = []
        seen = set()
        for item in nums:
            if item not in seen:
                seen.add(item)
                unique_list.append(item)

        return {
            "title": "List De-duplication",
            "output": f"Original: {nums} -> Deduplicated: {unique_list}",
            "details": {"original": nums, "deduplicated": unique_list}
        }

    # 30. Even Numbers in a Range
    @staticmethod
    def _program_30(inp: dict) -> dict:
        lower = int(inp.get("lower", 1))
        upper = int(inp.get("upper", 20))

        if lower > upper:
            raise ValueError("Lower bound must be <= upper bound.")

        evens = [x for x in range(lower, upper + 1) if x % 2 == 0]
        return {
            "title": f"Even Numbers in Range [{lower}, {upper}]",
            "output": f"Even numbers between {lower} and {upper}: {evens}",
            "details": {"lower": lower, "upper": upper, "even_numbers": evens}
        }
