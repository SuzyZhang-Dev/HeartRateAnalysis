*** Settings *** 
Documentation   HRV Analysis Logic Acceptance Tests
Library         Collections
Library         ../utils/calculations.py  WITH NAME      Engine

*** Test Cases ***
Verify High Stress Calculation
  [Documentation]      Test case for high stress scenario 
  @{high_stress_data}=    Evaluate    [500, 505, 500, 505, 500, 500]

  ${result}=    Engine.Calculate Metrics    ${high_stress_data}

  Log   Calculated Result:${result}

  ${hr}=    Get From Dictionary    ${result}    mean_hr
  Should Be Equal As Integers   ${hr}        119

  ${sdnn}=  Get From Dictionary   ${result}   SDNN
  Should Be True    ${sdnn} < 5

Verify Normal Relaxation Calculation
  [Documentation]     Test case for relaxation 
  @{relax_data}=    Evaluate     [950, 1050, 980, 1020, 1000]

  ${result}=    Engine.Calculate Metrics    ${relax_data}

  ${hr}=    Get From Dictionary    ${result}    mean_hr
  Should Be Equal As Integers    ${hr}    60
    
  ${sdnn}=    Get From Dictionary    ${result}    SDNN
  Should Be True    ${sdnn} > 20

