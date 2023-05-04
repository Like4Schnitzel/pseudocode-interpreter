# pseudocode-interpreter
My teacher really likes pseudocode but I don't, so here's an interpreter to at least make it runnable.
Needs Python 3.10+ to run due to match case statements.

## Docs for the pseudocode
* Operators
  * Mathematical operators
    * +, -, *, /, div, mod, ^, sqrt
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
