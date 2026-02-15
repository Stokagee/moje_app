# Custom Libraries Development

## Learning Objectives
- [ ] Understand custom library structure
- [ ] Create Python keywords
- [ ] Integrate with Robot Framework
- [ ] Follow best practices

## Prerequisites
- Python programming knowledge
- Completed BEGINNER topics

---

## Why Custom Libraries?

**Use cases:**
- Reusable business logic
- Complex computations
- External system integration
- Domain-specific operations
- Test utilities and helpers

**Example from project:**
`ImageComparisonLibrary/` - Custom visual regression library

---

## Basic Library Structure

### Minimal Library

```python
# MyLibrary.py

from robot.api.deco import keyword

class MyLibrary:
    """Custom Robot Framework library."""

    @keyword
    def My First Keyword(self, text):
        """Logs the given text.

        Arguments:
            text: The text to log
        """
        print(f"Hello from custom library: {text}")
```

### Use in Test

```robotframework
*** Settings ***
Library     MyLibrary.py

*** Test Cases ***
Use Custom Keyword
    My First Keyword    Robot Framework!
```

---

## Library with Dependencies

### Using Other Libraries

```python
# AdvancedUtils.py
import json
from datetime import datetime

from robot.api.deco import keyword

class AdvancedUtils:
    @keyword
    def Parse JSON File(self, file_path):
        """Parse JSON file and return as dictionary.

        Arguments:
            file_path: Path to JSON file

        Returns:
            Parsed JSON dictionary
        """
        with open(file_path, 'r') as f:
            return json.load(f)

    @keyword
    def Get Current Timestamp(self):
        """Get current timestamp in ISO format.

        Returns:
            Current timestamp string
        """
        return datetime.now().isoformat()
```

### Use in Test

```robotframework
*** Settings ***
Library     AdvancedUtils.py

*** Test Cases ***
Use Advanced Utils
    ${json}=    Parse JSON File    testdata.json
    ${ts}=      Get Current Timestamp

    Log    JSON loaded: ${json}
    Log    Timestamp: ${ts}
```

---

## Keyword Arguments

### Required Arguments

```python
class MyLibrary:
    @keyword
    def Calculate Sum(self, a, b):
        """Calculate sum of two numbers.

        Arguments:
            a: First number
            b: Second number

        Returns:
            Sum of a and b
        """
        return a + b
```

### Optional Arguments

```python
class MyLibrary:
    @keyword
    def Format Name(self, first, last, middle=""):
        """Format full name with optional middle name.

        Arguments:
            first: First name
            last: Last name
            middle: Middle name (optional)

        Returns:
            Formatted full name
        """
        if middle:
            return f"{first} {middle} {last}"
        return f"{first} {last}"
```

### Variable Arguments

```python
class MyLibrary:
    @keyword
    def Concatenate Strings(self, *strings):
        """Concatenate multiple strings.

        Arguments:
            *strings: Variable number of strings

        Returns:
            Concatenated string
        """
        return "".join(strings)
```

---

## Return Values

### Return Single Value

```python
class MyLibrary:
    @keyword
    def Get Random Number(self, min_val, max_val):
        """Generate random number in range.

        Arguments:
            min_val: Minimum value (inclusive)
            max_val: Maximum value (exclusive)

        Returns:
            Random number
        """
        import random
        return random.randint(min_val, max_val)
```

### Return Dictionary

```python
class MyLibrary:
    @keyword
    def Build User Data(self, email, name):
        """Build user data dictionary.

        Arguments:
            email: User email
            name: User name

        Returns:
            Dictionary with user data
        """
        return {
            'email': email,
            'name': name,
            'created_at': datetime.now().isoformat()
        }
```

### Return List

```python
class MyLibrary:
    @keyword
    def Get Even Numbers(self, limit):
        """Get list of even numbers.

        Arguments:
            limit: Maximum number to check

        Returns:
            List of even numbers
        """
        return [i for i in range(limit) if i % 2 == 0]
```

---

## Error Handling

### Try-Except in Keywords

```python
class MyLibrary:
    @keyword
    def Safe Divide(self, a, b):
        """Divide numbers safely.

        Arguments:
            a: Numerator
            b: Denominator

        Returns:
            Result or error message
        """
        try:
            return a / b
        except ZeroDivisionError:
            return "Error: Cannot divide by zero"
        except TypeError:
            return "Error: Invalid types"
```

### Raise Errors

```python
from robot.api.deco import keyword

class MyLibrary:
    @keyword
    def Validate Email(self, email):
        """Validate email format.

        Arguments:
            email: Email to validate

        Raises:
            ValueError: If email is invalid
        """
        import re
        pattern = r'^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$'

        if not re.match(pattern, email):
            raise ValueError(f"Invalid email format: {email}")

        return True
```

