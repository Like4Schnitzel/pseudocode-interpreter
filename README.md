# pseudocode-interpreter
My teacher really likes pseudocode but I don't, so here's an interpreter to at least make it runnable.
Needs Python 3.10+ to run due to match case statements.
Error messages might be slightly broken.
Translator to translate the pseudocode to Python code is currently unfinished.

## Docs for the pseudocode
* Operators
  * Mathematical operators
    * +, -, *, /, div, mod, %, ^, sqrt
    * 'div' is integer division.
    * 'mod' and '%' are synonymous.
  * Logical operators
    * <, <=, >, >=, ==, !=
    * "nicht, und, oder" as "not, and, or"

* Variables
  * Are global.
  * Do not need to be declared.
  * Do not have data types.
  
* Booleans
  * Are written as "true" or "false".
  
* Indentation
  * Is mandatory.
  * First indent that is found is taken as step value for the program.

* If statements
  * Are written as follows:
    ```
    falls condition
      dann ...
      sonst ...
    ```
    being equivalent to
    ```
    if condition
      then ...
      else ...
    ```
  * Multiple lines of code after a `dann` or `sonst` require indentation.
    ```
    falls condition
      dann ...
        ...
      sonst ...
    ```
    
  * else-/then-if statements require double indentation.
    ```
    falls condition1
      dann falls condition2
          dann ...
      sonst falls condition3
          dann ...
    ```

* Switch case statements
  * Are written as follows:
    ```
    falls value
      x: ...
      y: ...
        ...
      z: ...
      sonst: ...
    ```
    being equivalent to
    ```
    switch (value)
    {
      case x: ...
        break;
      case y: ...
        ...
        break;
      case z: ...
        break;
      default: ...
        break;
    }
    ```
  * Break statements don't exist.
  * `value` is stored into an internal variable and cannot be changed.
  * `x`/`y`/`z` get evaluated at time of comparison.
  * Any expression or variable is valid as `x`/`y`/`z`.

* While loops
  * Are written as follows:
    ```
    solange condition wiederhole
      ...
    ```
    being equivalent to
    ```
    while (condition)
    {
      ...
    }
    ```

* Do while loops
  * Are written as follows:
    ```
    wiederhole
      ...
    solange condition
    ```
    being equivalent to
    ```
    do
    {
      ...
    } while (condition)
    ```

* For loops
  * Are written as follows:
    ```
    für i von x bis y mit z wiederhole
      ...
    ```
    being equivalent to
    ```
    for (i = x; i <= y; i += z)
    {
      ...
    }
    ```
  * If `mit z` is ommitted the value defaults to 1
