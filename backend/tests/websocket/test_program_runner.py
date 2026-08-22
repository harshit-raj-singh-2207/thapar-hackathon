import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from app.main import app, startup_event
from app.core.database import Base, engine

client = TestClient(app)

def test_websocket_30_programs_execution():
    with client.websocket_connect("/api/v1/community/ws/programs") as ws:
        ack = ws.receive_json()
        assert ack["type"] == "connection_ack"

        # 1. Hello World
        ws.send_json({"type": "run_program", "program_id": 1, "inputs": {"name": "Alice", "age": 30}})
        res1 = ws.receive_json()
        assert res1["type"] == "program_result"
        assert "Hello, Alice!" in res1["message"]

        # 2. Calculator
        ws.send_json({"type": "run_program", "program_id": 2, "inputs": {"num1": 20, "num2": 4, "operation": "divide"}})
        res2 = ws.receive_json()
        assert "20.0 / 4.0 = 5.0" in res2["message"]

        # 3. Odd or Even
        ws.send_json({"type": "run_program", "program_id": 3, "inputs": {"n": 14}})
        res3 = ws.receive_json()
        assert "Even" in res3["message"]

        # 4. Area & Circumference
        ws.send_json({"type": "run_program", "program_id": 4, "inputs": {"radius": 10}})
        res4 = ws.receive_json()
        assert "Area: 314.16" in res4["message"]

        # 5. Swap Variables
        ws.send_json({"type": "run_program", "program_id": 5, "inputs": {"a": 100, "b": 200}})
        res5 = ws.receive_json()
        assert "Swapped: (a=200, b=100)" in res5["message"]

        # 6. Max of Three
        ws.send_json({"type": "run_program", "program_id": 6, "inputs": {"a": 12, "b": 99, "c": 45}})
        res6 = ws.receive_json()
        assert "largest" in res6["message"] and "99.0" in res6["message"]

        # 7. Leap Year
        ws.send_json({"type": "run_program", "program_id": 7, "inputs": {"year": 2000}})
        res7 = ws.receive_json()
        assert "Leap Year" in res7["message"]

        # 8. Celsius to Fahrenheit
        ws.send_json({"type": "run_program", "program_id": 8, "inputs": {"temp": 0, "mode": "c_to_f"}})
        res8 = ws.receive_json()
        assert "32.00°F" in res8["message"]

        # 9. Simple Interest
        ws.send_json({"type": "run_program", "program_id": 9, "inputs": {"principal": 1000, "rate": 5, "time": 2}})
        res9 = ws.receive_json()
        assert "Interest: $100.00" in res9["message"]

        # 10. Grading System
        ws.send_json({"type": "run_program", "program_id": 10, "inputs": {"marks": 95}})
        res10 = ws.receive_json()
        assert "Grade: A" in res10["message"]

        # 11. Factorial
        ws.send_json({"type": "run_program", "program_id": 11, "inputs": {"n": 5}})
        res11 = ws.receive_json()
        assert "5! = 120" in res11["message"]

        # 12. Multiplication Table
        ws.send_json({"type": "run_program", "program_id": 12, "inputs": {"n": 3, "limit": 5}})
        res12 = ws.receive_json()
        assert "3 x 5 = 15" in res12["message"]

        # 13. Sum of Natural Numbers
        ws.send_json({"type": "run_program", "program_id": 13, "inputs": {"n": 10}})
        res13 = ws.receive_json()
        assert "55" in res13["message"]

        # 14. Fibonacci Sequence
        ws.send_json({"type": "run_program", "program_id": 14, "inputs": {"n": 7}})
        res14 = ws.receive_json()
        assert "0, 1, 1, 2, 3, 5, 8" in str(res14["data"]["result"])

        # 15. Count Digits
        ws.send_json({"type": "run_program", "program_id": 15, "inputs": {"n": 54321}})
        res15 = ws.receive_json()
        assert "contains 5 digit(s)" in res15["message"]

        # 16. Reverse Number
        ws.send_json({"type": "run_program", "program_id": 16, "inputs": {"n": 12345}})
        res16 = ws.receive_json()
        assert "Reversed: 54321" in res16["message"]

        # 17. Palindrome Number
        ws.send_json({"type": "run_program", "program_id": 17, "inputs": {"n": 121}})
        res17 = ws.receive_json()
        assert "is a Palindrome" in res17["message"]

        # 18. Prime Number Checker
        ws.send_json({"type": "run_program", "program_id": 18, "inputs": {"n": 19}})
        res18 = ws.receive_json()
        assert "Prime Number" in res18["message"]

        # 19. Armstrong Number
        ws.send_json({"type": "run_program", "program_id": 19, "inputs": {"n": 153}})
        res19 = ws.receive_json()
        assert "Armstrong Number" in res19["message"]

        # 20. Vowel or Consonant
        ws.send_json({"type": "run_program", "program_id": 20, "inputs": {"char": "i"}})
        res20 = ws.receive_json()
        assert "Vowel" in res20["message"]

        # 21. List Elements Sum
        ws.send_json({"type": "run_program", "program_id": 21, "inputs": {"numbers": [1, 2, 3, 4, 5]}})
        res21 = ws.receive_json()
        assert "Sum of [1, 2, 3, 4, 5] = 15.0" in res21["message"]

        # 22. Find Min and Max
        ws.send_json({"type": "run_program", "program_id": 22, "inputs": {"numbers": [10, 50, 5, 80, 2]}})
        res22 = ws.receive_json()
        assert "Min: 2.0, Max: 80.0" in res22["message"]

        # 23. Count Elements
        ws.send_json({"type": "run_program", "program_id": 23, "inputs": {"numbers": [5, 5, 2, 5, 1], "target": 5}})
        res23 = ws.receive_json()
        assert "appears 3 time(s)" in res23["message"]

        # 24. String Reversal
        ws.send_json({"type": "run_program", "program_id": 24, "inputs": {"text": "hello"}})
        res24 = ws.receive_json()
        assert "Reversed: 'olleh'" in res24["message"]

        # 25. Count Vowels
        ws.send_json({"type": "run_program", "program_id": 25, "inputs": {"text": "education"}})
        res25 = ws.receive_json()
        assert "contains 5 vowel(s)" in res25["message"]

        # 26. Length of String
        ws.send_json({"type": "run_program", "program_id": 26, "inputs": {"text": "python"}})
        res26 = ws.receive_json()
        assert "Length of 'python' is 6" in res26["message"]

        # 27. Pattern Square
        ws.send_json({"type": "run_program", "program_id": 27, "inputs": {"size": 3}})
        res27 = ws.receive_json()
        assert "* * *" in res27["message"]

        # 28. Pattern Right Triangle
        ws.send_json({"type": "run_program", "program_id": 28, "inputs": {"rows": 3}})
        res28 = ws.receive_json()
        assert "* * *" in res28["message"]

        # 29. List Deduplication
        ws.send_json({"type": "run_program", "program_id": 29, "inputs": {"numbers": [1, 1, 2, 3, 2, 4]}})
        res29 = ws.receive_json()
        assert "Deduplicated: [1, 2, 3, 4]" in res29["message"]

        # 30. Even Numbers in Range
        ws.send_json({"type": "run_program", "program_id": 30, "inputs": {"lower": 1, "upper": 10}})
        res30 = ws.receive_json()
        assert "[2, 4, 6, 8, 10]" in res30["message"]

if __name__ == "__main__":
    test_websocket_30_programs_execution()
    print("ALL 30 WEBSOCKET PROGRAMS INTEGRATION TEST PASSED SUCCESSFULLY!")