---

## Application Example

### Custom Library for Form Testing

```python
# form_utils.py
from robot.api.deco import keyword
import hashlib

class FormUtils:
    """Utilities for form testing."""

    @keyword
    def Generate Unique Email(self, prefix="test"):
        """Generate unique email for testing.

        Arguments:
            prefix: Email prefix (default: test)

        Returns:
            Unique email address
        """
        import time
        timestamp = int(time.time() * 1000)
        return f"{prefix}_{timestamp}@test.com"

    @keyword
    def Hash String(self, text):
        """Create hash of string.

        Arguments:
            text: Text to hash

        Returns:
            Hexadecimal hash
        """
        return hashlib.md5(text.encode()).hexdigest()

    @keyword
    def Mask Email(self, email):
        """Mask email for logging.

        Arguments:
            email: Email to mask

        Returns:
            Masked email (user***@domain.com)
        """
        if '@' not in email:
            return email

        username, domain = email.split('@')
        return f"{username[:3]}***@{domain}"

    @keyword
    def Extract Domain From Email(self, email):
        """Extract domain from email.

        Arguments:
            email: Email address

        Returns:
            Domain part of email
        """
        if '@' not in email:
            raise ValueError(f"Invalid email: {email}")

        return email.split('@')[1]
```

### Use Custom Library

```robotframework
*** Settings ***
Library     form_utils.py
Library     FakerLibrary

*** Test Cases ***
Test With Custom Utils
    ${email}=    Generate Unique Email    prefix=user
    Log    Generated email: ${email}

    ${masked}=    Mask Email    ${email}
    Log    Masked email: ${masked}

    ${domain}=   Extract Domain From Email    ${email}
    Log    Domain: ${domain}

    Should Be Equal    ${domain}    test.com
```

---

## Best Practices

1. **Docstrings are important:**
   ```python
   def MyKeyword(self, arg1):
       """One-line description.

       Longer description with more details.

       Arguments:
           arg1: Description

       Returns:
           Description
       """
   ```

2. **Type hints:**
   ```python
   from typing import List, Dict, Optional

   def Process Items(self, items: List[str]) -> Dict[str, int]:
       ...
   ```

3. **Logging:**
   ```python
   from robot.api import logger

   def Log Info(self, message):
       logger.info(f"INFO: {message}")
   ```

4. **Error messages:**
   ```python
   def Calculate(self, a, b):
       if not isinstance(a, (int, float)):
           raise TypeError(f"a must be number, got {type(a)}")
   ```

---

## Self-Check Questions

1. How do you create a basic custom library?
2. What's the purpose of the @keyword decorator?
3. How do you return values from keywords?
4. How do you handle errors in custom keywords?

---

## Exercise: Create Custom Library

**Task:** Create a custom library with string utilities.

**Requirements:**
- Function to capitalize each word
- Function to reverse string
- Function to count words
- Function to generate test data

**Starter Code:**
```python
# string_utils.py

from robot.api.deco import keyword

class StringUtils:
    """Custom string manipulation library."""

    @keyword
    def Capitalize Each Word(self, text):
        # TODO: Implement

    @keyword
    def Reverse String(self, text):
        # TODO: Implement

    @keyword
    def Count Words(self, text):
        # TODO: Implement

    @keyword
    def Generate Test String(self, length):
        # TODO: Implement
```

---

## Hints

### Hint 1
Use Python string methods like `title()`, `[::-1]`, `split()`.

### Hint 2
```python
def Capitalize Each Word(self, text):
    return text.title()

def Reverse String(self, text):
    return text[::-1]

def Count Words(self, text):
    return len(text.split())
```

### Hint 3 (Full Solution)
```python
# string_utils.py

from robot.api.deco import keyword
import random
import string

class StringUtils:
    """Custom string manipulation library."""

    @keyword
    def Capitalize Each Word(self, text):
        """Capitalize the first letter of each word.

        Arguments:
            text: Input text

        Returns:
            Text with each word capitalized
        """
        return text.title()

    @keyword
    def Reverse String(self, text):
        """Reverse the given text.

        Arguments:
            text: Input text

        Returns:
            Reversed text
        """
        return text[::-1]

    @keyword
    def Count Words(self, text):
        """Count number of words in text.

        Arguments:
            text: Input text

        Returns:
            Number of words
        """
        words = text.split()
        return len([w for w in words if w.strip()])

    @keyword
    def Generate Test String(self, length):
        """Generate random test string of specified length.

        Arguments:
            length: Length of string to generate

        Returns:
            Random string
        """
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
```

---

## References

- [Robot Framework User Library Guide](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#creating-test-libraries)
- [Python Library Best Practices](https://docs.python-guide.com/writing/structure/)
- Project example: `/RF/ImageComparisonLibrary/`
